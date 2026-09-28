## Start here — for an external reviewer, 60 seconds

- **What this is.** A research-first systematic trading firm run by a multi-agent (Claude) team against a binding charter (`FUND_CHARTER.md`), with an enforcement harness that gates every backtest and every capital decision through code, not narration.
- **The book.** Paper capital, three blotters kept deliberately separate — order, execution, trade (`book/book.db`) — a point-in-time price store so research can't see vendor-adjusted or look-ahead data (`book/pit.db`), and a trial registry every backtest must route through (`book/registry.db`). **`book/pit.db` is not distributed** — it is 1.6 GB of licensed vendor data and is git-ignored, so `book/` here holds the book, the registry and the sealed holdout specs, and the tests run without it.
- **The gates** (`harness/castellan/gates.py`; Charter §4.2/§4.4): t-stat ≥ 3.0 (`T_STAT_HURDLE`, `gates.py:29`; `FUND_CHARTER.md:394`) · Deflated Sharpe Ratio ≥ 0.95 (`DSR_MIN`, `gates.py:31`; Charter `:353`/`:395`) · Probability of Backtest Overfitting ≤ 0.10 (`PBO_MAX_PAPER`, `gates.py:32`; Charter `:354`) · a locked, single-use holdout · a mechanical drawdown ladder. One FAIL fails the Gate — no partial credit.
- **Run the tests.** `pip install -e harness && python3 -m pytest harness/tests -q` → **393 passed, 22 failed, 415 total**. Use `python3`, not `python` (on many systems, including the one this was developed on, bare `python` does not exist), and don't pipe the command — a pipeline reports its last stage's exit status, so `| tail` would report success regardless of what pytest did (I-362, `logs/ISSUE_LOG.md`). Of the 22 reds: **16** fail at fixture setup with `sqlite3.OperationalError: no such table: write_grants`, before any assertion runs — one upstream fixture defect masking the acceptance suite for the I-034 cost-sign repair (`harness/tests/test_carry_accounting.py`, T4–T18) — and the remaining **6** are genuine, substantive assertion failures elsewhere in the suite. All 22 are Validation-owned, all bear on the Gate 1 floor, none on any sealed act, and unmasking the 16 is bound by event to before this family's first Gate 1 evaluation (I-396, `logs/ISSUE_LOG.md`).
- **Current status.** One family is sealed and in forward test — `funding-carry-conditioning-002` (`prereg_sha256 e5ebd3a6db02b97955518bc70db3906918e702f9879d3ad9928223ad6d2a105f`, checkable against `book/registry.db`, table `events`, `event_id=5`). Forward window opened 2026-09-15; the KC-002 observation date is 2027-03-21. The paper book itself is USD 10,000,000 with zero positions and zero trades. This is **not a performance claim**: the window is days old, Σα is nil and vacuous by construction, the firm holds zero terminal Gate-1 verdicts against a target of two, and the sealed family already carries two open substantive findings against its own falsifier (I-389: one leg of the falsifier spares pure noise ~12% of the time against a sealed assumption of 0.13%; I-376/I-377: at matched gross exposure the position carries residual long-spot delta the benchmark doesn't, so the test can pass on spot beta rather than the claimed conditioning). The only prior family to reach an intake verdict, the forward-lag family (`PREREG-001`), was **ADMITTED-AS-EXPLORATORY with the seal refused on the text as drafted and Gate 1 pre-declared unreachable** — see the verdict in its own terms at `research/VALIDATION-GATE0-001-forward-lag.md` §4.
- **What you are reading.** If you found this as `77Batman/castellan`, it is a **derived public mirror**. The private repository it is generated from is the sole book of record (Amendment A3); this copy is filtered for publication and is not authoritative. The candid half of this project — the issue log, including the firm's own sign-error incident (I-034, `logs/ISSUE_LOG.md`, filed 2026-07-28) — is meant to be read alongside this section, not instead of it.

---

# Castellan Capital

A research-first investment firm run by Claude agents. Ten seats, three independent reporting lines, one product: **a validated edge**.

## Two ways to run it

**1 — Master prompt (portable).** Paste `FUND_CHARTER.md` into a fresh Cowork session or any Claude chat. The model becomes Fable 5 and instantiates the firm by delegating. Self-contained; no files required.

**2 — Agent team (Claude Code).** Drop this folder into a project. `CLAUDE.md` briefs the lead session as Fable 5; `agents/*.md` define the nine subordinate seats with model and tool assignments. Run with Agent Teams enabled:

```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
claude
```

Then: *"Load the Castellan Capital charter and stand up the firm."*

## The firm

| Seat | Model | Reports to |
|---|---|---|
| Fable 5 — CIO & Orchestrator | Fable 5 | Principal |
| Director of Research | Opus | CIO |
| Head of Quantitative Validation | Opus | **Principal** |
| Chief Risk Officer | Opus | **Principal** |
| Devil's Advocate | Opus | **Principal** |
| PM — Pod A · Equity & Event | Sonnet | CIO |
| PM — Pod B · Digital Assets & Event Markets | Sonnet | CIO |
| PM — Pod C · Macro & Cross-Asset | Sonnet | CIO |
| Head of Data & Infrastructure | Sonnet | CIO |
| Execution & Operations | Haiku | CIO |

The three independent lines are the point. Fable 5 cannot overrule a risk halt, cannot overrule a validation failure, cannot suppress a red-team memo. Only the Principal can, in writing, logged.

## Files

```
FUND_CHARTER.md     the binding document (v1.1) — also the standalone master prompt
CLAUDE.md           orchestrator brief for Claude Code (harness-binding included)
agents/             one definition per seat (harness-binding included)
harness/            the enforcement layer — pip install -e harness
reference/
  GATES.md          validation protocol, thresholds, Gate 0/1/2
  RISK.md           limits, drawdown ladder, capital allocation, attribution
  CONSTRAINTS.md    what the firm actually has, and what that forecloses
  TEMPLATES.md      every document format
  CADENCE.md        meeting calendar, agendas, scheduled-task cron
research/           pre-registrations, memos, validation reports
book/               registry.db · vaults/ · pit.db · book.db · daily packs
logs/               issue log, decision record, post-mortems, overrides
```

## Setup (once, in Claude Code)

```bash
cd castellan-capital
git init && git add -A && git commit -m "Charter v1.1 + harness"
pip install -e harness && python -m pytest harness/tests -q   # 30 tests
```

The git repo is the book of record (Amendment A3): `book/registry.db` accumulates trial counts across sessions, `book/vaults/` holds the encrypted holdouts, `book/book.db` is the paper book. Do not run the firm from a fresh copy of this folder — a reset registry silently invalidates every statistic in Part IV. Keep the holdout passphrase outside the repo; you supply it only at Gate 1.

## Principal command set

`STATUS` · `STATUS <seat>` · `BOOK` · `PIPELINE` · `PITCH <idea>` · `CHALLENGE <claim>` · `GATE <strategy>` · `POSTMORTEM <event>` · `HALT` · `OVERRIDE <decision>`

## Before you start

Charter v1.1 folds in Amendments A1–A4: Validation Reports must be harness-generated (A1), trial counting means the registry (A2), the git repo is the book of record with Oracle as pointers only (A3), and prices are consumed only through the PIT store (A4). The amendment log is Appendix D.

### Original note

Read `reference/CONSTRAINTS.md`. The firm's honest edge is research discipline applied where free public data is genuinely adequate — crypto funding and basis, prediction-market microstructure, ETF-level macro and calendar effects, EDGAR-timestamped event work. Cross-sectional fundamental equity factor work **cannot be validated to standard here** and the firm is built to say so rather than produce a meaningless number.

Rename the firm to whatever you like — the name appears only in headers and report titles.
