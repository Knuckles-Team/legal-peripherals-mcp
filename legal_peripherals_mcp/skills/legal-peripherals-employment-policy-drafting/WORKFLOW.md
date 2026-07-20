# Legal Peripherals Employment Policy Drafting

Draft an employment handbook policy (with jurisdiction-specific state supplements where law differs) and diff a proposed handbook change against the current version, grounded in the employment domain ontology's HandbookPolicy class (which doubles as the compliance Control it implements). Use when the user says "draft a [topic] policy" or "update the handbook". Do NOT use for a regulatory (non-employment) policy redraft (legal-peripherals-policy-redraft) or for classifying a specific worker (legal-peripherals-worker-classification).

# Legal Peripherals — Employment Policy / Handbook Drafting

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
`legal_compliance_lookup`.

## Tools & actions
| Tool | Action | Purpose |
|------|--------|---------|
| `legal_compliance_lookup` | `regulation_detail` | Pull the Obligation/Control the policy must document (e.g. FLSA timekeeping) |
| `legal_compliance_lookup` | `sector_lookup` | Confirm which employment-adjacent regulations apply to the org's sector |

### Recipe
Ground a timekeeping/overtime policy draft in FLSA's actual control set:
```
legal_compliance_lookup(action="regulation_detail", regulation="FLSA")
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
