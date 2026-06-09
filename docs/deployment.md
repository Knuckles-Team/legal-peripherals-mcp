# Deployment

This page covers running `legal-peripherals-mcp` as a long-lived server: the
transports, a Docker Compose stack, the optional agent server, putting it behind a
Caddy reverse proxy, and giving it a DNS name with Technitium.

> `legal-peripherals-mcp` ships an **MCP server** (console script
> `legal-peripherals-mcp`) and an optional **Pydantic-AI agent server** (console
> script `legal-peripherals-agent`). The MCP server is a typed, deterministic tool
> surface a policy router / agent calls; the agent server wraps that surface for
> conversational use.

## Run the MCP server

The transport is selected with `--transport` (or the `TRANSPORT` env var):

=== "stdio (default)"

    ```bash
    legal-peripherals-mcp
    ```
    For IDE / desktop MCP clients that launch the server as a subprocess.

=== "streamable-http"

    ```bash
    legal-peripherals-mcp --transport streamable-http --host 0.0.0.0 --port 8000
    ```
    A network server with a `/health` endpoint and `/mcp` route.

=== "sse"

    ```bash
    legal-peripherals-mcp --transport sse --host 0.0.0.0 --port 8000
    ```

Health check (HTTP transports):

```bash
curl -s http://localhost:8000/health        # {"status":"OK"}
```

## Configuration (environment)

`legal-peripherals-mcp` is configured entirely from the environment. The **required**
set:

| Var | Default | Meaning |
|---|---|---|
| `SOSTOOL` | `True` | Register the `sos_entity_lookup` tool |
| `EINTOOL` | `True` | Register the `draft_ein_form` tool |
| `STATUTETOOL` | `True` | Register the `lookup_statute_rules` tool |
| `BYPASS_IRS_FILING_HOURS` | `False` | Bypass the IRS active-hours restriction (development only) |
| `LEGAL_PERIPHERALS_BASE_URL` | `http://localhost:8000` | Base URL of the backing legal-peripherals API |
| `LEGAL_PERIPHERALS_TOKEN` | _(empty)_ | Bearer credential for the backing API |
| `LEGAL_PERIPHERALS_SSL_VERIFY` | `True` | Verify TLS on backing requests |

Plus `HOST` / `PORT` / `TRANSPORT` for HTTP transports. Copy
[`.env.example`](https://github.com/Knuckles-Team/legal-peripherals-mcp/blob/main/.env.example)
to `.env` and populate only what you use; the connector remains inactive against the
backing API when `LEGAL_PERIPHERALS_TOKEN` is absent.

## Docker Compose

The repo ships [`docker/compose.yml`](https://github.com/Knuckles-Team/legal-peripherals-mcp/blob/main/docker/compose.yml).
It publishes the HTTP server on `:8000`:

```yaml
services:
  legal-peripherals-mcp:
    image: knucklessg1/legal-peripherals-mcp:latest
    container_name: legal-peripherals-mcp
    hostname: legal-peripherals-mcp
    restart: always
    environment:
      - PYTHONUNBUFFERED=1
      - TRANSPORT=streamable-http
      - HOST=0.0.0.0
      - PORT=8000
      - SOSTOOL=True
      - EINTOOL=True
      - STATUTETOOL=True
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

```bash
cp .env.example .env          # then edit the LEGAL_PERIPHERALS_* values
docker compose -f docker/compose.yml up -d
docker compose -f docker/compose.yml logs -f
```

## Agent server

The agent server (`legal-peripherals-agent`) wraps the MCP tool surface in a
Pydantic-AI agent with an optional web UI. It connects to a running MCP server via
`--mcp-url` (or loads tools directly from `mcp_config.json`):

```bash
pip install "legal-peripherals-mcp[agent]"

legal-peripherals-agent \
  --mcp-url http://legal-peripherals-mcp:8000/mcp \
  --host 0.0.0.0 --port 8001 --web
```

The same published image runs the agent by overriding the entrypoint. Add a second
service to your Compose stack that wires `MCP_URL` at the running MCP server:

```yaml
  legal-peripherals-agent:
    image: knucklessg1/legal-peripherals-mcp:latest
    container_name: legal-peripherals-agent
    entrypoint: ["legal-peripherals-agent"]
    command: ["--host", "0.0.0.0", "--port", "8001", "--mcp-url", "http://legal-peripherals-mcp:8000/mcp"]
    environment:
      - MCP_URL=http://legal-peripherals-mcp:8000/mcp
    depends_on:
      - legal-peripherals-mcp
    ports:
      - "8001:8001"
```

## Behind a Caddy reverse proxy

Expose the HTTP server on a hostname with automatic TLS. Add to your `Caddyfile`:

```caddy
# Internal (self-signed) — homelab .arpa zone
legal-peripherals-mcp.arpa {
    tls internal
    reverse_proxy legal-peripherals-mcp:8000
}
```

```caddy
# Public — automatic Let's Encrypt
legal-peripherals-mcp.example.com {
    reverse_proxy legal-peripherals-mcp:8000
}
```

Reload Caddy:

```bash
docker compose -f services/caddy/compose.yml exec caddy caddy reload --config /etc/caddy/Caddyfile
```

## DNS with Technitium

Point the hostname at the host running Caddy. Via the Technitium API:

```bash
curl -s "http://technitium.arpa:5380/api/zones/records/add" \
  --data-urlencode "token=$TECHNITIUM_DNS_TOKEN" \
  --data-urlencode "domain=legal-peripherals-mcp.arpa" \
  --data-urlencode "zone=arpa" \
  --data-urlencode "type=A" \
  --data-urlencode "ipAddress=10.0.0.10" \
  --data-urlencode "ttl=3600"
```

…or add an **A record** `legal-peripherals-mcp.arpa → <caddy-host-ip>` in the
Technitium web console (`http://technitium.arpa:5380`). The ecosystem
[`technitium-dns-mcp`](https://knuckles-team.github.io/technitium-dns-mcp/) automates
this as a tool.

## Register with an MCP client

Add to your client's `mcp_config.json`:

```json
{
  "mcpServers": {
    "legal_peripherals_mcp": {
      "command": "uv",
      "args": ["run", "legal-peripherals-mcp"],
      "env": {
        "SOSTOOL": "True",
        "EINTOOL": "True",
        "STATUTETOOL": "True"
      }
    }
  }
}
```

For a remote HTTP server, point the client at `http://legal-peripherals-mcp.arpa/mcp`
instead.
