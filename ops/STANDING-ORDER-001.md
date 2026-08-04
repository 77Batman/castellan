# STANDING ORDER 001 — Sprint 2

**Issued:** 2026-07-31 (D-015 §3) · **In force:** Sprint 2, 2026-08-03 → 2026-08-11
**Authority:** Principal · **Status:** binding

> **Provenance note.** This file was written on **2026-08-04** by the CIO at the opening
> of Sprint 2. The Principal's D-001 message stated the Standing Order was "committed at
> `ops/`"; it was not — no such file existed in the repository or in any commit. Its
> operative text lived only in `logs/DECISION_RECORD.md` D-015 §3–4, which is the source
> reconstructed below. Nothing here is invented; §1–§3 are D-015's text. §4 records the
> riders added by the Principal's D-001 message of 2026-08-03. Under **A3 the repo is the
> book of record**, so the order now exists where the Principal believed it already did.

---

## §1 · Compute ceiling

**30 invocations · 12 of them Opus.**

The ceiling is hard. D-015 records the Principal's reasoning for why it binds, and it is
the correct reading of Sprint 1:

> *"The ceiling binding at the seal is the control functioning; the seal that didn't
> happen this week is a seal that would have frozen two defects permanently."*

A ceiling that stops a seal is the ceiling working. It is not a missed milestone.

## §2 · First Director unit

The **PREREG-002 mechanism restatement, with I-045 in hand.** Funded from Sprint 2's
Opus allocation because the restatement is Opus-tier Director judgment, not Sonnet-scope
handling.

**Principal input on homogeneity remedies — NON-BINDING:**

| | Remedy |
|---|---|
| (a) | per-contract time-varying documented parameters |
| (b) | a declared break control |
| (c) | dropping SOL under the existing universe menu — menu size 5 already declared, so this costs no new `N` |

**Explicitly ruled out: a disclosure-only footnote.** Principal: it *"is out of scope for
the operative state variable, which also rules out Sonnet-scope handling."*

## §3 · Sequence

**M1 → seal → forward clock starts.**

The **two-terminal-verdicts goal carries into Sprint 2 unchanged, honest either way.**

## §4 · Riders (Principal, 2026-08-03)

**Rider A — VPS migration of the Polymarket capture** is promoted to the sprint's **first
Sonnet dispatch.** Spend approved, ~$5/month. Until cutover, gaps are logged as
host-sleep, and **all liveness analysis must distinguish not-polled from no-quote.**

**Rider B — `book/pit.db` has left git tracking** (GitHub size limits). Compressed
snapshots replace it; Seat 9 implements the scheduled version with weekly retention. The
**A3 clarification enters the decision record: git for decisions and code, snapshots for
bulk data.**

**Rider C — one Sonnet line-item at sprint close:** harvest the Issue Log into
`ops/CASEBOOK.md`.

**Per-turn Principal review is discontinued** as of 2026-08-03.

---

**Review date:** sprint close, 2026-08-11.
