# FINDINGS INDEX — format, what it fixes, what it does not

**Seat:** Execution & Operations · **Dispatch:** S4-D-010 · **Date:** 2026-08-25
**Issue-number range used:** I-280–I-283 (four entries; I-284–I-289 unused)

> **Placement note, CIO, 2026-08-27.** This file is **Execution & Operations' work, returned as text
> because the seat's `Write` tool refused the filename** — the harness blocks subagent writes to paths
> matching `findings/report/summary/analysis`, treating them as self-reports rather than deliverables.
> **The block was correct in general and wrong here**, and the seat did the right thing: it returned
> the content in full and said which tool refused it, rather than renaming the file to slip past the
> rule or dropping the deliverable. **Placed verbatim by the CIO; the content is the seat's.**
> **Filed as `I-118`.**

## 1. What was wrong

`logs/ISSUE_LOG.md`'s highest entry was **I-226** while six source memos, across four consecutive
dispatches, held roughly thirty findings numbered **I-210–I-274**. Each memo had already assigned
IDs, severities and owners to its own findings; **none of that reached the one artifact the firm
actually queries.** `ops/CASEBOOK.md`'s harvest reads the Issue Log, so **every finding above I-226
was unharvestable.**

## 2. The format adopted

Every transcribed finding is its own `## I-NNN · <date> · <title> · Severity: <as filed> · Owner: <as
filed>` block — **the exact header shape every other log entry uses.** Body: a *"Transcribed from
&lt;file&gt; &lt;section&gt;"* paragraph naming the filing seat and dispatch, and a *"Resolution: as filed —
open"* line, with any Ops cross-reference explicitly marked **"Ops notes without adjudicating."**

**Individual headers, not one pointer entry per memo**, so every finding is independently greppable by
ID and severity. **The CIO's prior pointer entries flagged the failure but did not fix the query.**

## 3. What it fixes — tested, not asserted

A script splitting the log on `^## I-\d+` and filtering `Severity: HIGH` in the header returns **54
HIGH entries, 12 of them newly transcribed** (I-210, I-211, I-240, I-241, I-242, I-247, I-251, I-252,
I-260, I-261, I-270, I-273). **Before this dispatch these were prose inside memo files, invisible to
that query.**

## 4. What it does not fix

- **Pre-existing ID collisions** — `I-006`, `I-100`, `I-101`, `I-102`, `I-103` each carried two
  headers. *(Found while testing; not introduced here. **Four resolved by the CIO at `I-116`;
  `I-006`'s remains open and is the CRO's under `TEMPLATES.md` §7.8.**)*
- **"Open" is not machine-verifiable** from severity + header alone: closure appears as a separate
  `CLOSED`/`STATUS` block in most cases but **inline in the header for `I-220`** — **three conventions
  where one is needed.**
- **Ruling-status (I-101, now `I-108`) is not carried.** The format could add a fifth field for
  entries about a ruling rather than a defect, **but that changes what the log is for — a scope
  decision for the Principal, reported here and not built.**

## 5. Counts — allocated versus found

| Range | Allocated | Found | Source |
|---|---:|---:|---|
| I-210–I-219 | 10 | **10** | `research/REDTEAM-002-funding-carry-seal.md` §11 |
| I-230–I-239 | 10 | **10** | `research/DATA-IMPL-008-harness-self-defence.md` §6 |
| I-240–I-249 | 10 | **8** | `research/REDTEAM-002A-withdrawal.md` §6 |
| I-250–I-256 | 7 | **6** | `research/DIR-RESTATE-001` §15.8, `PREREG-002` R-009 |
| I-260–I-269 | 10 | **10** | `research/VALIDATION-RULING-006-r4-scope.md` §9 |
| I-270–I-279 | 10 | **5** | `research/DATA-IMPL-009-grant-remediation.md` |

**49 transcribed · 4 filed by this dispatch · 53 appended, +619 lines.**

**The short ranges are the finding, not the arithmetic.** Ranges were allocated generously and seats
were told not to pad; **a range with five entries has five.** The gap between allocated and found is
**exactly the cardinal error this firm has made eleven times** — and reading it off the allocation
would have made a twelfth.

## 6. Line budget

**Projected ~250. Actual 619, appended in full.** Undershot on entry count (49 vs ~40) and per-entry
density — **each entry needs source pointer, severity, owner and resolution to satisfy the brief's own
"resolves to the finding" requirement**, which the casebook comparator's simpler cases did not need.

**Not trimmed to force the target**: cutting the source-pointer or resolution fields would have
produced entries that fail the stated test. **Flagged after the fact, because the true entry count was
only knowable after reading all six source memos in full.**
