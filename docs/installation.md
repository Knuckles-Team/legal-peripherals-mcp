# Installation

`legal-peripherals-mcp` is a standard Python package and a prebuilt container image.
Pick the path that matches how you want to run it.

## Requirements

- **Python 3.11 – 3.14**.
- [Playwright](https://playwright.dev/python/) browser binaries for the live
  Secretary of State crawlers (installed with `playwright install`); the fallback
  paths operate without them.

## From PyPI (recommended)

```bash
pip install legal-peripherals-mcp
```

### Optional extras

The base install is intentionally minimal. Install the extra for what you need:

| Extra | Install | Pulls in |
|---|---|---|
| `mcp` | `pip install "legal-peripherals-mcp[mcp]"` | FastMCP MCP-server runtime (`agent-utilities[mcp]`) |
| `agent` | `pip install "legal-peripherals-mcp[agent]"` | Pydantic-AI agent server + Logfire tracing |
| `all` | `pip install "legal-peripherals-mcp[all]"` | Everything above |
| `test` | `pip install "legal-peripherals-mcp[test]"` | `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-xdist` |

```bash
# Typical: run the MCP server and the agent server
pip install "legal-peripherals-mcp[all]"
playwright install chromium
```

## From source

```bash
git clone https://github.com/Knuckles-Team/legal-peripherals-mcp.git
cd legal-peripherals-mcp
pip install -e ".[all]"          # editable install with every extra
```

With [`uv`](https://docs.astral.sh/uv/):

```bash
uv pip install -e ".[all]"
uv run legal-peripherals-mcp
```

## Prebuilt Docker image

A multi-stage runtime image is published on every release (entrypoint
`legal-peripherals-mcp`):

```bash
docker pull example/legal-peripherals-mcp@sha256:<digest>

docker run --rm -i \
  -e SOSTOOL=True \
  -e EINTOOL=True \
  -e STATUTETOOL=True \
  example/legal-peripherals-mcp@sha256:<digest>        # stdio transport (default)
```

For an HTTP server with a published port, see [Deployment](deployment.md).

## Verify the install

```bash
legal-peripherals-mcp --help
python -c "import legal_peripherals_mcp; print(legal_peripherals_mcp.__version__)"
```

## Next steps

- **[Deployment](deployment.md)** — run it as a long-lived MCP server behind Caddy + DNS.
- **[Usage](usage.md)** — call the tools, the API, and example prompts.
- **[Configuration](deployment.md#configuration-environment)** — every environment variable.
