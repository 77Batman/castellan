# STANDING ORDER 002 — PRINCIPAL DELEGATION PROTOCOL, SPRINT 3

**SIGNED AND IN FORCE — 2026-08-10.**

*Issued by the Principal · Effective at Sprint 3 open · Calibration mode, second sprint · Supplements Charter Part IX; amends nothing*

> **Provenance.** Reissued under Standing Order 001 §7 following the Principal's §7 audit of 2026-08-10: **sixteen `[would-have-asked]` entries graded, fourteen clean, one split, one decided differently — explained-clean under §7(a).** Disposition: **amend and reissue**, with graduation proposed at the Quarterly Review on that audit's strength. Sprint 2's text is carried forward except where marked **[AMENDED]** or **[NEW]**.

---

## §1 · Goal — the objective function **[AMENDED — redirected at the measured constraint]**

Sprint 2 closed at **two of four** objectives with **zero terminal verdicts**, and its close named the constraint precisely: **no hypothesis has ever been registered.** The registry has read `0 hypotheses / 0 trials` since firm activation on 2026-07-28. Sprint 3's goal is redirected accordingly, and is stated once and optimized literally:

1. **The registration act.** PREREG-002's **Stage-1 budget registered** as its sealed `trial_budget`, **I-105 discharged**, and **the family sealed.** Under `GATES.md` §4.7.2 a control exists where the harness reads it and nowhere else; this objective is that doctrine applied to the firm's own first family.
2. **First trials logged. The registry leaves `0/0` permanently.**
3. **One terminal verdict, honest either way.** A correct kill counts identically to a pass. Any optimization that pressures a gate rather than resolving a hypothesis is a violation of this order, not a fulfillment of it.

**The Σα forward-test ledger and origin-ratio metrics continue to be maintained and reported.** They are no longer a numbered objective: Sprint 2 met that clause with a ledger of nothing, faithfully reported, and a metric that can be satisfied vacuously does not belong among objectives.

> **The Principal's framing, recorded because it is the standard this sprint is held to:**
> *"The instrument is built and audited; Sprint 3 is the science or it is nothing."*

---

## §2 · Budget **[AMENDED — termination insurance and re-tiering]**

**30 seat invocations, of which at most 12 Opus.** No rollover. **Failed invocations count as spent (D-012)** — no exception is created by any escalation, because an escalation that refunds its own cost makes filing profitable, and a control that pays the filer is not a control.

### §2.1 · Opus tier composition **[NEW]**

The twelve Opus units are **not** twelve units of working capacity. They are:

| | Units | |
|---:|---:|---|
| Freely allocable | **9** | dispatchable work |
| **Termination insurance** | **2** | reserved against infrastructure failure; **not spendable on new work** |
| DA Gate 1 reserve | **1** | one unit sealed per family approaching seal; unspendable otherwise |

**Re-tiering rationale, from Sprint 2's measured burn** [measured]: eleven Opus dispatches, **three terminations**, a **27% failure rate**, and **42% of the tier consumed producing two complete artifacts and one partial.** Nine freely allocable at a 27% observed failure rate yields **~6–7 productive dispatches**; the insurance restores the rest.

**The CIO recommends the ceiling be held at 12 and not raised**, and states the reason plainly: **a ceiling that moves when it binds is not a ceiling.** D-015 established that a binding ceiling is the control functioning. Making the termination cost *explicit* rather than *silent* is the correct repair; raising the tier is not. **This is a recommendation, not a term — the Principal sets the number.**

### §2.2 · Termination-insurance floor — mandatory conventions **[NEW]**

These ran as in-flight rulings in Sprint 2 and are hereby **terms of the order**:

- **Pre-split at scale.** Any dispatch projected past **~800 authored lines** is split into two invocations at dispatch time and **priced as two.** The CIO states the projection in the brief so the judgment is auditable, and instructs the seat to **stop and say so rather than truncate** if the projection is wrong.
- **Analysis before synthesis.** Every Opus dispatch writes its analysis to disk **before** synthesis begins, so a termination costs one section and never a read. Sprint 2's evidence: two terminations without the instruction preserved **0 lines**; the one with it preserved **817**.
- **Headroom check.** Every Principal message opens with `[usage: session X% · weekly-opus Y%]`. A note **older than ~2 hours, or any termination since it arrived**, means headroom is **unknown**, and the conservative posture applies: pre-split, incremental writes, and **no second long Opus dispatch inside the same window after a termination** — queued for the next Principal contact.
- **Insurance is drawn, not assumed.** Spending an insurance unit is logged in the decision record naming the termination it covers. **Exhausting the insurance is budget exhaustion under §4.**

