"""MCP tools for Dynatrace observability data."""

from __future__ import annotations

from mcpincident.clients.dynatrace import DynatraceClient
from mcpincident.core.config import ServerConfig


def get_dynatrace_problems(config: ServerConfig, limit: int = 10) -> dict:
    """Get open Dynatrace problem cards."""
    client = DynatraceClient(
        base_url=config.dynatrace_url,
        token=config.dynatrace_token,
        timeout=config.timeout_seconds,
    )
    problems = client.get_problems(limit=limit)

    return {
        "count": len(problems),
        "source": "dynatrace",
        "problems": [
            {
                "id": p.id,
                "title": p.title,
                "status": p.status,
                "severity": p.severity,
                "affected_entities": p.affected_entities,
                "root_cause": p.root_cause,
                "start_time": p.start_time,
                "impact_level": p.impact_level,
            }
            for p in problems
        ],
    }


def get_slo_status(config: ServerConfig, slo_id: str = "") -> dict:
    """Get SLO burn rate and error budget from Dynatrace."""
    client = DynatraceClient(
        base_url=config.dynatrace_url,
        token=config.dynatrace_token,
        timeout=config.timeout_seconds,
    )
    slos = client.get_slo_status(slo_id=slo_id)

    return {
        "count": len(slos),
        "source": "dynatrace",
        "slos": [
            {
                "name": s.name,
                "status": s.status,
                "target": s.target,
                "evaluated_percentage": round(s.evaluated_percentage, 4),
                "error_budget_remaining": round(s.error_budget_remaining, 2),
                "burn_rate": round(s.burn_rate, 2),
            }
            for s in slos
        ],
    }


def get_service_topology(config: ServerConfig, service_name: str) -> dict:
    """Get upstream and downstream service dependencies from Dynatrace."""
    client = DynatraceClient(
        base_url=config.dynatrace_url,
        token=config.dynatrace_token,
        timeout=config.timeout_seconds,
    )
    topology = client.get_service_topology(service_name=service_name)

    return {
        "source": "dynatrace",
        "service": topology.service_name,
        "entity_id": topology.entity_id,
        "upstream_dependencies": topology.upstream,
        "downstream_dependencies": topology.downstream,
        "total_dependencies": len(topology.upstream) + len(topology.downstream),
    }