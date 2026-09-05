"""
Automated Pytest Test Suite for Til Tumor Infiltrating Lymphocyte Scorer.
Domain: Clinical & Biomedical AI
Standard: CAP / CLSI / ISO Standards
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, AuditTrail, SecurityException
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_phi_guard_snsssn():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient SSN 123-45-6789")


def test_phi_guard_email():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Contact patient@example.com for results")


def test_phi_guard_empty():
    PHIGuard.assert_no_phi("")
    PHIGuard.assert_no_phi(None)


def test_phi_redaction():
    redacted = PHIGuard.redact_phi("Patient MRN-12345678 test")
    assert "MRN-12345678" not in redacted
    assert "[REDACTED_IDENTIFIER]" in redacted


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_supervisor_critical_escalation():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-CRIT-01",
        target_identifier="KEY-CRIT-01",
        primary_metric=30.0,
        secondary_metric=15.0,
        status_descriptor="DISCORDANT_ANOMALY",
        is_critical_flag=True
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.CRITICAL_STAT
    assert dossier.integrity_status == SystemIntegrityStatus.RECALIBRATION_REQUIRED
    assert dossier.critical_alerts_count > 0


def test_supervisor_elevated_escalation():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-ELEV-01",
        target_identifier="KEY-ELEV-01",
        primary_metric=30.0,
        secondary_metric=5.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ELEVATED
    assert dossier.integrity_status == SystemIntegrityStatus.DISCORDANT


def test_audit_trail_integrity():
    trail = AuditTrail(secret_key="test-key-123")
    trail.log("actor1", "tier1", "EVENT_1", {"data": "value1"})
    trail.log("actor2", "tier2", "EVENT_2", {"data": "value2"})
    assert trail.verify_integrity() is True
    assert len(trail.get_trail()) == 2


def test_audit_trail_tamper_detection():
    trail = AuditTrail(secret_key="test-key-456")
    trail.log("actor1", "tier1", "EVENT_1", {"data": "value1"})
    trail.log("actor2", "tier2", "EVENT_2", {"data": "value2"})
    # Tamper with the first entry
    trail.logs[0]["current_hash"] = "tampered_hash"
    assert trail.verify_integrity() is False


def test_cli_batch_file_not_found(tmp_path):
    result = main(["batch", "-i", "/nonexistent/file.csv"])
    assert result == 1


def test_cli_batch_invalid_csv(tmp_path):
    csv_in = tmp_path / "invalid.csv"
    csv_out = tmp_path / "out.csv"
    csv_in.write_text("", encoding="utf-8")
    result = main(["batch", "-i", str(csv_in), "-o", str(csv_out)])
    assert result == 1
