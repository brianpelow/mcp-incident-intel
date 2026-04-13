"""Configuration and credentials for mcp-incident-intel."""

from __future__ import annotations

import os
from pydantic import BaseModel, Field


class ServerConfig(BaseModel):
    """Runtime configuration for the MCP incident intel server."""

    pagerduty_token: str = Field("", description="PagerDuty API token")
    dynatrace_url: str = Field("", description="Dynatrace environment URL")
    dynatrace_token: str = Field("", description="Dynatrace API token")
    runbook_dir: str = Field("runbooks", description="Path to runbook markdown files")
    industry: str = Field("fintech", description="Industry context")
    timeout_seconds: int = Field(30, description="HTTP client timeout")

    @classmethod
    def from_env(cls) -> "ServerConfig":
        return cls(
            pagerduty_token=os.environ.get("PAGERDUTY_TOKEN", ""),
            dynatrace_url=os.environ.get("DYNATRACE_URL", ""),
            dynatrace_token=os.environ.get("DYNATRACE_TOKEN", ""),
            runbook_dir=os.environ.get("RUNBOOK_DIR", "runbooks"),
            industry=os.environ.get("MCP_INCIDENT_INDUSTRY", "fintech"),
        )

    @property
    def has_pagerduty(self) -> bool:
        return bool(self.pagerduty_token)

    @property
    def has_dynatrace(self) -> bool:
        return bool(self.dynatrace_url and self.dynatrace_token)