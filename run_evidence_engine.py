"""
BIDPROOF - Document Processing & Evidence Retrieval Engine

Connects:
1. PDF document processing
2. Text chunking
3. Evidence retrieval
4. JSON output
"""

import argparse
import json
from pathlib import Path

from bidproof.bidproof.document_processor import extract_pdf_text
from bidproof.bidproof.chunker import chunk_pages
from bidproof.bidproof.evidence_retriever import find_evidence


def process_document(file_path):
    """Extract text from a PDF and split it into chunks."""

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    pages = extract_pdf_text(file_path)

    chunks = chunk_pages(pages)

    return chunks


def run_evidence_engine(
    rfp_path,
    docs_dir="data/company_docs",
    output_path="reports/evidence_results.json"
):
    """Run the BidProof evidence processing pipeline."""

    print("=" * 70)
    print("BIDPROOF: DOCUMENT PROCESSING & EVIDENCE RETRIEVAL ENGINE")
    print("=" * 70)

    # ---------------------------------------------------------
    # STEP 1: Process RFP / Tender document
    # ---------------------------------------------------------

    print("\n[Step 1] Processing RFP / Tender document...")

    rfp_chunks = process_document(rfp_path)

    print(f"✓ RFP processed")
    print(f"✓ RFP chunks created: {len(rfp_chunks)}")

    # ---------------------------------------------------------
    # STEP 2: Process company documents
    # ---------------------------------------------------------

    print("\n[Step 2] Processing company documents...")

    company_dir = Path(docs_dir)

    if not company_dir.exists():
        print(f"⚠ Company document folder not found: {company_dir}")
        company_chunks = []
    else:
        company_chunks = []

        for file_path in company_dir.rglob("*.pdf"):
            try:
                chunks = process_document(file_path)
                company_chunks.extend(chunks)

                print(
                    f"✓ Processed {file_path.name}: "
                    f"{len(chunks)} chunks"
                )

            except Exception as error:
                print(
                    f"⚠ Could not process {file_path.name}: {error}"
                )

    print(f"✓ Total company chunks: {len(company_chunks)}")

    # ---------------------------------------------------------
    # STEP 3: Evidence retrieval
    # ---------------------------------------------------------

    print("\n[Step 3] Retrieving evidence...")

    results = []

    for chunk in rfp_chunks:
        query = chunk.get("text", "")

        if not query.strip():
            continue

        evidence = find_evidence(
            company_chunks,
            query,
            top_k=3
        )

        results.append({
            "query": query,
            "evidence": evidence
        })

    print(f"✓ Evidence retrieval completed")
    print(f"✓ Queries processed: {len(results)}")

    # ---------------------------------------------------------
    # STEP 4: Export results
    # ---------------------------------------------------------

    print("\n[Step 4] Exporting results...")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(f"✓ Results saved to: {output_file}")

    print("\n" + "=" * 70)
    print("BIDPROOF EVIDENCE ENGINE COMPLETE")
    print("=" * 70)

    return results


def main():

    parser = argparse.ArgumentParser(
        description="BIDPROOF Document Processing & Evidence Engine"
    )

    parser.add_argument(
        "--rfp",
        default="data/sample_rfp.pdf",
        help="Path to RFP/Tender PDF"
    )

    parser.add_argument(
        "--docs",
        default="data/company_docs",
        help="Path to company documents"
    )

    parser.add_argument(
        "--out",
        default="reports/evidence_results.json",
        help="Output JSON path"
    )

    args = parser.parse_args()

    run_evidence_engine(
        rfp_path=args.rfp,
        docs_dir=args.docs,
        output_path=args.out
    )


if __name__ == "__main__":
    main()
