---
name: legal-peripherals-leave-tracking
skill_type: skill
description: >-
  Log a new employee leave and check open leaves for deadline alerts and required decisions, grounded in the employment domain ontology's LeaveRequest class (leave type + decision deadline + requester). Use when an employee goes on leave and the deadline clock needs tracking, or weekly to check what requires action.
license: MIT
tags: [legal-peripherals, employment, leave, fmla, ada, mcp]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---

# Legal Peripherals — Leave Tracking

Scope: Log a new employee leave and check open leaves for deadline alerts and required decisions, grounded in the employment domain ontology's LeaveRequest class (leave type + decision deadline + requester). Use when an employee goes on leave and the deadline clock needs tracking, or weekly to check what requires action. Do NOT use for a workplace-complaint investigation (legal-peripherals-internal-investigation) or wage/hour questions (legal-peripherals-worker-classification).

Grounded in `domain_employment.ttl`'s `:LeaveRequest` (`:leaveType`,
`:leaveDecisionDeadline`, `:requestedBy` an `:Employee`).

## When to use
- Log a new leave (FMLA, ADA accommodation, parental, medical, or a
  state-specific leave type) with the minimum info needed to start tracking
  its deadline clock.
- Weekly (or on demand): check open leaves for deadline alerts and required
  decisions — surfaces only leaves that need action and explains why, not a
  full status board.

## When NOT to use
- The leave request is entangled with a discrimination/retaliation complaint
  → `legal-peripherals-internal-investigation`.
- General wage/hour questions unrelated to leave → `legal-peripherals-worker-classification`.

## Prerequisites & environment
Connect via `mcp-client` against `legal-peripherals-mcp`. This is
process/tracking guidance grounded in the ontology's `:LeaveRequest` shape;
no external tool call is strictly required, though
`legal_ingest_filing_file` can persist a drafted leave-decision letter as a
KG-linked artifact.

## Steps

1. Capture `leaveType` (fmla, ada_accommodation, parental, medical, state_specific) and the requesting `:Employee`. Verify both are present.
2. Compute `leaveDecisionDeadline` from the statute's clock (FMLA designation notice: 5 business days). Verify unfamiliar jurisdictions are flagged rather than guessed.
3. Record the `:LeaveRequest` with `:requestedBy` the employee. Verify the node exists via `graph_query` over `:LeaveRequest`.
4. For the weekly sweep, list open requests whose `leaveDecisionDeadline` is approaching or passed. Verify each row states the specific action required.
5. If a decision letter is drafted, persist it with `legal_ingest_filing_file`(file_path, filing_type). Verify it links to the leave record.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Deadline rule unknown for the jurisdiction | Clock is statute-specific and not hardcoded | Flag for review and record the deadline as unconfirmed |
| Sweep lists every leave | Filter on deadline not applied | Filter on `leaveDecisionDeadline` and rerun the `graph_query` over `:LeaveRequest` |
| Medical detail exposed | Content beyond deadline tracking was copied | Remove the detail and keep only type, dates, and action |

## Recipe
**Log a leave:** capture `leaveType` (`fmla` / `ada_accommodation` /
`parental` / `medical` / `state_specific`), the requesting `:Employee`, and
compute `leaveDecisionDeadline` from the applicable statute's clock (FMLA
designation notice: 5 business days; ADA interactive-process timing varies
by jurisdiction — flag rather than hardcode).

**Weekly sweep:** for each open `:LeaveRequest`, surface only the ones with
an approaching or passed `leaveDecisionDeadline`, and state the specific
action required (designation notice due, return-to-work date approaching,
accommodation follow-up needed) — never a blanket "review all leaves."

## KG grounding
Each leave is a typed `:LeaveRequest` node `:requestedBy` an `:Employee` —
queryable across the whole leave register (`graph_query`) instead of a
spreadsheet, and composable with `:InternalInvestigation` if a leave dispute
escalates to a complaint.

## Gotchas
- Leave-type deadline rules are jurisdiction- and statute-specific (FMLA vs.
  state paid-family-leave vs. ADA interactive process) — this skill doesn't
  hardcode every state's clock; flag unfamiliar jurisdictions for review
  rather than guessing a deadline.
- Never surface protected leave/medical details beyond what's needed for the
  deadline-tracking function — treat leave content as sensitive PII.

## Related
- `legal-peripherals-internal-investigation` — if a leave dispute becomes a complaint.
- `legal-peripherals-hiring-termination-review` — termination-adjacent leave interplay.
- `legal-peripherals-worker-classification` — eligibility often depends on classification/tenure.
