# ERIDSS: Enterprise Risk Intelligence & Decision Support System

ERIDSS is an enterprise document processing, intelligence extraction, and risk analysis platform. It automates the parsing of complex enterprise documents, executes zero-shot Named Entity Recognition (NER) and Relation Extraction (RE) via GLiNER and GLiREL, constructs document-level knowledge graphs, and provides interactive visualization alongside Neo4j graph synchronization.

---

## Key Features

- **Document Ingestion & Parsing:** Upload PDF and TXT files with automated text and layout extraction.
- **Entity & Relation Extraction:** Zero-shot NER using **GLiNER** and relation classification using **GLiREL** to discover entities (`vendor`, `technology`, `location`, `policy`, `contract`, `person`) and cross-entity relationships without task-specific fine-tuning.
- **Knowledge Graph Construction:** Maps structured relations into directed graph payloads (`nodes` and `edges`) persisted directly in PostgreSQL.
- **Interactive Graph UI:** Cytoscape.js canvas for interactive visualization, layout positioning (CoSE force-directed layout), node/edge inspection, and metadata exploration.
- **Graph Database Synchronization:** Direct export pipeline to sync verified knowledge graph structures to **Neo4j** for downstream graph analytics and enterprise risk path discovery.
- **Role-Based Document Management:** Multi-user authentication, JWT authorization, document status tracking, and download/preview services.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React (Vite), Cytoscape.js, `react-cytoscapejs`, Axios, React Router |
| **Backend** | FastAPI, Python 3.10+, Uvicorn, Pydantic |
| **Database & ORM** | PostgreSQL, SQLAlchemy |
| **NLP & Graph Models** | GLiNER (Named Entity Recognition), GLiREL (Relation Extraction) |
| **Graph Database** | Neo4j (Target Graph Store) |

---

## Architecture Overview

```text
               +--------------------------------------------------+
               |                  React Client                    |
               |  - Cytoscape.js Graph Canvas & Entity Inspector  |
               |  - Document Management & Upload UI               |
               +------------------------+-------------------------+
                                        | HTTP / REST (JWT Auth)
                                        v
               +--------------------------------------------------+
               |                  FastAPI Backend                 |
               |  - Document & Processing Pipeline Endpoints      |
               |  - GLiNER Entity Extraction Pipeline             |
               |  - GLiREL Relation Classification Engine         |
               +------------+-------------------------+-----------+
                            |                         |
                            v                         v
               +------------------------+   +---------------------+
               |   PostgreSQL Database  |   |    Neo4j Database   |
               | - users, documents     |   | - Knowledge Graph   |
               | - extracted_text       |   | - Risk Traversal    |
               | - entities, relations  |   | - Multi-hop Queries |
               | - knowledge_graphs     |   +---------------------+
               +------------------------+
