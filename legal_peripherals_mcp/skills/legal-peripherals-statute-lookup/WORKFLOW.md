# Legal Peripherals Statute Lookup

Query US state statutory default rules and retrieve corporate / LLC charter templates over the legal-peripherals-mcp MCP server. Use when the agent must find the default voting, governance, allocation, or distribution rules for an entity type in a given state, or generate a starter Articles of Incorporation / Operating Agreement, and optionally ingest the summary into the knowledge graph as a searchable :Document. Do NOT use for looking up a registered company (legal-peripherals-entity-lookup) or drafting an EIN application (legal-peripherals-ein-filing).

# Legal Peripherals — Statute & Charter-Template Lookup

Query state statutory default rules and pull corporate/LLC charter templates via the
**`legal-peripherals-mcp`** MCP server. Returns a statutory summary for a
(state, entity_type, topic) plus a recommended Articles-of-Incorporation or
Operating-Agreement template, with a general fallback for states lacking a curated entry.

## When to use
- Find a state's default rules for an entity type on a topic (voting, governance,
  allocations, distributions, management).
- Retrieve a starter charter / operating-agreement template for drafting.
- Ground formation decisions in statutory defaults before customizing a document.

## When NOT to use
- Looking up an existing registered company → `legal-peripherals-entity-lookup`.
- Drafting an IRS Form SS-4 / EIN application → `legal-peripherals-ein-filing`.
- Authoritative legal advice or full statute text — this returns curated defaults and
  templates, not primary-source case law.

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`legal-peripherals-mcp`** MCP server.

| Variable | Required | Notes |
|----------|----------|-------|
| `STATUTE_TIMEOUT_SECONDS` | optional | Per-lookup timeout (default 30) |

No external API token is required — statutory defaults + templates are served locally.

## Tools & actions
| Tool | Purpose |
|------|---------|
| `lookup_statute_rules` | Return statutory defaults + a recommended charter template for `state`, `entity_type`, `topic` |

### Key parameters
- `state` — two-letter US state/territory code.
- `entity_type` — e.g. `LLC` or `Corporation`.
- `topic` — the governance topic (e.g. `voting`, `distributions`, `management`).

## Recipes
Default voting rules + operating-agreement template for a Delaware LLC:
```
lookup_statute_rules(state="DE", entity_type="LLC", topic="voting")
```
Default distribution rules for a Wyoming corporation:
```
lookup_statute_rules(state="WY", entity_type="Corporation", topic="distributions")
```

## Native KG ingestion
Statutory summaries and templates can be persisted as searchable `:Document` nodes for
downstream semantic search via `legal_peripherals_mcp.kg_ingest.ingest_filing_document`
(id `legal:document:<...>`, `doc_type=statute_summary`). Rendered filing artifacts are
better stored as blobs — see `legal-peripherals-ein-filing`.

## Gotchas
- States without a curated entry return a **general fallback** summary + generic template;
  treat these as starting points, not authoritative statute text.
- `entity_type` and `topic` are normalized (case-insensitive); unknown topics fall back to a
  default-rules notice for that state.
- This is decision-support, not legal advice — always validate against the primary source
  before filing.

## Related
- `legal-peripherals-entity-lookup` — verify the entity in the state registry.
- `legal-peripherals-ein-filing` — draft the entity's SS-4 once formed.
- `mcp-client` — connect to and invoke the MCP server.
