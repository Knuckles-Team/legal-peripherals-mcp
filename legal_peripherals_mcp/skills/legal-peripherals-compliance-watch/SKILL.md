---
name: legal-peripherals-compliance-watch
skill_type: skill
description: >-
  Run one cross-domain sweep of regulatory, contract-renewal, leave, and entity deadlines held in the knowledge graph. Use for a portfolio-wide what-needs-attention-this-week review. Do NOT use when one domain matters (regulatory-gap-tracker, contract-lifecycle, leave-tracking, entity-compliance-tracker).
license: MIT
tags: [legal-peripherals, cross-domain, compliance-watch, deadlines, mcp]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---

# Legal Peripherals — Cross-Domain Compliance Watch

Scope: A single, cross-domain deadline/requirement watch that folds what would otherwise be several siloed single-purpose watcher agents (one each for regulatory feeds, contract renewals, data-room diligence, product-launch review, and court dockets) into one KG-native sweep over every ReportingRequirement, RenewalDeadline, and LeaveRequest deadline the compliance + domain ontology suite declares. Use for a portfolio-wide "what needs attention this week" sweep spanning regulatory, commercial, employment, and entity domains at once. Do NOT use for a single domain's dedicated tracker (e.g. legal-peripherals-regulatory-gap-tracker, legal-peripherals-contract-lifecycle, legal-peripherals-leave-tracking, legal-peripherals-entity-compliance-tracker) when only that one domain matters.

Legal-ops deadline monitoring is often split across **several separate
single-purpose watcher agents** — one each for regulatory feeds, contract
renewals, data-room diligence, product-launch review, and court dockets —
each its own reader → filter → writer pipeline wired to a different external
system, with its own per-vertical log file.

This skill takes a KG-native approach instead: every deadline-bearing type
across the ontology suite —
`compliance.ttl`'s `:ReportingRequirement`, `domain_commercial.ttl`'s
`:RenewalDeadline`, `domain_employment.ttl`'s `:LeaveRequest`,
`domain_corporate.ttl`'s `:EntityComplianceDeadline`,
`domain_regulatory.ttl`'s `:RegulatoryChangeNotice.commentDeadline` — is
queryable through **one** the compliance lookup tools (`legal_list_compliance_domains`, `legal_list_regulations`, `legal_get_regulation`, `legal_lookup_sector`, `legal_lookup_data_class`, `legal_gate_requirements`) surface instead of five
siloed watchers, each requiring its own connector adaptation. A real
per-source connector (Ironclad, CourtListener, Jira/Linear, Box/Datasite)
still needs wiring via `source_connector` to populate LIVE instances, but the
ontology shape to receive them — and the cross-domain query to sweep them
all at once — already exists.

## When to use
- A portfolio-wide "what needs attention this week/month" sweep spanning
  MULTIPLE domains at once (e.g. a compliance officer's Monday review).
- Standing up a new deadline-bearing type and want it to compose with the
  existing sweep rather than build a sixth siloed watcher.

## When NOT to use
- A single domain's dedicated, deeper tracker already covers the need →
  `legal-peripherals-regulatory-gap-tracker` /
  `legal-peripherals-contract-lifecycle` /
  `legal-peripherals-leave-tracking` /
  `legal-peripherals-entity-compliance-tracker`.

## Prerequisites & environment
Connect via `mcp-client` against `legal-peripherals-mcp`; `COMPLIANCETOOL`
for the compliance lookup tools (`legal_list_compliance_domains`, `legal_list_regulations`, `legal_get_regulation`, `legal_lookup_sector`, `legal_lookup_data_class`, `legal_gate_requirements`).

## Steps

1. Inventory the deadline-bearing modules with `legal_list_compliance_domains`. Verify the result names the compliance, commercial, employment, corporate, and regulatory modules before sweeping.
2. Resolve the applicable regulations for the org's data profile with `legal_gate_requirements`(data_classes="PHI,PII,FinancialData"). Verify the response lists at least one Regulation with required controls.
3. Drill into each returned regulation with `legal_get_regulation`(regulation) to collect its ReportingRequirement entries. Verify each requirement carries a due date or cadence.
4. Pull live deadlines with `graph_query` across `:ReportingRequirement`, `:RenewalDeadline`, `:LeaveRequest`, and `:EntityComplianceDeadline`, filtered to the requested window. Verify every row names its domain and date.
5. Report one consolidated list grouped by domain. Inspect the working notes with `grep -n "^- " drafts/review-notes.md`. Verify that illustrative ontology individuals are not presented as real deadlines.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| `legal_gate_requirements` returns no regulations | `data_classes` misspelled or not a known classification | Call `legal_lookup_data_class`(data_class) for each label and pass the exact id returned |
| `graph_query` returns no instance rows | No live source connector has populated deadline instances | State that only the ontology shape exists and wire a connector via `source_connector` before re-sweeping |
| Compliance lookup tools are missing | `COMPLIANCETOOL` is disabled or `rdflib` is not installed | Set `COMPLIANCETOOL=True` and install `legal-peripherals-mcp[ontology]` |

## Tools & actions
| Tool | Arguments | Purpose |
|------|--------|---------|
| `legal_list_compliance_domains` | - | Inventory every deadline-bearing module currently federated |
| `legal_gate_requirements` | `data_classes` | Resolve every Regulation + Control a given data-classification profile must satisfy |
| `legal_get_regulation` | `regulation` | Drill into a specific Regulation's ReportingRequirement(s) |

## Recipe
1. Inventory what's tracked:
   ```
   legal_list_compliance_domains()
   ```
2. For the org's actual data-classification profile, resolve every
   applicable Regulation and its reporting requirements in one call:
   ```
   legal_gate_requirements(data_classes="PHI,PII,FinancialData")
   ```
3. Cross-reference against the LIVE instance data each domain skill
   maintains (renewal deadlines from `legal-peripherals-contract-lifecycle`,
   leave deadlines from `legal-peripherals-leave-tracking`, entity deadlines
   from `legal-peripherals-entity-compliance-tracker`) and surface only what
   falls in the requested window — one consolidated list, not five reports.

## KG grounding
This is the whole point: every one of the deadline-bearing types above is a
typed node in the SAME federated graph, so a `graph_query` across
`:ReportingRequirement` ∪ `:RenewalDeadline` ∪ `:LeaveRequest` ∪
`:EntityComplianceDeadline` filtered by date is a single Cypher/SPARQL
sweep — no per-vertical log file to reconcile.

## Gotchas
- This skill's KG-native lookup describes what the ontology DECLARES is
  trackable; a live source connector is still needed to populate real
  instance data per org (see `scion-sdk-source-integration`) — don't
  present the illustrative example individuals in the `.ttl` files as real
  deadlines.
- Don't let the consolidated sweep bury domain-specific nuance — group by
  domain within the single report rather than flattening everything into
  one undifferentiated list.

## Related
- `legal-peripherals-regulatory-gap-tracker`, `legal-peripherals-contract-lifecycle`,
  `legal-peripherals-leave-tracking`, `legal-peripherals-entity-compliance-tracker`
  — the per-domain deep trackers this sweep composes.
