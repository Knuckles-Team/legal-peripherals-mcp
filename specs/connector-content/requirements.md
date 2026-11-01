# CONN-LEGAL-PERIPHERALS-MCP-CONNECTOR-CONTENT — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-LEGAL-PERIPHERALS-MCP-CONNECTOR-CONTENT-R001` | **Default content.** `pyproject.toml` declares `legal-peripherals-mcp` as the single `scion_sdk.connector` entry point. The server lists the packaged `skill://` and `ontology://` resources and the packaged prompts with no `content=` argument. Proving test: `tests/test_default_content_surfaces.py`. Caller chain: the `legal-peripherals-mcp` console script (pyproject.toml) loads the `scion_sdk.connector` entry point `legal_peripherals_mcp:connector` -> legal_peripherals_mcp/__init__.py::connector (a Connector with no content= argument) -> the SDK default content registration serves skill://, ontology:// and prompts. Shape: tests build the server from legal_peripherals_mcp and list resources and prompts over the packaged legal_peripherals_mcp/skills, legal_peripherals_mcp/ontology and legal_peripherals_mcp/prompts directories. | `resources/list` includes `skill://` and `ontology://`; `prompts/list` includes each packaged prompt. Test: `tests/test_default_content_surfaces.py::test_default_content_surfaces`. |
