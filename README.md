# mcp-incident-intel

> MCP server wiring PagerDuty, Dynatrace, and runbook context for AI-driven incident response.

![CI](https://github.com/brianpelow/mcp-incident-intel/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-green.svg)
![MCP](https://img.shields.io/badge/MCP-compatible-purple.svg)

## Overview

`mcp-incident-intel` is a Model Context Protocol server that gives AI agents
full incident context in a single, standardized interface. It wires together
PagerDuty incident data, Dynatrace observability signals, and operational
runbooks so that LLM-powered agents can triage, correlate, and begin
remediation without switching between tools.

Built for SRE and platform engineering teams in regulated financial services
and manufacturing where mean time to resolution is a compliance metric.

## Tools exposed

| Tool | Description |
|------|-------------|
| `get_active_incidents` | Fetch open PagerDuty incidents with severity and assignee |
| `get_dynatrace_problems` | Fetch open Dynatrace problem cards with root cause |
| `get_service_topology` | Get upstream/downstream dependencies for a service |
| `get_slo_status` | Fetch SLO burn rate and remaining error budget |
| `get_runbook` | Retrieve runbook content for a given alert name |
| `correlate_incident` | Cross-reference a PagerDuty incident with Dynatrace problems |

## Quick start

```bash
pip install mcp-incident-intel

export PAGERDUTY_TOKEN=your_pagerduty_token
export DYNATRACE_URL=https://your-env.live.dynatrace.com
export DYNATRACE_TOKEN=your_dynatrace_api_token

mcp-incident-intel
```

## Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `PAGERDUTY_TOKEN` | PagerDuty API token | Yes |
| `DYNATRACE_URL` | Dynatrace environment URL | Yes |
| `DYNATRACE_TOKEN` | Dynatrace API token | Yes |
| `RUNBOOK_DIR` | Path to runbook markdown files | No |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).