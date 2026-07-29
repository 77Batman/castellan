# VALIDATION RULING 001 — The Holdout Regime under Amendment P-1

**Seat:** Head of Quantitative Validation (Seat 3)
**Date:** 2026-07-28
**Reports to:** the Principal. This ruling was dispatched by the CIO; nothing in the dispatch binds the verdict.
**Status:** BINDING. Not overrulable except by the Principal, in writing.
**Blocks:** I-005, and through it I-001 (all firm ingest) and I-004 (forward-lag Gate 0).
**Type:** specification only. No code was modified, no data fetched, no backtest run.

House rule 6 applies throughout: every claim below is tagged **[measured]** (I read it in this
repository), **[cited]** (external source named in Charter Appendix C), **[inferred]** (reasoned
from measured facts), or **[assumed]** (a premise I could not verify and am flagging as such).

---

## 1. Scope and what was read

Three rulings were requested: (1) the vault design under P-1; (2) whether the holdout cutoff `C`
is pinned at pre-registration or recomputed at Gate 1; (3) the admissibility bar for "usable
history" that Data & Infrastructure must draft against. A binding rider from the Principal
requires itemized acceptance criteria for the implementation.

**Read in full** [measured]: `.claude/agents/quant-validation.md`; `FUND_CHARTER.md` Parts III and
IV, §5 (house rules), Seat 9, §7.3, Appendix B, Appendix C, Appendix D; `reference/GATES.md`;
`harness/README.md`; `harness/castellan/holdout.py`; `harness/castellan/registry.py`;
`harness/castellan/gates.py` (holdout section, lines 195–235); `harness/castellan/loaders.py`
(design rules and the yfinance path); `harness/castellan/data.py` (API surface);
`harness/tests/test_harness.py` (holdout test, lines 171–188); `logs/DECISION_RECORD.md` D-001
through D-004; `logs/ISSUE_LOG.md` I-001 through I-006.

**Suite state** [measured]: 30 test functions — 16 in `test_harness.py`, 14 in `test_data_book.py`.
The rider's "currently 30/30" is correct. Note in passing that `harness/README.md` line 43 says
"(16 tests)"; it is stale and refers to one file only. Cosmetic, but the README is the document a
future session reads first, and a stale count in the enforcement layer's own documentation is the
kind of drift that Appendix B #4 describes. Seat 9 should correct it in the same change.

**Holdout coverage today** [measured]: exactly one test function,
`test_holdout_locks_splits_and_opens_once`, covering six properties — the 75/25 split, wrong
passphrase refused, successful open, holdout strictly after in-sample, second open raising
`HoldoutRetiredError`, and both event kinds landing in the registry. "Equivalent coverage" in the
rider is therefore a low bar in count and a real bar in properties. §5 below sets a materially
higher bar, because the new design has more failure modes than the old one.

---

## 2. RULING 1 — the vault design under P-1

### 2.0 What I am and am not ruling on

P-1 is a Principal amendment (D-003). Whether the firm adopts an air-gapped holdout is settled and
is not mine to reopen. What is mine, under Seat 3, is *how* the vault must work and *what claims
may be made for it*. I am ruling on the design, and I am correcting a characterization in D-003
that is materially wrong and that will otherwise be relied upon.

### 2.1 The correction: P-1 is not "strictly stronger"

D-003 records the effect of P-1 as "**Strictly stronger**." That claim is false in two respects and
conditional in a third. The CIO has communicated it to the Principal. It requires correction on the
record before it hardens into a premise.

**Where P-1 is genuinely stronger:**

| # | Property | Basis |
|---|---|---|
| S1 | Holdout plaintext never enters the ingest path, so the accidental-exposure surface (a seat reading `pit.db` wholesale, a notebook loading the full store, the Ops seat marking the book off a table containing holdout rows) is removed | [inferred] from `holdout.py:72–91` — the current `lock(df, …)` requires the caller to hold the complete series, holdout included, before the split happens |
| S2 | The ingest boundary becomes mechanically auditable: `max(event_time)` per dataset in `pit.db` can be compared against `C` by anyone, cheaply | [inferred] |
| S3 | For the portion of `[C, G]` lying in the future relative to pre-registration wall-clock, the data **does not exist** at research time and cannot be fetched by anyone, deliberately or accidentally | [inferred] — this is the only genuinely technical guarantee in the entire design |

**Where P-1 is genuinely weaker:**

| # | Property | Basis |
|---|---|---|
| W1 | **Loss of evidentiary permanence between C and G.** Under the old regime the ciphertext sealed at lock time *was* the evidence: whatever decrypted at Gate 1 was provably the series set aside at `C`. Under P-1 no artifact exists until Gate 1, so there is nothing to verify the Gate-1 fetch against. If the vendor's history for `[C, G]` changed in the interim — restatement, re-adjustment, contract re-resolution, backfill removal — the Gate-1 fetch silently returns a different series than a fetch at `C` would have, and the discrepancy is undetectable because the counterfactual was never stored. The old regime had a tamper-evident payload; P-1 has a tamper-evident promise | [inferred] from `holdout.py:93–111` vs. the P-1 requirement |
| W2 | **Availability risk at the worst moment.** The holdout now depends on a live third party at Gate 1. Endpoint gone, rate-limited, repaginated, contract delisted — and the holdout cannot be constituted at all. A solved problem becomes an execution risk exactly when the family is being judged | [inferred] |
| W3 | **The split moves from code into a parameter.** This is the one that will actually bite. Under the old regime, over-ingesting was harmless: the caller fetched everything and `lock()` performed the split in code. Under P-1, the split *is* the ingest query's end date — a human- or agent-authored argument. An off-by-one on an inclusive bound, a vendor returning one extra bar, a timezone boundary at UTC midnight, a `end=None` default: any of these silently writes holdout rows into `pit.db` and raises nothing. The failure mode moves from **impossible** to **silent and plausible** | [inferred] |

