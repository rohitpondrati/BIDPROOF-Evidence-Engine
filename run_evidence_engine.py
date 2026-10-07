"""
BIDPROOF - Document Processing & Evidence Retrieval Engine CLI
This script runs Module 1 (Tender Ingestion) & Module 2 (Evidence Retrieval).
Generates standardized evidence JSON for downstream verification and reporting modules.
"""
import argparse
import json
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from bidproof.module1_extraction.extractor import RequirementExtractor
from bidproof.module2_retrieval.retriever import EvidenceRetriever


def run_evidence_engine(
    rfp_path: str = "data/sample_rfp.json",
    docs_dir: str = "data/company_docs",
    output_path: str = "reports/evidence_results.json",
):
    print("================================================================================")
    print("🔍 BIDPROOF: DOCUMENT PROCESSING & EVIDENCE RETRIEVAL ENGINE")
    print("================================================================================")

    # 1. Document Extraction (Module 1)
    rfp_file = Path(rfp_path)
    print(f"\n[Step 1] Ingesting RFP / Tender Document: {rfp_file}")
    extractor = RequirementExtractor()
    tender = extractor.extract_from_file(rfp_file)
    print(f"  ✓ Tender Title: {tender.tender_title}")
    print(f"  ✓ Extracted Requirements: {len(tender.requirements)} clauses")

    # 2. Document Ingestion & Chunking (Module 2)
    company_dir = Path(docs_dir)
    print(f"\n[Step 2] Indexing Company Knowledge Base from: {company_dir}")
    retriever = EvidenceRetriever(top_k=3)
    chunk_count = retriever.index_directory(company_dir)
    print(f"  ✓ Indexed Chunks: {chunk_count} passages across company documents (PDF, TXT, etc.)")

    # 3. Grounded Evidence Retrieval
    print(f"\n[Step 3] Retrieving Grounded Evidence for Each Requirement...")
    result = retriever.retrieve_all_requirements(tender.requirements, tender_id=tender.tender_id)

    # 4. Display Results Summary
    print("\n--------------------------------------------------------------------------------")
    print(f"{'Req ID':<8} | {'Status':<20} | {'Conf':<6} | {'Source Document (Page, Section)':<35}")
    print("--------------------------------------------------------------------------------")

    for bundle in result.evidence_bundles:
        status_str = bundle.status
        source_cite = f"{bundle.source_document} (P.{bundle.page_number}, {bundle.section[:15]})"
        print(f"{bundle.requirement_id:<8} | {status_str:<20} | {bundle.confidence:<6.2f} | {source_cite:<35}")
        clean_text = bundle.evidence_text.replace("\n", " ").strip()
        if len(clean_text) > 85:
            clean_text = clean_text[:82] + "..."
        print(f"         Evidence: \"{clean_text}\"\n")

    # 5. Export JSON
    out_file = Path(output_path)
    retriever.export_evidence_json(result, out_file)
    print("================================================================================")
    print(f"✅ Evidence Retrieval Complete! Total Found: {result.evidence_found_count}/{result.total_requirements}")
    print(f"📁 Exported Standard JSON: {out_file.resolve()}")
    print("================================================================================")
    return result


def main():
    parser = argparse.ArgumentParser(description="BIDPROOF Document Processing & Evidence Engine")
    parser.add_argument("--rfp", default="data/sample_rfp.json", help="Path to Tender/RFP document (PDF, JSON, or TXT)")
    parser.add_argument("--docs", default="data/company_docs", help="Path to company documents folder")
    parser.add_argument("--out", default="reports/evidence_results.json", help="Path to save output JSON")

    args = parser.parse_args()
    run_evidence_engine(rfp_path=args.rfp, docs_dir=args.docs, output_path=args.out)


if __name__ == "__main__":
    main()
