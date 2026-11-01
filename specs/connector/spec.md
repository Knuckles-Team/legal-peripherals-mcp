# CONN-LEGAL-PERIPHERALS-MCP — Read-only operations

Owner: legal-peripherals-mcp. Cross-repo IDs: none.

## Purpose and user stories

A fleet operator must check the connector without a filing or an ingest. The connector must expose read-only lookups with the read-only annotation.

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

## User Scenarios & Testing

### User Story 1 - Read-only operations (Priority: P1)

A fleet operator must check the connector without a filing or an ingest. The connector must expose read-only lookups with the read-only annotation.

**Acceptance Scenarios**:

1. **Given** the connector is configured, **When** the behaviour of row `CONN-LEGAL-PERIPHERALS-MCP-R001` (read-only lookups) is exercised, **Then** `tests/test_read_only_tools.py` must show: the four lookups are listed read-only and not destructive, the filing draft is not read-only, and the coverage tool returns the covered pairs and topics with no argument. Test: `tests/test_read_only_tools.py::test_lookups_are_listed_read_only`.

### Edge Cases

- If `CONN-LEGAL-PERIPHERALS-MCP-R001` is not met, its proving test fails: read-only lookups.

## Requirements

- **FR-001**: Read-only lookups. Rows: `CONN-LEGAL-PERIPHERALS-MCP-R001`.

## Success Criteria

- **SC-001**: `tests/test_read_only_tools.py` must show: the four lookups are listed read-only and not destructive, the filing draft is not read-only, and the coverage tool returns the covered pairs and topics with no argument. Rows: `CONN-LEGAL-PERIPHERALS-MCP-R001`.

## Assumptions

- The external system is reachable with operator-supplied credentials.
- The SDK and engine contracts the rows cite are at the floors declared in `pyproject.toml`.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-LEGAL-PERIPHERALS-MCP-R001` | [plan.md](plan.md) | T-001 | [test-spec.md](test-spec.md) |
