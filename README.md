# 🛡️ BIDPROOF: Document Processing & Grounded Evidence Engine

> **Self-Contained Module Package for RFP Ingestion, Multi-Format Document Parsing & Citation-Grounded Evidence Retrieval**

---

## 📌 Overview

This package contains the complete, self-contained **Document Processing + Evidence Engine** developed for the **BIDPROOF** project.

It provides an end-to-end evidence discovery pipeline:
1. **Multi-Format Tender/RFP Ingestion**: Parses PDFs, JSON, or text tenders into structured requirement objects while preserving exact page and clause references.
2. **Multi-Format Company Document Indexing**: Indexes company knowledge bases (PDFs, TXT, MD, DOCX) preserving 1-indexed page numbers and section headers.
3. **Citation-Grounded Hybrid Retrieval**: Combines BM25 sparse keyword matching (for strict codes, e.g. ISO 27001, 99.9%, SOC 2) with semantic overlap to discover candidate evidence.
4. **Standardized Contract Output**: Emits a deterministic JSON output schema containing requirement ID, verbatim evidence text, source document, page number, section header, confidence score, and status.

---

## ⚙️ 1. Installation

### Requirements
- Python 3.10+ (tested and verified on Python 3.11.9)

### Install Dependencies
Run from the root of this folder:
```powershell
pip install -r requirements.txt
```

> **Dependencies**:
> - `pypdf>=3.0.0` (Native PDF document parsing and page-by-page text extraction)
> - `python-docx>=0.8.11` (Word document support)
> - Standard library (`dataclasses`, `json`, `math`, `re`, `pathlib`) for zero runtime overhead.

---

## 🚀 2. How to Run

### Command-Line Execution
Run the standalone engine with default sample data (Smart City IoT RFP + Company Corpus):
```powershell
python run_evidence_engine.py
```

### Custom Inputs & Outputs
You can pass custom RFP and company document directories:
```powershell
python run_evidence_engine.py --rfp "data/sample_rfp.pdf" --docs "data/company_docs" --out "reports/evidence_results.json"
```

### Run Unit Tests
To verify all module features (PDF extraction, page preservation, schema conformity):
```powershell
python -m unittest discover -s tests -p "test_*.py"
```

---

## 📥 3. Input Formats

### Tender / RFP Documents (`--rfp`)
Supports three formats:
1. **PDF (`.pdf`)**: Native multi-page RFP documents (e.g. `data/sample_rfp.pdf`). Parses clauses and automatically extracts page citations (e.g. `Section 1.1 (Page 1)`).
2. **JSON (`.json`)**: Structured tender schema containing `tender_id`, `tender_title`, and an array of `requirements` with threshold constraints (e.g. `data/sample_rfp.json`).
3. **Text / Markdown (`.txt`, `.md`)**: Raw text tenders decomposed via clause header heuristics.

### Company Knowledge Base (`--docs`)
A directory containing company evidence records:
- **Formats supported**: `.pdf`, `.txt`, `.md`, `.docx`, `.json`, `.csv`.
- Every chunk automatically tracks:
  - `source_file`: File name (e.g., `doc7_disaster_recovery_policy.pdf`).
  - `page_number`: Actual 1-indexed page where text appears.
  - `section_header`: Section title or heading preceding the passage.

---

## 📤 4. Final Output Format (Standard JSON Specification)

The engine saves the retrieved evidence to `reports/evidence_results.json` (or your `--out` path).

```json
{
  "tender_id": "RFP-2026-MUNI-98",
  "total_requirements": 6,
  "evidence_found_count": 6,
  "evidence": [
    {
      "requirement_id": "REQ-01",
      "clause_reference": "Section 3.1.1 (Eligibility)",
      "status": "EVIDENCE_FOUND",
      "confidence": 0.99,
      "evidence_text": "This certificate confirms that the Information Security Management System operates in complete compliance with ISO/IEC 27001:2022 requirements.",
      "source_document": "doc1_iso_certificate.txt",
      "page_number": 1,
      "section": "Key Certification Dates:",
      "matched_terms": [
        "ISO 27001",
        "certification",
        "surveillance audit"
      ],
      "candidates": [
        {
          "chunk": {
            "chunk_id": "doc1_iso_certificate_p1_c4",
            "source_file": "doc1_iso_certificate.txt",
            "doc_title": "Doc1 Iso Certificate",
            "section_header": "Key Certification Dates:",
            "content": "Accreditation Body: Global Security Certifications Board (GSCB / IAF MLA signatory). This certificate confirms that the Information Security Management System operates in complete compliance with ISO/IEC 27001:2022 requirements.",
            "line_number": 14,
            "page_number": 1
          },
          "relevance_score": 16.6164,
          "verbatim_snippet": "This certificate confirms that the Information Security Management System operates in complete compliance with ISO/IEC 27001:2022 requirements."
        }
      ]
    }
  ]
}
```