**Where the strength is conditional, and why it matters immediately:**

S3 — the "unseeable rather than merely unseen" property, which is the headline justification in
D-003 — holds **only for the sub-window of `[C, G]` that postdates the pre-registration timestamp**.
If `C` is pinned in the past (say `C = 2024-06-01` with today at 2026-07-28), then `[C, G]` is
entirely historical, already exists, is freely fetchable by anyone with an internet connection, and
S3 is simply false for it.

This is not hypothetical. Per Ruling 3 below, the forward-lag family's binding constraint is that
Polymarket history is thin (§3.2 [cited]), which pushes toward pinning `C` *early* to preserve
in-sample length — which makes the entire holdout historical. **The firm's first hypothesis is very
likely to run under a holdout to which P-1's headline protection does not apply at all**
[inferred]. Nobody has said this out loud yet. It is said now.

**Verdict on the characterization:** P-1 is stronger on leak surface (S1, S2), conditionally and
often not-at-all stronger on unseeability (S3), and weaker on evidentiary permanence (W1),
availability (W2), and split enforcement (W3). It is a **different** control with a different
threat model, not a dominating one. D-003's "strictly stronger" should be amended to reflect this.
I am not asking for P-1 to be reversed — S1 and W3 can both be had, and §2.3 shows how — but the
Principal should hold an accurate picture of what he bought.

### 2.2 The attack the dispatch demanded: what stops a researcher fetching `[C, G]` themselves?

**Nothing. In either regime.** And the framing offered in the dispatch — "under the old regime
encryption was the barrier" — is itself wrong, which is worth being precise about because a
misunderstood control is more dangerous than a missing one.

Encryption never protected the *information*. It protected *the vault's copy of the information*.
The underlying data is free and public in both regimes (§3.2 [cited]: Yahoo, FRED, ccxt,
Polymarket, all free). A researcher under the old regime who wanted to see the holdout did not need
to break Fernet; they needed to type a date range into `yfinance`. The old vault's actual guarantee
was narrower than it looks: **acquisition-without-a-log was impossible only for the sealed copy,
never for the underlying series**.

So P-1 is not weaker on this specific axis. Both regimes are equally exposed. The dispatch's
premise is rejected.

What P-1 *does* change is which path is the default. Under the old regime the natural way to obtain
data was "call `vault.lock()` and use what it returns" — the safe path was also the path of least
effort. Under P-1 the natural way is "call the loader with a date range," and the loader knows
nothing about `C` unless we teach it. **P-1 removes the property that the safe path is the default
path**, and that is the real regression, W3 above.

The design principle that follows, and which governs the rest of this ruling:

> **The safe path must be the default path. A seat that does the obvious thing must not be able to
> leak the holdout. Enforcement belongs in the store, not in the caller.**

### 2.3 The design I specify

I adopt the CIO's proposal in outline and modify it in four load-bearing places. Numbered so Seat 9
can implement against them directly.

**D1 — The vault has two artifacts and four states, not one artifact and two.**

States: `SEALED` → (`ACQUISITION_FAILED` ⇄) → `ACQUIRED` → `RETIRED`.

Artifacts:
- `spec.json` + its sha256 in the registry, written at pre-registration. **Hash-committed, not
  encrypted.** There is no secret in a specification; encrypting it would be theatre, and a control
  that looks stronger than it is invites over-reliance. The property required is immutability plus
  tamper-evidence, and a hash in the append-only `events` table
  (`registry.py:51–57`, `log_event` [measured]) delivers exactly that.
- `payload.enc` — created at Gate 1 from the fetched series, encrypted under the Principal's
  passphrase with the existing PBKDF2→Fernet construction (`holdout.py:38–42` [measured]), and
  **retained permanently**, with its sha256 logged.

**D1 is a modification, not a restatement.** The CIO's proposal describes the fetch and stops
there. Under P-1 there is a natural temptation to reason "we fetched it, we evaluated it, we are
done" — leaving the Gate-1 evaluation unreproducible and unauditable forever after. Sealing and
retaining the fetch recovers W1 from the acquisition moment onward. It cannot recover the `C`-to-`G`
gap; nothing can. But it bounds the damage, and it means an auditor in six months can verify what
Validation actually evaluated.

**D2 — An ingest ceiling enforced inside `PITStore`. This is the ruling's most important element.**

Without this, P-1's air gap is enforced by whoever typed the `end=` parameter.

- A `ingest_ceiling` table in `pit.db`, keyed by `(source, dataset_id)`, written at seal time from
  the sealed spec's `C`.
- `PITStore.ingest()` **refuses** any batch containing an observation with `event_time > C` for a
  ceilinged dataset: raises `HoldoutCeilingError`, **ingests nothing** (atomic — a partial ingest
  that silently drops post-`C` rows is worse than a failure, because it is indistinguishable from
  success), and logs `holdout_ceiling_violation` to the registry.
- The ceiling is liftable only through the passphrase-authorized acquisition path of D3, and the
  lift is scoped to that single sealed acquisition — never to the dataset generally.
- `event_time == C` is **in-sample** (inclusive lower boundary of the holdout is `C + 1` bar).
  Stated explicitly because an unstated boundary convention is a leak waiting for a timezone.

This restores "the safe path is the default path." Seat 9 may call any loader with any end date and
cannot leak, because the store refuses. It also converts W3 from a silent failure into a loud one.

**D3 — `acquire_once()`: what the passphrase actually does, and the retry corner.**

The CIO writes that "the passphrase's job changes from gating decryption to gating acquisition."
That overstates it and I am sharpening it, because an overstated control gets trusted past its
strength. **A passphrase cannot prevent an HTTP GET.** Any process in this firm can fetch anything
without it. What the passphrase can do is two things, both real:

