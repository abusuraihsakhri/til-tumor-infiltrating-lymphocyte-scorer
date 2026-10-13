"""
FastAPI REST API Server for Til Tumor Infiltrating Lymphocyte Scorer.
"""
from pathlib import Path
import os
import secrets
from fastapi import FastAPI, HTTPException, Response, Header
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from til_scorer import calculate_metrics
from .base import AuditLogger, PHIGuard, SecurityException
from .metrics import GLOBAL_METRICS
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Til Tumor Infiltrating Lymphocyte Scorer API",
    description="Local manual stromal TIL area scorer and a separate synthetic audit demo",
    version="3.1.0",
)


class ChatRequest(BaseModel):
    query: str


class ScoreRequest(BaseModel):
    stromal_area: float = Field(gt=0, allow_inf_nan=False)
    til_area: float = Field(ge=0, allow_inf_nan=False)


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(Path(__file__).resolve().parents[1] / "index.html")


@app.post("/api/score")
def api_score(payload: ScoreRequest):
    try:
        return calculate_metrics(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "til-tumor-infiltrating-lymphocyte-scorer", "scoring": "manual area percentage", "audit": "synthetic demo only", "version": "3.1.0"}


@app.get("/metrics")
def metrics():
    return Response(
        content=GLOBAL_METRICS.export_prometheus_text(),
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
        return dossier.to_dict()
    except SecurityException as exc:
        raise HTTPException(status_code=422, detail="Input contains a disallowed identifier") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Demo operation failed") from exc


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException as exc:
        raise HTTPException(status_code=422, detail="Input contains a disallowed identifier") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Demo operation failed") from exc


@app.get("/api/audit/logs")
def api_audit_logs(x_audit_token: str | None = Header(default=None)):
    expected = os.getenv("AUDIT_LOGS_TOKEN")
    if not expected or not x_audit_token or not secrets.compare_digest(x_audit_token, expected):
        raise HTTPException(status_code=403, detail="Audit log access denied")
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}


app.mount("/web", StaticFiles(directory=Path(__file__).resolve().parents[1] / "web"), name="web")
