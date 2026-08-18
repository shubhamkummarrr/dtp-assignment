import fitz  # PyMuPDF
import docx
import os


def extract_text(file_path: str, file_type: str) -> str:
    """
    File type ke basis pe text extract karta hai
    Supports: PDF, DOCX, TXT
    """
    try:
        if file_type == 'pdf':
            return _extract_from_pdf(file_path)
        elif file_type == 'docx':
            return _extract_from_docx(file_path)
        elif file_type == 'txt':
            return _extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    except Exception as e:
        raise Exception(f"Text extraction failed: {str(e)}")


def _extract_from_pdf(file_path: str) -> str:
    """PDF se text extract karo PyMuPDF se"""
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()

    if not text.strip():
        raise ValueError("PDF is empty or contains no extractable text")

    return text.strip()


def _extract_from_docx(file_path: str) -> str:
    """DOCX se text extract karo python-docx se"""
    doc = docx.Document(file_path)
    text = "\n".join([
        paragraph.text
        for paragraph in doc.paragraphs
        if paragraph.text.strip()
    ])

    if not text.strip():
        raise ValueError("DOCX is empty or contains no extractable text")

    return text.strip()


def _extract_from_txt(file_path: str) -> str:
    """TXT file simply read karo"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    if not text.strip():
        raise ValueError("TXT file is empty")

    return text.strip()


def get_file_type(file_name: str) -> str:
    """File extension se type determine karo"""
    ext = os.path.splitext(file_name)[1].lower()
    type_map = {
        '.pdf': 'pdf',
        '.docx': 'docx',
        '.txt': 'txt',
    }
    if ext not in type_map:
        raise ValueError(f"Unsupported file type: {ext}. Only PDF, DOCX, TXT allowed.")

    return type_map[ext]