1. be the mandatory argument to the only code path that will *write a sealed holdout artifact,
   lift the D2 ceiling, and log the acquisition*; and
2. serve as the key sealing the result, so the fetched plaintext cannot be re-read afterwards
   without the Principal.

Its job is **authorization-and-sealing**, not prevention. That is what may be claimed for it and
nothing more.

Semantics:
- `holdout_acquisition_attempted` is logged **before any network call**, carrying the spec hash and
  caller identity. Same principle as the current `open_once`, which logs before returning plaintext
  (`holdout.py:159–164` [measured]) — the irreversible act is marked before it can be walked back.
- Success → seal `payload.enc`, log `holdout_acquired` with the payload sha256, state `RETIRED`.
- Second successful acquisition → `HoldoutRetiredError`, log `holdout_second_acquisition_attempt`,
  return nothing. Unchanged from today.
- **The retry corner, ruled explicitly.** A fetch can fail for reasons that have nothing to do with
  the researcher: a 503, a rate limit, an empty page. Two obvious policies are both wrong.
  *"Retire on first attempt regardless of outcome"* is too brittle — one transient network error
  permanently kills a hypothesis family, which will produce enormous pressure to quietly re-seal a
  new vault, and that pressure is how holdout discipline actually dies. *"Retire only on success"*
  is the loophole — fetch, inspect, kill the process before the seal is written, retry, repeat;
  an unlimited-draws channel with no entry in `N`.
  **Ruling:** the attempt is always logged; success seals and retires; failure moves the vault to
  `ACQUISITION_FAILED` and a further attempt raises unless a `holdout_retry_authorized` event
  exists, which requires the Principal's passphrase *and* a written Issue Log entry naming the
  cause. Every retry authorization is counted and **surfaced in the Validation Report**, because a
  family that needed four retries is a family whose holdout deserves scrutiny.

**D4 — Spec binding at acquisition, and a defect I found in `gates.py`.**

At acquisition the vault recomputes `sha256(spec.json)` and compares it against the
`holdout_spec_sealed` event. Mismatch → refuse before any network call, log
`holdout_spec_tampered`. This hash comparison is what replaces encryption as the integrity
guarantee, and it is the entire reason the spec-sealing design works at all.

Separately — **a live defect in the current harness that must be fixed in the same change**
[measured]: `gates.py:209–210` queries `registry.events(kind="holdout_opened")` and
`kind="holdout_second_open_attempt")` **globally, with no family or vault filter**. In a
single-family firm this is invisible. The moment a second family exists, family A's holdout opening
satisfies family B's Gate-1 criterion, and family A's second-open violation fails family B. Both
directions are wrong and the first direction is the dangerous one — it makes a Gate criterion pass
on evidence from an unrelated strategy. The firm has zero families today (D-001 [measured]), so
this has never fired. It would have fired on the second one.

### 2.4 The residual weakness, named plainly

**A seat that calls `yfinance`, `ccxt`, or the Polymarket API directly from a scratch script,
outside `castellan.loaders`, defeats every control in this design and leaves no trace.**

This is not closable in code under this firm's constraints. We cannot sandbox network egress per
seat. I am not going to pretend otherwise, and I am not going to bury it in a subsection nobody
reads.

Three things bound it, and I state their limits honestly:

1. **A4 [cited — Charter §4.6] means the leak cannot legally produce a reportable number.** Any
   figure not derived through `pit_adjusted_close` / `pit_price_panel` is inadmissible. This
   protects the *record*. It does nothing about the part that actually matters — a researcher who
   has seen the holdout cannot unsee it, and every subsequent design choice they make is
   contaminated in a way no audit can detect. Appendix B #3 [cited] calls this irreversible and it
   is right.
2. **A detection control I am specifying (D1 in §5, test group D):** at Gate 1 the vault compares
   the sealed acquired series against `pit.db` for any row in `(C, G]` whose `knowledge_time`
   predates the acquisition event. Any such row is a leak, detected mechanically, and **fails the
   Gate**. This catches the accidental case — which is the common case, and which W3 makes more
   likely under P-1 than it was before. It does not catch a deliberate one that never touched
   `pit.db`.
3. **S3, where it applies.** Data that does not yet exist cannot be fetched by anyone. This is the
   only unconditional protection in the design, and per §2.1 it applies only to the forward portion
   of `[C, G]`.

**Therefore, stated for the record and for the Principal:** against a determined or careless seat
operating outside the loaders, the holdout's integrity rests on that seat's compliance — and it
always did, under both regimes. The vault is a control against accident and a generator of audit
trail. It is not a control against intent. Any document that describes it as one is wrong.

**Operational consequence I am attaching to that:** because S3 is the only real protection, the
firm should **prefer holdouts whose window lies forward of the pre-registration wall-clock**, and
where a family's data is too thin to permit that, the Validation Report must state on its face that
the holdout is historical and procedurally protected only. That statement is now a required field.

---

## 3. RULING 2 — is `C` pinned at pre-registration, or recomputed at Gate 1?

### 3.1 Required independence statement

The Principal asked that his position be entered and was explicit that the decision is mine. His
position: *"C is pinned at pre-registration as an immutable date, and the sealed spec pins exact
source and query."*

**I reach the same conclusion on the first half. I did not reach it from his reasoning, because he
supplied a conclusion and no reasoning.** The three arguments in §3.2 are mine. Argument (1) is
harness-specific and rests on code I read in this session; argument (3) is specific to P-1's
interaction with the holdout window; neither appears anywhere in D-003, in the dispatch, or in the
Principal's stated position. D-003's justification is a single subordinate clause — "or the
in-sample set silently grows" — which is argument (2) in compressed form and is the weakest of the
three.

**I disagree with the second half of his position as stated**, and rule differently on it in §3.4.
"Pin exact source and query" is necessary but, taken literally, is both insufficient and
operationally fragile.

