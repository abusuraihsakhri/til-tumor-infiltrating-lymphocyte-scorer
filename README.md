# Til Tumor Infiltrating Lymphocyte Scorer

> **Domain:** Digital Pathology & Quantitative Histopathology  
> **Reference Guidelines & Standards:** `College of American Pathologists (CAP) Synoptic Protocols & DICOM WSI`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Stromal TILs Immunotherapy Scorer
Quantifies percentage stromal Tumor-Infiltrating Lymphocytes (sTILs) according to International Immuno-Oncology Guidelines.

Zero-dependency Python implementation with single and batch evaluation.
Author: Dr. Abu Suraih Sakhri
License: MIT

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`calculate_metrics()`**: Core domain algorithm for til-tumor-infiltrating-lymphocyte-scorer.
- **`process_single()`** — calculates and validates process_single parameters.
- **`process_batch()`** — calculates and validates process_batch parameters.
- **`main()`** — calculates and validates main parameters.

---

## 📐 Mathematical Formulation & Logic

```text
  score = primary_val
  rounded_score = round(score, 2)
  res = calculate_metrics(**kwargs)
  calc_res = calculate_metrics(**r)
```

---

## 💻 CLI Quickstart & Usage

### Installation
```bash
pip install -r pyproject.toml
# or for development:
pip install -e ".[dev]"
```

### 1. Single Case Evaluation
```bash
# Using til_scorer.py directly
python til_scorer.py single --v1 14.5 --v2 4.2 --v3 1.8

# Using the enterprise CLI with supervisor
python cli.py audit --task-id TASK-001 --target SPECIMEN-01 --primary 28.5 --secondary 14.2
```

### 2. Batch CSV Processing
```bash
# Using til_scorer.py
python til_scorer.py batch -i sample.csv -o results.csv

# Using the enterprise CLI
python cli.py batch -i sample.csv -o results.csv
```

### Input Data Schema for Enterprise CLI Batch Mode

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task/case identifier | Required |
| `target_identifier` | Entity or specimen identifier | Required |
| `primary_metric` | Primary measurement value | Required |
| `secondary_metric` | Secondary measurement value | Optional (default: 0.0) |
| `status_descriptor` | Status code (e.g., NOMINAL, DISCORDANT_ANOMALY) | Optional (default: NOMINAL) |
| `is_critical_flag` | Emergency escalation flag (true/false) | Optional (default: false) |

### Input Data Schema for til_scorer.py Batch Mode

| Field | Description | Requirement |
|:------|:------------|:------------|
| `v1` | Primary parameter | Required |
| `v2` | Secondary parameter | Optional |
| `v3` | Tertiary parameter | Optional |

### 3. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 4. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### 5. Chat with Supervisor
```bash
python cli.py chat "Explain the scoring methodology"
```

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Run with coverage:

```bash
pytest -v --cov=. --cov-report=term-missing
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t til-tumor-infiltrating-lymphocyte-scorer .
docker run -p 8000:8000 til-tumor-infiltrating-lymphocyte-scorer
```
