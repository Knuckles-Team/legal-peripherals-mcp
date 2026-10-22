# CONN-LEGAL-PERIPHERALS-MCP — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Level | Setup and input | Expected observation | Evidence |
|---|---|---|---|---|---|
| T-001 | FR-001 | Unit | Mocked HTTP | the four lookups are listed read-only and not destructive, the filing draft is not read-only, and the coverage tool returns the covered pairs and topics with no argument. | `tests/test_read_only_tools.py` |

## Negative and boundary cases

The tests cover the error path that each row names.

## Quality and release proof

Run `pytest -q`. The served proof is the fleet acceptance check through the gateway.