**On the appearance of agreement.** Appendix B #1 [cited] names the yes-machine as failure mode #1,
and I-003 [measured] records that the base rate has no denominator yet. This is the first
ruling-level input the Principal has offered and I have agreed with him on it. That is 1 for 1 and
it is statistically uninformative; I note it so the count exists from the start rather than being
reconstructed later. The evidence that the agreement is not deference is in §3.3: **the ruling
tightens the constraint on the Principal's own flagship hypothesis**, and in §3.4, where I decline
the second half of his position.

### 3.2 Ruling: `C` is pinned at pre-registration as an immutable calendar date

Three arguments, each independently sufficient.

**(1) Recomputing `C` breaks the statistical assumption behind two Gate-1 criteria.** [measured +
inferred] `registry.returns_matrix` (`registry.py:202–217`) assembles the `(T, N)` trial matrix by
truncating every logged series "to the shortest common length from the end." That matrix is what
CSCV/PBO runs on and what supplies the cross-sectional Sharpe dispersion that DSR consumes
(`README.md` line 17 [measured]). Both PBO and DSR assume the `N` trials are draws over a **common
sample**. If `C` is recomputed at Gate 1, trials run before the recompute were computed on
`[start, C_P]` and trials after on `[start, C_G]` with `C_G > C_P`. The matrix would then be
assembled from series computed on different underlying data, and the truncation would hide it
rather than surface it. Two of the five headline Gate-1 numbers would be silently invalid. This
argument alone settles the question.

**(2) It creates a researcher-controlled tuning knob on the sample, invisible to `N`.** [inferred]
If `C` moves with `G`, then delaying Gate 1 enlarges in-sample — and enlarges it with the most
recent, most regime-relevant data, which is exactly the data most likely to rescue a marginal
strategy. A sponsor whose result is borderline acquires a mechanical incentive to wait. That is
data-snooping with the calendar as the search parameter, and the registry has no field for it:
no trial is logged, `N` does not increment, and §4.1's governing fact is computed against a
denominator that omits the search. Appendix B #2 [cited] is "trial counts are lost"; this is the
variant where the *sample* is what is being searched over and the loss is structural rather than
sloppy.

**(3) It destroys the one genuine strength of P-1.** [inferred] S3 depends on the holdout being
anchored at a date fixed *before* research began. If `C` floats to `G`, then `[C_G, G]` is
zero-length or near it — and worse, the resulting "holdout" is the most recent data, which under a
recompute rule was in-sample for every trial run up to the instant of the recompute. That is not a
holdout. It is a rounding error with a ceremony attached.

### 3.3 The cost of pinning, stated rather than hidden

Pinning is not free, and the direction of the cost is worth being explicit about.

**Pinning `C` freezes the in-sample set at whatever length existed at pre-registration.** Only the
holdout grows with wall-clock. For a data-poor family — which, per I-004 [measured], is precisely
the forward-lag family the Principal opened — this binds hard: the family **cannot buy in-sample
length by waiting**, and §4.4's `≥ 4 years AND ≥ MinBTL(N)` requirement is evaluated against a
sample frozen today. Pinning therefore makes the firm's flagship hypothesis *harder* to pass, not
easier. I-004's note that "a family short on holdout today can become admissible by waiting" remains
correct and is the only legitimate use of elapsed time here — but it buys holdout only, never
in-sample.

**Closing the obvious loophole.** If `C` is immutable within a family, the escape route is to
abandon the family and re-pre-register a successor with a later `C`. I rule that route closed:
**a re-pinned `C` creates a successor family whose `N` is initialized to the predecessor's total
trial count, not to zero.** The researcher has seen the predecessor's results; those trials happened
and remain in the denominator. Seat 9 must implement `open_hypothesis` support for a
`predecessor_family` field, and `family_stats` must sum `N` transitively across the chain. Neither
the Principal nor the CIO raised this; without it, pinning is advisory.

### 3.4 The second half — must the sealed spec pin exact source and query?

**Ruling: pin the semantic identity, not the transport. The Principal's position, taken literally,
is fragile in a way that will break the firm.**

Consider what the dispatch asked me to consider, and what each case actually does:

| Event between `C` and `G` | Effect on a spec that pins the literal query |
|---|---|
| Vendor changes endpoint (`/events` → `/v2/events`) | Spec is unexecutable at `G`. If mismatch ⇒ refuse, a routine vendor version bump **bricks every open holdout in the firm** |
| Symbol renamed | Query returns nothing — or worse, returns a *different instrument* now occupying that symbol. Silent wrong-data, no error raised |
| Contract re-resolved after dispute | The query is byte-identical and **the answer changed**. Pinning the query provides no protection whatsoever; this is not a query problem |

The third row is the important one: **pinning the query does not address re-resolution at all**,
and re-resolution is the single most likely `[C, G]` mutation on a prediction-market venue
[inferred]. The Principal's formulation would give the firm a false sense that the problem is
handled.

**What the sealed spec must pin (binding — a change to any of these RETIRES the vault):**

- `dataset_id` — a firm-internal stable identifier, not a URL.
- `instrument_identity` — for Polymarket, the **immutable on-chain condition/market id**, never the
  slug or the question text, both of which are mutable [assumed — Seat 9 to confirm that a stable
  immutable identifier is exposed by the public API; if it is not, say so in writing, because that
  changes this ruling].
- `query_semantics` — fields requested, date bounds, filter predicates, expressed declaratively.
- `cutoff C` and the holdout end rule.
- `schema_fingerprint` — expected columns and dtypes.
- `resolution_source` and the resolution-versioning rule below.

**What is recorded as provenance only (informational — a change does NOT retire the vault):**

- the literal transport: URL, endpoint path, API version, pagination scheme, client library version.

