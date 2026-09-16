import uuid
import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


def gen_id():
    return str(uuid.uuid4())


class JSONText(db.TypeDecorator):
    """Stores a Python object as JSON text (portable across SQLite/MySQL)."""
    impl = db.Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return json.dumps(value) if value is not None else None

    def process_result_value(self, value, dialect):
        return json.loads(value) if value else None


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(36), primary_key=True, default=gen_id)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    documents = db.relationship("Document", backref="owner", lazy=True)

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)


class Document(db.Model):
    __tablename__ = "documents"
    id = db.Column(db.String(36), primary_key=True, default=gen_id)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    document_type = db.Column(db.String(80), nullable=True)  # e.g. "Employment Agreement"
    status = db.Column(db.String(30), default="uploaded")  # uploaded, processing, analyzed, failed
    raw_text_excerpt = db.Column(db.Text, nullable=True)  # short excerpt only, not full sensitive text
    char_count = db.Column(db.Integer, default=0)
    is_demo = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    chunks = db.relationship("DocumentChunk", backref="document", lazy=True, cascade="all,delete")
    analysis = db.relationship("Analysis", backref="document", uselist=False, cascade="all,delete")
    clauses = db.relationship("Clause", backref="document", lazy=True, cascade="all,delete")
    risk_findings = db.relationship("RiskFinding", backref="document", lazy=True, cascade="all,delete")
    checklist_items = db.relationship("ChecklistItem", backref="document", lazy=True, cascade="all,delete")

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "file_type": self.file_type,
            "document_type": self.document_type,
            "status": self.status,
            "char_count": self.char_count,
            "is_demo": self.is_demo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DocumentChunk(db.Model):
    __tablename__ = "document_chunks"
    id = db.Column(db.String(36), primary_key=True, default=gen_id)
    document_id = db.Column(db.String(36), db.ForeignKey("documents.id"), nullable=False, index=True)
    chunk_index = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    section_label = db.Column(db.String(120), nullable=True)  # heading guess, used as "page/section"
    char_start = db.Column(db.Integer, default=0)


class Analysis(db.Model):
    __tablename__ = "analyses"
    id = db.Column(db.String(36), primary_key=True, default=gen_id)
    document_id = db.Column(db.String(36), db.ForeignKey("documents.id"), nullable=False, index=True)
    executive_summary = db.Column(db.Text)
    key_points = db.Column(JSONText)
    your_obligations = db.Column(JSONText)
    other_party_obligations = db.Column(JSONText)
    important_dates = db.Column(JSONText)
    financial_terms = db.Column(JSONText)
    parties = db.Column(JSONText)
    governing_law = db.Column(db.String(255))
    attention_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "executive_summary": self.executive_summary,
            "key_points": self.key_points or [],
            "your_obligations": self.your_obligations or [],
            "other_party_obligations": self.other_party_obligations or [],
            "important_dates": self.important_dates or [],
            "financial_terms": self.financial_terms or [],
            "parties": self.parties or [],
            "governing_law": self.governing_law,
            "attention_score": self.attention_score,
        }


class Clause(db.Model):
    __tablename__ = "clauses"
    id = db.Column(db.String(36), primary_key=True, default=gen_id)
    document_id = db.Column(db.String(36), db.ForeignKey("documents.id"), nullable=False, index=True)
    clause_type = db.Column(db.String(80))  # Termination, Liability, IP, etc.
    original_text = db.Column(db.Text)
    plain_explanation = db.Column(db.Text)
    why_it_matters = db.Column(db.Text)
    what_to_check = db.Column(JSONText)
    section_label = db.Column(db.String(120))
    negotiation_tips = db.Column(JSONText, nullable=True)  # USP: cached negotiation tips

    def to_dict(self):
        return {
            "id": self.id,
            "clause_type": self.clause_type,
            "original_text": self.original_text,
            "plain_explanation": self.plain_explanation,
            "why_it_matters": self.why_it_matters,
            "what_to_check": self.what_to_check or [],
            "section_label": self.section_label,
            "negotiation_tips": self.negotiation_tips,  # None until generated
        }


class RiskFinding(db.Model):
    __tablename__ = "risk_findings"
    id = db.Column(db.String(36), primary_key=True, default=gen_id)
    document_id = db.Column(db.String(36), db.ForeignKey("documents.id"), nullable=False, index=True)
    clause_snippet = db.Column(db.Text)
    risk_level = db.Column(db.String(20))  # high, medium, low, standard
    category = db.Column(db.String(80))
    explanation = db.Column(db.Text)
    why_it_matters = db.Column(db.Text)
    suggested_question = db.Column(db.Text)
    section_label = db.Column(db.String(120))

    def to_dict(self):
        return {
            "id": self.id,
            "clause_snippet": self.clause_snippet,
            "risk_level": self.risk_level,
            "category": self.category,
            "explanation": self.explanation,
            "why_it_matters": self.why_it_matters,
            "suggested_question": self.suggested_question,
            "section_label": self.section_label,
        }


class ChatSession(db.Model):
    __tablename__ = "chat_sessions"
    id = db.Column(db.String(36), primary_key=True, default=gen_id)
    document_id = db.Column(db.String(36), db.ForeignKey("documents.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    messages = db.relationship("ChatMessage", backref="session", lazy=True, cascade="all,delete")


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"
    id = db.Column(db.String(36), primary_key=True, default=gen_id)
    session_id = db.Column(db.String(36), db.ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = db.Column(db.String(10))  # user | assistant
    content = db.Column(db.Text)
    source_label = db.Column(db.String(255), nullable=True)
    confidence = db.Column(db.String(20), nullable=True)  # high, medium, low, not_found
    answer_type = db.Column(db.String(30), nullable=True)  # document_based, general_info, needs_review
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "source_label": self.source_label,
            "confidence": self.confidence,
            "answer_type": self.answer_type,
        }


class ChecklistItem(db.Model):
    __tablename__ = "checklists"
    id = db.Column(db.String(36), primary_key=True, default=gen_id)
    document_id = db.Column(db.String(36), db.ForeignKey("documents.id"), nullable=False, index=True)
    text = db.Column(db.String(500))
    explanation = db.Column(db.Text)
    is_done = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {"id": self.id, "text": self.text, "explanation": self.explanation, "is_done": self.is_done}


class DocumentComparison(db.Model):
    __tablename__ = "document_comparisons"
    id = db.Column(db.String(36), primary_key=True, default=gen_id)
    document_a_id = db.Column(db.String(36), db.ForeignKey("documents.id"), nullable=False, index=True)
    document_b_id = db.Column(db.String(36), db.ForeignKey("documents.id"), nullable=False, index=True)
    added = db.Column(JSONText)
    removed = db.Column(JSONText)
    modified = db.Column(JSONText)
    plain_summary = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "added": self.added or [],
            "removed": self.removed or [],
            "modified": self.modified or [],
            "plain_summary": self.plain_summary,
        }


class LawyerPrep(db.Model):
    __tablename__ = "lawyer_questions"
    id = db.Column(db.String(36), primary_key=True, default=gen_id)
    document_id = db.Column(db.String(36), db.ForeignKey("documents.id"), nullable=False, index=True)
    summary_for_lawyer = db.Column(db.Text)
    questions = db.Column(JSONText)
    documents_to_bring = db.Column(JSONText)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "summary_for_lawyer": self.summary_for_lawyer,
            "questions": self.questions or [],
            "documents_to_bring": self.documents_to_bring or [],
        }
