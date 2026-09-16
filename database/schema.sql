-- LexiGuide AI — production MySQL schema
-- The app runs on SQLite by default for zero-setup demos (see backend/.env.example).
-- Point DATABASE_URL at a MySQL instance built from this file for production use.

CREATE DATABASE IF NOT EXISTS lexiguide CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE lexiguide;

CREATE TABLE users (
    id            CHAR(36) PRIMARY KEY,
    name          VARCHAR(120) NOT NULL,
    email         VARCHAR(160) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE documents (
    id                CHAR(36) PRIMARY KEY,
    user_id           CHAR(36) NULL,
    filename          VARCHAR(255) NOT NULL,
    file_type         VARCHAR(10) NOT NULL,
    document_type     VARCHAR(80) NULL,
    status            VARCHAR(30) DEFAULT 'uploaded',
    raw_text_excerpt  TEXT NULL,           -- short excerpt only; full text is not persisted in DB
    char_count        INT DEFAULT 0,
    is_demo           BOOLEAN DEFAULT FALSE,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE document_chunks (
    id            CHAR(36) PRIMARY KEY,
    document_id   CHAR(36) NOT NULL,
    chunk_index   INT NOT NULL,
    content       TEXT NOT NULL,
    section_label VARCHAR(120) NULL,
    char_start    INT DEFAULT 0,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    INDEX idx_document_chunks_doc (document_id)
);

CREATE TABLE analyses (
    id                        CHAR(36) PRIMARY KEY,
    document_id               CHAR(36) NOT NULL,
    executive_summary         TEXT,
    key_points                JSON,
    your_obligations          JSON,
    other_party_obligations   JSON,
    important_dates           JSON,
    financial_terms           JSON,
    parties                   JSON,
    governing_law             VARCHAR(255),
    attention_score           INT DEFAULT 0,
    created_at                DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE TABLE clauses (
    id               CHAR(36) PRIMARY KEY,
    document_id      CHAR(36) NOT NULL,
    clause_type      VARCHAR(80),
    original_text    TEXT,
    plain_explanation TEXT,
    why_it_matters   TEXT,
    what_to_check    JSON,
    section_label    VARCHAR(120),
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE TABLE risk_findings (
    id                  CHAR(36) PRIMARY KEY,
    document_id         CHAR(36) NOT NULL,
    clause_snippet      TEXT,
    risk_level          ENUM('high','medium','low','standard'),
    category            VARCHAR(80),
    explanation         TEXT,
    why_it_matters      TEXT,
    suggested_question  TEXT,
    section_label       VARCHAR(120),
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE TABLE chat_sessions (
    id          CHAR(36) PRIMARY KEY,
    document_id CHAR(36) NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE TABLE chat_messages (
    id          CHAR(36) PRIMARY KEY,
    session_id  CHAR(36) NOT NULL,
    role        ENUM('user','assistant') NOT NULL,
    content     TEXT NOT NULL,
    source_label VARCHAR(255) NULL,
    confidence  ENUM('high','medium','low','not_found') NULL,
    answer_type VARCHAR(30) NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
);

CREATE TABLE checklists (
    id           CHAR(36) PRIMARY KEY,
    document_id  CHAR(36) NOT NULL,
    text         VARCHAR(500),
    explanation  TEXT,
    is_done      BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE TABLE document_comparisons (
    id             CHAR(36) PRIMARY KEY,
    document_a_id  CHAR(36) NOT NULL,
    document_b_id  CHAR(36) NOT NULL,
    added          JSON,
    removed        JSON,
    modified       JSON,
    plain_summary  TEXT,
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_a_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (document_b_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE TABLE lawyer_questions (
    id                  CHAR(36) PRIMARY KEY,
    document_id         CHAR(36) NOT NULL,
    summary_for_lawyer  TEXT,
    questions           JSON,
    documents_to_bring  JSON,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);