**The enforcement asymmetry is the whole ruling.** A transport change is an Issue Log incident plus
a Validation-reviewed spec amendment, logged as `holdout_spec_amended` with before/after and a
written justification, and the vault survives. A change to any binding field retires the vault.
Pinning everything at equal strength forces a choice between a firm bricked by a URL change and a
firm that learns to wave spec amendments through — and once amendments are routine, Appendix B #4
[cited], "thresholds drift by a little, repeatedly, each time for a defensible-sounding reason,"
has its foothold. Validation reviews every amendment, and the amendment count per family is
reported at Gate 1.

**On re-resolution specifically.** Primary ruling: re-resolution is a **restatement**, handled by
the PIT machinery, not by exclusion. The resolution carries its own `knowledge_time`; a
re-resolution after `C` creates a new version with a later `knowledge_time`; the store preserves the
old row and auto-logs a `data_restatement` incident (`README.md` line 53, `data.py` [measured]).
The strategy is then evaluated on **the resolution knowable at its decision time plus a stated
settlement lag, in both samples symmetrically**. This is the A4-consistent answer and it requires no
new judgment.

Fallback, only if Seat 9 establishes in writing that Polymarket resolutions cannot be versioned in
`PITStore`: re-resolved contracts are excluded, the exclusion rule is **pre-registered in the spec**
(not chosen after seeing the data — an exclusion applied post-hoc is a filter, not a control),
applied symmetrically in-sample and in-holdout, and the excluded count reported. **If excluded
contract-days exceed 5% of holdout contract-days, the holdout is INSUFFICIENT-DATA.** Seat 9 must
state which of the two regimes applies before measurement begins.

---

## 4. RULING 3 — the admissibility bar for "usable history"

### 4.1 The framing I require, and I adopt the Principal's rider

I adopt the Principal's rider — Data & Infra defines usable history **in writing, before
measuring** — and I adopt it for a stated reason rather than because he asked: **a data-quality
standard chosen after seeing which threshold yields four years of history is not a standard, it is
a fit.** The sequencing is the entire control. It is the same logic as pre-registering a falsifier
(house rule 2 [cited]) applied one level down, to the measurement instrument.

The question is not *"how old is Polymarket."* It is: **how many effectively-independent tradable
observations exist for this strategy's unit of trade, and over what calendar span do they lie?**
Those are two different quantities, they bind two different Gate-1 criteria, and conflating them is
how a thin venue gets talked into looking adequate.

**Which quantity binds which criterion** [inferred, from §4.4 and `gates.py:195–205` measured]:

| Criterion | Binding quantity | Why |
|---|---|---|
| §4.4 "≥ 4 years **and** ≥ 1 full regime cycle" | **Calendar span** | This clause is about regime coverage, not sample size. Four years of dense data spanning one regime still fails |
| §4.4 "≥ MinBTL(N)", DSR, PBO | **Effective observation count** | These are sampling-error statements. `min_backtest_length_years` converts observations to years at the rebalance frequency |
| §4.4 "holdout ≥ 12 months" | **Calendar span of `[C, G]`**, with a tradable-day density floor | A 12-month window containing 30 tradable days is not a 12-month holdout |

**Answering the dispatch's last sub-question directly: neither calendar span nor effective
observation count alone is "the" binding quantity. They bind different criteria and both must be
satisfied independently.** A report that gives one without the other is incomplete and I will
return it.

**Unit of "4 years": calendar days.** Contract-days are the unit of `N`, never of span. Stated
explicitly because "50,000 contract-days" sounds ample and can span eight months.

**A continuity requirement I am adding**, because §4.4 was written without a gappy venue in mind
and its "4 years" clause is otherwise gameable: tradable days must cover **≥ 60% of calendar days**
in the span, and **no single gap may exceed 90 consecutive calendar days**. Otherwise "4 years" is
satisfiable by two dense clusters four years apart, which tests nothing about regime. This is a new
requirement and I am flagging it as such: it is a Validation-set standard under Seat 3's ownership
of admissibility, not a Charter amendment, and it applies to prediction-market families.

### 4.2 The criteria bar Data & Infra must draft against

A **contract-day counts as TRADABLE** only if all seven hold. Where I set a threshold, it binds.
Where I set a *rule for deriving* a threshold, Seat 9 derives it and justifies it — this is
deliberate: several of these depend on the strategy's intended size and claimed edge, and an
absolute number chosen independently of those is a number chosen for convenience.

**Overriding constraint on all seven:** every screen is evaluated on information available at the
decision time (`knowledge_time ≤ decision_time`, §4.6 [cited]). **Screening a day on its own
realized full-day volume is look-ahead** and would contaminate the measurement itself. Screen on
the trailing window. This is the most common way a liquidity filter silently becomes a lookahead
filter and I want it addressed explicitly in the draft.

| # | Criterion | Bar |
|---|---|---|
| T1 | **Volume floor** | Trailing-window (Seat 9 proposes the window; 5 or 20 sessions is the defensible range) median notional traded ≥ `F`. **`F` is not a free parameter:** `F ≥ 20 ×` the strategy's intended per-contract position notional, so that `ADV_PARTICIPATION_MAX = 0.05` (§4.2 [cited]) is satisfiable at the intended size. Seat 9 states the intended notional first; `F` follows |
| T2 | **Two-sided market** | Both bid and ask present, with a finite quoted spread, for ≥ a stated fraction of the observation window. A one-sided book is not tradable at any size |
| T3 | **Spread ceiling** | Quoted half-spread ≤ 50% of the strategy's claimed per-trade gross edge. Above that the trade is not takeable. Jointly determined with the pre-registration, since it depends on the claimed edge |
| T4 | **Depth at intended size** | Resting size within the T3 band ≥ intended position notional, **on both sides**. Measured at touch-plus-ceiling, not total book depth — size resting forty ticks away is not depth. This answers the dispatch's depth-vs-position-size question: depth is defined *relative to the size the strategy needs*, never in the abstract |
| T5 | **Outside resolution blackout** | Contract-days inside the settlement window, where price is mechanically pinned by a known outcome, do not count as signal observations. Seat 9 defines the blackout rule; I require one to exist |
| T6 | **Price not at the bounds** | Days at ≤ 2¢ or ≥ 98¢ excluded by default — the tick grid dominates and the return distribution is degenerate. If the strategy is *specifically* a tail-price strategy, the inversion must be pre-registered with a stated reason |
| T7 | **Resolution rule known and stable at entry** | Resolution criteria, resolution source, and dispute mechanism published and unchanged as of the decision time. A contract whose rules were clarified mid-life is not a clean observation |