### Output Schema Fields:
| Field | Type | Description |
|:---|:---|:---|
| `requirement_id` | `string` | Unique identifier matching the RFP clause (e.g. `REQ-01`). |
| `clause_reference` | `string` | Clause title, section number, and page citation. |
| `status` | `string` | `EVIDENCE_FOUND`, `INSUFFICIENT_EVIDENCE`, or `NO_EVIDENCE_FOUND`. |
| `confidence` | `float` | Normalized confidence score ($0.00$ to $1.00$). |
| `evidence_text` | `string` | Verbatim sentence/passage proving or addressing the clause. |
| `source_document` | `string` | Name of the file containing the citation. |
| `page_number` | `int` | Exact 1-indexed page number of the source document. |
| `section` | `string` | Section header where the evidence was located. |
| `matched_terms` | `list[str]` | Keywords from the RFP matched in the evidence text. |
| `candidates` | `list[dict]` | Full list of top $K$ candidate passages with scores. |

---

## 🤝 5. How Team Members Can Connect Their Modules

### Option 1: Direct Python In-Memory API (For Verification / Reasoning Modules)
Teammates building the **Verification Engine** or **LLM Agent** can directly import and call this module:

```python
from bidproof.module1_extraction.extractor import RequirementExtractor
from bidproof.module2_retrieval.retriever import EvidenceRetriever

# 1. Ingest Tender / RFP (PDF, JSON, or TXT)
extractor = RequirementExtractor()
tender = extractor.extract_from_file("data/sample_rfp.json")

# 2. Index Company Documents
retriever = EvidenceRetriever(top_k=3)
retriever.index_directory("data/company_docs")

# 3. Retrieve Evidence
result = retriever.retrieve_all_requirements(tender.requirements, tender_id=tender.tender_id)

# 4. Access evidence objects
for bundle in result.evidence_bundles:
    print(f"[{bundle.requirement_id}] Status: {bundle.status} (Confidence: {bundle.confidence:.2f})")
    print(f"Citation: {bundle.source_document} (Page {bundle.page_number}, {bundle.section})")
    print(f"Quote: \"{bundle.evidence_text}\"\n")
```

### Option 2: File-Based JSON Hand-Off (For UI Dashboard / REST API)
1. Run the CLI:
   ```powershell
   python run_evidence_engine.py --rfp "data/sample_rfp.json" --out "reports/evidence_results.json"
   ```
2. In the UI or downstream service, read `evidence_results.json`:
   ```python
   import json

   with open("reports/evidence_results.json", "r", encoding="utf-8") as f:
       data = json.load(f)

   for item in data["evidence"]:
       print(item["requirement_id"], item["source_document"], item["page_number"])
   ```

---

## 📂 Package File Manifest

```
bidproof_evidence_engine/
├── README.md                                 # This guide
├── requirements.txt                          # Dependencies
├── .gitignore                                # Git ignore file
├── run_evidence_engine.py                    # Standalone CLI entrypoint
├── bidproof/
│   ├── __init__.py                           # Package init
│   ├── config.py                             # Configuration & default paths
│   ├── document_loader.py                    # Multi-format document parser (PDF, DOCX, TXT)
│   ├── module1_extraction/                   # Module 1: Ingestion & Clause Extraction
│   │   ├── __init__.py
│   │   ├── extractor.py                      # PDF, JSON, and text tender parser
│   │   └── models.py                         # Requirement, MandatoryLevel, Category models
│   └── module2_retrieval/                    # Module 2: Grounded Evidence Retrieval
│       ├── __init__.py
│       ├── retriever.py                      # Hybrid BM25 + key-term retrieval engine
│       └── models.py                         # DocumentChunk, EvidenceCandidate, EvidenceBundle
├── data/
│   ├── sample_rfp.json                       # Sample JSON tender (6 clauses)
│   ├── sample_rfp.pdf                        # Sample multi-page PDF tender
│   └── company_docs/                         # Sample company documents
│       ├── doc1_iso_certificate.txt          # Active ISO 27001 certificate
│       ├── doc2_cloud_infrastructure_sla.txt # 99.9% uptime SLA policy
│       ├── doc3_past_projects_iot.txt        # Past commercial project track record
│       ├── doc4_financial_audit_2023.txt     # Audited annual revenue statement
│       ├── doc5_security_compliance.txt      # SOC 2 attestation report
│       ├── doc6_company_profile.txt          # Corporate profile & office locations
│       └── doc7_disaster_recovery_policy.pdf # Multi-page PDF policy document
├── reports/                                  # Default output directory for JSON results
└── tests/                                    # Automated unit test suite
    ├── test_module1_extraction.py            # Tests for RFP extraction
    ├── test_module2_retrieval.py             # Tests for company doc indexing & retrieval
    └── test_pdf_and_evidence_engine.py       # Tests for PDF parsing & output JSON schema
```