---

## §3 · Delegated by default

Unchanged from Standing Order 001. The CIO exercises every authority the Charter grants without checkpointing the Principal — dispatch and sequencing, intra-budget reallocation, incident response, worktree/merge mechanics, agenda adjustments within the sprint goal — logging each decision in the decision record as it is made, and tagging `[would-have-asked]` on any decision it would previously have brought to the Principal, with one line stating what it decided and why.

**§3.1 · Standing policies are disclosed at adoption, not at their first failure. [NEW]**

*Arising from the audit's split verdict on entry 16.* Where the CIO adopts a **standing operating policy** — as distinct from a per-dispatch judgment — it is recorded in the decision record **when adopted**, not when it produces an incident. The per-dispatch worktree choices were defensible; running the policy undisclosed for two weeks until it produced I-054 and I-072 is the finding, and this clause is its remedy.

---

## §4 · Hard interrupts — enumerated, mechanical, no judgment

The loop halts and queues for the Principal on any of the following. These are triggers, not thresholds; **no seat, including the CIO, decides whether an item "really" qualifies:**

- Any Charter §2 reserved authority: real capital, any override, any validation-threshold change, any new asset class or data source, any Charter amendment, anything that spends money outside the stated budget.
- Any seal, any kill-condition signature or restatement, any KC silence-kill firing.
- Any issue filed HIGH.
- Any finding by Validation, the CRO, or the Devil's Advocate addressed to the Principal.
- Any drawdown-ladder rung, at any level.
- Any action requiring the holdout passphrase.
- Any detected Charter–harness divergence.
- Budget exhaustion in either tier, **including exhaustion of the §2.1 termination insurance.**

Interrupt items block their own thread until ruled; unrelated work continues. **Silence is never approval for an interrupt item.**

**§4.1 · Act versus visibility [NEW — as ruled in flight, 2026-08-06]**

> **§4 buys visibility, not decisions.**

**A finding that requests no act still interrupts.** The trigger fires on the *class* of finding, not on whether the filer wants something. Sprint 2's `RULING-005 §9` requested nothing, explicitly declined to ask for anything, and was correctly queued. **The CIO may not decline to queue an item on the ground that it appears to need no ruling** — that assessment is the Principal's, and making it is the narrowing §8 forbids.

**§4.2 · Estimator-change asymmetry [carried from the §8 addendum, 2026-08-05]**

Estimator corrections **toward** a statistic's stated assumptions belong to Validation and need no Principal act. Any estimator change that **loosens** — relaxes an assumption, widens a tolerance, swaps to a more permissive construction — **is a §2 threshold matter and interrupts, regardless of framing.** Operative test: **does the corrected statistic measure more of what it always claimed to measure, or less?**

---

## §5 · Dead-man clause

If **10 invocations** are spent, or **5 calendar days** elapse, since the last Principal checkpoint — whichever comes first — the loop halts everything and waits. **A halted firm is a correct outcome; an unsupervised one is not.**

**The count runs from the most recent Principal checkpoint and is restated in every CIO report.** *(Sprint 2 note: the CIO misreported this figure from a stale checkpoint across two reports. The error ran conservative and was still an error.)*

---

## §6 · Checkpoint cadence

The Principal reviews: the **Friday Research Review**, the **Monthly Letter**, and the **interrupt queue as it arrives.** The decision record, the `[would-have-asked]` log, and the **findings index (§7.1)** are the review surface between checkpoints. Per-turn Principal review is discontinued.

**The weekly `[PRINCIPAL]` Friday ritual, alongside the Research Review**, now carries two items, each pasted to the record per `TEMPLATES.md` §7.9. **A skipped week is a skipped verification and is logged as such.**

3. **I-095 gap review [NEW — 2026-08-11].** Until the registry/vault read-only-by-default fix lands, the `python3`/`sqlite3` write path is **ungoverned by the permission layer** and the gap is **class (c) — named in the record, reviewed here.** Confirm at each ritual that the registry and vault remain at their expected state and that no unsanctioned write has occurred. **Retires when the code-layer fix lands, which is bound to *before first trials log*, not to the seal.**
4. **Version-floor verification [NEW — 2026-08-11].** No key in `.claude/settings.json` pins a version, so **"floor 2.1.227" is a class-(c) declared commitment, not a control.** Verified manually — `claude doctor` — at each ritual. **Upgrades to class (a) only if cycle 2 finds a real pinning mechanism.**