**The measurability problem Seat 9 must confront rather than route around.** T2 and T4 require
**historical order-book data**. §3.2 [cited] lists Polymarket order book as available — but a *live*
order-book endpoint is not the same thing as *retrievable historical book snapshots*
[inferred]. If historical depth is not retrievable, T2 and T4 are unmeasurable retrospectively.
Seat 9 must **say so in writing** rather than silently substituting a volume proxy. If a proxy is
necessary: name it, state its bias direction (a volume proxy will **overstate** tradability, since
volume can be high while the book is thin and fast), and report the resulting history count as an
**upper bound**. An unlabelled proxy is a house-rule-6 defect and I will return the measurement as
INSUFFICIENT-DATA.

### 4.3 Poolability across heterogeneous resolution rules

Contracts may be pooled into one hypothesis family only where they share all four of:
(i) resolution source class; (ii) settlement mechanics (binary cash-settled / scalar /
multi-outcome); (iii) dispute and escalation exposure; (iv) the economic mechanism the hypothesis
asserts.

Seat 9 delivers a **stratification table** — contracts grouped on those four axes, tradable
contract-days per stratum — **before** any pooling.

**The rule attached:** if a single stratum contributes **> 50% of tradable contract-days**, the
family's evidence *is* that stratum's, and either the hypothesis is restated as being about that
stratum, or the pooled result is reported with the concentration flagged **and** §4.4's
subperiod-positivity criterion (≥ 60% of blocks net-positive) is additionally evaluated **per
stratum**. Pooling heterogeneous resolution regimes and reporting one Sharpe is the
prediction-market equivalent of reporting a factor return on a survivorship-contaminated universe:
the number is an average over things that do not share a data-generating process.

**Poolability feeds effective-`N`.** Contracts on the same underlying event — multiple strikes on
one election, correlated legs of one outcome — are near-perfectly correlated and are **not**
independent observations. Seat 9 must report the contract → underlying-event mapping.

**Effective-`N` estimator, specified so it is not guessed.** Per period, effective breadth
`N_eff = n / (1 + (n − 1)·ρ̄)`, with `ρ̄` the average pairwise correlation of contemporaneous
contract returns within the strategy's universe [cited — the standard breadth adjustment; the form
is Grinold–Kahn's transfer/breadth correction]. Effective observations = `Σ N_eff` over periods,
converted to years at the strategy's true rebalance frequency for the `MinBTL(N)` comparison.
**Report the raw contract-day count and the effective count side by side.** I expect the ratio to be
large on a venue where correlated contracts cluster around a handful of events, and the raw count to
be misleading by a wide margin [inferred, not measured — this is the hypothesis Seat 9's
measurement will settle].

### 4.4 Deliverable, and the verdict rule I pre-commit to now

**Deliverable:** `research/DATA-SPEC-polymarket-usable-history.md`, drafted and delivered to
Validation **before any measurement**, containing: T1–T7 with proposed thresholds and a written
justification for each; the derivations for `F` (T1) and the T3 ceiling; the stratification schema;
the effective-`N` estimator with the `ρ̄` method; an explicit statement of which criteria are
unmeasurable from available history, with the standing proxy and its bias direction; the
contract → event mapping method; and the pre-committed measurement procedure. Validation accepts or
returns it. **Only then does measurement run**, reported against the accepted spec **unchanged**.

I am not writing this draft and I am not performing the measurement. Both are Seat 9's, per
Charter Seat 9 "decides alone: how to implement a stated requirement" [cited]. The standard is
mine, per "cannot decide alone: what counts as point-in-time correct; relaxing a data-quality
standard" [cited].

**Verdict rule, pre-committed before the measurement exists** — this is the point of stating it now:

> If measured tradable history under the accepted spec is **< 4 years of calendar span**, or fails
> the §4.1 continuity rule, the forward-lag family is **REJECTED for Gate 1** and may be
> **ADMITTED-AS-EXPLORATORY** only. No Sharpe changes this. The failure is evidentiary length, not
> absence of edge, and it is not appealable to Validation — only to the Principal, in writing, as a
> §4.4 amendment made *in advance* of the evaluation.

**A tradeoff neither the CIO nor the Principal has surfaced, which the measurement must let us
compute.** §4.4 requires holdout ≥ 12 months. Under a pinned `C`, the holdout is `[C, G]` and grows
with wall-clock. Two options exist and they trade off directly:

| | Pin `C` early enough that `[C, G]` already spans 12 tradable months | Pin `C` at today and wait for `[C, G]` to accrue |
|---|---|---|
| In-sample length | Shortened — directly threatens the `≥ 4 years` and `MinBTL(N)` clauses | Maximal available today |
| Holdout protection | **Entirely historical → S3 does not apply → procedurally protected only** (§2.1) | **Genuinely unseeable** — the only real protection the design has |
| Time to Gate 1 | Immediate | 12+ months |

Seat 9's measurement must report the **full tradable-day timeline**, not just a total, so this
tradeoff is computed rather than guessed. **The choice between these is a sprint-scheduling decision
and is the Principal's, not mine** — I am surfacing it under house rule 7 [cited] rather than
resolving it silently. My only binding constraint on it is §2.4: whichever is chosen, the Validation
Report states on its face whether the holdout is unseeable or historical.

