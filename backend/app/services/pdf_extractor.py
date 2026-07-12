from pathlib import Path

import pdfplumber


def extract_pdf_text(file_path: Path) -> str:
    """
    Extract text from a PDF file.
    """

    text = []

    with pdfplumber.open(file_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text.append(page_text)

    return "\n".join(text)