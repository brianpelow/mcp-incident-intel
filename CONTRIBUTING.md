# Contributing

## Development setup

```bash
git clone https://github.com/brianpelow/mcp-incident-intel
cd mcp-incident-intel
uv sync
uv run pytest
```

## Running the MCP server locally

```bash
export PAGERDUTY_TOKEN=your_token
export DYNATRACE_URL=https://your-env.live.dynatrace.com
export DYNATRACE_TOKEN=your_token
uv run mcp-incident-intel
```

## Standards

- All PRs require passing CI
- Test coverage must not decrease
- Update CHANGELOG.md for user-facing changes