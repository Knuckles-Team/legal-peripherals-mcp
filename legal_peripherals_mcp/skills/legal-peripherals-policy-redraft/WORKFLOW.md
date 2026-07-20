# Legal Peripherals Policy Redraft

Diff a regulatory change against current policy and produce a proposed marked-up redraft closing the gap, grounded in the compliance ontology's Obligation/Control set. Use when a regulation has changed (or a gap was found) and the user needs a first-draft policy fix for internal review. Do NOT use for tracking which gaps are still open (legal-peripherals-regulatory-gap-tracker) or for drafting an employment handbook policy specifically (legal-peripherals-employment-policy-drafting).

# Legal Peripherals — Regulatory Policy Redraft

Given a regulatory change (or a known gap), produce a first-draft policy
redline closing it — grounded in the exact Obligation/Control set the ontology
declares, so the draft's substance is traceable rather than freehand.

## When to use
- A tracked Regulation changed (or `legal-peripherals-regulatory-gap-tracker`
  found an open gap) and the user needs a proposed redraft for internal
  review.
- "Update the policy", "close this gap with a policy change".

## When NOT to use
- Just identifying what's open → `legal-peripherals-regulatory-gap-tracker`.
- An employee-handbook-specific policy → `legal-peripherals-employment-policy-drafting`.
- A privacy policy specifically → `legal-peripherals-privacy-gap-monitor`.

## Prerequisites & environment
Connect via `mcp-client` against `legal-peripherals-mcp`; `COMPLIANCETOOL` for
`legal_compliance_lookup`. This skill is drafting guidance — the agent
composes the redline text; the tool supplies the grounded requirement list.

## Tools & actions
| Tool | Action | Purpose |
|------|--------|---------|
| `legal_compliance_lookup` | `regulation_detail` | Pull the Obligation/Control/Penalty set the redraft must satisfy |
| `legal_compliance_lookup` | `gate_requirements` | Cross-check against every applicable Regulation when the policy spans data classes |

## Recipes
Pull the full obligation set for the regulation that changed:
```
legal_compliance_lookup(action="regulation_detail", regulation="GDPR")
```
For each `obligations[].controls[]` entry not yet reflected in current
policy text, draft a redline clause implementing it — cite the control's
`comment` field as the substantive basis, and note the `penalties` the
Obligation risks if left unaddressed, so reviewers see the "why."

## Recommended output shape
1. **What changed** — the Regulation/Obligation delta.
2. **Marked-up redline** — proposed clause text (insertions/deletions).
3. **Traceability** — each new clause cites the `:Control` id it implements.
4. **Open questions** — anything the ontology doesn't resolve (jurisdiction
   nuance, org-specific process) flagged for attorney review, never guessed.

## Gotchas
- This is a **first draft for internal review**, never a final policy — say
  so explicitly in the output.
- The ontology gives the *substance* (what a control must do); house style
  and specific jurisdictional carve-outs are not modeled here — flag them as
  open questions rather than fabricating detail.

## Related
- `legal-peripherals-regulatory-gap-tracker` — what's open.
- `legal-peripherals-regulatory-feed-watch` — what changed.
- `legal-peripherals-employment-policy-drafting` — handbook-specific drafting.
