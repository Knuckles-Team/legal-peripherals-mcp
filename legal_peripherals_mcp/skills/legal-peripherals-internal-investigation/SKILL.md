---
name: legal-peripherals-internal-investigation
skill_type: skill
description: >-
  Run a privileged internal investigation lifecycle — open, add evidence,
  query the log, draft the memo, and produce an audience-specific summary —
  grounded in the employment domain ontology's InternalInvestigation class
  linked to an EmploymentLawMatter. Use when a workplace complaint (discrimination, harassment, retaliation)
  needs a privileged investigation. Do NOT use for a routine hiring/
  termination review (legal-peripherals-hiring-termination-review) or a
  litigation-stage matter (subpoena/legal hold — see domain_litigation.ttl).
license: MIT
tags: [legal-peripherals, employment, investigation, privilege, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---

# Legal Peripherals — Internal Investigation Lifecycle

Spans the full internal-investigation arc — Open → Add evidence → Query →
Memo → Summarize — in one skill, grounded in `domain_employment.ttl`'s
`:InternalInvestigation` (`:investigates` an `:EmploymentLawMatter`,
`:subjectOfInvestigation` links to `:Employee`).

## When to use
- A complaint (discrimination, harassment, retaliation) needs a privileged
  internal investigation, from intake through the final memo.
- Adding evidence/interview notes to an open investigation.
- Querying "what did witness X say" / "where do accounts conflict" against
  an open investigation's log.
- Drafting the privileged memo, or an audience-specific summary (HR,
  leadership, outside counsel) from it.

## When NOT to use
- Routine hiring/termination review with no open complaint →
  `legal-peripherals-hiring-termination-review`.
- The matter has moved to litigation (subpoena, legal hold, deposition) —
  see this package's `domain_litigation.ttl` for that lifecycle instead.

## Prerequisites & environment
Connect via `mcp-client` against `legal-peripherals-mcp`. This skill is
process/drafting guidance grounded in the ontology's shape; no external
tool call is required to run the lifecycle, but `legal_compliance_lookup`
is available if the investigation implicates a specific regulatory
obligation (e.g. an EEOC-adjacent Obligation).

## Lifecycle
1. **Open** — intake the complaint; create an `:InternalInvestigation`
   `:investigates` a new (or existing) `:EmploymentLawMatter` with
   `employmentLawType` set (`discrimination`, `harassment`, `retaliation`);
   `:subjectOfInvestigation` the `:Employee`(s) concerned. Generate the
   sources checklist (documents, interview list).
2. **Add** — process new documents/interview notes/observations against the
   pull criteria; surface significant items and remaining gaps as they come
   in, not as a bulk batch at the end.
3. **Query** — answer targeted questions against the accumulated log: what a
   witness said, where accounts conflict, what the strongest evidence is per
   issue, what's still missing.
4. **Memo** — draft (or update) the privileged investigation memo once
   there's enough to write a first cut; mark PRIVILEGED AND CONFIDENTIAL,
   attorney work product where applicable.
5. **Summary** — produce an audience-specific cut (HR / leadership / outside
   counsel) from the memo — different altitude, same underlying facts, never
   contradicting the memo.

## KG grounding
The investigation and its subject(s)/matter are typed nodes
(`:InternalInvestigation`, `:EmploymentLawMatter`, `:Employee`) — queryable
across every investigation the org has run, not siloed per-matter files.
`legal_ingest_filing_file` (existing tool) can persist the drafted memo/
summary file as a `:MediaAsset` blob linked to the matter.

## Gotchas
- **Privilege is the whole point** — every artifact (log, memo, summary)
  must be clearly marked privileged/work-product; never draft as if it will
  be produced in discovery without that marking.
- Don't let `investigation-query` answers assert more than the log
  supports — flag conflicting accounts as conflicting, not resolved.
- Termination flowing from a substantiated finding routes back to
  `legal-peripherals-hiring-termination-review`'s high-risk-flag review.

## Related
- `legal-peripherals-hiring-termination-review` — termination following a finding.
- `legal-peripherals-worker-classification` — if the complaint concerns misclassification.
- `legal-peripherals-leave-tracking` — if a leave/accommodation issue is entangled.
