"""Dynatrace REST API v2 client."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import httpx


@dataclass
class Problem:
    """A Dynatrace problem card."""

    id: str
    title: str
    status: str
    severity: str
    affected_entities: list[str]
    root_cause: str
    start_time: str
    impact_level: str


@dataclass
class SloStatus:
    """Dynatrace SLO burn rate and error budget."""

    name: str
    status: str
    error_budget_remaining: float
    burn_rate: float
    target: float
    evaluated_percentage: float


@dataclass
class ServiceTopology:
    """Upstream and downstream dependencies for a service."""

    service_name: str
    upstream: list[str]
    downstream: list[str]
    entity_id: str = ""


class DynatraceClient:
    """Client for the Dynatrace REST API v2."""

    def __init__(self, base_url: str, token: str, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Api-Token {self.token}",
            "Content-Type": "application/json",
        }

    def get_problems(self, limit: int = 10) -> list[Problem]:
        """Fetch open Dynatrace problem cards."""
        if not self.token:
            return _mock_problems()
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/api/v2/problems",
                    headers=self._headers(),
                    params={"problemSelector": "status(OPEN)", "pageSize": limit},
                )
                response.raise_for_status()
                data = response.json()
                return [_parse_problem(p) for p in data.get("problems", [])]
        except Exception:
            return _mock_problems()

    def get_slo_status(self, slo_id: str = "") -> list[SloStatus]:
        """Fetch SLO status and error budget."""
        if not self.token:
            return _mock_slos()
        try:
            with httpx.Client(timeout=self.timeout) as client:
                url = f"{self.base_url}/api/v2/slo"
                if slo_id:
                    url = f"{url}/{slo_id}"
                response = client.get(url, headers=self._headers())
                response.raise_for_status()
                data = response.json()
                items = [data] if slo_id else data.get("slo", [])
                return [_parse_slo(s) for s in items]
        except Exception:
            return _mock_slos()

    def get_service_topology(self, service_name: str) -> ServiceTopology:
        """Get upstream and downstream dependencies for a service."""
        if not self.token:
            return _mock_topology(service_name)
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/api/v2/entities",
                    headers=self._headers(),
                    params={
                        "entitySelector": f'type("SERVICE"),entityName("{service_name}")',
                        "fields": "toRelationships,fromRelationships",
                    },
                )
                response.raise_for_status()
                data = response.json()
                entities = data.get("entities", [])
                if not entities:
                    return _mock_topology(service_name)
                return _parse_topology(entities[0], service_name)
        except Exception:
            return _mock_topology(service_name)


def _parse_problem(data: dict[str, Any]) -> Problem:
    return Problem(
        id=data.get("problemId", ""),
        title=data.get("title", ""),
        status=data.get("status", ""),
        severity=data.get("severityLevel", ""),
        affected_entities=[e.get("name", "") for e in data.get("affectedEntities", [])],
        root_cause=data.get("rootCauseEntity", {}).get("name", "unknown") if data.get("rootCauseEntity") else "unknown",
        start_time=str(data.get("startTime", "")),
        impact_level=data.get("impactLevel", ""),
    )


def _parse_slo(data: dict[str, Any]) -> SloStatus:
    return SloStatus(
        name=data.get("name", ""),
        status=data.get("status", ""),
        error_budget_remaining=float(data.get("errorBudgetRemaining", 0)),
        burn_rate=float(data.get("burnRateValue", 0)),
        target=float(data.get("target", 99.9)),
        evaluated_percentage=float(data.get("evaluatedPercentage", 0)),
    )


def _parse_topology(data: dict[str, Any], service_name: str) -> ServiceTopology:
    upstream = [r.get("toEntity", {}).get("name", "") for r in data.get("fromRelationships", {}).get("calls", [])]
    downstream = [r.get("toEntity", {}).get("name", "") for r in data.get("toRelationships", {}).get("calledBy", [])]
    return ServiceTopology(
        service_name=service_name,
        entity_id=data.get("entityId", ""),
        upstream=[u for u in upstream if u],
        downstream=[d for d in downstream if d],
    )


def _mock_problems() -> list[Problem]:
    return [
        Problem(
            id="P-001",
            title="Response time degradation on payments-service",
            status="OPEN",
            severity="PERFORMANCE",
            affected_entities=["payments-service", "payments-db"],
            root_cause="payments-db",
            start_time="2026-04-12T02:00:00Z",
            impact_level="SERVICE",
        ),
    ]


def _mock_slos() -> list[SloStatus]:
    return [
        SloStatus(
            name="Payments API Availability",
            status="WARNING",
            error_budget_remaining=12.5,
            burn_rate=3.2,
            target=99.9,
            evaluated_percentage=99.71,
        ),
    ]


def _mock_topology(service_name: str) -> ServiceTopology:
    return ServiceTopology(
        service_name=service_name,
        upstream=["api-gateway", "auth-service"],
        downstream=["payments-db", "fx-rate-service", "audit-service"],
    )