# ⚖️ Legal Peripherals MCP Server

<p align="center">
  <img src="https://img.shields.io/badge/FastMCP-Server-4A154B?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastMCP Server">
  <img src="https://img.shields.io/badge/Compliance-IRS%20%7C%2050%20States-20639B?style=for-the-badge" alt="Compliance">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
</p>

A premium Model Context Protocol (MCP) server powered by **FastMCP** that exposes highly robust tools for automating legal operations and filing compliance. This server handles state-level Secretary of State (SOS) entities, off-hours compliant IRS Form SS-4 EIN drafting/scheduling, and corporate/LLC charter templates lookup.

> **Documentation** — Installation, deployment, usage across the API and MCP
> interfaces, and the optional agent server are maintained in the
> [official documentation](https://knuckles-team.github.io/legal-peripherals-mcp/).

---

## 🗺️ System Architecture

The following diagram illustrates how the `Legal Peripherals MCP Server` coordinates between external LLM clients, state Secretary of State (SOS) databases, the IRS Form SS-4 preparation engine, and local template resources:

```mermaid
graph TD
    Client[LLM / Agent Client] <-->|stdio / Server-Sent Events| MCP[FastMCP Server]

    subgraph Core Features [Legal Peripherals Engine]
        MCP -->|SOSTOOL| SOS[Secretary of State Lookup]
        MCP -->|EINTOOL| EIN[IRS Form SS-4 EIN Engine]
        MCP -->|STATUTETOOL| STATUTE["Statute & Charter Templates"]
    end

    subgraph State Scraping Layer
        SOS -->|Deep Scraper| TX[Texas Secretary of State]
        SOS -->|Deep Scraper| DE[Delaware Division of Corporations]
        SOS -->|Deep Scraper| WY[Wyoming Secretary of State]
        SOS -->|Deep Scraper| NV[Nevada SilverFlume]
        SOS -->|LLM Fallback| FB[Resilient Fallback Scraper]
    end

    subgraph IRS Filing Layer
        EIN -->|Check EST Time| activeCheck{"Is Monday-Friday<br/>7:00 AM - 10:00 PM EST?"}
        activeCheck -->|Yes / Override| fileNow[FILING IMMEDIATELY]
        activeCheck -->|No| queueLater[QUEUED FOR SCHEDULING]
    end

    subgraph Statute Knowledge
        STATUTE -->|State Statutes| defaults[Default Rules Mapping]
        STATUTE -->|Documents| templates[Corporate/LLC Charter Templates]
    end
```

---

## 🛠️ MCP Tools Mapping

The server registers the following standard FastMCP tools, which can be dynamically enabled or disabled via environment toggles:

Auto-generated — do not edit between the markers below.

<!-- MCP-TOOLS-TABLE:START -->

#### Condensed action-routed tools (default — `MCP_TOOL_MODE=condensed`)

| MCP Tool | Toggle Env Var | Description |
|----------|----------------|-------------|
| `draft_ein_form` | `EINTOOL` | Draft IRS Form SS-4 and schedule EIN filing with off-hours compliance (Mon-Fri 7:00 AM - 10:00 PM EST). |
| `lookup_statute_rules` | `STATUTETOOL` | Query state statutory default rules and retrieve corporate/LLC charter templates. |
| `sos_entity_lookup` | `SOSTOOL` | Perform Secretary of State entity lookup across 50 states (scrapers for TX, DE, WY, NV, resilient fallback for others). |

#### Verbose 1:1 API-mapped tools (`MCP_TOOL_MODE=verbose` or `both`)

<details>
<summary>1 per-operation tools — one per public API method (click to expand)</summary>

| MCP Tool | Toggle Env Var | Description |
|----------|----------------|-------------|
| `legal_peripherals_request` | `APITOOL` | Invoke the request operation. |

</details>

_3 action-routed tool(s) (default) · 1 verbose 1:1 tool(s). Each is enabled unless its `<DOMAIN>TOOL` toggle is set false; `MCP_TOOL_MODE` selects the surface (`condensed` default · `verbose` 1:1 · `both`). Auto-generated — do not edit._
<!-- MCP-TOOLS-TABLE:END -->

---

### MCP Configuration Examples

<!-- MCP-CONFIG-EXAMPLES:START -->

> **Install the slim `[mcp]` extra.** All examples install `legal-peripherals-mcp[mcp]` — the
> MCP-server extra that pulls only the FastMCP / FastAPI tooling (`agent-utilities[mcp]`).
> It deliberately **excludes** the heavy agent runtime (`pydantic-ai`, the epistemic-graph
> engine, `dspy`, `llama-index`), so `uvx` / container installs are far smaller. Use the
> full `[agent]` extra only when you need the integrated Pydantic AI agent.

#### stdio Transport (local IDEs — Cursor, Claude Desktop, VS Code)

```json
{
  "mcpServers": {
    "legal-peripherals-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "legal-peripherals-mcp[mcp]",
        "legal-peripherals-mcp"
      ],
      "env": {
        "MCP_TOOL_MODE": "condensed",
        "BYPASS_IRS_FILING_HOURS": "False",
        "EINTOOL": "True",
        "EIN_TIMEOUT_SECONDS": "30",
        "LEGAL_PERIPHERALS_BASE_URL": "http://localhost:8000",
        "LEGAL_PERIPHERALS_TOKEN": "",
        "OPENCORPORATES_API_TOKEN": "",
        "SOSTOOL": "True",
        "SOS_TIMEOUT_SECONDS": "30",
        "STATUTETOOL": "True",
        "STATUTE_TIMEOUT_SECONDS": "30"
      }
    }
  }
}
```

#### Streamable-HTTP Transport (networked / production)

```json
{
  "mcpServers": {
    "legal-peripherals-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "legal-peripherals-mcp[mcp]",
        "legal-peripherals-mcp",
        "--transport",
        "streamable-http",
        "--port",
        "8000"
      ],
      "env": {
        "TRANSPORT": "streamable-http",
        "HOST": "0.0.0.0",
        "PORT": "8000",
        "MCP_TOOL_MODE": "condensed",
        "BYPASS_IRS_FILING_HOURS": "False",
        "EINTOOL": "True",
        "EIN_TIMEOUT_SECONDS": "30",
        "LEGAL_PERIPHERALS_BASE_URL": "http://localhost:8000",
        "LEGAL_PERIPHERALS_TOKEN": "",
        "OPENCORPORATES_API_TOKEN": "",
        "SOSTOOL": "True",
        "SOS_TIMEOUT_SECONDS": "30",
        "STATUTETOOL": "True",
        "STATUTE_TIMEOUT_SECONDS": "30"
      }
    }
  }
}
```

Alternatively, connect to a pre-deployed Streamable-HTTP instance by `url`:

```json
{
  "mcpServers": {
    "legal-peripherals-mcp": {
      "url": "http://localhost:8000/legal-peripherals-mcp/mcp"
    }
  }
}
```

Deploying the Streamable-HTTP server via Docker:

```bash
docker run -d \
  --name legal-peripherals-mcp-mcp \
  -p 8000:8000 \
  -e TRANSPORT=streamable-http \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  -e MCP_TOOL_MODE=condensed \
  -e BYPASS_IRS_FILING_HOURS=False \
  -e EINTOOL=True \
  -e EIN_TIMEOUT_SECONDS=30 \
  -e LEGAL_PERIPHERALS_BASE_URL=http://localhost:8000 \
  -e LEGAL_PERIPHERALS_TOKEN="" \
  -e OPENCORPORATES_API_TOKEN="" \
  -e SOSTOOL=True \
  -e SOS_TIMEOUT_SECONDS=30 \
  -e STATUTETOOL=True \
  -e STATUTE_TIMEOUT_SECONDS=30 \
  knucklessg1/legal-peripherals-mcp:mcp
```

_Auto-generated from the code-read env surface (`MCP_TOOL_MODE` + package vars) — do not edit._
<!-- MCP-CONFIG-EXAMPLES:END -->

<!-- BEGIN GENERATED: additional-deployment-options -->
### Additional Deployment Options

`legal-peripherals-mcp` can also run as a **local container** (Docker / Podman / `uv`) or be
consumed from a **remote deployment**. The
[Deployment guide](https://knuckles-team.github.io/legal-peripherals-mcp/deployment/) has full, copy-paste
`mcp_config.json` for all four transports — **stdio**, **streamable-http**,
**local container / uv**, and **remote URL**:

- **Local container / uv** — launch the server from `mcp_config.json` via `uvx`,
  `docker run`, or `podman run`, or point at a local streamable-http container by `url`.
- **Remote URL** — connect to a server deployed behind Caddy at
  `http://legal-peripherals-mcp.arpa/mcp` using the `"url"` key.
<!-- END GENERATED: additional-deployment-options -->


<!-- BEGIN agent-os-genesis-deploy (generated; do not edit between markers) -->

## Deploy with `agent-os-genesis`

This package can be provisioned for you — skill-guided — by the **`agent-os-genesis`**
universal skill (its *single-package deploy mode*): it picks your install method, seeds
secrets to OpenBao/Vault (or `.env`), trusts your enterprise CA, registers the MCP
server, and verifies it — the same machinery that stands up the whole Agent OS, narrowed
to just this package. Ask your agent to **"deploy `legal-peripherals-mcp` with agent-os-genesis"**.

| Install mode | Command |
|------|---------|
| Bare-metal, prod (PyPI) | `uvx legal-peripherals-mcp` · or `uv tool install legal-peripherals-mcp` |
| Bare-metal, dev (editable) | `uv pip install -e ".[all]"` · or `pip install -e ".[all]"` |
| Container, prod | deploy `knucklessg1/legal-peripherals-mcp:latest` via docker-compose / swarm / podman / podman-compose / kubernetes |
| Container, dev (editable) | deploy `docker/compose.dev.yml` (source-mounted at `/src`; edits live on restart) |

Secrets are read-existing + seeded via `vault_sync` — you are only prompted for what's missing.

<!-- END agent-os-genesis-deploy -->

## Environment Variables

<!-- ENV-VARS-TABLE:START -->

#### Package environment variables

| Variable | Example | Description |
|----------|---------|-------------|
| `SOSTOOL` | `True` | Tool Suite Toggles |
| `EINTOOL` | `True` |  |
| `STATUTETOOL` | `True` |  |
| `BYPASS_IRS_FILING_HOURS` | `False` | IRS EIN API hours simulation override (optional, True to bypass hours restriction in dev) |
| `EIN_TIMEOUT_SECONDS` | `30` | EIN draft request timeout in seconds |
| `SOS_TIMEOUT_SECONDS` | `30` | Secretary of State entity lookup (OpenCorporates company registry) |
| `OPENCORPORATES_API_TOKEN` | — |  |
| `OPENCORPORATES_BASE_URL` | `https://api.opencorporates.com/v0.4` |  |
| `STATUTE_TIMEOUT_SECONDS` | `30` | Statute / charter lookup request timeout in seconds |
| `LEGAL_PERIPHERALS_BASE_URL` | `http://localhost:8000` | API Client Connection Configuration |
| `LEGAL_PERIPHERALS_TOKEN` | — |  |
| `LEGAL_PERIPHERALS_SSL_VERIFY` | `True` |  |

#### Inherited agent-utilities variables (apply to every connector)

| Variable | Example | Description |
|----------|---------|-------------|
| `TRANSPORT` | `stdio` | MCP transport: `stdio` | `streamable-http` | `sse` |
| `HOST` | `0.0.0.0` | Bind host (HTTP transports) |
| `PORT` | `8000` | Bind port (HTTP transports) |
| `MCP_TOOL_MODE` | `condensed` | Tool surface: `condensed` | `verbose` | `both` |
| `MCP_ENABLED_TOOLS` | — | Comma-separated tool allow-list |
| `MCP_DISABLED_TOOLS` | — | Comma-separated tool deny-list |
| `MCP_ENABLED_TAGS` | — | Comma-separated tag allow-list |
| `MCP_DISABLED_TAGS` | — | Comma-separated tag deny-list |
| `EUNOMIA_TYPE` | `none` | Authorization mode: `none` | `embedded` | `remote` |
| `EUNOMIA_POLICY_FILE` | `mcp_policies.json` | Embedded Eunomia policy file |
| `EUNOMIA_REMOTE_URL` | — | Remote Eunomia authorization server URL |
| `ENABLE_OTEL` | `False` | Enable OpenTelemetry export |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | — | OTLP collector endpoint |
| `MCP_CLIENT_AUTH` | — | Outbound MCP auth (`oidc-client-credentials` for fleet calls) |
| `OIDC_CLIENT_ID` | — | OIDC client id (service-account auth) |
| `OIDC_CLIENT_SECRET` | — | OIDC client secret (service-account auth) |
| `DEBUG` | `False` | Verbose logging |
| `PYTHONUNBUFFERED` | `1` | Unbuffered stdout (recommended in containers) |
| `MCP_URL` | `http://localhost:8000/mcp` | URL of the MCP server the agent connects to |
| `PROVIDER` | `openai` | LLM provider for the agent |
| `MODEL_ID` | `gpt-4o` | Model id for the agent |
| `ENABLE_WEB_UI` | `True` | Serve the AG-UI web interface |

_12 package + 22 inherited variable(s). Auto-generated from `.env.example` + the shared agent-utilities set — do not edit._
<!-- ENV-VARS-TABLE:END -->
