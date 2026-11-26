---
name: legal-peripherals-privacy-gap-monitor
skill_type: skill
description: >-
  Diff a changed privacy regulation (GDPR, CCPA) against current policy to produce a gap list and remediation plan, and sweep PIAs, DPA reviews, and DSAR results for policy drift. Use when a privacy rule changes or the policy needs a drift check. Do NOT use for non-privacy rules (regulatory-gap-tracker).
license: MIT
tags: [legal-peripherals, privacy, gap-analysis, policy-monitor, mcp]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---

# Legal Peripherals — Privacy Gap Analysis & Policy Monitor

Scope: Diff a new or changed privacy regulation against current policy/practice (outputting a gap list and remediation plan with owners/dates), and keep the privacy policy current via a weekly sweep of PIAs/DPA reviews/triage results or a direct query — grounded in the GDPR/CCPA Regulation individuals in the privacy domain module. Use when a privacy regulation changes or the privacy policy needs a drift check. Do NOT use for the general regulatory gap tracker (legal-peripherals-regulatory-gap-tracker, non-privacy frameworks) or a single PIA (legal-peripherals-privacy-impact-assessment).

The privacy-specific counterpart of
`legal-peripherals-regulatory-gap-tracker`, grounded in `domain_privacy.ttl`'s
`:GDPR`/`:CCPA` Obligation/Control set.

## When to use
- A privacy regulation (GDPR, CCPA, or a newly tracked framework) changed —
  diff it against current policy/practice and produce a gap list +
  remediation plan with owners and target dates.
- Weekly sweep of saved PIAs, DPA reviews, and triage results to find policy
  drift; or a direct query ("does our policy cover X") on demand.

## When NOT to use
- Non-privacy regulatory frameworks (HIPAA, FLSA, BSA/AML, ...) →
  `legal-peripherals-regulatory-gap-tracker`.
- A single new processing activity's assessment →
  `legal-peripherals-privacy-impact-assessment`.

## Prerequisites & environment
Connect via `mcp-client` against `legal-peripherals-mcp`; `COMPLIANCETOOL`
for the compliance lookup tools (`legal_list_compliance_domains`, `legal_list_regulations`, `legal_get_regulation`, `legal_lookup_sector`, `legal_lookup_data_class`, `legal_gate_requirements`).

## Steps

1. Choose the mode: gap analysis, weekly monitor, or direct query. Inspect the working notes with `grep -n "^- " drafts/review-notes.md`. Verify the chosen mode is stated so the two are not mixed.
2. For gap analysis, pull the obligations with `legal_get_regulation`(regulation="CCPA"). Verify the controls are listed.
3. Diff each `obligations[].controls[]` against current policy and add missing items with an owner and target date. Verify no date is invented, and ask when none exists.
4. For the weekly monitor, sweep saved PIAs, DPA reviews, and DSAR triage for policy drift, or use `legal_gate_requirements`(data_classes) for cross-regulation scope. Verify only genuine drift is surfaced.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Owner or date missing | Process has no target | Ask the requester for the owner and date before recording the gap |
| Direct query triggers a full sweep | Modes were mixed | Answer only the question asked using `legal_get_regulation` |
| `legal_get_regulation` returns no regulation | Regulation id mistyped | Pass the exact local id such as `GDPR` or `CCPA` |

## Tools & actions
| Tool | Arguments | Purpose |
|------|--------|---------|
| `legal_get_regulation` | `regulation` | Full GDPR/CCPA Obligation/Control set to diff against current policy |
| `legal_gate_requirements` | `data_classes` | Cross-regulation control set when the org's data spans PII + PHI + financial |

## Recipes
**Gap analysis:** pull the authoritative obligation set:
```
legal_get_regulation(regulation="CCPA")
```
For each `obligations[].controls[]` not yet reflected in current
policy/practice, add it to the gap list with a proposed owner and target
date — mirror `legal-peripherals-regulatory-gap-tracker`'s
`:ComplianceGapRemediation` pattern but scoped to `domain_privacy.ttl`.

**Weekly monitor:** sweep saved PIAs (`legal-peripherals-privacy-impact-assessment`
output), DPA reviews (`legal-peripherals-privacy-agreement-review` output),
and DSAR triage results (`legal-peripherals-dsar-response`) for anything
that implies the published privacy policy is now stale (a new data category
processed, a new subprocessor, a new legal basis) — surface only genuine
drift, not every routine review.

## KG grounding
Because GDPR/CCPA are declared `:Regulation` individuals in
`domain_privacy.ttl` (not a bespoke privacy-only model), this monitor
composes with the SAME `gate_requirements` join every other domain skill
uses — a service classified `:PII` resolves to both GDPR and CCPA
obligations in one call.

## Gotchas
- A "direct query" mode should answer precisely what was asked ("does our
  policy cover the right to portability") without re-running the full
  weekly sweep — keep the two modes distinct.
- Gap remediation dates are commitments — don't fabricate a date; ask for
  one if the process doesn't already have a target.

## Related
- `legal-peripherals-regulatory-gap-tracker` — the non-privacy counterpart.
- `legal-peripherals-privacy-impact-assessment` — the per-activity assessment.
- `legal-peripherals-privacy-agreement-review` — DPA-specific review.
