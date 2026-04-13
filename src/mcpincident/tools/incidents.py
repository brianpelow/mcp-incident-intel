"""MCP tools for PagerDuty incident data."""

from __future__ import annotations

from mcpincident.clients.pagerduty import PagerDutyClient
from mcpincident.core.config import ServerConfig


def get_active_incidents(config: ServerConfig, limit: int = 10) -> dict:
    """Get currently open PagerDuty incidents."""
    client = PagerDutyClient(token=config.pagerduty_token, timeout=config.timeout_seconds)
    incidents = client.get_active_incidents(limit=limit)

    return {
        "count": len(incidents),
        "source": "pagerduty",
        "incidents": [
            {
                "id": i.id,
                "title": i.title,
                "status": i.status,
                "severity": i.severity,
                "service": i.service,
                "assignee": i.assignee,
                "created_at": i.created_at,
                "url": i.html_url,
                "body": i.body[:500] if i.body else "",
            }
            for i in incidents
        ],
    }


def get_oncall_roster(config: ServerConfig) -> dict:
    """Get the current on-call roster from PagerDuty."""
    client = PagerDutyClient(token=config.pagerduty_token, timeout=config.timeout_seconds)
    oncall = client.get_oncall()

    return {
        "source": "pagerduty",
        "oncall": [
            {
                "user": o.user,
                "email": o.email,
                "schedule": o.schedule,
                "escalation_level": o.escalation_level,
            }
            for o in oncall
        ],
    }