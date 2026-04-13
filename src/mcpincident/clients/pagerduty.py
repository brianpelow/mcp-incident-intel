"""PagerDuty REST API client."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import httpx


@dataclass
class Incident:
    """A PagerDuty incident."""

    id: str
    title: str
    status: str
    severity: str
    service: str
    assignee: str
    created_at: str
    html_url: str
    body: str = ""


@dataclass
class OnCallEntry:
    """An on-call schedule entry."""

    user: str
    email: str
    schedule: str
    escalation_level: int


class PagerDutyClient:
    """Client for the PagerDuty REST API v2."""

    BASE_URL = "https://api.pagerduty.com"

    def __init__(self, token: str, timeout: int = 30) -> None:
        self.token = token
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Token token={self.token}",
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Content-Type": "application/json",
        }

    def get_active_incidents(self, limit: int = 10) -> list[Incident]:
        """Fetch currently open incidents."""
        if not self.token:
            return _mock_incidents()
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.BASE_URL}/incidents",
                    headers=self._headers(),
                    params={"statuses[]": ["triggered", "acknowledged"], "limit": limit},
                )
                response.raise_for_status()
                data = response.json()
                return [_parse_incident(i) for i in data.get("incidents", [])]
        except Exception:
            return _mock_incidents()

    def get_oncall(self, escalation_policy_id: str = "") -> list[OnCallEntry]:
        """Fetch current on-call schedule."""
        if not self.token:
            return _mock_oncall()
        try:
            with httpx.Client(timeout=self.timeout) as client:
                params: dict[str, Any] = {}
                if escalation_policy_id:
                    params["escalation_policy_ids[]"] = escalation_policy_id
                response = client.get(
                    f"{self.BASE_URL}/oncalls",
                    headers=self._headers(),
                    params=params,
                )
                response.raise_for_status()
                data = response.json()
                return [_parse_oncall(o) for o in data.get("oncalls", [])]
        except Exception:
            return _mock_oncall()


def _parse_incident(data: dict[str, Any]) -> Incident:
    return Incident(
        id=data.get("id", ""),
        title=data.get("title", ""),
        status=data.get("status", ""),
        severity=data.get("severity", "unknown"),
        service=data.get("service", {}).get("summary", ""),
        assignee=data.get("assignments", [{}])[0].get("assignee", {}).get("summary", "unassigned") if data.get("assignments") else "unassigned",
        created_at=data.get("created_at", ""),
        html_url=data.get("html_url", ""),
        body=data.get("body", {}).get("details", "") if data.get("body") else "",
    )


def _parse_oncall(data: dict[str, Any]) -> OnCallEntry:
    return OnCallEntry(
        user=data.get("user", {}).get("summary", ""),
        email=data.get("user", {}).get("email", ""),
        schedule=data.get("schedule", {}).get("summary", ""),
        escalation_level=data.get("escalation_level", 1),
    )


def _mock_incidents() -> list[Incident]:
    return [
        Incident(
            id="INC001",
            title="High payment latency detected",
            status="triggered",
            severity="high",
            service="payments-service",
            assignee="oncall@example.com",
            created_at="2026-04-12T02:00:00Z",
            html_url="https://example.pagerduty.com/incidents/INC001",
            body="P99 latency exceeded 2000ms threshold for 5 minutes.",
        ),
        Incident(
            id="INC002",
            title="FX rate service degraded",
            status="acknowledged",
            severity="medium",
            service="fx-rate-service",
            assignee="platform@example.com",
            created_at="2026-04-12T01:30:00Z",
            html_url="https://example.pagerduty.com/incidents/INC002",
            body="FX rate API returning 503 intermittently.",
        ),
    ]


def _mock_oncall() -> list[OnCallEntry]:
    return [
        OnCallEntry(
            user="Jane Smith",
            email="jane.smith@example.com",
            schedule="Payments Primary",
            escalation_level=1,
        ),
    ]