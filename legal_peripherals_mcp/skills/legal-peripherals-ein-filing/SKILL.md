---
name: legal-peripherals-ein-filing
description: >-
  Draft an IRS Form SS-4 (Employer Identification Number application) over the
  legal-peripherals-mcp MCP server, with IRS off-hours filing-window compliance,
  and natively ingest the draft into the knowledge graph as an :EINApplication
  filing linked to its :BusinessEntity. Use when the agent must prepare an EIN
  application for a new LLC / corporation / trust and schedule its submission. Do
  NOT use for looking up an existing company (legal-peripherals-entity-lookup) or
  reading statutory rules / charter templates (legal-peripherals-statute-lookup).
license: MIT
tags: [legal-peripherals, ein, ss4, irs, filing, kg-ingest, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---

# Legal Peripherals — EIN (Form SS-4) Filing

Prepare and schedule an IRS **Form SS-4** Employer Identification Number application
via the **`legal-peripherals-mcp`** MCP server. The tool renders a masked SS-4 draft
and either files immediately (during IRS operating hours, Mon–Fri 7:00 AM – 10:00 PM
ET) or queues it for the next valid window.

## When to use
- Prepare an EIN application for a new business entity (LLC, corporation, trust, etc.).
- Produce a review-ready SS-4 draft with responsible-party SSN masked.
- Schedule submission with IRS off-hours compliance.

## When NOT to use
- Verifying / searching an existing registered company → `legal-peripherals-entity-lookup`.
- Statutory default rules or charter/operating-agreement templates →
  `legal-peripherals-statute-lookup`.
- Actually transmitting to the IRS e-file system — this tool drafts and schedules; it does
  not replace an authorized IRS submission channel.

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`legal-peripherals-mcp`** MCP server.

| Variable | Required | Notes |
|----------|----------|-------|
| `BYPASS_IRS_FILING_HOURS` | optional | `true` forces "file immediately" regardless of the clock (testing) |
| `EIN_TIMEOUT_SECONDS` | optional | Per-draft timeout (default 30) |
| `LEGAL_KG_INGEST` | optional | `true` (default) auto-ingests each draft into the KG; set `false` to disable |

## Tools & actions
| Tool | Purpose |
|------|---------|
| `draft_ein_form` | Draft an SS-4 and schedule its filing per IRS hours |
| `legal_ingest_filing_file` | Wire-First: store a rendered filing file (e.g. `drafts/ein_ss4_draft.txt`) as a blob + `:MediaAsset` in the KG |

### Key parameters
- `legal_name` (required) — exact legal name of the entity.
- `business_type` — one of LLC, Corporation, S Corporation, Partnership, Sole Proprietor,
  Trust, Estate, Non-Profit, Church, Government, Other (default `LLC`).
- `responsible_party_ssn` / `responsible_party_name`, `trade_name`, `mailing_address`,
  `county_state`, `reason_for_applying`, `first_date_wages_paid`, `max_employees`,
  `closing_month_tax_year`.

## Recipes
Draft an SS-4 for a new Wyoming LLC:
```
draft_ein_form(legal_name="Acme Holdings LLC", business_type="LLC",
               responsible_party_name="Jane Doe", responsible_party_ssn="123456789",
               county_state="Laramie, WY", reason_for_applying="Started new business")
```
Persist a produced draft file as a durable blob in the KG:
```
legal_ingest_filing_file(file_path="drafts/ein_ss4_draft.txt", filing_type="ss4_ein")
```

## Native KG ingestion
Every draft auto-ingests (unless `LEGAL_KG_INGEST=false`):
- the application → an `:EINApplication` node (id `legal:einapplication:<slug>`), a subclass of
  `:RegulatoryFiling`, carrying `filingType=ss4_ein`, `filingAgency=IRS`, `filingStatus`,
  `business_type`, and the rendered draft `text`.
- the entity → a `:BusinessEntity` node with an `:appliesForEntity` link.

Rendered filing **files** (the `drafts/*.txt` artifacts) are stored as content-addressed
**blobs** with a `:MediaAsset` node via `legal_ingest_filing_file`.

## Gotchas
- The SSN is always masked (`***-**-1234`) in the rendered draft — never echo a full SSN.
- Filing status depends on the wall clock in `America/New_York`; use `BYPASS_IRS_FILING_HOURS=true`
  only for tests.
- Ingestion is best-effort and engine-guarded: no reachable engine ⇒ silent no-op; the draft
  is unaffected.
- `business_type` must be one of the accepted SS-4 values or the tool returns a validation error.

## Related
- `legal-peripherals-entity-lookup` — verify the entity before drafting.
- `legal-peripherals-statute-lookup` — charter/operating-agreement templates for the entity.
- `mcp-client` — connect to and invoke the MCP server.
