# DECISION RECORD — Castellan Capital

Every firm decision, its dissent, its conditions, its review date, its falsifier.
Append-only. Newest at the bottom.

---

## D-001 · 2026-07-28 · Firm activation (Charter Part IX)

**Decision:** Castellan Capital activated under Charter v1.1 (Amendments A1–A4).
Paper book opened at USD 10,000,000. Trial registry initialized empty.
Nine seats registered as invocable subagents.

**Verdict:** ACTIVATED — cold start, no operating continuity recovered.

**State at activation:**

| Item | State |
|---|---|
| `book/book.db` | cash 10,000,000.00 · 0 positions · reconcile clean · 0 orders / 0 executions / 0 trades |
| `book/registry.db` | 0 hypothesis families · 0 trials · 0 gate verdicts |
| `book/vaults/` | empty — no holdout locked |
| `book/pit.db` | **does not exist** — no price data ingested |
| `harness` | installed editable · 30/30 tests pass |
| `research/` `logs/` | empty prior to this record |

**Named dissent:** none — activation is mechanical, not a judgment call.

**Conditions attached:** no hypothesis may enter Gate 0 until the PIT store exists
and a holdout is locked for the relevant dataset. See I-001.

**Review date:** first Weekly Research Review after the Principal approves an agenda.

---

## D-002 · 2026-07-28 · Seat registration path

**Decision:** `.claude/agents` symlinked to `agents/`, making the nine seat
definitions discoverable by the Agent tool. `agents/` remains the single source
of truth and stays under version control.

**Rationale:** the seat definitions were present in the repo but not on the
discovery path. The roster existed as prose and could not be delegated to.

**Open condition:** Principal to confirm the seats appear under `/agents`. If
symlink resolution fails, fall back to copied files and accept the drift risk.

**CLOSED 2026-07-28.** Principal confirmed nine seats visible. CIO verification
against the Charter roster: 9/9 present, all model assignments match (Opus ×4,
Sonnet ×4, Haiku ×1), filenames match `name:` frontmatter, no unexpected seats,
no missing `tools:` line. Symlink retained; a proposed inversion of the symlink
direction was rejected by the Principal as unnecessary.

---

## D-003 · 2026-07-28 · Principal amendment P-1 — holdout ingest ceiling

**Decision (Principal):** Data & Infrastructure ingests only up to each dataset's
holdout cutoff. Holdout periods are fetched and locked at Gate 1, by Validation,
with the Principal's passphrase supplied at that moment and never stored.

**Effect.** Replaces the Charter's fetch-then-encrypt holdout with an air gap.
~~Strictly stronger: holdout plaintext never enters the ingest path, and because the
fetch happens at Gate 1 date `G` rather than pre-registration date `C`, the window
`[C, G]` contains data that did not exist when the hypothesis was written —
unseeable rather than merely unseen.~~

> **CORRECTION, 2026-07-28, on Validation Ruling 001 §2.1. The original wording
> above is struck rather than deleted; the record is not rewritten.**
>
> **"Strictly stronger" was wrong and was the CIO's characterization, not the
> Principal's.** Validation ruled P-1 a *different* control with a different threat
> model, not a dominating one:
>
> - **Stronger** on leak surface — holdout plaintext never enters the ingest path,
>   and the ingest boundary becomes cheaply auditable via `max(event_time)` vs `C`.
> - **Weaker** on (W1) *evidentiary permanence* — the old ciphertext sealed at `C`
>   **was** the evidence; under P-1 no artifact exists between `C` and `G`, so a
>   vendor restatement or re-resolution in the interim silently changes the Gate-1
>   fetch and the discrepancy is undetectable. Tamper-evident payload → tamper-evident
>   promise. (W2) *availability* — the holdout now depends on a live third party at
>   the exact moment the family is judged. (W3) *split enforcement* — the split moves
>   from code into a query parameter, so over-ingest goes from **impossible** to
>   **silent and plausible**.
> - **Conditional, not general,** on the headline "unseeable" property: it holds only
>   for the sub-window of `[C, G]` postdating pre-registration. If `C` is pinned in
>   the past the holdout is entirely historical and freely fetchable, and the property
>   is simply false for it. Per Ruling 3, thin Polymarket history pushes toward pinning
>   `C` early — so **the firm's first hypothesis will very likely run under a holdout
>   to which P-1's headline protection does not apply at all.**
>
> The CIO's further claim that "under the old regime encryption was the barrier" was
> also rejected. Encryption never protected the information, only the vault's copy of
> it; the underlying series is free and public in both regimes. What P-1 actually
> removes is the property that **the safe path is the default path** — which is why
> Validation moved enforcement into `PITStore` rather than the fetch call.
>
> P-1 is **not** reversed. S1 and W3 are both obtainable; Ruling 001 §2.3 specifies how.

**Consequence requiring action — blocking.** `HoldoutVault.lock(df, passphrase)`
requires the full series in hand and `open_once()` decrypts a stored payload.
Under P-1 there is no payload at lock time. Resolution proposed: the vault seals a
**holdout specification** (dataset, source, query, pinned cutoff `C`) with its hash
in the registry; at Gate 1 the passphrase authorizes the **fetch** rather than a
decrypt, and single-use semantics apply to that fetch. **Validation rules — it is
their vault under Seat 3.** No ingest until they do.

**Open question routed to Validation, not the Principal:** whether `C` is pinned as
an immutable calendar date at pre-registration or recomputed at Gate 1. It must be
the former or the in-sample set silently grows. CIO recommendation: pin it.

**Named dissent:** none recorded. The amendment tightens; the Charter's asymmetry
(brakes unilateral, accelerators collective) means a tightening needs no defence.

**Review date:** first Monthly Letter, 2026-08-01.

---

## D-004 · 2026-07-28 · Sprint 1 approved · compute ceiling set

**Decision (Principal):** Sprint 1 agenda approved with amendment P-1. Compute
ceiling **25 seat invocations, maximum 10 Opus, no rollover.** Opening hypothesis:
the forward-lag family only, on the terms of I-002 — the 71.5% figure is a pointer,
not a prior. No further Principal hypotheses this sprint; the CIO generates the
rest.

**Decision (Principal):** reduced meeting schedule approved in structure, but **no
scheduled tasks created.** Friday Research Review and Monday Risk sessions opened
manually through Sprint 1. Automation revisited at the first Monthly Letter.

**CIO note on the budget.** The four ritual sessions inside this sprint (2× Friday
Research Review chaired by the Director of Research, 2× Monday Risk chaired by the
CRO) are Opus invocations and are counted against the ceiling, not excluded from
it. This puts Opus at exactly 10 with zero headroom. Pre-committed cut if it
overruns: the **second Monday Risk meeting**, on the grounds that an empty book
generates no risk content. Recorded so the cut is a decision, not an omission.

**Falsifier for the agenda itself:** if Data & Infra's first deliverable shows
usable Polymarket history under four years, the forward-lag family cannot reach
Gate 1 at any Sharpe (§4.4 length requirement) and Sprint 1's Pod B allocation is
redirected the same day. See I-004.

**Review date:** 2026-08-11, sprint close.
