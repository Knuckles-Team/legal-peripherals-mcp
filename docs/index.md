# legal-peripherals-mcp

Legal compliance automation **API + MCP Server** for the agent-utilities ecosystem
— Secretary of State entity lookups, IRS Form SS-4 (EIN) drafting with off-hours
filing compliance, and corporate / LLC statute and charter templates.

!!! info "Official documentation"
    This site is the canonical reference for `legal-peripherals-mcp`, maintained
    alongside every release.

[![PyPI](https://img.shields.io/pypi/v/legal-peripherals-mcp)](https://pypi.org/project/legal-peripherals-mcp/)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
[![License](https://img.shields.io/pypi/l/legal-peripherals-mcp)](https://github.com/Knuckles-Team/legal-peripherals-mcp/blob/main/LICENSE)
[![GitHub](https://img.shields.io/badge/source-GitHub-181717?logo=github)](https://github.com/Knuckles-Team/legal-peripherals-mcp)

## Overview

`legal-peripherals-mcp` exposes legal and corporate filing automation as typed,
deterministic MCP tools an agent can call. It provides:

- **Secretary of State crawlers** — Playwright-driven business entity lookups across
  all 50 states, with optimized scrapers for Texas, Delaware, Wyoming, and Nevada and
  a resilient fallback for the remainder.
- **IRS EIN (Form SS-4) drafting** — structured SS-4 preparation that schedules
  filings inside the IRS active window (Mon–Fri 7:00 AM – 10:00 PM EST) and queues
  off-hours requests.
- **Statute catalog & charter templates** — programmatic lookup of state statutory
  default rules and corporate / LLC charter templates.

The package also ships an optional **Pydantic-AI agent server** (`legal-peripherals-agent`)
for conversational use of the same tool surface.

## Explore the documentation

<div class="grid cards" markdown>

- :material-rocket-launch: **[Installation](installation.md)** — pip, source, extras, and the prebuilt Docker image.
- :material-server-network: **[Deployment](deployment.md)** — run the MCP server, the agent server, Docker Compose, Caddy + Technitium.
- :material-console: **[Usage](usage.md)** — the MCP tools, the `Api` client, and example prompts.
- :material-sitemap: **[Overview](overview.md)** — the three core domains and how they fit together.
- :material-tag-multiple: **[Concepts](concepts.md)** — the `CONCEPT:LEGAL-*` registry.

</div>

## Quick start

```bash
pip install "legal-peripherals-mcp[mcp]"
legal-peripherals-mcp            # stdio MCP server (default transport)
```

Run it as a network server:

```bash
legal-peripherals-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

See **[Installation](installation.md)** and **[Deployment](deployment.md)** for the
full matrix (PyPI extras, Docker image, all transports, the agent server, reverse
proxy, DNS).
