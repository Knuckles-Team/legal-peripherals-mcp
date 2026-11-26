---
name: legal-peripherals-employment-policy-drafting
skill_type: skill
description: >-
  Draft an employment handbook policy (with jurisdiction-specific state supplements where law differs) and diff a proposed handbook change against the current version, grounded in the employment domain ontology's HandbookPolicy class (which doubles as the compliance Control it implements). Use when the user says "draft a [topic] policy" or "update the handbook".
license: MIT
tags: [legal-peripherals, employment, handbook, policy-drafting, mcp]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---

# Legal Peripherals — Employment Policy / Handbook Drafting

Scope: Draft an employment handbook policy (with jurisdiction-specific state supplements where law differs) and diff a proposed handbook change against the current version, grounded in the employment domain ontology's HandbookPolicy class (which doubles as the compliance Control it implements). Use when the user says "draft a [topic] policy" or "update the handbook". Do NOT use for a regulatory (non-employment) policy redraft (legal-peripherals-policy-redraft) or for classifying a specific worker (legal-peripherals-worker-classification).

Drafts employment handbook policies grounded in the ontology.
`domain_employment.ttl`'s `:HandbookPolicy` is declared `rdfs:subClassOf
:Policy, :Control` — a handbook policy IS the documented Control satisfying a
compliance Obligation (e.g. `:FLSATimekeepingControl
:documentedInPolicy :TimekeepingHandbookPolicy`), so drafting one is grounded
in a real ontology obligation, not a blank page.

## When to use
- "Draft a [topic] policy", "we need a policy for X".
- Diff a proposed handbook change against the current version and flag
  ripple effects / state-supplement impacts.

## When NOT to use
- A non-employment regulatory policy → `legal-peripherals-policy-redraft`.
- Classifying a specific worker → `legal-peripherals-worker-classification`.

## Prerequisites & environment
Connect via `mcp-client` against `legal-peripherals-mcp`; `COMPLIANCETOOL` for
the compliance lookup tools (`legal_list_compliance_domains`, `legal_list_regulations`, `legal_get_regulation`, `legal_lookup_sector`, `legal_lookup_data_class`, `legal_gate_requirements`).

## Steps

1. Identify the policy topic and the obligation it documents. Inspect the working notes with `grep -n "^- " drafts/review-notes.md`. Verify the topic maps to a regulation such as FLSA for timekeeping.
2. Pull the obligation and control set with `legal_get_regulation`(regulation="FLSA"). Verify the response lists the controls the policy must implement.
3. Confirm sector applicability with `legal_lookup_sector`(sector). Verify the returned regulations match the org's sector.
4. Draft the policy body implementing each control, and list state supplements (meal and rest breaks, paid sick leave, predictive scheduling) as jurisdiction-review items. Inspect the working notes with `grep -n "^- " drafts/review-notes.md`. Verify no state rule is asserted without attorney review.
5. Type the document as a `:HandbookPolicy` linked by `:documentedInPolicy` from its `:Control`. Verify the link exists and any ripple effect on other policies is called out.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| `legal_get_regulation` returns no regulation | Regulation id mistyped | List ids with `legal_list_regulations` and pass the exact local id |
| State supplement requested | State rules are not modeled in the ontology | Flag the item for jurisdiction-specific attorney review |
| Compliance tools missing | `COMPLIANCETOOL` disabled or `rdflib` missing | Enable `COMPLIANCETOOL` and install `legal-peripherals-mcp[ontology]` |

## Tools & actions
| Tool | Arguments | Purpose |
|------|--------|---------|
| `legal_get_regulation` | `regulation` | Pull the Obligation/Control the policy must document (e.g. FLSA timekeeping) |
| `legal_lookup_sector` | `sector` | Confirm which employment-adjacent regulations apply to the org's sector |

### Recipe
Ground a timekeeping/overtime policy draft in FLSA's actual control set:
```
legal_get_regulation(regulation="FLSA")
```
Draft the policy body implementing each relevant `Control`, then note, per
jurisdiction in the org's footprint, any state supplement needed (meal/rest
break rules, paid-sick-leave accrual, predictive-scheduling) — these are
practice-specific and NOT modeled in the ontology; flag them for
jurisdiction-specific review rather than guessing.

## KG grounding
Type the resulting document as a `:HandbookPolicy`
(`domain_employment.ttl`) and link it `:documentedInPolicy` from the
`:Control` it implements — so "which policies satisfy which compliance
controls" is a graph query, not a spreadsheet.

## Gotchas
- State supplements are jurisdiction-specific and not individually modeled —
  this skill grounds the FEDERAL baseline (FLSA); supplement content needs
  attorney review per state.
- A handbook-update diff should explicitly call out ripple effects (does
  this change any OTHER policy's Control coverage?) rather than reviewing
  the single policy in isolation.

## Related
- `legal-peripherals-worker-classification` — the FLSA obligations this policy documents.
- `legal-peripherals-hiring-termination-review` — hiring/termination-specific review.
- `legal-peripherals-regulatory-gap-tracker` — what's still uncontrolled.
