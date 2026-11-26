---
name: legal-peripherals-contract-escalation
skill_type: skill
description: >-
  Route a contract review finding to the right approver per the escalation matrix and draft the ask, or translate a contract review into a two-minute stakeholder summary ("can I sign this and what do I need to change"), grounded in the commercial domain ontology's EscalationRoute class. Use after a contract review produced findings that need routing or business-friendly translation.
license: MIT
tags: [legal-peripherals, commercial, escalation, stakeholder-summary, mcp]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---

# Legal Peripherals — Contract Escalation & Stakeholder Summary

Scope: Route a contract review finding to the right approver per the escalation matrix and draft the ask, or translate a contract review into a two-minute stakeholder summary ("can I sign this and what do I need to change"), grounded in the commercial domain ontology's EscalationRoute class. Use after a contract review produced findings that need routing or business-friendly translation. Do NOT use for the review itself (legal-peripherals-contract-review) or lifecycle/renewal tracking (legal-peripherals-contract-lifecycle).

Grounded in
`domain_commercial.ttl`'s `:EscalationRoute` (`:escalatesFinding`,
`:routesToApprover`).

## When to use
- A `legal-peripherals-contract-review` finding needs routing to the right
  approver per the org's escalation matrix, with the ask drafted.
- Translate a contract review into a summary the business stakeholder will
  actually read — not a legal memo, a two-minute "can I sign this and what
  do I need to change" answer.
- Review/approve (or reject) a proposed playbook update.

## When NOT to use
- Running the review itself → `legal-peripherals-contract-review`.
- Amendment/renewal tracking → `legal-peripherals-contract-lifecycle`.

## Prerequisites & environment
Connect via `mcp-client` against `legal-peripherals-mcp`. Process/drafting
guidance grounded in the ontology's `:EscalationRoute` shape; no external
tool call is required.

## Steps

1. List the `:ContractReviewFinding` items rated YELLOW or RED from the review. Verify each finding has a severity and a clause reference before routing.
2. Select the approver for each finding from the org's escalation matrix (severity, contract value, data classification). Verify a named `:Person` exists for every finding.
3. Create an `:EscalationRoute` with `:escalatesFinding` and `:routesToApprover` for each finding. Verify the ask states what is flagged, why it matters, and the decision needed.
4. Compress the review into a stakeholder summary with the bottom line, the one to three points that matter, and the changes. Inspect the working notes with `grep -n "^- " drafts/review-notes.md`. Verify no RED finding is omitted from the summary.
5. For a proposed playbook update, compare it with current practice and apply it only after explicit approval. Inspect the working notes with `grep -n "^- " drafts/review-notes.md`. Verify the approval is recorded and no risk threshold was loosened.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| No approver can be determined | The escalation matrix is missing or does not cover the finding | Ask the requester for the matrix row and do not guess a `:Person` |
| Summary omits a RED finding | Language was compressed past risk disclosure | Rewrite the summary so every RED finding appears in plain words before sending |
| Playbook change was drafted without approval | Approval step skipped | Hold the change unapplied and request explicit approval first |

## Recipes
**Escalation:** for each `:ContractReviewFinding` rated YELLOW/RED, create an
`:EscalationRoute` `:escalatesFinding` it and `:routesToApprover` the
correct `:Person` per the org's matrix (finding severity + contract value +
data classification typically drive the routing rule — practice-specific,
not modeled here). Draft the ask: what's being flagged, why it matters, and
the specific decision needed from the approver.

**Stakeholder summary:** compress the review into: (1) bottom line — sign,
don't sign, or sign-with-changes; (2) the 1-3 things that actually matter to
the business (not every finding); (3) what changes if anything, in plain
language. Never a legal memo dressed down — a genuinely different, shorter
artifact.

**Playbook governance:** when reviewing a proposed playbook update, check it
against current practice, confirm it doesn't silently loosen a risk
threshold, and apply only once explicitly approved.

## KG grounding
`:EscalationRoute` ties the specific `:ContractReviewFinding` to the
`:Person` who owns the decision — so "what's stuck in someone's escalation
queue right now" is a graph query across every contract in review, not a
per-deal email thread.

## Gotchas
- A stakeholder summary that hides a RED finding to avoid friction is a
  failure mode — compress language, never compress risk disclosure.
- Playbook changes should never be auto-applied without the explicit
  approval step — this is a deliberate safety guard.

## Related
- `legal-peripherals-contract-review` — produces the findings this routes.
- `legal-peripherals-contract-lifecycle` — amendment/renewal tracking.