---

## 5. Acceptance criteria for implementation — itemized

**Binding rider from the Principal:** the I-005 change ships with test coverage equivalent to the
current holdout tests and the **full harness suite passing** before any ingest begins. Current
baseline: **30/30** [measured]. Itemized below. Acceptance is **Validation's to grant in writing** —
a green suite is necessary, not sufficient.

**A — Spec sealing**
- **A1** Sealing writes `spec.json` and a `holdout_spec_sealed` registry event carrying its sha256; the spec's binding fields are immutable thereafter.
- **A2** Re-sealing an existing vault raises. (Analogue of the current "vault already exists; re-locking would allow choosing a favorable split. Refused." at `holdout.py:82–86` — the property being preserved is that `C` cannot be chosen after the fact.)
- **A3** Sealing with `C` in the future relative to wall-clock is **permitted** and recorded (this is the preferred case, §2.4). Sealing with an empty/malformed query, a missing `dataset_id`, or a missing `schema_fingerprint` raises.
- **A4** The registry's recorded hash matches `sha256(spec.json)` on disk; a byte-level edit to `spec.json` is detected.

**B — Ingest ceiling (D2; test hardest, this is the compensating control for W3)**
- **B1** The ceiling row is written to `pit.db` at seal time from the spec's `C`.
- **B2** `PITStore.ingest` accepts observations with `event_time ≤ C`.
- **B3** `PITStore.ingest` **refuses** a batch containing any `event_time > C`: raises `HoldoutCeilingError`, **ingests nothing** (assert row count unchanged — atomicity is the assertion, not just the raise), logs `holdout_ceiling_violation`.
- **B4** A non-ceilinged dataset is unaffected by any ceiling.
- **B5** The ceiling cannot be raised, lowered, or removed through any API other than the D3 acquisition path; a direct mutation attempt raises.
- **B6** Boundary: `event_time == C` is **in-sample** (accepted). Tested with both tz-naive and tz-aware inputs, and across a UTC-midnight boundary.

**C — Acquisition**
- **C1** Correct passphrase + matching spec hash + `C` reached → returns the holdout, writes `payload.enc`, logs `holdout_acquisition_attempted` **then** `holdout_acquired` (order asserted), state `RETIRED`.
- **C2** *(negative — rider-named)* **Second acquisition** raises `HoldoutRetiredError`, logs `holdout_second_acquisition_attempt`, returns nothing.
- **C3** *(negative — rider-named)* **Spec-hash mismatch between seal and acquisition** → refuse, log `holdout_spec_tampered`, **no network call attempted** (assert the injected fetch callable was never invoked).
- **C4** *(negative — rider-named)* **Wrong passphrase** → refuse before any fetch; assert no network call. **The vault is NOT retired by a wrong-passphrase attempt** — a typo must not brick a family — but the attempt is logged as `holdout_bad_passphrase_attempt` and the count is surfaced in the Validation Report. (This preserves the current wrong-passphrase test at `test_harness.py:176–178`.)
- **C5** *(negative — rider-named)* **Fetch attempted before pinned `C` is reached** (wall-clock `< C`, so `[C, G]` is empty) → refuse with a distinct error type, logged. **Adjacent case, also required:** `C` reached but `[C, G]` shorter than the §4.4 12-month minimum → acquisition **permitted**, artifact flagged, and `evaluate_gate1` reports the holdout criterion **FAIL** (not INSUFFICIENT-DATA — the fact is known, and it is a failure).
- **C6** Acquisition failure (injected network error / empty response) → logs `holdout_acquisition_attempted` and `holdout_acquisition_failed`, state `ACQUISITION_FAILED`, **not** retired; a subsequent attempt without a `holdout_retry_authorized` event raises.
- **C7** A retry following a valid `holdout_retry_authorized` event succeeds, and the retry count appears in the report.
- **C8** The acquired payload is encrypted at rest: raw `payload.enc` bytes do not contain a known plaintext value from the fixture series.
- **C9** Re-reading the sealed payload later requires the passphrase; a wrong passphrase raises.
- **C10** Schema-fingerprint mismatch between the sealed spec and the fetched frame → refuse to seal, log, treat as acquisition failure per C6.

**D — Leak detection (§2.4 control 2)**
- **D1** If `pit.db` holds any row for the ceilinged dataset with `event_time ∈ (C, G]` whose `knowledge_time` predates the acquisition event, the vault flags `holdout_pre_acquisition_leak` and `evaluate_gate1` returns **FAIL** on the holdout criterion.
- **D2** Clean case: no such rows → the criterion passes.

**E — Gate integration (includes the §2.4 defect fix)**
- **E1** `evaluate_gate1`'s holdout criterion is evaluated **per vault/family**, not globally. Two assertions, both required: a second-acquisition violation on family A must **not** fail family B; an acquisition on family A must **not** satisfy family B's criterion. *(Fixes the live defect at `gates.py:209–210`.)*
- **E2** `evaluate_gate1` with no acquisition event for the family → **INSUFFICIENT-DATA**, never PASS.
- **E3** The report embeds the spec hash and the acquired-payload sha256, alongside the existing returns sha256 (§7.3, A1 [cited]).

**F — Migration and anti-erosion**
- **F1** The legacy `lock()` / `open_once()` path is **removed, or hard-raises `HoldoutRegimeError`** pointing to the P-1 API. Not deprecated-with-warning: a code path that violates a Principal amendment must not remain silently callable.
- **F2** Full suite green: the 30 existing tests **plus** A1–F1. **No existing test may be deleted or weakened to accommodate the change.** Any existing test requiring modification needs a written justification to Validation before the change lands. This clause exists because "make the suite pass" is otherwise satisfiable by editing assertions, and that is Appendix B #4 [cited] in its purest form.
- **F3** `harness/README.md` updated: the stale "(16 tests)" corrected, and the holdout paragraph (line 15) rewritten to describe the P-1 regime rather than the fetch-then-encrypt regime it currently documents.
- **F4** Registry support for `predecessor_family` (§3.3), with `family_stats` summing `N` transitively across the chain, and a test that a successor family's `N` starts at the predecessor's total rather than zero.

