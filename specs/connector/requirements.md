# CONN-LEGAL-PERIPHERALS-MCP — Requirements

Governing spec: [spec.md](spec.md).

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-LEGAL-PERIPHERALS-MCP-R001` | **Read-only lookups.** The connector must annotate `sos_entity_lookup`, `lookup_statute_rules` and `legal_compliance_lookup` as read-only in `legal_peripherals_mcp/mcp_server.py`. The connector must expose `legal_list_statute_coverage` with no argument. | `tests/test_read_only_tools.py` must show: the four lookups are listed read-only and not destructive, the filing draft is not read-only, and the coverage tool returns the covered pairs and topics with no argument. |
