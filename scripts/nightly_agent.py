"""Nightly agent — automated maintenance for mcp-incident-intel."""

from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

REPO_ROOT = Path(__file__).parent.parent


def update_tool_manifest() -> None:
    """Write a manifest of all exposed MCP tools to docs."""
    tools = [
        {"name": "get_active_incidents_tool", "source": "pagerduty", "description": "Open incidents with severity and assignee"},
        {"name": "get_oncall_roster_tool", "source": "pagerduty", "description": "Current on-call schedule"},
        {"name": "get_dynatrace_problems_tool", "source": "dynatrace", "description": "Open problem cards with root cause"},
        {"name": "get_slo_status_tool", "source": "dynatrace", "description": "SLO burn rate and error budget"},
        {"name": "get_service_topology_tool", "source": "dynatrace", "description": "Upstream and downstream dependencies"},
        {"name": "get_runbook_tool", "source": "runbooks", "description": "Runbook retrieval by alert name"},
        {"name": "correlate_incident_tool", "source": "multi", "description": "Cross-reference PagerDuty and Dynatrace"},
    ]
    manifest = {
        "generated_at": datetime.utcnow().isoformat(),
        "date": date.today().isoformat(),
        "tool_count": len(tools),
        "tools": tools,
    }
    out = REPO_ROOT / "docs" / "tool-manifest.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2))
    print(f"[agent] Updated tool manifest -> {out}")


def refresh_changelog() -> None:
    changelog = REPO_ROOT / "CHANGELOG.md"
    if not changelog.exists():
        return
    today = date.today().isoformat()
    content = changelog.read_text()
    if today not in content:
        content = content.replace("## [Unreleased]", f"## [Unreleased]\n\n_Last checked: {today}_", 1)
        changelog.write_text(content)
    print("[agent] Refreshed CHANGELOG timestamp")


if __name__ == "__main__":
    print(f"[agent] Starting nightly agent - {date.today().isoformat()}")
    update_tool_manifest()
    refresh_changelog()
    print("[agent] Done.")