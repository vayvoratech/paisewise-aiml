from datetime import datetime, timedelta, timezone

from app.services.on_call_service import OnCallService


def test_sla_met():
    service = OnCallService(
        service_name="ai-service",
        response_sla_minutes=30,
    )

    detected_at = datetime.now(timezone.utc)

    service.create_incident(
        incident_id="INC-001",
        severity="HIGH",
        description="AI service production issue",
        detected_at=detected_at,
    )

    service.assign_on_call(
        incident_id="INC-001",
        engineer="on-call-engineer",
    )

    service.acknowledge_incident(
        incident_id="INC-001",
        acknowledged_at=detected_at + timedelta(minutes=15),
    )

    result = service.evaluate_response("INC-001")

    assert result.response_time_minutes == 15
    assert result.sla_minutes == 30
    assert result.status == "SLA_MET"

    print("SLA MET TEST PASSED")
    print(result)


def test_sla_breached():
    service = OnCallService(
        service_name="ai-service",
        response_sla_minutes=30,
    )

    detected_at = datetime.now(timezone.utc)

    service.create_incident(
        incident_id="INC-002",
        severity="CRITICAL",
        description="AI service unavailable",
        detected_at=detected_at,
    )

    service.assign_on_call(
        incident_id="INC-002",
        engineer="on-call-engineer",
    )

    service.acknowledge_incident(
        incident_id="INC-002",
        acknowledged_at=detected_at + timedelta(minutes=35),
    )

    result = service.evaluate_response("INC-002")

    assert result.response_time_minutes == 35
    assert result.sla_minutes == 30
    assert result.status == "SLA_BREACHED"

    print("SLA BREACHED TEST PASSED")
    print(result)


if __name__ == "__main__":
    test_sla_met()
    test_sla_breached()

    print("\nON-CALL SERVICE TESTS PASSED")