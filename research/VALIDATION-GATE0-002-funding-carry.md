# VALIDATION — GATE 0 INTAKE VERDICT · `funding-carry-conditioning-002`

**Seat:** Head of Quantitative Validation (Seat 3) · **Reports to: the Principal** · **Date:** 2026-08-12
**Dispatch:** S3-D-022, Row 3 · **Discharges:** **C2** · **C13(1)(2)(3)(e)(f)(h)(k)** · **I-181** · **I-182**
**Subject:** `research/PREREG-002-crypto-funding-basis.md` at R-007+S3-D-019 · payload `research/REGISTRATION-PAYLOAD-PREREG-002.md`
**Registry:** `book/registry.db` — **0 hypotheses / 0 trials / 3 events** [measured, read-only, this session; opening and closing]

---

## 0. LINE BUDGET, STATED BEFORE WRITING

| § | Section | Projected |
|---|---|---:|
| 1 | What this verdict does **not** rule — the deferred enumeration | 75 |
| 2 | Gate 0 criterion table | 55 |
| 3 | Leakage audit | 55 |
| 4 | C13(k) — the instance ruling | 60 |
| 5 | I-181 — resolution, and the one character I inserted | 55 |
| 6 | The executed diff — guardrail 3, graded | 50 |
| 7 | The span, and §10.4's restated arithmetic | 65 |
| 8 | The remaining C13 items, ruled | 45 |
| 9 | Registry · N · holdout · harness binding | 35 |
| 10 | Conditions, and what would have to be true to pass | 55 |
| 11 | Issues filed, I-200 … I-209 | 75 |
| 12 | To the Principal | 25 |
| — | header, verdict box, footer | 50 |
| | **TOTAL** | **~700** |

**Under the ~800 ratchet with ~100 lines of headroom. Nothing proposed for cutting.**

---

> # VERDICT: **ADMIT-CONDITIONAL**
>
> **`funding-carry-conditioning-002` is ADMITTED to Gate 0, conditional on the four items at §10.1,
> two of which are already cleared by this document.** It may be sealed, and it may spend Stage 1.
>
> **It may NOT be evaluated at Gate 1 and no PROCEED may be reported, on nine independent grounds
> enumerated at §1.** The Principal's C5 lock is one of them; the other eight are named here for the
> first time as a set.
>
> **This is a SCOPED verdict. §1 is the scope statement and it is not optional reading.**
>
> **Seal-blocking after this document: C7 and C8. Nothing else.**

---

## 1. WHAT THIS VERDICT DOES NOT RULE — THE DEFERRED SET, ENUMERATED AND COUNTED

*The Principal's addition, binding on the verdict's form: the deferred named as deferred, so the seal's
record shows a scoped verdict and not a complete one wearing scoped clothes.*

**Membership test, stated before the list so the count is auditable and not assertable.** An item is
in the deferred set iff **(a)** it was in front of this intake, by §20 of `PREREG-002` or as a
Validation-owned open issue on this family; **(b)** it is not ruled by this document; **(c)** it binds
at **Gate 1 evaluation**. Items ruled here are at §4, §5, §7, §8; items that block only the **seal** are
at §10.1 and are not deferred — they are conditions.

