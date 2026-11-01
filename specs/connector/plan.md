# CONN-LEGAL-PERIPHERALS-MCP — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

The statute, entity and compliance lookups existed without annotations. The statute data source existed in `legal_peripherals_mcp/mcp/mcp_statute.py`. `legal_list_statute_coverage` reads the bundled statute source and returns its covered states, entity types and topics. It takes no argument and writes nothing.

## Technical Context

- **Language/Version**: Python 3.14 (floor 3.12)
- **Primary Dependencies**: scion-sdk, fastmcp
- **Storage**: N/A; the connector stores nothing
- **Testing**: pytest; the proof level each row names
- **Target Platform**: Linux containers
- **Project Type**: connector (MCP server)
- **Performance Goals**: N/A
- **Constraints**: one tool per API operation; shared capabilities come from the SDK
- **Scale/Scope**: 1 rows

## Constitution Check

- One owner per concept: pass. The connector owns one external system's calls, mappings and tools only.
- Connectors depend on the SDK and are called through arbora: pass.
- No ratchets: pass. The rows add no suppression.

## Project Structure

```text
legal_peripherals_mcp/mcp_server.py  existing
```

## Phase 0: Research

No unknowns. Each row names the code it touches.

## Phase 1: Design

### Interfaces and data model

The change adds no wire field. The tool returns the API response document.

### Live integration path

The fleet gateway lists the tool, reads its annotation and calls it as the gateway identity.

### Quality and release gates

The focused tests run with `pytest -q`. A merge to the default branch publishes the package and the image.

### Risks, alternatives, and decisions

No new risk. The operation reads state and changes nothing.

## Phase 2: Task approach

`tasks.md` holds one task line per row, producer first.

## Complexity Tracking

None. The constitution check passed.

## Build contract

The repository pre-commit hooks apply: `ruff-format`, `connector-standard`, `secrets`, `tests-fast`. Each row names its proving test. No suppression and no duplicate implementation.

## Production caller chain

1. `CONN-LEGAL-PERIPHERALS-MCP-R001`: the `legal-peripherals-mcp` console script (pyproject.toml, legal_peripherals_mcp.mcp_server:mcp_server) -> get_mcp_instance -> register_server_surface:191 -> register_tool_surface -> the registrars register_sos_tools:29, register_statute_tools:80 and register_compliance_tools:154 that define the lookups.

## Cross-repo seams

none
