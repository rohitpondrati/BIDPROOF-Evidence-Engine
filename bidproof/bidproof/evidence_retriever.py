def find_evidence(chunks, query, top_k=5):
    """
    Find the most relevant document chunks for a given query.
    Uses simple keyword matching as the initial retrieval method.
    """

    query_words = set(query.lower().split())
    results = []

    for chunk in chunks:
        text = chunk.get("text", "")
        text_words = set(text.lower().split())

        score = len(query_words.intersection(text_words))

        if score > 0:
            results.append({
                "document": chunk.get("document"),
                "page": chunk.get("page"),
                "text": text,
                "score": score
            })

    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:top_k]
