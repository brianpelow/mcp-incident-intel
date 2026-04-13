"""Tests for MCP tool functions."""

import tempfile
from pathlib import Path
from mcpincident.core.config import ServerConfig
from mcpincident.tools.incidents import get_active_incidents, get_oncall_roster
from mcpincident.tools.observability import get_dynatrace_problems, get_slo_status, get_service_topology
from mcpincident.tools.runbooks import get_runbook, correlate_incident


def make_config(**kwargs) -> ServerConfig:
    return ServerConfig(**kwargs)


def test_get_active_incidents_returns_dict() -> None:
    config = make_config()
    result = get_active_incidents(config)
    assert "incidents" in result
    assert "count" in result
    assert result["source"] == "pagerduty"


def test_get_oncall_roster_returns_dict() -> None:
    config = make_config()
    result = get_oncall_roster(config)
    assert "oncall" in result
    assert result["source"] == "pagerduty"


def test_get_dynatrace_problems_returns_dict() -> None:
    config = make_config()
    result = get_dynatrace_problems(config)
    assert "problems" in result
    assert result["source"] == "dynatrace"


def test_get_slo_status_returns_dict() -> None:
    config = make_config()
    result = get_slo_status(config)
    assert "slos" in result
    assert result["source"] == "dynatrace"


def test_get_service_topology_returns_dict() -> None:
    config = make_config()
    result = get_service_topology(config, service_name="payments-service")
    assert "upstream_dependencies" in result
    assert "downstream_dependencies" in result
    assert result["source"] == "dynatrace"


def test_get_runbook_not_found() -> None:
    config = make_config(runbook_dir="/nonexistent/path")
    result = get_runbook(config, alert_name="HIGH_LATENCY")
    assert result["found"] is False


def test_get_runbook_found() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        rb = Path(tmpdir) / "high-latency-runbook.md"
        rb.write_text("# High Latency Runbook\n\nCheck the database.")
        config = make_config(runbook_dir=tmpdir)
        result = get_runbook(config, alert_name="high-latency")
        assert result["found"] is True
        assert "content" in result


def test_correlate_incident_returns_confidence() -> None:
    config = make_config()
    result = correlate_incident(config, incident_title="High latency", incident_service="payments-service")
    assert "correlation_confidence" in result
    assert result["correlation_confidence"] in ("high", "medium", "low")