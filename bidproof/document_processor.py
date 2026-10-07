import fitz
from pathlib import Path


def extract_pdf_text(pdf_path):
    """
    Extract text from a PDF while preserving
    the document name and page number.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"File not found: {pdf_path}")

    document = fitz.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text("text")

        pages.append({
            "document": pdf_path.name,
            "page": page_number,
            "text": text.strip()
        })

    document.close()

    return pages


def process_document(pdf_path):
    """
    Process a PDF and return extracted page-level content.
    """

    pages = extract_pdf_text(pdf_path)

    return {
        "document": Path(pdf_path).name,
        "total_pages": len(pages),
        "pages": pages
    }