1. **Pull-and-merge** — summary of new / unchanged / RESTATED / exit code.
2. **Dated-clause review [NEW — 2026-08-10; scope widened 2026-08-11].**

   **Every dated clause the firm holds** — kill conditions, **condition precedents**, observation dates — evaluated against the store and against the repository. **Widened from kill conditions alone after I-140**, where a condition precedent with a 2026-08-11 deadline would have downgraded PREREG-002 to ADMITTED-AS-EXPLORATORY on a premise falsified twelve days earlier. The Principal's doctrine: ***"a condition precedent with a date is a kill condition wearing different clothes, and nothing evaluates it — same gap as I-133's KC finding."***

   Original scope, retained: Every registered kill condition, every clause, evaluated against the store. **Added because no harness path evaluates a kill condition on any date, for any family** (I-135) — so KC-002, signature-required and carrying an absolute observation date, was enforced by nothing. The Principal: ***"'defeatable by not running it' cannot describe a signature-required clause."***

   **This is a class-(b) control under the R-005 labeling mandate and carries its three fields: executor the Principal, cadence weekly Friday, artifact the pasted evaluation.** It reverts to class (a) when Validation's harness kill-condition evaluator lands — read registered KC fields, evaluate every clause on invocation, **exit nonzero on any firing *or* on inability-to-evaluate**, per the exit-code pattern the merge script proved. Specced this sprint; Sonnet implements red-first.

---

## §7 · Calibration audit, findings index, and graduation

At sprint close the Principal audits every `[would-have-asked]` entry. Each one the Principal would have decided differently is a calibration finding, discussed on the record.

**§7.1 · The findings index [NEW — I-094's remedy]**

Sprint 2's harvest could not reach its two most valuable findings — the 932 cross-host agreements, and an authority declining an available option — **because both lived in the decision record and the harvest reads the Issue Log.** The Issue Log indexes **defects**; the firm has been using it to index **learnings**, and those sets are not the same.

**Validation and the CIO design a findings index at Sprint 3's open**, so the §7 audit and the casebook harvest can retrieve what the Issue Log structurally cannot. **Sonnet-scope. Delivered before the first harvest that would need it, not by it.**

**§7.2 · Graduation**

Graduation to standing policy requires **(a)** a clean or explained audit and **(b)** a Charter Part IX amendment ratified at the Quarterly Review.

**Graduation is proposed at the Quarterly Review on the Sprint 2 audit's strength.** The Principal's ruling, recorded because it sets what Sprint 3 is judged on: *the delegation layer is calibrated and is not the constraint — but graduation cannot precede the Quarterly Review by §7's own text, and should not precede the first terminal verdict by §1's own spirit.* **Sprint 3's verdicts, not its process, are the graduation evidence.**

**§7.3 · Sunset and promotion path [NEW — amendment (iv)]**

This order **expires with the sprint** and must be reissued.

**Every durable rule born inside this order is assigned a permanent home at sprint close** — `reference/GATES.md`, `reference/TEMPLATES.md`, or a Charter amendment — **as a standing mechanism, not a hand-rescue.** Sprint 2 rescued three by hand: the estimator asymmetry, the `[PRINCIPAL]`-step convention, and two standing doctrines. **A rule that lives only in an expiring document is a rule the firm loses on schedule**, and the promotion pass is now part of closing the sprint rather than something someone remembers.

---

## §8 · Erosion guard

The interrupt set may be **widened by any seat** and **narrowed only by the Principal in writing.** No adjective ("material," "significant," "routine") may be introduced into §4 by interpretation. **The CIO may not batch, summarize, or soften interrupt items — they arrive as filed.**

This order does not modify the independence of **Seats 2, 6, and 7**, whose reporting line to the Principal is untouched and outside this protocol.

---

*Signed: the Principal, 2026-08-10. The Principal has the last say — this order changes where the say is exercised, not who holds it.*

> **Countersigned amendments, 2026-08-10.** §1's Σα demotion approved — *"it reports; it doesn't count."* §2 held at 12 with the CIO's reasoning adopted over the Principal's looser wording: *"a ceiling that moves when it binds is not a ceiling — D-015, and also the `min(t_NW, t_raw)` doctrine applied to budgets: repairs make costs explicit; they don't enlarge the allowance."* The 9/2/1 composition stands with its arithmetic stated in the order, **so overruling it later requires engaging the arithmetic rather than forgetting it.** §3.1, §4.1, §7.1 and §7.3 countersigned as drafted.
>
> **Audit citation, corrected at filing.** The §7 audit's *decided differently* finding attaches to **entry 14** (concurrent Opus at zero slack). **Entry 3** (the Rider B hold) is **clean as graded.** The mis-citation was the Principal's, caught at filing.