**Count:** 4 + 6 + 10 + 2 + 3 + 4 = **29 new test cases**, target suite **59/59**. Seat 9 may merge
cases where two assertions genuinely test one property, but a merge that drops an assertion is a
reduction in coverage and requires Validation's sign-off.

---

## 6. What is unblocked, and what remains blocked

**Unblocked now** — both of these are Seat 9's, they are independent of each other, and they should
run **concurrently**, not in sequence:

| Work | Owner | Depends on |
|---|---|---|
| Implement the vault per §2.3 D1–D4 and §5 A–F | head-of-data-infra | this ruling only |
| Draft `research/DATA-SPEC-polymarket-usable-history.md` per §4.2–4.4 | head-of-data-infra | this ruling only — **requires no data and no ingest** |

**Still blocked:**

| Blocked | On | Owner of the blocker |
|---|---|---|
| **All ingest** (I-001) | Validation's **written acceptance** of §5 F2. A green suite is necessary, not sufficient | quant-validation, on Seat 9's delivery |
| Measurement of usable Polymarket history | Validation's acceptance of the DATA-SPEC draft (§4.4) — the spec is accepted *before* measuring, per the Principal's rider | quant-validation, on Seat 9's draft |
| Pod B pre-registration / forward-lag Gate 0 verdict (I-004) | Both of the above, plus a `C` placement decision informed by the §4.4 timeline tradeoff | pm-digital-markets, gated by Validation |
| The `C`-placement / sprint-schedule tradeoff (§4.4) | The Principal. Surfaced under house rule 7, not resolved here | Principal |

**Issue Log entries this ruling touches** — the CRO owns the log; these are my inputs to it, not
edits I have made:

- **I-005** — resolved *in specification*. It closes on Validation's acceptance of the
  implementation, not on this document.
- **New entry requested, MEDIUM, owner head-of-data-infra:** the `gates.py:209–210` global-event
  defect (§2.3 D4). Latent, never fired (zero families exist), would have fired on the second
  family. Pattern tag `harness-correctness-latent`.
- **D-003 amendment requested:** "Strictly stronger" corrected per §2.1 to "stronger on leak
  surface, conditionally stronger on unseeability, weaker on evidentiary permanence, availability,
  and split enforcement."

---

## 7. What would change my mind

Stated as falsifiers, per house rule 2 — each is a specific observable, not a mood.

**Ruling 1 (vault design).**
- If Seat 9 demonstrates that `PITStore.ingest` cannot enforce the D2 ceiling atomically without an unacceptable rewrite of the append-only store, I would reconsider the ceiling's location — but **not** its existence. The requirement that enforcement live below the caller is not negotiable; only its implementation site is. If it cannot live in `PITStore`, it must live in `loaders`, and I would then have to accept that a direct `PITStore.ingest` call bypasses it and say so in every Validation Report.
- If a mechanism exists to bind a fetch to a verifiable third-party attestation of the series as it stood at `C` — a signed vendor snapshot, an on-chain commitment, an archive with a content hash — that would materially repair W1 and I would require it rather than merely permitting retention of the Gate-1 seal. I am not aware of one for the venues in §3.2 [assumed — I have not surveyed this and did not spend the budget to].
- I would **not** change my mind on the residual weakness in §2.4 on any argument that the seats are trustworthy. Trustworthiness is not a control, and the whole design exists because Appendix B #3 is irreversible.

**Ruling 2 (`C` pinned).**
- Argument (1) is the load-bearing one. If `registry.returns_matrix` were changed to record and enforce the sample window per trial, and to refuse to assemble a CSCV matrix across trials with differing windows, then recomputing `C` would become *statistically* detectable rather than silent. Arguments (2) and (3) would still stand, so I would still rule for pinning — but I would drop argument (1) and say so, and the ruling would be weaker.
- Argument (2) collapses if the interval between pre-registration and Gate 1 were fixed and externally imposed, removing the sponsor's discretion over `G`. The firm has no such mechanism today [measured — D-004 sets a sprint window, not a Gate date].
- I would reverse entirely if the Principal amends §4.4 in writing, *in advance*, to define the holdout as a fixed-length forward window from Gate 1 rather than a fraction of the series. That is a coherent alternative design and it is his to make; it is not available as an in-flight adjustment during an evaluation.

**Ruling 3 (usable history).**
- If Seat 9 establishes that historical order-book snapshots are genuinely unavailable, T2 and T4 become unmeasurable, the tradable count becomes an acknowledged upper bound, and I would tighten the §4.4 verdict rule rather than relax it — an upper bound that only just clears 4 years does not clear 4 years.
- The `> 50%` stratum-concentration trigger and the `≥ 60%` / 90-day continuity floors are **my judgment calls, marked as such** [inferred, not cited — no external standard prescribes them; Appendix C's closing caveat, that no external body publishes numeric validation thresholds, applies here as it does to §4.2]. I will move any of the three on a reasoned argument from Seat 9 or the Devil's Advocate **before** the measurement runs. I will not move them after, for any reason including the measurement's outcome. That asymmetry is deliberate and it is the point.
- The `≥ 4 years` and `≥ 12 months` figures are **Charter constants** and are not mine to move at all (§4.2, "not negotiable mid-evaluation" [cited]). Only the Principal, in writing, in advance.

---

*Head of Quantitative Validation · Castellan Capital · 2026-07-28*
*This ruling is binding on Seats 1, 2, 6–10. It is appealable only to the Principal, in writing.*
