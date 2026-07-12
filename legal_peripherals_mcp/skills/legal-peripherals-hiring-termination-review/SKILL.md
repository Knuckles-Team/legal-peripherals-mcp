---
name: legal-peripherals-hiring-termination-review
skill_type: skill
description: >-
  Review an offer letter and restrictive covenants at hire, or run a
  termination review (high-risk flag detection, severance/release, final-pay
  timing by jurisdiction) at separation — grounded in the employment domain
  ontology's EmploymentContract/RestrictiveCovenant classes and
  EmploymentLawMatter. Use for offer-letter review
  or termination risk review. Do NOT use for worker classification
  (legal-peripherals-worker-classification) or an open harassment/discrimination
  complaint (legal-peripherals-internal-investigation).
license: MIT
tags: [legal-peripherals, employment, hiring, termination, restrictive-covenant, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---

# Legal Peripherals — Hiring & Termination Review

Reviews hiring and termination around one lifecycle: `domain_employment.ttl`'s
`:EmploymentContract` (offer letters, restrictive covenants) at hire, and
legal.ttl's `:EmploymentLawMatter` (`:employmentLawType` = `wrongful_termination`)
at separation.

## When to use
- Review an offer letter and any restrictive covenants (non-compete /
  non-solicit / confidentiality), jurisdiction check included.
- Termination review: high-risk flag detection, severance + release terms,
  final-pay timing by jurisdiction.

## When NOT to use
- Classifying the worker's employment status → `legal-peripherals-worker-classification`.
- An open harassment/discrimination complaint → `legal-peripherals-internal-investigation`.
- Litigation once a wrongful-termination claim is filed → `domain_litigation.ttl`
  models the matter shape; drafting motions is out of scope here.

## Prerequisites & environment
Connect via `mcp-client` against `legal-peripherals-mcp`; `COMPLIANCETOOL` for
`legal_compliance_lookup` (FLSA final-pay obligations).

## Tools & actions
| Tool | Action | Purpose |
|------|--------|---------|
| `legal_compliance_lookup` | `regulation_detail` | FLSA obligations bearing on final pay / recordkeeping |

### Recipes
**Hiring:** classify each restrictive covenant (`:RestrictiveCovenant`,
subclass of legal.ttl's `:ContractClause`) by jurisdiction enforceability —
several states ban or narrowly limit non-competes; flag rather than assume
enforceable. Note pay-transparency and salary-history-inquiry restrictions if
the jurisdiction has them (practice-specific, not modeled here).

**Termination:** pull FLSA's obligations to confirm final-pay timing risk:
```
legal_compliance_lookup(action="regulation_detail", regulation="FLSA")
```
Flag high-risk terminations (recent complaint, protected-class proximity,
performance-documentation gaps) and check severance/release language against
house risk posture; type the underlying matter as an
`:EmploymentLawMatter` with `employmentLawType = "wrongful_termination"`.

## KG grounding
Offer letters/covenants type as `:EmploymentContract`/`:RestrictiveCovenant`
(`domain_employment.ttl`); a termination review that surfaces risk opens
(or updates) legal.ttl's `:EmploymentLawMatter`, queryable alongside any
`domain_litigation.ttl` artifacts (demand letters, claim charts) the matter
later accumulates.

## Gotchas
- Restrictive-covenant enforceability is state-specific (some states void
  non-competes outright) — this skill doesn't hardcode a state-by-state
  table; flag for jurisdiction-specific review.
- Final-pay TIMING rules (immediate vs. next-payroll) are state-specific on
  top of the federal FLSA baseline — same caveat.

## Related
- `legal-peripherals-worker-classification` — is this even an employee?
- `legal-peripherals-employment-policy-drafting` — the handbook policy side.
- `legal-peripherals-internal-investigation` — open complaint lifecycle.
