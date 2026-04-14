import io
from pypdf import PdfReader
from app.core.logging import get_logger

logger = get_logger("pdf_service")

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from a PDF file provided as bytes.
    """
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {str(e)}")
        raise RuntimeError(f"Could not extract text from PDF: {str(e)}")
