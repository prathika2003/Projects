from pathlib import Path

from docx import Document
from PyPDF2 import PdfReader


def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def extract_resume_text(file_path):
    """Extract text from supported resume formats."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()

    if suffix == ".docx":
        document = Document(str(path))
        return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()

    raise ValueError("Unsupported resume format. Please upload a PDF or DOCX file.")
