import pytest
from app.models import Document, DocumentChunk
from app.extensions import db

def test_document_creation(app):
    with app.app_context():
        doc = Document(
            filename="test.pdf",
            file_type="pdf",
            char_count=100,
            status="processed"
        )
        db.session.add(doc)
        db.session.commit()
        
        saved_doc = db.session.get(Document, doc.id)
        assert saved_doc is not None
        assert saved_doc.filename == "test.pdf"

def test_document_chunk_creation(app):
    with app.app_context():
        doc = Document(
            filename="test2.pdf",
            file_type="pdf",
            char_count=200,
            status="processed"
        )
        db.session.add(doc)
        db.session.commit()

        chunk = DocumentChunk(
            document_id=doc.id,
            chunk_index=0,
            content="This is another test document."
        )
        db.session.add(chunk)
        db.session.commit()

        saved_chunk = db.session.get(DocumentChunk, chunk.id)
        assert saved_chunk is not None
        assert saved_chunk.document_id == doc.id
        assert saved_chunk.content == "This is another test document."
