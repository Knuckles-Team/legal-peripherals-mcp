# CONN-LEGAL-PERIPHERALS-MCP — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Existing system and reuse

The statute, entity and compliance lookups existed without annotations. The statute data source existed in `legal_peripherals_mcp/mcp/mcp_statute.py`.

## Architecture

`legal_list_statute_coverage` reads the bundled statute source and returns its covered states, entity types and topics. It takes no argument and writes nothing.

## Interfaces and data model

The change adds no wire field. The tool returns the API response document.

## Live integration path

The fleet gateway lists the tool, reads its annotation and calls it as the gateway identity.

## Quality and release gates

The focused tests run with `pytest -q`. A merge to the default branch publishes the package and the image.

## Risks, alternatives, and decisions

No new risk. The operation reads state and changes nothing.
