"""MCP tools for runbook retrieval."""

from __future__ import annotations

import re
from pathlib import Path

from mcpincident.core.config import ServerConfig


def get_runbook(config: ServerConfig, alert_name: str) -> dict:
    """Retrieve a runbook matching an alert name from the runbook directory."""
    runbook_dir = Path(config.runbook_dir)

    if not runbook_dir.exists():
        return {
            "found": False,
            "alert_name": alert_name,
            "message": f"Runbook directory not found: {runbook_dir}",
        }

    normalized = alert_name.lower().replace(" ", "-").replace("_", "-")
    candidates = list(runbook_dir.glob("*.md"))

    best_match = None
    best_score = 0

    for candidate in candidates:
        stem = candidate.stem.lower()
        score = 0
        if normalized in stem:
            score = 3
        elif any(word in stem for word in normalized.split("-") if len(word) > 3):
            score = 1
        if score > best_score:
            best_score = score
            best_match = candidate

    if best_match and best_score > 0:
        content = best_match.read_text(errors="ignore")
        return {
            "found": True,
            "alert_name": alert_name,
            "runbook_file": best_match.name,
            "content": content[:3000],
            "truncated": len(content) > 3000,
        }

    return {
        "found": False,
        "alert_name": alert_name,
        "message": f"No runbook found matching '{alert_name}'",
        "available_runbooks": [c.name for c in candidates],
    }


def correlate_incident(
    config: ServerConfig,
    incident_title: str,
    incident_service: str,
) -> dict:
    """Cross-reference a PagerDuty incident with Dynatrace problems and runbooks."""
    from mcpincident.clients.pagerduty import PagerDutyClient
    from mcpincident.clients.dynatrace import DynatraceClient

    pd_client = PagerDutyClient(token=config.pagerduty_token)
    dt_client = DynatraceClient(base_url=config.dynatrace_url, token=config.dynatrace_token)

    incidents = pd_client.get_active_incidents()
    problems = dt_client.get_problems()
    topology = dt_client.get_service_topology(incident_service)
    runbook = get_runbook(config, incident_title)

    title_lower = incident_title.lower()
    related_problems = [
        p for p in problems
        if any(e.lower() in incident_service.lower() or incident_service.lower() in e.lower()
               for e in p.affected_entities)
        or incident_service.lower() in p.title.lower()
    ]

    return {
        "incident_title": incident_title,
        "incident_service": incident_service,
        "related_dynatrace_problems": [
            {"id": p.id, "title": p.title, "severity": p.severity, "root_cause": p.root_cause}
            for p in related_problems
        ],
        "service_topology": {
            "upstream": topology.upstream,
            "downstream": topology.downstream,
        },
        "runbook": runbook,
        "correlation_confidence": "high" if related_problems and runbook["found"] else
                                  "medium" if related_problems or runbook["found"] else "low",
    }