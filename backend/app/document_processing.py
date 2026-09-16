"""
Text extraction + chunking.

Pipeline stage: Document Processing -> Text Extraction -> Chunking
(see docs/architecture.md)
"""
import re
import io
from pypdf import PdfReader
import docx


class ExtractionError(Exception):
    pass


def extract_text(file_stream, filename: str) -> str:
    """Extract raw text from an uploaded PDF, DOCX, or TXT file."""
    ext = filename.rsplit(".", 1)[-1].lower()
    try:
        if ext == "pdf":
            reader = PdfReader(file_stream)
            pages = [page.extract_text() or "" for page in reader.pages]
            text = "\n\n".join(pages)
        elif ext == "docx":
            document = docx.Document(file_stream)
            text = "\n".join(p.text for p in document.paragraphs)
        elif ext == "txt":
            raw = file_stream.read()
            text = raw.decode("utf-8", errors="ignore") if isinstance(raw, bytes) else raw
        else:
            raise ExtractionError(f"Unsupported file type: {ext}")
    except ExtractionError:
        raise
    except Exception as exc:
        raise ExtractionError(f"Could not read {ext.upper()} file: {exc}") from exc

    text = text.strip()
    if not text:
        raise ExtractionError(
            "No readable text was found in this document. It may be a scanned "
            "image without embedded text (OCR is not enabled in this build)."
        )
    return text


HEADING_PATTERN = re.compile(
    r"^\s*(?:\d+\.\s*)?([A-Z][A-Za-z /&\-]{3,60})\s*:?\s*$"
)


def _guess_section_label(paragraph: str, fallback_index: int) -> str:
    first_line = paragraph.strip().split("\n")[0].strip()
    match = HEADING_PATTERN.match(first_line)
    if match and len(first_line) < 70:
        return match.group(1).strip().title()
    return f"Section {fallback_index}"


def chunk_text(text: str, target_chars: int = 900, overlap: int = 120):
    """
    Split text into clause-sized chunks, splitting on paragraph/heading
    boundaries where possible rather than raw character counts, so each
    chunk is a reasonably coherent unit for retrieval.

    Returns a list of dicts: {content, section_label, char_start}
    """
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        paragraphs = [text]

    chunks = []
    buffer = ""
    buffer_start = 0
    running_offset = 0
    section_counter = 0

    def flush(label):
        nonlocal buffer, buffer_start
        if buffer.strip():
            chunks.append(
                {
                    "content": buffer.strip(),
                    "section_label": label,
                    "char_start": buffer_start,
                }
            )
        buffer = ""

    for para in paragraphs:
        section_counter += 1
        label = _guess_section_label(para, section_counter)

        if len(buffer) + len(para) > target_chars and buffer:
            flush(label)  # flush with the current paragraph's label
            # keep a small overlap for context continuity
            buffer = buffer[-overlap:] if overlap else ""
            buffer_start = running_offset

        if not buffer:
            buffer_start = running_offset
        buffer += ("\n\n" if buffer else "") + para
        running_offset += len(para) + 2

        if len(buffer) >= target_chars:
            flush(label)

    flush(chunks[-1]["section_label"] if chunks else "Section 1")

    # Re-label each flushed chunk with its own best-guess heading
    for i, c in enumerate(chunks):
        guess = _guess_section_label(c["content"], i + 1)
        c["section_label"] = guess

    return chunks
