# Usage — API / MCP

`legal-peripherals-mcp` exposes its capability two ways: as **MCP tools** an agent
calls, and as a **Python API** (`Api`) you import to reach the backing
legal-peripherals platform. The three tool domains and the architecture are described
in [Overview](overview.md).

## As an MCP server

Once [deployed](deployment.md), the server registers three tools, each independently
toggled by an environment flag (`SOSTOOL`, `EINTOOL`, `STATUTETOOL`).

| Tool | Parameters | Description |
|---|---|---|
| `sos_entity_lookup` | `state`, `entity_name`, `entity_id` (optional) | Secretary of State entity lookup across 50 states — optimized scrapers for TX, DE, WY, NV and a resilient fallback for the rest |
| `draft_ein_form` | `legal_name`, `responsible_party_name`, `business_type`, … | Drafts IRS Form SS-4 and schedules the EIN filing inside the IRS active window (Mon–Fri 7:00 AM – 10:00 PM EST) |
| `lookup_statute_rules` | `state`, `entity_type`, `topic` | Queries state statutory default rules and retrieves corporate / LLC charter templates |

Example agent prompts that map onto these tools:

- *"Look up the entity 'Acme Holdings LLC' with the Delaware Secretary of State"* → `sos_entity_lookup`
- *"Draft an SS-4 EIN application for a new Wyoming LLC named 'Northwind Ventures'"* → `draft_ein_form`
- *"What are Texas LLC default rules on director voting and indemnification?"* → `lookup_statute_rules`

## As a Python API

`Api` is a thin `requests`-backed facade over the backing legal-peripherals platform.
It attaches the bearer token and honours the TLS-verification setting:

```python
from legal_peripherals_mcp.api_client import Api

api = Api(
    base_url="http://localhost:8000",
    token="<your-token>",
    verify=True,
)

# Read calls against the backing platform
entities = api.request("GET", "/sos/entities", params={"state": "DE"})
statutes = api.request("GET", "/statutes/TX/LLC")
```

Build a client straight from the environment (reads `LEGAL_PERIPHERALS_BASE_URL`,
`LEGAL_PERIPHERALS_TOKEN`, `LEGAL_PERIPHERALS_SSL_VERIFY`):

```python
from legal_peripherals_mcp.auth import get_client

api = get_client()        # configured entirely from the environment / .env
```

## As an agent

The optional agent server exposes the same tool surface conversationally. Start it
against a running MCP server and interact through its web UI or API:

```bash
legal-peripherals-agent \
  --mcp-url http://localhost:8000/mcp \
  --host 0.0.0.0 --port 8001 --web
```

See [Deployment](deployment.md#agent-server) for the full agent configuration.
