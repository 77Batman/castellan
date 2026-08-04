## TRANSMITTAL — D-002, 2026-08-04

*Principal's cover paragraph, supplied with the canonical text and included at his
instruction. Set off from the order body only because it is dated 2026-08-04 while the
order below is the verbatim original authored 2026-07-31 — the two are not merged, so the
file does not assert that a 2026-08-04 instruction was part of the 2026-07-31 order. Not
one word of either is altered. See I-046 for why this firm now demarcates authorship dates
rather than trusting a label.*

> D-002 · Canonical Standing Order text, Principal-supplied by paste per your specified
> path. This is the verbatim original, authored 2026-07-31, source of the D-015 excerpts.
> It governs on receipt. Write it to `ops/STANDING-ORDER-001.md` replacing the
> reconstruction, verify with `git show HEAD:ops/STANDING-ORDER-001.md` after committing,
> diff your reconstruction against it, and log what the reconstruction lacked — as
> measured fact now, not assumption. Commit `2d9ef4f`'s false label stands recorded,
> unrewritten. I-046's uncertainty clears only when the verified commit exists.

---

# STANDING ORDER 001 — PRINCIPAL DELEGATION PROTOCOL

*Issued by the Principal · Effective at Sprint 2 open · Calibration mode · Supplements Charter Part IX; amends nothing*

## §1 · Goal — the objective function

Sprint 2's goal, stated once and optimized literally:

- PREREG-002 sealed and executing, with its forward-test ledger entry recorded.
- The ML trial-accounting ruling landed (search space declared at Gate 0; every fitted configuration a logged trial; purged/nested CV mandatory; seeds fixed).
- Two hypotheses driven to terminal verdicts — a correct kill counts identically to a pass. The goal is verdicts, not survivals. Any optimization that pressures a gate rather than resolving a hypothesis is a violation of this order, not a fulfillment of it.
- The Σα forward-test ledger and origin-ratio metrics maintained and reported.

## §2 · Budget

30 seat invocations, of which at most 12 Opus. No rollover. Failed invocations count as spent (D-012). The DA's Gate 1 reserve convention continues: one Opus unit sealed per family approaching seal.

## §3 · Delegated by default

The CIO exercises every authority the Charter already grants it without checkpointing the Principal, including: dispatch and sequencing, intra-budget reallocation between seats, incident response, worktree/merge mechanics, and agenda adjustments within the sprint goal. Each such decision is logged in the decision record as it is made. Calibration rule: any decision the CIO would previously have brought to the Principal is additionally tagged `[would-have-asked]`, with one line stating what it decided and why. The tag changes nothing about execution; it exists to be audited at sprint close (§7).

## §4 · Hard interrupts — enumerated, mechanical, no judgment

The loop halts and queues for the Principal on any of the following. These are triggers, not thresholds; no seat, including the CIO, decides whether an item "really" qualifies:

- Any Charter §2 reserved authority: real capital, any override, any validation-threshold change, any new asset class or data source, any Charter amendment, anything that spends money outside the stated budget.
- Any seal, any kill-condition signature or restatement, any KC silence-kill firing.
- Any issue filed HIGH.
- Any finding by Validation, the CRO, or the Devil's Advocate addressed to the Principal.
- Any drawdown-ladder rung, at any level.
- Any action requiring the holdout passphrase.
- Any detected Charter–harness divergence.
- Budget exhaustion in either tier.

Interrupt items block their own thread until ruled; unrelated work continues. Silence is never approval for an interrupt item.

## §5 · Dead-man clause

If 10 invocations are spent, or 5 calendar days elapse, since the last Principal checkpoint — whichever comes first — the loop halts everything and waits. A halted firm is a correct outcome; an unsupervised one is not.

## §6 · Checkpoint cadence

The Principal reviews: the Friday Research Review, the Monthly Letter, and the interrupt queue as it arrives. The decision record and `[would-have-asked]` log are the review surface between checkpoints. Per-turn Principal review is discontinued.

## §7 · Calibration audit and graduation

At sprint close, the Principal audits every `[would-have-asked]` entry. Each one the Principal would have decided differently is a calibration finding, discussed on the record. Graduation of this order to standing policy requires (a) a clean or explained audit, and (b) a Charter Part IX amendment ratified at the Quarterly Review. Until then this order expires with the sprint and must be reissued.

## §8 · Erosion guard

The interrupt set may be widened by any seat and narrowed only by the Principal in writing. No adjective ("material," "significant," "routine") may be introduced into §4 by interpretation. The CIO may not batch, summarize, or soften interrupt items — they arrive as filed. This order does not modify the independence of Seats 2, 6, and 7, whose reporting line to the Principal is untouched and outside this protocol.

*Signed: the Principal. The Principal has the last say — this order changes where the say is exercised, not who holds it.*

---

## ADDENDUM — I-050 ruling, 2026-08-05 · estimator-change asymmetry · §8 WIDENING

*Recorded here rather than only in the decision record because §8 provides that the
interrupt set may be widened by any seat and narrowed only by the Principal in writing.
This is a Principal widening, in writing, and belongs in the order it widens.*

> Estimator corrections toward a statistic's stated assumptions belong to Validation and
> need no Principal act. **Any estimator change that loosens — relaxes an assumption,
> widens a tolerance, swaps to a more permissive construction — is a §2 threshold matter
> and interrupts, regardless of framing.**

**Why it is stated as an asymmetry.** The Principal's own reason: *"so this ruling can't be
cited sideways later."* The I-050 precedent is that a permissive measurement defect is
repaired without ceremony. Left unqualified, that precedent is exactly the shape a future
seat would cite to wave through a loosening as "just an estimator change." The direction of
the change, not its vocabulary, decides which side of §4 it falls on.

**Operative test for any seat proposing an estimator change:** does the corrected statistic
measure more of what it always claimed to measure, or less? Toward the stated assumption →
Validation's, no interrupt. Away from it, by any framing → **§4, and it queues.**

---

## ADDENDUM — D-003, 2026-08-04 · tool-permission policy

*Appended at the Principal's instruction. Verified before acceptance: `.claude/settings.json`
is present on disk and in `HEAD` at commit `9678e5c`, and its contents match this
description — routine operations allowed; `sudo`, `rm -rf`, `crontab`, `launchctl`,
`~/.ssh/**` and `~/.aws/**` denied.*

> D-003: a tool-permission policy is committed at `.claude/settings.json` matching your
> delegated authority — routine operations no longer prompt; denied categories (sudo,
> scheduled tasks, bulk deletion, credential paths) remain Principal-only. Any residual
> prompt means the task is reaching outside scope — queue it, don't work around it.

**CIO note on the last clause.** "Queue it, don't work around it" is read as an extension
of §4 rather than a convenience: a permission prompt is now itself an interrupt signal, and
the CIO may not re-route a denied operation through an allowed tool to achieve the same
effect. This has immediate bite on **Rider A** — Seat 9's VPS migration touches scheduled
tasks (`crontab`/`launchctl`, denied) and would spend money (§4 reserved). Both were
already scoped to `[PRINCIPAL]` steps before this policy existed; the policy now enforces
mechanically what the dispatch enforced by instruction.
