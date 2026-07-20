---
name: legal-peripherals-mcp-operations
description: >-
  Operate legal-peripherals-mcp through its governed MCP and GraphOS capabilities, including legal peripherals compliance watch, legal peripherals contract escalation, legal peripherals contract lifecycle, legal peripherals contract review, legal peripherals dsar response, legal peripherals ein filing, legal peripherals employment policy drafting, legal peripherals entity compliance tracker, and related workflows. Use when a request requires this provider's read, change, automation, ingestion, troubleshooting, or evidence workflows.
---

# Legal Peripherals Mcp Operations

Use the provider's governed MCP tools through GraphOS delegation.

## Workflow

1. Establish the verified GraphSession and tenant before discovery or retrieval.
2. Discover the current condensed tool surface; never assume a stale tool name or schema.
3. Prefer read-only inspection first. For changes, present impact and use the provider's
   dry-run or preview mode when available.
4. Execute mutations as fenced WorkItems so retries remain idempotent and auditable.
5. Ingest source data only through the signed connector preset and ChangeEnvelope path.
6. Verify the durable result and its trace/evidence before reporting completion.

## Safety contract

- Never persist credentials, endpoints, raw personal identifiers, hostnames, or local paths.
- Resolve TLS trust and verification from environment/configuration; never hardcode bypasses.
- Treat unknown ACL, tenant, schema, or tool-contract state as a hard failure.
- Require explicit approval for destructive, externally visible, or irreversible actions.
- Keep runtime traces policy-scoped and privacy-sanitized.

## Specialized workflows

Read [the workflow catalog](references/catalog.md) only when the request needs a
provider-specific procedure, parameter map, script, or reference asset.
