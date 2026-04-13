"""Tests for PagerDuty client."""

from mcpincident.clients.pagerduty import PagerDutyClient, _mock_incidents, _mock_oncall


def test_mock_incidents_returned_when_no_token() -> None:
    client = PagerDutyClient(token="")
    incidents = client.get_active_incidents()
    assert len(incidents) > 0
    assert incidents[0].id == "INC001"


def test_mock_oncall_returned_when_no_token() -> None:
    client = PagerDutyClient(token="")
    oncall = client.get_oncall()
    assert len(oncall) > 0
    assert oncall[0].escalation_level == 1


def test_incident_has_required_fields() -> None:
    incidents = _mock_incidents()
    for i in incidents:
        assert i.id
        assert i.title
        assert i.status
        assert i.service


def test_oncall_has_required_fields() -> None:
    oncall = _mock_oncall()
    for o in oncall:
        assert o.user
        assert o.email
        assert o.escalation_level >= 1