| # | Deferred item | Source | Why it binds at Gate 1 |
|---:|---|---|---|
| **D-1** | **C5** — the point of application of §4.6's 50% published-signal haircut, its §4 ratification, and its executor | §20 C5; I-143; I-152 | The Principal's lock: **no Gate 1 evaluation, no PROCEED, until ruled.** Part 2 is the Principal's and I cannot supply it; **I decline part 1 without part 2**, because a point of application ruled without ratification and without an executor is class (c) and leaves I-143's permissive branch exactly where it is. The gap is **2× at `t`** |
| **D-2** | **C4** — which window `oos_index` carries under §11.3 Option D, and therefore the earliest date Gate 1 is reachable | §20 C4 | **Without `oos_index` the length criterion is INSUFFICIENT-DATA, never PASS** (G1–G5, carried in the family's own `success_criteria`) |
| **D-3** | **C6** — whether reading `field='funding_rate'` via `PITStore.asof` / `rows_in_window` is an admissible A4 path, there being no `pit_*` panel accessor for a non-close field | §20 C6 | If the read path is inadmissible under A4, **every trial derived from it is inadmissible**, and this family's state variable is that series |
| **D-4** | **C13(g) / I-045** — SOL's dated structural break; three answerable questions the Director has now declined four times; closure routes to this seat | §20 C13(g); I-045, **HIGH** | SOL is out of the sealed universe (K4 option 4), so it does not touch a number. It binds as an **open HIGH data-provenance issue that Charter §7.3 requires on the Gate 1 report's face** |
| **D-5** | **C13(j) / I-151** — House Rule 5's breakeven instrument costs **0–42 logged trials** against a Stage 1 that sums to **exactly 47 with zero slack** | §20 C13(j); I-151 | House Rule 5 makes the breakeven **mandatory on every Gate 1 submission**. See §8.4 for why I refuse to rule it rather than rule it inertly |
| **D-6** | **I-173 / I-186 — the post-repair dated-clause firing count.** Floor **27**, mechanically certain; unbounded above at **51** | I-173, I-186, both **HIGH/MEDIUM** | **E-24: a nonzero exit makes the Gate verdict INSUFFICIENT-DATA.** `harness/scripts/evaluate_dated_clauses.py` **does not exist** [measured — I-186], so no number here is a harness number, including the 27 |
| **D-7** | **I-170** — no document defines the canonical string of a prose binding field, and `dated_clauses.source_offset` requires an integer over it; **88 of 90 offsets differ between the two readings** | I-170, MEDIUM; mine | A register that guesses wrong puts 88 rows `DANGLING` and 88 sites `UNCOVERED` — **exit 4, from a whitespace convention** |
| **D-8** | **I-172** — **zero `SPAN` sites exist in this family**, so E-9's recomputation and E-21's named proof case never run | I-172, **HIGH** | The direction-blindness apparatus built for this family's span **has no site to act on.** A missing control, not a wrong number — which is worse, not better |
| **D-9** | **I-076** — `test_mbs_12`'s 20% aggregation-invariance band missed at ρ=0.83, seed 1011 (**1.2536** against ≤1.20) | I-076, MEDIUM; routed back to this seat | It is a tolerance on **`variance_inflation`**, and `VIF_gate(ρ̂)` is the whole of §10.4.1's sealed ceiling function. **A family whose ceiling is a function of an estimator carries that estimator's open tolerance** |

### **MY COUNT FROM THE ENUMERATION: NINE.**

**The CIO's table names four (C5 · the 27–51 estimate · I-045 · I-076); the Principal's ruling says
five. Counted from the enumeration under the stated membership test, it is nine.** The five neither
document named are **D-2 (C4)**, **D-3 (C6)**, **D-5 (C13(j))**, **D-7 (I-170)** and **D-8 (I-172)** —
every one of them a §20 row or a Validation-owned open issue against this family, and every one of
them Gate-1-binding on the test above. **Filed I-205.** I did not take a count from either party and
this is the seventh cardinal in three sprints stated from a table rather than from an enumeration.

**None of the nine can produce a wrong seal.** Every one bears on **evaluation**, which the ruled slip
has moved to Sprint 4. A wrong seal is what §10.1's conditions guard, and they are a different list.

---

## 2. GATE 0 — THE SEVEN CRITERIA, §4.3

| # | Criterion | Computed / observed | Verdict |
|---:|---|---|---|
| 1 | Written **economic or structural mechanism**, in terms of who is on the other side and why they accept the loss | Three named payer classes, and — decisively — **§21 `mechanism` states on its own face that the unconditioned carry is NOT an edge**: *"a premium that persists because it is a fair price for a service is not alpha."* The claim under test is narrower: alpha **to `R_bench`**, not raw Sharpe | **PASS** |
| 2 | **Pre-registered falsifier** | F-002, four legs, three pre-specified series, four pre-committed constants; joint false-survival rate **1.3e-4 [derived]**, with the leg-(ii) term **[assumed]** pending C11 (§10.2) | **PASS**, with the assumed term disclosed |
| 3 | Universe, horizon, rebalance, **success criteria stated before the first run** | Registry holds **0 trials** [measured]. Nothing has been run. `success_criteria` was **unreadable as a bracket-balanced string until this document** — see §5 | **PASS** (was FAIL until §5's repair) |
| 4 | Required data **exists** within Part III | Public crypto exchange APIs — Part III's best surface. §8.3: *"no PIT fundamentals, no survivorship-free equity universe, no tick data, no borrow data, no paid news, no brokerage connectivity."* **Every Part III hard wall untouched** | **PASS** |
| 5 | Survivorship and look-ahead exposure **identified with a mitigation named** | §9.1/§9.2. Two continuously-listed instruments, not a screen output. **Venue survivorship is identified and its mitigation is disclosure, not correction** — the sponsor says so itself. §9.2's four look-ahead channels each carry a named, measured mitigation | **PASS** |
| 6 | **Trial counter opened and instrumented** (A2) | **0 hypotheses in `book/registry.db`.** Registration **is** the seal, and the seal is the act this verdict authorizes | **PENDING BY CONSTRUCTION** — see below |
| 7 | **Holdout period defined and locked** | Defined: `FORWARD`, `forward_window_start = C`, min length 12.0 months. **`book/vaults/` holds only `.gitkeep`** [measured] — **not locked** | **PENDING BY CONSTRUCTION** — locks at C8 |

> **Criteria 6 and 7 cannot be PASS at a Gate 0 evaluation, in this firm, ever.** `open_hypothesis`
> computes `prereg_sha256` on first registration — registration and sealing are one operation — and
> `HoldoutVault.seal()` is bound to the same session and UTC day. **The two criteria are satisfied by
> the act the verdict authorizes, so a Gate 0 verdict that required them PASS could never issue.**
> `VALIDATION-GATE0-001` did not name this and it should have. **Filed I-206.** They are recorded here
> as **PENDING BY CONSTRUCTION**, which is neither PASS nor FAIL nor INSUFFICIENT-DATA, and the
> conditions at §10.1 are what make them mechanical.

**No criterion FAILs. One FAIL would fail Gate 0 and there is not one.**

---

## 3. LEAKAGE AUDIT — RUN IN FULL, EVERY TIME

| # | Check | Finding | Verdict |
|---:|---|---|---|
| 1 | Any field filtering on `event_time` rather than `knowledge_time`? | §8.2: *"the two-timestamp rule still binds and every query filters `knowledge_time ≤ decision_time`."* **The admissibility of the funding read path itself is C6 and is deferred (D-3)** | **CLEAN**, pending D-3 |
| 2 | Restated fundamentals? | **No fundamentals are used.** The equity-side fatality (78% restate within 400 days) does not reach this mandate. **But a restatement did occur** — `binanceusdm` re-adjusted the 2026-07-29 perp bar on both legs, 3 fields each, auto-logged as events 2 and 3 (I-190). **Blast radius zero at 0 trials** [measured] | **CLEAN**, with the venue's restatement behaviour now a measured fact, not an assumption |
| 3 | Survivorship-contaminated universe? | **Quantified, not asserted.** Two continuously-listed instruments; the residual is **venue** survivorship, and the sponsor states it in its sharpest form: *"a surviving venue is a carry strategy backtested on the branch where the tail did not happen."* Mitigation is disclosure. **`CostModel` has no field that can charge liquidation or venue-insolvency risk — the largest risk in this mandate — and that is class (c), C-25, unrepaired** | **IDENTIFIED, MITIGATED BY DISCLOSURE ONLY.** Admissible at Gate 0; it is a real exposure and I record it as one |
| 4 | Prices retroactively adjusted in a way the signal could not have seen? | A4 path: raw into `PITStore` via `castellan.loaders`, `pit_adjusted_close` on consumption. **No `yfinance` series is used.** `knowledge_time` on the backfill is the ingestion instant and **the sponsor declares that this family may not claim to have tested point-in-time on the backfilled rows** | **CLEAN, with the backfill limitation declared by the sponsor against itself** |
| 5 | Same-bar fill? | `run_backtest(execution_lag=1)`; `execution_lag < 1` raises **`SameBarFillError`** [`engine.py:30`]. Funding posts 00/08/16 UTC; the day-`t` aggregate is complete at 16:00Z and fills at `t+1` — **a genuine 8-hour margin, not a boundary case** | **CLEAN — class (a), enforced in code.** This is the check that took a documented reversal Sharpe 1.41 → 0.26 [cited — DB *Seven Sins*]; here it cannot be waived |
| 6 | Standard k-fold where purged k-fold with 1% embargo was required? | **The sponsor carries the defect in its own sealed field rather than waiting to be told:** `walk_forward_windows` applies **no purge and no embargo at all**, and `purged_kfold_splits` embargoes `ceil(0.01·T) = 24` bars on a 2,398-bar sample — **shorter than this family's own 30-day K1 lookback** | **DEFECT, CARRIED AND DISCLOSED PRE-SEAL.** Not a Gate 0 bar. **It is a Gate 1 bar** and the 1%-embargo criterion cannot PASS while the embargo is shorter than the lookback that generates the signal |
| 7 | Parameter chosen at the argmax rather than the plateau centroid? | **Only `plateau_centroid_params` advances**, by sealed commitment; centroid **and** argmax are both reported, *"the distance between them being itself the overfitting diagnostic."* §10.7(c) closes the walk-forward hole: **no window re-selects** | **CLEAN — and it is what keeps ML-1 from firing.** §8.1 |
| 8 | Was the holdout consulted, in any form, before this evaluation? | **`book/vaults/` contains only `.gitkeep`** [measured]. **No vault exists, so none has been opened, and no key has been issued.** The holdout is FORWARD — it is data that does not exist yet | **CLEAN. Not consulted, and structurally unconsultable** |

**Two live leakage defects, both disclosed by the sponsor before I found them (check 6 and check 3's
venue residual). Neither is fatal at Gate 0. Check 6 is fatal at Gate 1 as the document stands.**

---

## 4. C13(k) — THE INSTANCE RULING

**RULED: the conformance stands. `C + 187 days` governs, in every instance, in the field body and in
its opening. I do not require the drafted literal `2027-01-31`.**

**I do not dissent from the Principal's ratification. My concurrence is independent and rests on a
ground he did not state, so the adversarial check survives his ruling rather than being displaced
by it.**

**The Principal's ground** was the field's own declaration — *"the drafted date is not binding, the
formula is"* — a sentence written **before** the ambiguity was found, and therefore not a post-hoc
rescue. That ground is sound and I adopt it. It is not what decides the instance.

**What decides the instance is that taking the drafted literal is not the harder test. It is a
threshold change nobody chose.**

KC-002 clause (b) carries an **unchanged 30-conditioning-day threshold**, calibrated against a
**187-day** window and against *"~184 daily bars and ~552 funding prints."* **Thirty is a count, not a
rate.** Hold the count and shorten the window and the implied rate moves:

| Window | Source | 30 days as a fraction of the window |
|---|---|---:|
| **187 days** | `C + 187 days`, the calibrated basis | **16.04%** |
| **171 days** | drafted literal, at a seal on 2026-08-13 | **17.54%** |

`(30/171) ÷ (30/187) = **1.0936**` [measured, this session]. **Requiring the drafted literal moves a
pre-registered kill-condition threshold by 9.4% — and the size of the move is a function of how many
days elapsed between drafting and sealing, which is a quantity with no statistical meaning
whatsoever.**

**That is not tightening. It is randomizing.** Adversarial rigour means a harder test, not a
differently-arbitrary one, and **a threshold that moves by an interpretation while its literal stays
put is the exact shape the Principal's own C5 doctrine reserves to himself under Charter §4.** I
cannot effect a §4 reserved act by declining a conformance. **Refusing the conformance would have been
the permissive act wearing the adversarial seat's clothes.**

**One condition attaches, and it is a prohibition rather than a task — §10.1(S-2).** Under the
conformance the drafted `2027-01-31` literals remain in `forward_kill_condition` as struck residue at
eight sites. **I-171 establishes that E-14's `DIVERGENT` verdict on that field — the only control that
catches clause 5 extracting as a bare `C` under E-2's case-sensitive `FORMULA` recognizer — fires
ONLY BECAUSE those struck literals are still there.** Strip them and clause 5, the automatic-
termination clause, becomes a bare `C` that resolves to the seal day and **FIRES on the day of the
seal**. The document is presently protected by its own uncorrected text, **and that is not a control.**

**I rule, on I-171, in both available directions at once:** E-2's `FORMULA` recognizer **is
case-insensitive on the unit** — a spec amendment to `VALIDATION-SPEC-004`, mine, tightening, not
funded in this dispatch — **and until it lands, the eight struck `2027-01-31` literals may not be
removed from `forward_kill_condition` by any conforming pass, by any seat.** **Filed I-204, HIGH.**

---

## 5. I-181 — RESOLVED. THE FIELD CAN SEAL.

**The Principal ruled: it resolves before hashing or the field does not seal. It resolves. I made the
repair myself and I state exactly what I did.**

**The edit, in full.** One character, in `research/PREREG-002-crypto-funding-basis.md`, at the end of
line 2559 of `success_criteria`'s §21 text:

```
  before:   ...N_conditioning (7) nor the MinBTL figures move; what moves is what
                 may be SPENT.
   after:   ...N_conditioning (7) nor the MinBTL figures move; what moves is what
                 may be SPENT.]
```

**Why this boundary and not another — and why it required no judgment about R13 versus R14.** The
Director's stated obstacle was distinguishing R13's content from R14's inside a consolidated marker.
**That question does not have to be answered.** Only one question does: where does the consolidated
marker close. **The document answers it, twice, in the same field, by its own convention:**

- `[R3, 2026-08-04: the item 'SOL on its own span with its own N' is STRUCK - SOL is not in the universe]`
- `[R19(b), 2026-08-10, PRE-SEAL - STRUCK. ... REPLACED BY:]` — **and the replacement text sits outside the bracket.**

**In every other marker in this field the bracket holds the revision NOTE and the substantive text
sits OUTSIDE it. Markers are siblings; none nests.** R13's note is complete and self-contained through
*"...what moves is what may be SPENT."* What follows is `[R20, 2026-08-10, ...]` — **a later-dated
sibling**, well-formed and self-closing — and after R20 closes, the text resumes as substantive field
prose (*"The ceiling this family is graded against is `N_max = min(109, ...)`"*), which is exactly the
R19(b) pattern. **The sibling reading is the only convention-consistent parse, and it is determined by
the document rather than chosen by me.**

**Verification, measured, this session:**

| | before | after |
|---|---:|---:|
| `success_criteria` bracket depth at field end | **1** (unbalanced) | **0** |
| minimum bracket depth over the field | 0 | **0** (no negative excursion) |
| `success_criteria` length, verbatim | 42,055 | **42,056** (+1) |
| **`extract_dated_sites.py` TOTAL SITES** | **68** | **68 — unchanged** |

**The insertion is provably semantically null with respect to the extractor and syntactically
required by the Principal's ruling. It changes no word, no number, no threshold and no claim.**
**I-182 falls with it:** R20's close was never the missing bracket; R20 was well-formed all along and
only appeared unresolvable because it sat inside R13's unclosed scope.

> **THE NEAR-MISS, RECORDED BECAUSE IT IS THE MOST INSTRUCTIVE THING IN THIS SECTION.** The obvious
> mechanical repair — close the marker at the field's end — would have placed **§10.4's entire sealed
> ceiling function, the §10.8 verdict bands, the mandatory disclosure lines, the tiered success
> criteria, the I-050 statement and both harness leakage defects** inside a revision marker. Under
> S3-D-016's relocation rule, **all of it would then have been eligible to be moved out of the hashed
> field into §21.1.** The family would have sealed with its ceiling function outside
> `prereg_sha256`'s input. **Guardrail 1's STOP-AND-QUEUE prevented that, and it is the single
> highest-value thing that guardrail has done.** Filed **I-203**.

**`success_criteria` is now bracket-balanced and can be hashed. The field can seal.**

---

## 6. THE EXECUTED DIFF — GUARDRAIL 3, GRADED ONCE, BY THIS SEAT

**The classification is CORRECT. The execution is ACCEPTED. The refusal to chase 55 was right and I
say so as the seat with no incentive to.**

**I reconciled the arithmetic end to end rather than accepting it, live, this session:**

| Step | Sites | Source |
|---|---:|---|
| Pre-edit, live | **92** | I-180; reproduced by field sum below |
| Relocated by S3-D-016 | **−27** | I-185 |
| Post-edit, S3-D-016 | **= 65** | I-185, stated |
| **Written back in by S3-D-019's span-conforming pass** | **+3** | **this session, measured** |
| **Live now** | **68** | `extract_dated_sites.py`, this session |

**Per-field, measured now:** `statement` 2 · `mechanism` 0 · `falsifier` 5 · `universe` 11 · `horizon`
0 · `success_criteria` 14 · `forward_kill_condition` 36 = **68**. Against the payload's pre-edit
roster (2 · 2 · 5 · 17 · 0 · 23 · 41) **+2 for R38** = **92**. **The +3 lands exactly where I-191 says
it wrote conforming notes: `universe` +2, `success_criteria` +1.** Every figure reconciles to the
site. **Nothing in the executed diff is unexplained.**

**Grading the three judgment calls the executing seat routed here:**

1. **The 8 exceptions (I-181–I-184) were correctly withheld.** Each requires deciding where revision
   apparatus ends and substantive prose resumes. **I-183's four brackets pair a `stamp:true` date with
   a `stamp:false` date inside one bracket** — relocating whole would have carried a substantive date
   out of a hashed field; splitting was not a decision the per-date roster ever made. **Correct stop.**
2. **The relocation target is genuinely outside the fence — verified, not accepted.** §21's fenced
   block runs lines **2029 → 3410**; §21.1 begins at **3414** [measured, this session]. The CIO's
   3392/3396 figures have since drifted with S3-D-019's edits; **the property they asserted holds at
   the current head.** §21.1 is outside `prereg_sha256`'s input and always will be under P2.
3. **The refusal to reach 55 is the finding, not the shortfall.** 55 was `90 − 35` against a baseline
   that was **92**, and 8 of the 35 were unrelocatable, so the reachable floor was **57** and 55 was
   **unreachable by construction**. A seat that had hit 55 would have done so by guessing a bracket
   boundary — i.e. by committing I-181's exact error to satisfy a number. **Refusing was the correct
   act and the Principal's ruling on it is right.**

> **AND THE 68 IS THE REAL FINDING.** I-178 said the register can never be finished while binding
> fields carry commentary. **It has now been measured twice: a dispatch ordered to record a
> measurement wrote three new dated sites into the fields a prior dispatch had just cleaned.** The
> count moves every time any seat touches the document for any reason, including reasons that are
> correct. **Filed I-201.**

---

## 7. THE SPAN, AND §10.4's ARITHMETIC CONSEQUENCE — RESTATED

**The Principal's ruling on the span is adopted without qualification and I state the ground I find
strongest.** `2026-08-12` was the currently-forming UTC day at ingest — spot BTC volume **398.04**
against a several-thousand trailing norm — and the same shape produced I-190's restatement of
`2026-07-29` one bar earlier. **The venue's restatement of a forming bar is now a measured behaviour
of this exact data source, not a hypothesis.** Sealing 6.6120 would put a value known in advance to
restate inside a P7-frozen field and manufacture a future A4 event there. **The span seals at 2,414
days, `[2020-01-01, 2026-08-11]`, settled bars only.**

`2414 / 365.2425 = **6.609308**` [measured, this session].

### 7.1 §10.4's arithmetic, recomputed — and BOTH circulating margins are rounded-input arithmetic

**`MinBTL(86, SR 1.0)` does not move.** It is a function of `N`, `SR` and `ppy`, never of what is on
disk. **Measured this session via `castellan.stats.min_backtest_length_years(86, 1.0, 252)` =
`6.135900`** — which is §10.4.2's own figure, not the `6.14` that §10.4's table displays.

| Quantity | At sealed 6.571 | **At settled 6.6093** | Moves? |
|---|---:|---:|---|
| `MinBTL(86, SR 1.0)` | 6.135900 | **6.135900** | **No** |
| **Margin against the span** | **0.4351** | **0.4734** | **Yes** |
| Margin as % of required length | 7.09% | **7.71%** | Yes |
| Maximum admissible VIF | 1.070910 | **1.077152** | Yes |
| **Binding AR(1) `ρ̂`** | **0.034241** | **0.037143** | **Yes — loosens 8.5%** |
| `max_admissible_trials(span, 1.0, 252, vif=1.0)` | **109** | **112** | **Yes — loosens by 3** |
| Declared ceiling `N` (7 + 79) | 86 | **86** | **No** |
| Authorized Stage 1 ceiling (7 + 47) | 54 | **54** | **No** |

> **THE 0.43 AND THE 0.469 ARE BOTH WRONG AT THE PRECISION THEY ARE QUOTED, AND FOR THE SAME REASON.**
> Both subtract the **displayed** `6.14` rather than the **measured** `6.1359`. `6.571 − 6.14 = 0.431`;
> `6.6093 − 6.14 = 0.4693`. The correct values are **0.4351** and **0.4734**. **The document already
> disagrees with itself:** §10.4.2 carries *"the margin is **0.435** years, 7.1% of the required
> length"* while §10.4, §10.1, §10.3, R6, R8(b), R19(c) and the payload §2.8 all carry **0.43**.
> **Filed I-200.** The propagated figure runs **against** the family — it understates margin — which is
> why seven revisions passed over it.

### 7.2 The ruling on the loosening — and the thing §10.4 is not

**Three quantities move in the family's favour. I rule that none of them may be banked, and the reason
is that none of them binds anything.**

- **The absolute ceiling 109 → 112 is inert.** `86 < 109 < 112`. It changes only *unused headroom*,
  23 → 26 trials, and unused headroom grades nothing. **The declared and authorized ceilings do not
  move and I do not move them.**
- **The binding `ρ̂` 0.0342 → 0.0371 is not a threshold anything reads.** It is a *description* of the
  `ρ̂` at which the declared `N` exhausts the span. `gates.py` computes VIF from logged trials,
  recomputes `MinBTL_serial`, and compares against the span carried by `oos_index` — **at evaluation
  time, from the registry, never from a sealed literal.** The description moves because the
  computation moves; nothing is being relaxed.
- **The margin 0.4351 → 0.4734 is a report, not a control.**

> ### **THE RULING §10.4 ACTUALLY NEEDS, WHICH THE DIRECTOR CORRECTLY DECLINED TO PROPOSE.**
>
> **Every number in §10.4 is class (c).** Name the field the harness reads to enforce §10.4's margin:
> **there is none.** `gates.py` recomputes the length criterion from `oos_index` at every call. §10.4
> is a *planning statement about what that computation will return*, and it is stale the moment ingest
> runs — which it did, on 2026-08-12, for the first time in fourteen days.
>
> **Therefore §10.4 is NOT conformed to the settled span, and I require no further edit to a hashed
> field.** The computed values live **here**, on a Validation Report, which is where a computed number
> belongs — §4.7.3 applied to §10.4's own reporting surface. The sealed field's `[SUPERSEDED - S3-D-019]`
> note reading *"margin widens from 0.43 to ~0.47 yr"* is **consistent with the measured 0.4734 and is
> conservative in both of its figures**, and I will not authorize a second hashed-field edit to
> improve the family's stated margin. **The one hashed-field edit in this document is §5's, and it
> moves no number.**
>
> **Two literals will nonetheless freeze stale under P7: the integer `109` (§10.4 table, §10.4.1,
> §10.4.3's mandatory render string, §18's family-exit trigger, §1's box) and `0.034` (§10.4.2,
> `success_criteria`). Both are stale in the CONSERVATIVE direction — they understate what the
> arithmetic permits — so they are admissible sealed. Filed I-207 so the record shows they were seen
> and accepted rather than missed.**

### 7.3 One consequence of the span that is not arithmetic

§11.1 declares the in-sample window as **`[2020-01-01, C]`**. At any seal date `C > 2026-08-12` that
window again runs past the last bar on disk — **R37's exact finding, recurring, structurally.**
**I rule: the in-sample span of this family is the measured common bar span, and any figure computed
as `C − 2020-01-01` is inadmissible in any artifact.** `gates.py` already does the right thing —
`years_calendar` comes from `oos_index` — so the control is class (a) and the rule above is a
prohibition on narration, not on the engine.

---

## 8. THE REMAINING C13 ITEMS PUT TO THIS INTAKE — RULED

**8.1 · C13(1) — the ML-2 assertion and the §10.7(a) check. ACCEPTED.** ML-1 does not fire: K1–K7 were
selected pre-measurement against a registry holding 0 trials [measured]; K4's R3 move was made on a
**documented vendor act dated 2022-11-09**, not on any statistic, and no return statistic on SOL has
ever been computed by this family; the grid advances the plateau centroid by rule; §10.7(c) closes the
walk-forward hole so **no window re-selects**. **The non-firing is CONDITIONAL on those two
commitments and they are now sealed, which is the only form in which I would accept it.** ML-2's
sentence is present in `success_criteria`, so this is not a partial ML block and **not the ML-2
rejection.**

**8.2 · C13(2) — §7.2's escalation rule. ACCEPTED IN ITS HARD-STOP FORM. Do not wait on I-053.** A
HARD STOP can only refuse work; it can never admit any. **Sealing the conservative form costs the
family and protects the firm, and waiting for the harness repair costs forward window to buy a
weakening.** The sponsor's own §10.7(d) already raises the sharpest available criticism against
itself — that the 135,000 → 7 discount rested on an enforcement inoperative between R-001 and R-002.
**Recorded, not cured, and the hard stop is what stops it recurring.**

**8.3 · C13(3) — ML-17's formula. SUPERSEDED, NOT CORRECTED.** GATES.md **§4.7.1** now rules that
inheritance is computed by the registry's transitive summation and never re-declared, with
`InheritedCountDoubleCountError` enforcing it. **A formula in a prose ruling that tells a sponsor to
declare what the registry computes is §4.7.1's own named defect.** ML-17's arithmetic is struck as
inoperative rather than corrected; correcting a superseded formula is an act that buys nothing.

**8.4 · C13(j) / I-151 — I REFUSE TO RULE IT, AND THE REFUSAL IS THE RULING.** The statistically
correct answer is that a bisection over a cost parameter with a monotone objective **performs no
selection** — the root is unique, nothing is maximized, and the 42 evaluations are one strategy at 42
cost levels, not 42 candidates. **On the statistics, it should not deflate DSR.** But apply §4.7.2's
test: **name the field the harness reads to distinguish a reporting trial from a search trial. There
is none.** `gates.py` deflates against `fam.n_trials` flat. **A ruling that "reporting trials do not
count" would be read by nothing, would leave the registry counting them anyway, and would be class (c)
— an asserted control that is not there. I will not issue one.** The two implementable answers are:
fund the ≤9 survive-path evaluations from Stage 2's contingent 32, or accept `iters ≤ 3` at 250 bps/yr
resolution, **which cannot discriminate on an 11–14%/yr carry and I agree with the sponsor about
that.** **The remedy is a registry-side trial-kind distinction and it is mine to spec. Deferred as D-5.**

**8.5 · C13(e) — `n_inherited = 7`. ACCEPTED.** `predecessor_family = None`, so
`InheritedCountDoubleCountError`'s guard is never entered and there is no chain to double-count. **The
registry cannot compute `N_conditioning`** — it holds no knowledge of menus. §4.7.1 governs
inheritance *from a predecessor*; this is a first family with none. **And I accept it on the direction
it moves:** at `n_inherited = 0` the unlock table admits 30 where §10.5.2 declares 23 and 8 where it
declares 1 — **permissive at exactly the two rungs where the family is in trouble.** The 7 costs the
family `MinBTL` at 86 rather than 79 and pays §10.3's 0.13-year I-027 residual rather than mitigating
it. **A sponsor choosing the tighter of two available registrations is the correct answer to C13(e)
and there is no third outcome.**

**8.6 · C13(f) — the Stage 2 CONTINGENT extension. ACCEPTED IN THE SELF-ISSUED CONTINGENT FORM. No
countersignature required.** B-16 is right: the extension is authorized by a computation, the
criterion recomputes `N_max` at evaluation time and **never trusts the event's assertion that the
predicate held**, and the cap is aggregate. **Forging the event buys nothing.** A DISCRETIONARY form
with a countersignature would substitute a person's signature for arithmetic and would be strictly
weaker.

**8.7 · C13(h) — I-134 / I-135. DISCLOSURE IS SUFFICIENT AT GATE 0 AND IS NOT SUFFICIENT AT GATE 1.**
That no harness path applies the haircut and none evaluates a kill condition on any date does not bear
on **admissibility**. It bears entirely on **evaluation**, where it is D-1 and where the Principal has
already put a lock on it.

**8.8 · C10 — SUBSTANTIVELY SATISFIED, VERIFIED BY ME, NOT ACCEPTED ON REPORT.** I read `gates.py`
this session: **the only `= True` in the file is `p7_fail = True` at line 1029 — a failure flag.** The
literal `True` verdict I-022 quotes **does not exist in `_trial_budget_criterion`**. C10's second
condition — that the document register Stage 1 as its sealed budget — is met at `trial_budget = 47`.
**Both conditions met. The formal closure of I-022 is a log act belonging to head-of-data-infra and
is not mine to perform.**

---

## 9. REGISTRY · N · HOLDOUT · HARNESS BINDING

| Item | Value | Source |
|---|---|---|
| Hypotheses in `book/registry.db` | **0** | [measured, read-only, opening and closing this session] |
| Trials logged | **0** | [measured] |
| Events | **3** — `book_open`, and `data_restatement` ×2 (I-190) | [measured] |
| **Trial count N used in this evaluation** | **`n_logged` = 0; `n_inherited` = 7 declared. N is KNOWN EXACTLY, not unknown** | registry + payload §2.8 |
| **Cross-sectional variance of trial Sharpes** | **UNDEFINED — zero trials, therefore zero return series** | [measured] |
| Sealed holdout vaults | **0** — `book/vaults/` holds `.gitkeep` only | [measured] |
| Holdout status | **DEFINED, NOT LOCKED. NEVER OPENED. NEVER CONSULTED. No key has been issued** | [measured] |
| Suite | 272 passed / 50 failed / 322, 46 red by design | [cited — dispatch; **not measured by me**, and labelled so] |

> **ON MY OWN HARD RULE, STATED SO IT IS NOT READ AS WAIVED.** *"If N is unknown or unreconstructable,
> the verdict is INSUFFICIENT-DATA. Never PASS."* **N here is known exactly: 0 logged, 7 declared.**
> The rule is **satisfied**, not suspended. It governs a claimed edge, and **there is no performance
> number anywhere in this evaluation** — no Sharpe, no `t`, no DSR, no net return, from any source.
> **No sponsor presented one, so nothing was inadmissible.** A1's harness-artifact requirement
> attaches to a Gate **1** report; this is Gate 0, whose object is a document and a registry state,
> both of which I read directly and report above.

**Context the sponsor should carry into Stage 1, computed here [measured — `castellan.stats.expected_max_sharpe`]:**
at a full Stage 1 spend the registry-enforced `N` is **54**, and **`E[max SR]` on data with zero true
edge is 2.31·σ_SR**. At full Stage 2, `N` = 86 and it is **2.48·σ_SR**. **The family's Gate 1 Sharpe
floor is 1.0. The noise ceiling at its own budget is more than twice that.** This is why §7.3's σ_SR is
a reporting requirement and not a formality.

---

## 10. CONDITIONS, AND WHAT WOULD HAVE TO BE TRUE

### 10.1 Conditions on the seal — four, two already cleared

| | Condition | Status |
|---|---|---|
| **S-1** | **I-181 resolved; `success_criteria` bracket-balanced and hashable** | **CLEARED by §5 of this document** [measured: depth 0, no negative excursion, site count unchanged] |
| **S-2** | **The eight struck `2027-01-31` literals may NOT be removed from `forward_kill_condition` by any seat until E-2's recognizer is case-insensitive** | **STANDING PROHIBITION, in force from this document** (§4; I-204) |
| **S-3** | **C7** — Pod B's written acceptance of KC-002 as sponsor, and the Principal's signature | **OPEN.** Not this seat's |
| **S-4** | **C8** — `open_hypothesis` and `HoldoutVault.seal(cutoff=...)` in the same session and the same UTC calendar day, `forward_window_start` equal to both, passphrase supplied by the Principal at that moment and written nowhere | **OPEN.** Executes at the seal |

**C11 is REMOVED from the seal-blocking set, and the reason is that it could never have cleared.** It
requires ≤2 logged trials; `log_trial` refuses a family that is not registered; registration **is** the
seal. **The condition asks for work whose precondition is the act it blocks.** The registration
payload's own §2.2 already budgets C11's ≤2 trials **inside** the post-seal 47, so §20 and the payload
have disagreed about this since R-004. **Filed I-202.**

**C11 is re-imposed as a class-(b) Gate 1 condition with its three fields named**, per §4.7.2:
**executor** — Validation; **cadence** — once, at the first `evaluate_gate1` call on this family;
**artifact** — the Validation Report must state on its face whether §5.3's `≤ 0.10` is `[assumed]` or
`[measured]`, and if measured, the trial ids of the two calibration trials and that they are trials 1
and 2 of the ledger. **Trial order is in the registry, so this is checkable rather than asserted.**
**Any Gate 1 report quoting F-002's 1.3e-4 joint false-survival rate before that conversion is
quoting an assumed number and must say so.**

**Nothing else is seal-blocking. C2 clears on this document. C1 is discharged. C3 is not a seal
condition and never was.**

### 10.2 C3 — unchanged, unspent, unskippable

**The Devil's Advocate Red-Team Memo does not exist and this verdict does not substitute for it.**
Charter §4.4 requires one at Gate 1 and §6.4 defers a packet without one. **KC-002 is the sponsor's own
kill condition, and a kill condition authored by the sponsor is structurally weaker than one authored
against it** — the sponsor says so itself at §20 C3. **C3 remains submission-gating.**

### 10.3 What would have to be true for this family to pass Gate 1

Not a coaching list — the conditions under which a PASS would be computable at all:

1. **All nine deferred items at §1 resolved**, C5 first, because the Principal's lock makes every
   other answer moot until it is ruled — **and C5 discharges only on a ruling carrying executor,
   cadence and artifact.**
2. **`evaluate_dated_clauses.py` exists and exits 0 on this family** (D-6). As the document stands it
   does not, and E-24 makes that a **permanent INSUFFICIENT-DATA**. **This is currently the family's
   binding constraint and it is document-side, not statistical.**
3. **The embargo defect at leakage check 6 repaired**: `walk_forward_windows` must purge and embargo,
   and `purged_kfold_splits`' 24-bar embargo must not be shorter than the 30-day K1 lookback that
   generates the signal. **As it stands the 1%-embargo criterion cannot PASS.**
4. **Measured `ρ̂ ≤ 0.034`** on net returns. At `0.034 < ρ̂ ≤ 0.15` the pre-committed band is FAIL-on-
   length and PARK; above 0.30 it is KILL. **These bands are the sponsor's own, pre-registered, and I
   will hold it to them.**
5. **A net `t ≥ 3.0` that survives C5's ruling.** If C5 lands on reading (ii), the effective bar is
   **6.0**, and composed with I-050's corrected estimator at the firm's one measured `ρ = 0.83` the
   required uncorrected pre-haircut `t` is **order 20** — the sponsor's own arithmetic, against
   itself. **The sponsor's own pre-registered expectation is PARK-WITH-TRIGGER, not PROCEED, and I
   record that I find that expectation credible.**
6. **The breakeven round-trip cost at which `t` falls below 3.0, reported** — which the family cannot
   currently afford to compute (D-5).
7. **A Red-Team Memo with a kill condition authored against the family** (C3).

**Baselines I will hold the sponsor to at Gate 1, stated now.** Perpetual carry is published; the
**50% haircut** applies and the sponsor has accepted it in full. The base case is **88% erosion**
[cited — Chen & Velikov, *JFQA*] and **~26% out-of-sample / ~58% post-publication decay** [cited —
McLean & Pontiff 2016]. **This family's thesis does not require that this time is different** — it
concedes the unconditioned carry is factor P&L the firm does not pay for and claims only conditioning
alpha to `R_bench`. **That is the correct framing and it is the reason this document is admitted.**

---

## 11. ISSUES FILED — I-200 THROUGH I-209

| # | Finding | Sev | Owner |
|---|---|---|---|
| **I-200** | **§10.4's 0.43-year margin is arithmetic on a rounded input, and the document disagrees with itself.** `6.571 − 6.14 = 0.431` propagated to seven sites while §10.4.2 carries the correct **0.435**. Measured: `MinBTL(86,1.0) = 6.135900`, margin **0.4351** at the sealed span and **0.4734** at the settled span. **S3-D-019's and the dispatch's 0.469 inherits the same rounding.** Direction is against the family | **MEDIUM** | quant-validation (values supplied here) → director-of-research |
| **I-201** | **The dated-site count moved 65 → 68 between S3-D-016 and S3-D-019.** A dispatch ordered to record a measurement wrote three new dated sites into the two fields a prior dispatch had just cleaned. Ledger reconciled to the site: `92 − 27 + 3 = 68`, `universe` +2 / `success_criteria` +1. **I-178 measured a second time** | **MEDIUM** | quant-validation → director-of-research |
| **I-202** | **C11 could never have cleared as a seal condition.** It requires ≤2 logged trials; `log_trial` refuses an unregistered family; registration is the seal. §20 has contradicted the registration payload's §2.2 — which budgets C11 inside the post-seal 47 — since R-004. **Reclassified to class (b) at Gate 1 by §10.1** | **MEDIUM** | quant-validation |
| **I-203** | **I-181's near-miss, recorded.** Closing the marker at the field's end rather than at the marker's would have placed §10.4's sealed ceiling function, §10.8's verdict bands, the mandatory disclosure lines and both harness leakage defects inside a revision marker — **and therefore eligible for relocation out of the hashed field under S3-D-016's rule.** Guardrail 1's STOP prevented it | **MEDIUM** (records a HIGH near-miss) | quant-validation |
| **I-204** | **The struck `2027-01-31` literals are load-bearing as a control and may not be removed.** E-14's `DIVERGENT` on `forward_kill_condition` fires only because they are present; strip them and clause 5 becomes a bare `C` firing on the seal day. **Standing prohibition in force; E-2's recognizer ruled case-insensitive on the unit, spec amendment unfunded** | **HIGH** | quant-validation |
| **I-205** | **The deferred set enumerates to NINE; the CIO's table named four and the Principal's ruling five.** A cardinal stated from a table rather than from an enumeration, for the seventh time in three sprints — **in the dispatch that ordered the enumeration precisely to prevent it** | **MEDIUM** | quant-validation → CIO |
| **I-206** | **Gate 0 criteria (6) and (7) can never be PASS at a Gate 0 evaluation.** Registration **is** the seal and the vault seal is bound to the same UTC day, so both are satisfied by the act the verdict authorizes. `VALIDATION-GATE0-001` did not name it. **Remedy: §4.3(6)–(7) should read "instrumented and executable", or Gate 0's output should be defined as authorizing the opening** | **LOW-MEDIUM** | quant-validation → Principal (Charter clarification) |
| **I-207** | **Two literals will freeze stale under P7 and are accepted rather than missed.** The integer **109** (five sites, incl. §10.4.3's mandatory render string and §18's family-exit trigger) is `max_admissible_trials(6.571,…)` and is **112** at the settled span; **0.034** (§10.4.2, `success_criteria`) is **0.0371**. **Both stale in the conservative direction, therefore admissible sealed** | **LOW-MEDIUM** | director-of-research |
| **I-208** | **`success_criteria` is 42,056 characters verbatim / 26,479 dedented — a 15,577-character gap between the two canonicalizations — carrying 14 dated sites and a nested revision history inside one hashed string.** I-170's offset problem is a symptom of the field's size. **A binding field this long is not auditable by the seat required to audit it.** Remedy: a length ceiling on binding prose fields | **MEDIUM** | director-of-research → quant-validation |
| **I-209** | **`book/registry.db` events 2 and 3 (`data_restatement`, I-190) carry `family = NULL`** [measured]. A4's auto-log fired correctly at zero blast radius, but **no `family_stats` call, chain walk or Gate report will ever surface them to the family whose primary universe they restated.** The restatement is discoverable only by reading the events table by hand | **MEDIUM** | quant-validation → head-of-data-infra |

---

## 12. TO THE PRINCIPAL

**Four items, and only the first two need an act.**

1. **C5, part 2, is yours and nothing moves without it.** Your own lock is correct and it is now the
   family's binding constraint alongside the dated-clause exit. **I decline to rule part 1 in
   isolation**, because a point of application without your ratification and without an executor is a
   class-(c) no-op that would look like progress. **The gap is 2× at `t` — 3.0 against an effective
   6.0 — and it is either a real hurdle or nothing.**

2. **I-206 asks for one sentence of Charter clarification.** Gate 0's criteria (6) and (7) cannot be
   satisfied before the verdict that authorizes them. I have recorded them as **PENDING BY
   CONSTRUCTION**; if you prefer different wording, that is a §4.3 amendment and it is yours.

3. **On C13(k), I concur with your ratification and my ground is different from yours**, which is the
   point of the seat. Yours is the field's own pre-existing declaration. Mine is that requiring the
   drafted literal would move KC-002's 30-conditioning-day threshold by **9.4%** as a function of how
   long the seal took — **a §4 reserved act arriving by scheduling accident.** Both grounds hold; on
   mine, refusing the conformance was the *permissive* choice.

4. **I edited one character of a hashed field and I want you to see it plainly.** §5 records the
   before and after, the convention that determined the boundary, and the measurement showing the
   extraction is byte-for-byte unchanged. **I made it rather than routing it back because the sponsor
   should not close a bracket around its own criteria, and because the alternative you offered — the
   field does not seal — costs the firm a dispatch it does not have to buy nothing.**

**Registry read 0 hypotheses / 0 trials on opening and reads 0 hypotheses / 0 trials on closing.
No hypothesis opened. No trial run. No vault sealed. No registry write. No commit. `harness/` and
`book/` untouched by this seat. `research/REGISTRATION-PAYLOAD-*` untouched. The one edit to
`research/PREREG-002-crypto-funding-basis.md` is the single character disclosed at §5.**

> **ONE PROVENANCE NOTE, MEASURED, BECAUSE IT SHARPENS I-209.** `book/registry.db` shows dirty in
> `git status`. **It is not mine** — all three of my reads used `mode=ro` URI handles. `HEAD` carries
> **1 event** (`book_open`); the working copy carries **3**, the two extra being S3-D-019's
> `data_restatement` rows auto-logged by `PITStore.ingest` earlier today [measured — `git show
> HEAD:book/registry.db` compared against the working copy, this session]. **Under A3 the git
> repository is the book of record, and the book of record therefore does not yet contain the A4
> restatement events at all.** They are `family = NULL`, uncommitted, and discoverable only by hand.
> **I-209's severity rests on both facts, not just the first.**

---

*Head of Quantitative Validation · Castellan Capital · 2026-08-12 · dispatch S3-D-022*
*Reports to the Principal. This verdict is final short of a written Principal override.*
