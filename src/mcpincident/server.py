"""FastMCP server entry point for mcp-incident-intel."""

from __future__ import annotations

import json
from mcpincident.core.config import ServerConfig
from mcpincident.tools.incidents import get_active_incidents, get_oncall_roster
from mcpincident.tools.observability import get_dynatrace_problems, get_slo_status, get_service_topology
from mcpincident.tools.runbooks import get_runbook, correlate_incident


def create_server() -> object:
    """Create and configure the FastMCP server."""
    try:
        from fastmcp import FastMCP
    except ImportError:
        raise ImportError("fastmcp is required. Run: pip install fastmcp")

    config = ServerConfig.from_env()
    mcp = FastMCP(
        name="mcp-incident-intel",
        instructions=(
            "I provide incident intelligence by combining PagerDuty alerts, "
            "Dynatrace observability data, and operational runbooks. "
            "Use me to triage incidents, understand service topology, "
            "check SLO burn rates, and retrieve remediation runbooks."
        ),
    )

    @mcp.tool()
    def get_active_incidents_tool(limit: int = 10) -> str:
        """Get currently open PagerDuty incidents with severity and assignee."""
        result = get_active_incidents(config, limit=limit)
        return json.dumps(result, indent=2)

    @mcp.tool()
    def get_oncall_roster_tool() -> str:
        """Get the current on-call roster from PagerDuty."""
        result = get_oncall_roster(config)
        return json.dumps(result, indent=2)

    @mcp.tool()
    def get_dynatrace_problems_tool(limit: int = 10) -> str:
        """Get open Dynatrace problem cards with root cause analysis."""
        result = get_dynatrace_problems(config, limit=limit)
        return json.dumps(result, indent=2)

    @mcp.tool()
    def get_slo_status_tool(slo_id: str = "") -> str:
        """Get SLO burn rate and remaining error budget from Dynatrace."""
        result = get_slo_status(config, slo_id=slo_id)
        return json.dumps(result, indent=2)

    @mcp.tool()
    def get_service_topology_tool(service_name: str) -> str:
        """Get upstream and downstream service dependencies from Dynatrace."""
        result = get_service_topology(config, service_name=service_name)
        return json.dumps(result, indent=2)

    @mcp.tool()
    def get_runbook_tool(alert_name: str) -> str:
        """Retrieve a runbook for a given alert name."""
        result = get_runbook(config, alert_name=alert_name)
        return json.dumps(result, indent=2)

    @mcp.tool()
    def correlate_incident_tool(incident_title: str, incident_service: str) -> str:
        """Cross-reference a PagerDuty incident with Dynatrace problems and runbooks."""
        result = correlate_incident(config, incident_title=incident_title, incident_service=incident_service)
        return json.dumps(result, indent=2)

    return mcp


def main() -> None:
    """Entry point for the MCP server."""
    mcp = create_server()
    mcp.run()


if __name__ == "__main__":
    main()