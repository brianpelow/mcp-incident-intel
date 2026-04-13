"""Tests for Dynatrace client."""

from mcpincident.clients.dynatrace import DynatraceClient, _mock_problems, _mock_slos, _mock_topology


def test_mock_problems_returned_when_no_token() -> None:
    client = DynatraceClient(base_url="", token="")
    problems = client.get_problems()
    assert len(problems) > 0
    assert problems[0].id == "P-001"


def test_mock_slos_returned_when_no_token() -> None:
    client = DynatraceClient(base_url="", token="")
    slos = client.get_slo_status()
    assert len(slos) > 0
    assert slos[0].target == 99.9


def test_mock_topology_returned_when_no_token() -> None:
    client = DynatraceClient(base_url="", token="")
    topology = client.get_service_topology("payments-service")
    assert topology.service_name == "payments-service"
    assert len(topology.upstream) > 0
    assert len(topology.downstream) > 0


def test_problem_has_required_fields() -> None:
    problems = _mock_problems()
    for p in problems:
        assert p.id
        assert p.title
        assert p.severity
        assert isinstance(p.affected_entities, list)


def test_slo_burn_rate_is_float() -> None:
    slos = _mock_slos()
    for s in slos:
        assert isinstance(s.burn_rate, float)
        assert isinstance(s.error_budget_remaining, float)