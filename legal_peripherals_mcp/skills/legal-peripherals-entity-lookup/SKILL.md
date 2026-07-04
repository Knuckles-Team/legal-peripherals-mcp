---
name: legal-peripherals-entity-lookup
description: >-
  Secretary-of-State business-entity lookup over the legal-peripherals-mcp MCP
  server — search a company registry (OpenCorporates-backed) by state + name or
  fetch one by company number, and natively ingest the matches into the knowledge
  graph as typed :BusinessEntity nodes. Use when the agent must verify a company's
  registration status, jurisdiction, incorporation date, or registered address, or
  seed the KG with SOS records. Do NOT use for drafting an EIN application
  (legal-peripherals-ein-filing) or reading statutory default rules /charter
  templates (legal-peripherals-statute-lookup).
license: MIT
tags: [legal-peripherals, sos, secretary-of-state, company-registry, kg-ingest, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---

# Legal Peripherals — Secretary-of-State Entity Lookup

Domain-typed access to US Secretary-of-State / company-registry filings via the
**`legal-peripherals-mcp`** MCP server, backed by the OpenCorporates aggregator
(`us_<state>` jurisdictions). Lookups return real registry records or an honest
"not configured / not found" notice — never a fabricated entity.

## When to use
- Verify a company's registration: status, entity type, jurisdiction, incorporation
  / dissolution date, registered address.
- Search a state's registry by entity name, or fetch one entity by company number.
- Seed the knowledge graph with `:BusinessEntity` records for downstream reasoning.

## When NOT to use
- Drafting an IRS Form SS-4 / EIN application → `legal-peripherals-ein-filing`.
- Statutory default rules or charter/operating-agreement templates →
  `legal-peripherals-statute-lookup`.
- Non-US or arbitrary web company data — this tool is scoped to US SOS jurisdictions.

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`legal-peripherals-mcp`** MCP server.

| Variable | Required | Notes |
|----------|----------|-------|
| `OPENCORPORATES_API_TOKEN` | ✅ | Registry API token; without it lookups report "not configured" and return no record |
| `OPENCORPORATES_BASE_URL` | optional | Override for a self-hosted/proxy registry (default `https://api.opencorporates.com/v0.4`) |
| `SOS_TIMEOUT_SECONDS` | optional | Per-lookup timeout (default 30) |
| `LEGAL_KG_INGEST` | optional | `true` (default) auto-ingests looked-up entities into the KG; set `false` to disable |

## Tools & actions
| Tool | Purpose |
|------|---------|
| `sos_entity_lookup` | Search / fetch a SOS business entity (`state`, `entity_name`, optional `entity_id`) |
| `legal_ingest_sos_entities` | Wire-First: list registry records for `state`+`entity_name` and push them to the KG as `:BusinessEntity` nodes |

### Key parameters
- `state` — two-letter US state/territory code (e.g. `DE`, `WY`, `TX`).
- `entity_name` — the company name to search (≤500 chars).
- `entity_id` — optional registry company number for a direct fetch (skips search).
- `limit` — (ingest tool) max records to fetch/ingest (default 10).

## Recipes
Search Delaware for a company by name:
```
sos_entity_lookup(state="DE", entity_name="Acme Holdings")
```
Fetch one Wyoming entity directly by company number:
```
sos_entity_lookup(state="WY", entity_name="Acme Holdings", entity_id="2021-000123456")
```
Ingest the top matches into the knowledge graph (Wire-First):
```
legal_ingest_sos_entities(state="DE", entity_name="Acme Holdings", limit=5)
```

## Native KG ingestion
Every successful lookup auto-ingests its company records (unless `LEGAL_KG_INGEST=false`):
- each record → a `:BusinessEntity` node, id `legal:businessentity:<jurisdiction>_<number>`,
  carrying `name`, `companyNumber`, `registryStatus`, `incorporationDate`, `registered_address`,
  `source_uri`.
- its jurisdiction → a `:Jurisdiction` node with an `:incorporatedIn` link.

`legal_ingest_sos_entities` is the explicit Wire-First entry point and also returns the
raw `entities` list plus `{"ingested": {...}|None}`.

## Gotchas
- No `OPENCORPORATES_API_TOKEN` ⇒ the tool truthfully reports "not configured" and returns
  no record; ingestion no-ops.
- Ingestion is best-effort and engine-guarded: with no reachable epistemic-graph engine it
  silently no-ops; the lookup result is never affected.
- Company number formats are jurisdiction-specific; prefer a name search first, then a
  direct fetch with the returned `Company Number`.

## Related
- `legal-peripherals-ein-filing` — draft an SS-4 for a looked-up entity.
- `legal-peripherals-statute-lookup` — statutory defaults & charter templates.
- `mcp-client` — connect to and invoke the MCP server.
