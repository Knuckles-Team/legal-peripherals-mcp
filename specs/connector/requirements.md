# CONN-LEGAL-PERIPHERALS-MCP — Requirements

Governing spec: [spec.md](spec.md).

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-LEGAL-PERIPHERALS-MCP-R001` | **Read-only lookups.** The connector must annotate `sos_entity_lookup`, `lookup_statute_rules` and `legal_compliance_lookup` as read-only in `legal_peripherals_mcp/mcp_server.py`. The connector must expose `legal_list_statute_coverage` with no argument. Caller chain: the `legal-peripherals-mcp` console script (pyproject.toml, legal_peripherals_mcp.mcp_server:mcp_server) -> get_mcp_instance -> register_server_surface:191 -> register_tool_surface -> the registrars register_sos_tools:29, register_statute_tools:80 and register_compliance_tools:154 that define the lookups. Shape: legal_peripherals_mcp/mcp_server.py applies the module-level READ_ONLY annotation dict (readOnlyHint, destructiveHint false, idempotentHint) to sos_entity_lookup, lookup_statute_rules, legal_list_statute_coverage and legal_compliance_lookup; draft_ein_form stays unannotated and the coverage tool takes no parameters. | `tests/test_read_only_tools.py` must show: the four lookups are listed read-only and not destructive, the filing draft is not read-only, and the coverage tool returns the covered pairs and topics with no argument. Test: `tests/test_read_only_tools.py::test_lookups_are_listed_read_only`. |
