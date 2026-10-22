# CONN-LEGAL-PERIPHERALS-MCP — Read-only operations

Owner: legal-peripherals-mcp. Cross-repo IDs: none.

## Purpose and user stories

A fleet operator must check the connector without a filing or an ingest. The connector must expose read-only lookups with the read-only annotation.

## Requirements and acceptance

- FR-001: The connector must annotate `sos_entity_lookup`, `lookup_statute_rules` and `legal_compliance_lookup` as read-only in `legal_peripherals_mcp/mcp_server.py`. The connector must expose `legal_list_statute_coverage` with no argument.
- SC-001: the four lookups are listed read-only and not destructive, the filing draft is not read-only, and the coverage tool returns the covered pairs and topics with no argument.

## Why a new spec

The `specs/` tree held only the template and the index.
No local spec owned this behavior, so this spec is the first capability spec.

## Scope and interfaces

The connector owns its operations and their MCP tool annotations.
The connector SDK owns tool registration, transport and the shared client contracts.
Code: ../../legal_peripherals_mcp/mcp/mcp_statute.py ../../legal_peripherals_mcp/mcp_server.py ../../tests/test_read_only_tools.py

## Traceability

| Requirement | Design section | Test ID | Evidence |
|---|---|---|---|
| FR-001 | plan.md#architecture | T-001 | `tests/test_read_only_tools.py` |

## Open questions

- None.
