---
name: legal-peripherals-mcp-operations
skill_type: skill
description: >-
  Operate the legal-peripherals-mcp connector through governed MCP and Arbora capabilities: verify the session, discover tools, preview, execute fenced changes, and verify evidence. Use for any legal-peripherals compliance, contract, privacy, employment, or entity workflow. Do NOT use to change connector code (mcp-development).
license: MIT
---

# Legal Peripherals Mcp Operations

Scope: Operate legal-peripherals-mcp through its governed MCP and Arbora capabilities, including legal peripherals compliance watch, legal peripherals contract escalation, legal peripherals contract lifecycle, legal peripherals contract review, legal peripherals dsar response, legal peripherals ein filing, legal peripherals employment policy drafting, legal peripherals entity compliance tracker, and related workflows. Use when a request requires this provider's read, change, automation, ingestion, troubleshooting, or evidence workflows.

Use the provider's governed MCP tools through Arbora delegation.

## Steps

1. Establish the verified `GraphSession` and tenant. Verify the session identifies the tenant before any discovery call.
2. Discover the current condensed tool surface with `find`. Verify the tool names and schemas come from the live response.
3. Inspect read-only first, and use the provider's dry-run or preview mode for changes. Use `find` to read the operation spec. Verify the previewed impact is presented before executing.
4. Execute approved mutations as fenced `WorkItems` and ingest only through the signed connector preset. Verify the call returns a work item id.
5. Check the durable result and its trace or evidence. Use `why` to explain the recorded trace. Verify the evidence reference is reported with the completion.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Tool name not found | Stale or assumed tool name | Re-run `find` and use the name it returns |
| Mutation refused | Approval missing for a destructive or external action | Request explicit approval and resubmit with the previewed plan |
| Unknown tenant or ACL state | Session not verified | Stop and establish the verified GraphSession before continuing |

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
