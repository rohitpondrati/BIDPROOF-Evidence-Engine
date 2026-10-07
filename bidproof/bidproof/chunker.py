def chunk_pages(pages, chunk_size=1000):
    """
    Split extracted page text into smaller chunks
    while preserving document name and page number.
    """

    chunks = []

    for page in pages:
        text = page["text"]
        document = page["document"]
        page_number = page["page"]

        if not text:
            continue

        for start in range(0, len(text), chunk_size):
            chunk_text = text[start:start + chunk_size]

            chunks.append({
                "document": document,
                "page": page_number,
                "text": chunk_text
            })

    return chunks
