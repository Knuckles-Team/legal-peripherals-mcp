---
name: legal-peripherals-worker-classification
skill_type: skill
description: >-
  Classify a worker engagement (employee, contractor, temp, vendor) against FLSA obligations and answer wage/hour questions by jurisdiction. Use to assess misclassification risk or overtime and final-pay questions. Do NOT use for termination analysis (hiring-termination-review) or handbook drafting (employment-policy-drafting).
license: MIT
tags: [legal-peripherals, employment, worker-classification, flsa, wage-hour, mcp]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---

# Legal Peripherals — Worker Classification & Wage/Hour Q&A

Scope: Classify a proposed worker engagement (employee, independent contractor, temp, or vendor) and answer jurisdiction-aware wage/hour questions (overtime, meal/rest breaks, final pay), grounded in the FLSA compliance module and the employment domain ontology's WorkerClassificationAssessment. Use when the user needs to classify a worker engagement or answer a wage/hour question for a specific jurisdiction. Do NOT use for termination-specific analysis (legal-peripherals-hiring-termination-review) or for drafting the handbook policy that documents the control (legal-peripherals-employment-policy-drafting).

Grounded in `domain_employment.ttl`'s `:WorkerClassificationAssessment`
(`:classificationOutcome`, `:classificationTriggersObligation`) cross-linked
straight to `compliance_flsa.ttl`'s `:Regulation`/`:Obligation`/`:Control`
set — an "employee" outcome resolves to the exact FLSA obligations
(minimum wage, overtime, recordkeeping) that now apply, not a free-text
assertion.

## When to use
- Classify a proposed engagement (employee / independent contractor / temp /
  vendor) and flag misclassification risk.
- Jurisdiction-aware wage/hour Q&A: overtime eligibility, meal/rest breaks,
  final-pay timing.

## When NOT to use
- Termination-specific severance/release analysis → `legal-peripherals-hiring-termination-review`.
- Drafting the handbook policy documenting the resulting control →
  `legal-peripherals-employment-policy-drafting`.
- The litigation side of a wage claim → this package's `domain_litigation.ttl`
  models the matter shape but drafting motions is out of scope for this MCP.

## Prerequisites & environment
Connect via `mcp-client` against `legal-peripherals-mcp`; `COMPLIANCETOOL` for
the compliance lookup tools (`legal_list_compliance_domains`, `legal_list_regulations`, `legal_get_regulation`, `legal_lookup_sector`, `legal_lookup_data_class`, `legal_gate_requirements`).

## Steps

1. Describe the engagement and jurisdiction. Inspect the working notes with `grep -n "^- " drafts/review-notes.md`. Verify the proposed status (employee, contractor, temp, vendor) is stated.
2. Pull FLSA obligations with `legal_get_regulation`(regulation="FLSA"). Verify minimum wage, overtime, and recordkeeping obligations are returned.
3. Apply the jurisdiction's test (economic-realities, ABC, or common-law control). Inspect the working notes with `grep -n "^- " drafts/review-notes.md`. Verify the test used is named.
4. If the outcome is employee, walk `obligations[]` as the misclassification checklist. Verify each item is marked met or at risk.
5. Record a `:WorkerClassificationAssessment` with `:classificationOutcome` and `:classificationTriggersObligation`. Verify state-specific statutes are flagged for review, not assumed.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| `legal_get_regulation` returns no regulation | Regulation id mistyped | Pass `FLSA` exactly |
| State test unclear | State statutes not modeled | Flag for jurisdiction-specific review |
| Temp or vendor outcome | Joint-employer risk out of scope | Refer the staffing contract to a separate contractual analysis |

## Tools & actions
| Tool | Arguments | Purpose |
|------|--------|---------|
| `legal_get_regulation` | `regulation` | Pull FLSA's full Obligation/Control/Penalty set |
| `legal_lookup_data_class` | `data_class` | Confirm FLSA applies (PII data class) alongside any state-specific statute |

### Recipe
Pull the FLSA obligation set an "employee" classification triggers:
```
legal_get_regulation(regulation="FLSA")
```
Compare the proposed engagement against the applicable jurisdiction's test
(economic-realities / ABC / common-law-control, per state) and, if the
outcome is "employee", walk through `obligations[]` — minimum wage, overtime,
recordkeeping — as the concrete misclassification-risk checklist. Mirror
`domain_employment.ttl`'s `:MisclassifiedContractorAssessment` example
individual as the target record shape.

## KG grounding
Record the determination as a `:WorkerClassificationAssessment`
(`domain_employment.ttl`) with `:classificationOutcome` and
`:classificationTriggersObligation` pointing at the specific FLSA (or
state-statute) Obligation(s) now in force — queryable across every engagement
the org has classified, not siloed per matter.

## Gotchas
- State tests vary (ABC test states are stricter than the federal
  economic-realities test) — this skill grounds the FEDERAL FLSA obligation
  set; state-specific statutes are not individually modeled and must be
  flagged for jurisdiction-specific review, not assumed.
- A "temp" or "vendor" outcome still needs its own contractual analysis
  (staffing-agency joint-employer risk) — out of scope here.

## Related
- `legal-peripherals-employment-policy-drafting` — document the control in the handbook.
- `legal-peripherals-hiring-termination-review` — the hiring/termination lifecycle.
- `legal-peripherals-internal-investigation` — if the classification dispute becomes a complaint.
