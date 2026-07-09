from pypdf import PdfReader
from pypdf.errors import PdfReadError, PdfStreamError

def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text

    except (PdfReadError, PdfStreamError, Exception):
        return ""