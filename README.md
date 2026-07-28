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
