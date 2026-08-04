# VALIDATION RULING 004 — ML trial accounting: search space, configuration counting, nested CV, seeds, and the definition of `N`

**Seat:** Head of Quantitative Validation (Seat 3) · **Reports to:** the Principal
**Date:** 2026-08-04 · *first run 2026-08-03, terminated on infrastructure error before any
write; completed 2026-08-04. Both dates are stated rather than one label asserted, per I-046.*
**Status:** BINDING on Seats 1, 2, 6–10. Appealable only to the Principal, in writing.
**Instrument:** binding specification + pre-authored acceptance tests. No Charter constant is
moved by this document and no Charter amendment is requested by it.
**Dispatched by:** the CIO, S2-D-006, discharging Standing Order 001 §1's third objective.
Nothing in the dispatch binds the verdict.
**Type:** specification and verdict only. No code modified, no data fetched, no backtest run,
no hypothesis opened, no trial registered. `book/registry.db` stands at 0 hypotheses / 0 trials.

House rule 6 applies throughout: **[measured]** = read or computed in this repository this
session; **[cited]** = external source named in Charter Appendix C, or an internal document
named inline; **[inferred]** = reasoned from measured facts; **[assumed]** = a premise I could
not verify and am flagging as such.

---

## 0. Provenance — what was read, what was run, what this seat did not do

**Read in full** [measured]: `ops/STANDING-ORDER-001.md`; `reference/GATES.md`;
`reference/CONSTRAINTS.md`; `FUND_CHARTER.md` (Parts I–IX and Appendices B–D);
`research/VALIDATION-RULING-001-holdout-regime.md`; `-002-c-placement.md`;
`-003-carry-accounting.md`; `harness/castellan/registry.py`; `harness/castellan/grid.py`;
`harness/castellan/engine.py`; `harness/castellan/cv.py`; `harness/castellan/gates.py`;
`harness/castellan/stats.py`; `harness/castellan/__init__.py`.

**Read in part** [measured]: `research/PREREG-002-crypto-funding-basis.md` §7, §8, §9, §10
(the sections the dispatch names); `research/VALIDATION-GATE0-001-forward-lag.md` §1.3
(the C-001 E-series); `logs/ISSUE_LOG.md` (index and I-001–I-003, I-011, I-022, I-027,
I-045–I-048); `logs/DECISION_RECORD.md` (S2-D-002 §3–§5, S2-D-005).

**Run** [measured]: `python3 -m pytest harness/tests -q` → **160 passed**, before and after.
Pure-function arithmetic on `castellan.stats` in a throwaway interpreter —
`expected_max_sharpe`, `min_backtest_length_years`, and closed-form algebra derived from
them. **No market data was touched, no `run_backtest` call was made, and no registry write
occurred.** `min_backtest_length_years` is a pure function of `(N, SR, periods_per_year)`
and consumes no sample; computing it is not a backtest, and PREREG-002 §7.3 and §10.4
already establish that precedent [cited].

**Not done, per the dispatch constraints:** no code modified, no data fetched, nothing
sealed, nothing committed, no trial logged, no hypothesis opened. Nothing in `harness/`,
`book/`, or `research/` other than this file and the four Issue Log entries at §11 was
written.

### 0.1 A citation in the dispatch that does not resolve, corrected on the record

The dispatch directs me to `FUND_CHARTER.md` **Part VII §7.2** for "conditioning choices,
menus, `N` accounting, `n_inherited`." Charter §7.2 is the **Research Memo** template
[measured]; it contains none of those. The material described is at
**`research/PREREG-002-crypto-funding-basis.md` §7.1–§7.4 and §10.1–§10.6**, and the
`n_inherited` machinery is at `harness/castellan/registry.py` `_BINDING_FIELDS`,
`open_hypothesis`, and `family_stats` [measured]. I read the intended material and this
ruling is built on it. The mis-citation is recorded because a future reader sent to
Charter §7.2 will find nothing and may conclude the rule does not exist.

### 0.2 Continuity disclosure — this ruling was produced across two runs

The first run of this dispatch terminated on an infrastructure error immediately after
completing its reading and arithmetic and before any file was written. **Nothing of the
first run reached disk** [measured — the CIO verified the absence of this file, an intact
0/0 registry, an unmodified tree, and a green 160-test suite; I re-verified the suite].

**What was lost and re-derived:** nothing. The reading context carried across the
termination intact, including every measured figure in §2 and §3 below.

**Whether the conclusion moved between runs:** it did not. **The only evidence for that
statement is my own account of my own prior reasoning, and there is no artifact against
which to check it, because the first run wrote none. It is therefore marked `[assumed]`,
not `[measured]`, and a reader should treat it with exactly that weight.** The arithmetic
in §2–§3 is independently re-runnable by anyone and is `[measured]`; the claim about the
stability of my reasoning is not.

---
