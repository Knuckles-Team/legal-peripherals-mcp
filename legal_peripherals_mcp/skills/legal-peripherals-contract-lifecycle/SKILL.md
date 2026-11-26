---
name: legal-peripherals-contract-lifecycle
skill_type: skill
description: >-
  Trace a contract's amendment history (full change summary or a provision-level trace) and show contracts with upcoming cancel-by/renewal deadlines before the notice window closes, grounded in the commercial domain ontology's ContractAmendment and RenewalDeadline classes. Use when tracking how a contract has changed over time or which contracts need action before auto-renewal.
license: MIT
tags: [legal-peripherals, commercial, contract-lifecycle, renewal, amendment, mcp]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---

# Legal Peripherals — Contract Amendment History & Renewal Tracking

Scope: Trace a contract's amendment history (full change summary or a provision-level trace) and show contracts with upcoming cancel-by/renewal deadlines before the notice window closes, grounded in the commercial domain ontology's ContractAmendment and RenewalDeadline classes. Use when tracking how a contract has changed over time or which contracts need action before auto-renewal. Do NOT use for the initial playbook review (legal-peripherals-contract-review) or for routing a finding to an approver (legal-peripherals-contract-escalation).

Grounded in `domain_commercial.ttl`'s `:ContractAmendment`
(`:amendsContract`) and `:RenewalDeadline` (`:cancelByDate`,
`:noticeWindowDays`, `:hasRenewalDeadline`).

## When to use
- Trace how a contract has changed across its base agreement and all
  amendments — either a full change summary or a provision-level trace for a
  specific clause.
- Show contracts with cancel-by deadlines coming up, warning before the
  notice window closes.

## When NOT to use
- The initial playbook review of a new contract → `legal-peripherals-contract-review`.
- Escalating a finding, or a stakeholder summary → `legal-peripherals-contract-escalation`.

## Prerequisites & environment
Connect via `mcp-client` against `legal-peripherals-mcp`. Process/tracking
guidance grounded in the ontology's `:ContractAmendment`/`:RenewalDeadline`
shape; no external tool call is required for the trace itself (this composes
with a real contract-repository connector — Ironclad, DocuSign CLM, etc. —
once one is wired via `source_connector`).

## Steps

1. Identify the base `:Contract` and gather every `:ContractAmendment` linked by `:amendsContract`. Verify amendments are ordered chronologically and the total count is stated.
2. For a provision-level trace, filter to amendments touching the target `:ContractClause`. Verify the report says "N amendments total, M touched this clause".
3. Find contracts with a `:hasRenewalDeadline` using `graph_query` over `:RenewalDeadline`. Verify each row carries `:cancelByDate` and `:noticeWindowDays`.
4. Compute the notice-must-be-sent-by date as `:cancelByDate` minus `:noticeWindowDays`. Verify both dates are shown for every flagged contract.
5. Report only contracts whose notice date is approaching or passed. Inspect the working notes with `grep -n "^- " drafts/review-notes.md`. Verify the list is not a full repository dump.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| No renewal deadlines found | No contract-repository connector has populated `:RenewalDeadline` nodes | Report the gap and wire a connector via `source_connector` before re-querying |
| Amendment chain looks incomplete | An amendment lacks an `:amendsContract` link | List the unlinked amendment and ask the owner to link it to the base contract |
| Notice date is off by one | Only the cancel-by date was reported | Recompute and show both `:cancelByDate` and the send-by date |

## Recipes
**Amendment history:** for a full summary, walk every `:ContractAmendment`
`:amendsContract` the base `:Contract` in chronological order, noting what
changed and why. For a provision-level trace, filter to only amendments that
touched a specific `:ContractClause`.

**Renewal tracking:** for every `:Contract` `:hasRenewalDeadline` a
`:RenewalDeadline`, flag any whose `:cancelByDate` minus `:noticeWindowDays`
is approaching (or passed) — surface only the ones needing action, with the
specific deadline and window, not a full contract-repository dump.

## KG grounding
Both the amendment chain and the renewal deadline are typed nodes tied to
the base `:Contract` — so "every renewal due in the next 30 days across the
whole portfolio" or "every amendment that touched the liability-cap clause"
are graph queries, composing with `legal-peripherals-compliance-watch`'s
cross-domain deadline sweep.

## Gotchas
- Notice-window math is easy to get off-by-one on — always state both the
  `cancelByDate` AND the actual notice-must-be-sent-by date explicitly, not
  just the cancel-by date.
- An amendment-history trace should never silently drop an amendment that
  didn't touch the queried clause — say "N amendments total, M touched this
  clause" so the user knows the trace is complete.

## Related
- `legal-peripherals-contract-review` — the initial playbook review.
- `legal-peripherals-contract-escalation` — routing + stakeholder summary.
- `legal-peripherals-compliance-watch` — cross-domain deadline sweep.
