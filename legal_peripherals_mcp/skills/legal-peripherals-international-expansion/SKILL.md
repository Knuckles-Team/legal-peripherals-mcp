---
name: legal-peripherals-international-expansion
skill_type: skill
description: >-
  Kick off (or update the status of) international employment-expansion planning for a new country — EOR vs. entity framing, cross-functional tax/finance/HR triggers, and country-specific structural considerations — grounded in the employment domain ontology's InternationalExpansionProject class. Use when planning to hire in a new country.
license: MIT
tags: [legal-peripherals, employment, international-expansion, eor, mcp]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---

# Legal Peripherals — International Expansion Planning

Scope: Kick off (or update the status of) international employment-expansion planning for a new country — EOR vs. entity framing, cross-functional tax/finance/HR triggers, and country-specific structural considerations — grounded in the employment domain ontology's InternationalExpansionProject class. Use when planning to hire in a new country. Do NOT use for a single hire's offer-letter review (legal-peripherals-hiring-termination-review) or entity-formation filings in the US (the package's existing `legal-peripherals-entity-lookup`/`legal-peripherals-ein-filing` skills).

Grounded in
`domain_employment.ttl`'s `:InternationalExpansionProject`
(`:expandsToJurisdiction`, `:expansionStructureType` —
`employer_of_record` vs. `local_entity`).

## When to use
- Kick off planning for a new country: gather intake, frame the EOR-vs-entity
  decision, draft cross-functional (tax/finance/HR) questions, surface
  country-specific structural considerations.
- Update an in-progress expansion project's status: recalculate what's now
  unblocked, flag anything overdue, surface the next priority.

## When NOT to use
- A single hire's offer letter in an already-established jurisdiction →
  `legal-peripherals-hiring-termination-review`.
- US entity formation (LLC/corp filings) → the package's existing
  `legal-peripherals-entity-lookup` / `legal-peripherals-ein-filing` /
  `legal-peripherals-statute-lookup` skills, and `domain_corporate.ttl`.

## Prerequisites & environment
Connect via `mcp-client` against `legal-peripherals-mcp`. Process/planning
guidance grounded in the ontology's project shape; no external tool call is
required to run the framing exercise.

## Steps

1. Create an `:InternationalExpansionProject` with `:expandsToJurisdiction` set to the target `:Jurisdiction`. Verify the jurisdiction node exists.
2. Frame `:expansionStructureType` as `employer_of_record` or `local_entity` with the trade-offs. Verify both options are presented and no choice is made unilaterally.
3. Draft the cross-functional trigger list for tax (Finance), payroll and benefits (HR), and data residency (Privacy). Inspect the working notes with `grep -n "^- " drafts/review-notes.md`. Verify each trigger has an owner.
4. On update, mark resolved triggers and flag overdue ones against target dates. Inspect the working notes with `grep -n "^- " drafts/review-notes.md`. Verify the single next-priority action is stated.
5. List country-specific items (notice periods, statutory severance, works councils) for local-counsel review. Inspect the working notes with `grep -n "^- " drafts/review-notes.md`. Verify none is assumed to match US at-will employment.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Target jurisdiction not in the graph | `:Jurisdiction` node was never created | Create the node, then link the project with `:expandsToJurisdiction` |
| Trigger has no owner | Cross-functional input missing | Ask the owning team lead for a name and target date before logging it |
| Country rules requested | Not modeled per country | Route to local counsel and record the open question |

## Recipe
**Kickoff:** create an `:InternationalExpansionProject`
`:expandsToJurisdiction` the target `:Jurisdiction` (legal.ttl). Frame the
`:expansionStructureType` decision:
- **EOR (`employer_of_record`)** — faster, no local entity needed, higher
  per-head cost, less control over benefits/equity administration.
- **Local entity (`local_entity`)** — slower (weeks-months), needs local
  registration/tax-ID/banking, but full control and typically lower
  long-run cost at scale.

Draft the cross-functional trigger list: tax nexus questions for Finance,
payroll/benefits questions for HR, data-residency questions for Privacy (see
`legal-peripherals-privacy-impact-assessment` if PII flows cross-border).

**Update:** re-check which triggers are now resolved, which are overdue
against their target date, and state the single next-priority action —
using a "what's now unblocked" framing rather than a
static status dump.

## KG grounding
The project is a typed `:InternationalExpansionProject` node
`:expandsToJurisdiction` a `:Jurisdiction` — composable with
`domain_corporate.ttl`'s `:Company`/`:subsidiaryOf` if the entity path is
chosen, and with `domain_privacy.ttl`'s cross-border data-transfer concerns.

## Gotchas
- EOR-vs-entity is a business decision informed by legal risk, not purely a
  legal call — present the trade-off, don't unilaterally pick.
- Country-specific employment law (notice periods, statutory severance,
  works-council requirements) is NOT individually modeled per country in
  this ontology — flag for local-counsel review per jurisdiction rather than
  assuming US-style at-will employment applies.

## Related
- `legal-peripherals-worker-classification` — worker status once hired.
- `legal-peripherals-employment-policy-drafting` — the resulting country supplement.
- `legal-peripherals-privacy-impact-assessment` — cross-border data-transfer review.
