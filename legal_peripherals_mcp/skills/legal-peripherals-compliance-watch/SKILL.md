---
name: legal-peripherals-compliance-watch
skill_type: skill
description: >-
  A single, cross-domain deadline/requirement watch that folds what would
  otherwise be several siloed single-purpose watcher agents (one each for
  regulatory feeds, contract renewals, data-room diligence, product-launch
  review, and court dockets) into one KG-native sweep over every
  ReportingRequirement, RenewalDeadline, and LeaveRequest deadline the
  compliance + domain ontology suite declares. Use for a portfolio-wide "what needs attention
  this week" sweep spanning regulatory, commercial, employment, and entity
  domains at once. Do NOT use for a single domain's dedicated tracker (e.g.
  legal-peripherals-regulatory-gap-tracker, legal-peripherals-contract-lifecycle,
  legal-peripherals-leave-tracking, legal-peripherals-entity-compliance-tracker)
  when only that one domain matters.
license: MIT
tags: [legal-peripherals, cross-domain, compliance-watch, deadlines, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---

# Legal Peripherals — Cross-Domain Compliance Watch

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
queryable through **one** `legal_compliance_lookup` surface instead of five
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
for `legal_compliance_lookup`.

## Tools & actions
| Tool | Action | Purpose |
|------|--------|---------|
| `legal_compliance_lookup` | `list_domains` | Inventory every deadline-bearing module currently federated |
| `legal_compliance_lookup` | `gate_requirements` | Resolve every Regulation + Control a given data-classification profile must satisfy |
| `legal_compliance_lookup` | `regulation_detail` | Drill into a specific Regulation's ReportingRequirement(s) |

## Recipe
1. Inventory what's tracked:
   ```
   legal_compliance_lookup(action="list_domains")
   ```
2. For the org's actual data-classification profile, resolve every
   applicable Regulation and its reporting requirements in one call:
   ```
   legal_compliance_lookup(action="gate_requirements", data_classes="PHI,PII,FinancialData")
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
  instance data per org (see `agent-utilities-source-integration`) — don't
  present the illustrative example individuals in the `.ttl` files as real
  deadlines.
- Don't let the consolidated sweep bury domain-specific nuance — group by
  domain within the single report rather than flattening everything into
  one undifferentiated list.

## Related
- `legal-peripherals-regulatory-gap-tracker`, `legal-peripherals-contract-lifecycle`,
  `legal-peripherals-leave-tracking`, `legal-peripherals-entity-compliance-tracker`
  — the per-domain deep trackers this sweep composes.
