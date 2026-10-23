# CONN-LEGAL-PERIPHERALS-MCP-CONNECTOR-CONTENT — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Architecture

`pyproject.toml` declares `legal-peripherals-mcp` as the connector identity. `create_mcp_server` resolves the packaged content of `legal_peripherals_mcp` from it.
