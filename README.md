# Stromal Tumor-Infiltrating Lymphocyte (TIL) Scorer

A manual stromal TIL area-percentage calculator for research and pathology education. Enter the eligible intratumoral stromal area and the stromal area occupied by mononuclear inflammatory cells to calculate a **continuous percentage**. The interface supports single measurements and CSV batches.

## Scoring method

`stromal_til_percent = 100 × til_area / stromal_area`

Both inputs must use the same units; `stromal_area > 0` and `0 ≤ til_area ≤ stromal_area`. Areas must be identified and annotated by a qualified reviewer. The tool does **not** read whole-slide images, segment tissue, identify lymphocytes, estimate uncertainty, assign a validated prognostic threshold, or recommend therapy. A percentage of stromal area occupied by TILs is distinct from the proportion of stromal nuclei that are lymphocytes.

When annotating, assess within the invasive tumor, across the eligible tumor area rather than hotspots. Exclude necrotic regions, crush artefact, biopsy-site changes, DCIS-associated and non-tumor stroma; include mononuclear cells (lymphocytes and plasma cells), not granulocytes. See [Salgado et al., 2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC6267863/) and [Hendry et al., 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5564448/).

## Browser application

Open `index.html` in a modern desktop or mobile browser, or use a verified GitHub Pages deployment if enabled. The page uses plain JavaScript with no network dependency, server requirement, Python interpreter, or external libraries. Uploaded CSVs are processed **entirely on-device**; nothing is transmitted or persisted by the app. Do not enter identifiable patient data.

For CSV input, use column names `stromal_area,til_area` and optionally `sample_id` or other metadata; a `stromal_til_percent` column is added during export. Limit: 2 MB / 5,000 records. Invalid rows stop the batch rather than returning partial scores. Spreadsheet-leading formula characters in labels are escaped on export.

## Python CLI

```bash
python -m pip install -e '.[dev]'
til-scorer single --stromal-area 200 --til-area 50
til-scorer batch -i sample.csv -o results.csv
python -m pytest
node --test tests/browser.test.cjs
```

Alternatively run `python til_scorer.py single --stromal-area 200 --til-area 50`. The old generic `v1/v2/v3` weighted-sum interface has been replaced because it did not calculate a valid stromal TIL percentage. Scores are returned as percentages with two decimal places.

## API and separate legacy demonstration

`python cli.py serve --host 127.0.0.1 --port 8000` starts FastAPI. The app is served at `/`; `POST /api/score` accepts JSON such as `{"stromal_area":200,"til_area":50}`. The historical `til-audit-demo`/`cli.py audit` and `/api/audit` endpoints are retained for compatibility, **but their generic thresholds, urgency labels, mock chat, and in-memory audit trail are synthetic demonstrations—not clinical scoring, guideline compliance, emergency triage, or an externally validated security/PHI control**. Do not expose that API directly to untrusted networks. The audit log endpoint requires the `AUDIT_LOGS_TOKEN` environment variable and matching `X-Audit-Token` header. Audit records are in memory only; without a persistent key and secure storage they are not durable evidence.

## Development and deployment

Python ≥3.10 is supported. Tests run with pytest and Node (Node ≥18); `python -m build --wheel` builds the distributable package. Docker starts the optional FastAPI server. The static browser app is suitable for GitHub Pages; `.github/workflows/pages.yml` publishes from `master` when Pages is configured to use **GitHub Actions**. A working live URL should be linked here only after deployment is verified. The browser calculation itself requires no Pyodide/PyScript.

## License

MIT — see [LICENSE](LICENSE).
