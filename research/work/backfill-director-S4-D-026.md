## I-290 · 2026-09-10 · The one-day carry budget on the suppression band's right-hand side is an undeclared convention, not a derivation · Severity: MEDIUM · Owner: director-of-research

**BACK-FILLED 2026-09-15** under the Principal's Option-B ruling on I-370. The finding was made and described at `research/DIR-RESTATE-001-prereg002-mechanism.md:2511-2517` (§16.7(a)) on 2026-09-10, during revision R-010 (dispatch S4-D-011); the log entry was never written. **Authored from the artifact, not from the citation** (§7.12).

While deriving `band` for revision R-010, this seat named — rather than re-derived — one term on the right-hand side of the governing inequality. *Why* one day of carry is the correct allowance for the smallest authorized rebalance is a **declared conservatism**, not something the artifact derives [measured, this seat's own §16.7 text: "Two terms in §16.4 are not derived, and this seat names them rather than presenting the inequality as fully determinate"]. Its direction runs in the family's favour: a two-day budget gives `band ≤ 1.083` — a wider band and a wider suppression window than the sealed `band = 0.54`. The one-day horizon was retained byte-identical because the governing ruling scoped the *charge*, not the horizon, and moving a binding literal's derivation on an unruled axis inside a scoped dispatch is what this seat's artifact calls the SO-003 §3.1 violation. Quoted from the artifact: *"Named, not repaired: filed I-290."*

**Resolution:** open — disclosed as a convention running in the family's favour; not used; a future ruling on it moves `band` again, pre-seal, per the registration payload's own standing instruction (payload §3.5).
**Pattern tag:** `undeclared-convention-in-familys-favour` · `unruled-axis-inside-a-scoped-dispatch`

---

## I-291 · 2026-09-10 · The impact term priced in the cost preset is omitted from the sealed carry-band figure, and the omission cannot be priced pre-seal · Severity: LOW · Owner: director-of-research

**BACK-FILLED 2026-09-15** under the Principal's Option-B ruling on I-370. The finding was made and described at `research/DIR-RESTATE-001-prereg002-mechanism.md:2519-2524` (§16.7(b)) on 2026-09-10, during revision R-010 (dispatch S4-D-011); the log entry was never written. **Authored from the artifact, not from the citation** (§7.12).

The second undeclared term named alongside I-290: `Y · σ · √(Q/ADV)` is present in the cost preset but is **not** in the sealed 6.0 bp figure, because pricing it requires a measured `σ` and a measured ADV inside a binding literal — exactly what I-223 objects to [this seat's own text]. Its direction also runs in the family's favour: including it would *raise* the charge and *narrow* the suppression window, so omitting it is the **against-family** choice and needs no relief; including it would need a measurement this dispatch forbids. Quoted: *"Filed I-291."*

**Resolution:** open — disclosed, against-family, unpriceable pre-seal; not used; a future ruling on it moves `band` again, pre-seal.
**Pattern tag:** `undeclared-convention-in-familys-favour` · `unpriceable-pre-seal`

---

## I-292 · 2026-09-10 · R-009 selected a cost convention the sanctioned engine contradicts in source, and the check that would have caught it was never run before the choice · Severity: MEDIUM · Owner: director-of-research

**BACK-FILLED 2026-09-15** under the Principal's Option-B ruling on I-370. The finding was made and described at `research/DIR-RESTATE-001-prereg002-mechanism.md:2546-2549` (§16.9) on 2026-09-10, during revision R-010 (dispatch S4-D-011); the log entry was never written. **Authored from the artifact, not from the citation** (§7.12).

R-009 had selected a 12 bp round-trip cost convention for the carry-band derivation as the "friendlier" reading and escalated on it. R-010 measured what the harness actually charges [measured — `engine.py:141-143`, `:197-198`, cited in the artifact: "the engine charges exactly one per-side price per unit of `|Δw|`, once, at the bar the weight changes"] and found the round-trip reading is a cost `run_backtest` will never apply, and is additionally not conservative-but-defensible: as a per-rebalance charge it counts every side twice, since the return leg of any increment is itself a band rebalance carrying its own charge, and on a monotone same-direction path there is no reversal at all. This seat's own words: *"the check that settles it was a two-line read of `engine.py` that this seat did not perform before choosing. The cheapest test of a cost convention is to read what the engine charges."* R-009's stated reason is withdrawn by this seat, not overruled by the Principal.

**Resolution:** closed — resolved by R-010's derivation (`band` moved from the R-009 convention to the engine-consistent figure); the convention error itself is not repaired retroactively, it is corrected going forward.
**Pattern tag:** `friendlier-reading-not-checked-against-source` · `cheapest-test-skipped-before-choosing`

---

## I-293 · 2026-09-10 · §20's `Blocking?` cell for C12 read BLOCKING ON SEALING for twenty days after the note beneath the table had already recorded it DISCHARGED · Severity: HIGH · Owner: director-of-research

**BACK-FILLED 2026-09-15** under the Principal's Option-B ruling on I-370. The finding was made and described at `research/DIR-RESTATE-001-prereg002-mechanism.md:2549-2552` (§16.9) on 2026-09-10, during revision R-010 (dispatch S4-D-011); the log entry was never written. **Authored from the artifact, not from the citation** (§7.12).

While conforming §20's `Blocking?` column against a ruling-supplied list naming C2, C3 and C11, this seat found a fourth cell in disagreement that the list never named: **C12's `Blocking?` cell had read `BLOCKING ON SEALING` since R5**, while the note directly beneath the same table had read `DISCHARGED` since R12 — twenty days, one 590-line Gate 0 verdict, a Red-Team memo, a withdrawal and four revisions apart. This seat's own words: *"a table asserting a seal blocker the document itself closed twenty days earlier, found only because §20 was read column-by-column rather than against a supplied list."* The transferable rule this seat records: *"when a ruling supplies the list of artifacts it touches, the executing seat still reads the table's own columns, because the list is evidence about the rulings and not about the table."* C12 was conformed to `DISCHARGED (NARROWLY)` on the face of R-010, verified by re-running the extractor: all sixteen hashed fields unchanged from the post-I-363 baseline, because §20 sits outside §21's fenced block.

**Resolution:** closed — the §20 cell was conformed on the face of revision R-010, verified against the extractor.
**Pattern tag:** `ruling-never-reached-the-artifact` · `list-is-evidence-about-rulings-not-about-the-table`

---

## I-296 · 2026-09-10 · The R-010 addendum ran 73% over its line-budget projection, and its own mid-task flag understated the overrun because it was estimated rather than measured · Severity: LOW · Owner: director-of-research

**BACK-FILLED 2026-09-15** under the Principal's Option-B ruling on I-370. The finding was made and described at `research/DIR-RESTATE-001-prereg002-mechanism.md:2565-2567` (§16.9) on 2026-09-10, during revision R-010 (dispatch S4-D-011); the log entry was never written. **Authored from the artifact, not from the citation** (§7.12).

This seat's own line-budget accounting for the R-010 addendum: *"this addendum authored 381 lines against a ~220 projection, 73% over, and its own mid-task budget flag understated the overrun as ~32% because it was estimated rather than measured; corrected on the face of R-010"* [measured]. The overrun figure was corrected once a real diff was taken rather than left standing on the earlier estimate.

**Divergence flagged, not resolved (§7.12):** `PREREG-002:115`, inside the frozen R-010 revision block, gives different figures for what appears to be the same overrun measurement — total authored lines across `DIR-RESTATE` §16 (219) + `PREREG-002` (158) + payload (18) = **395**, stated as **80%** over the ~220 projection, with the mid-task estimate quoted as "~290, over by ~32%." Neither the 395-line total nor the 80% figure matches this seat's own 381-line / 73% figure at the cited artifact site, and it is not evident from either document alone whether "this addendum" in the artifact means the addendum's own line count versus the payload's three-file total. `PREREG-002` is P7-frozen and cannot be corrected; this entry is authored from the artifact per §7.12, and the disagreement between the two is recorded here rather than smoothed over.

**Resolution:** closed — flagged on the face of R-010 in the artifact itself; the CIO's estimation habit named as the recurring defect (repeated one revision later at I-345).
**Pattern tag:** `estimate-in-a-slot-that-calls-for-a-measurement` · `frozen-citation-disagrees-with-its-own-artifact`

---

## I-340 · 2026-09-14 · Three prior statements of the holdout-vault count disagreed with each other and with the lookup's own semantics; the correct count is four, and the rule was in the document the whole time · Severity: HIGH · Owner: director-of-research

**BACK-FILLED 2026-09-15** under the Principal's Option-B ruling on I-370. The finding was made and described at `research/DIR-RESTATE-001-prereg002-mechanism.md:2697-2699` (§17.8) on 2026-09-14, during revision R-011 (dispatch S4-D-016); the log entry was never written. **Authored from the artifact, not from the citation** (§7.12).

`HoldoutVault.seal()` and `PITStore.set_holdout_ceiling()` each bind exactly one `(source, dataset_id)` pair — an exact-match lookup with no wildcard [measured — `data.py:204`, `:271`]. The primary universe holds four such pairs, measured by a read-only `GROUP BY` against `book/pit.db`. Three prior statements of this one cardinal quantity existed and no two agreed: this seat's own words, *"the vault count: three prior statements of one cardinal quantity — §21's comment said two, the payload's item 6 said one, the CIO's report said two by reading the comment rather than the lookup semantics — and no two agreed; the correct rule was in §11.1 the whole time, making this a conformance failure rather than an analysis failure."* Sealing on any of the wrong counts would not have failed loudly — a `dataset_id` that does not exactly match a future `ingest()` call seals successfully and never binds, leaving three of four legs with no holdout ceiling while the record reports clean.

**Resolution:** closed — repaired pre-seal at revision R-011: the vault block rewritten to four explicit `seal()` calls, one per pair, §20's C8 row and §11.1's sequencing row conformed with it.
**Pattern tag:** `three-statements-of-one-cardinal-none-agreed` · `control-reports-clean-while-protecting-nothing` · `conformance-failure-not-analysis-failure`

---

## I-341 · 2026-09-14 · `instrument_identity` named all four universe symbols on a vault that binds exactly one pair, and the narrowing was authored rather than transcribed from measurement · Severity: MEDIUM · Owner: director-of-research

**BACK-FILLED 2026-09-15** under the Principal's Option-B ruling on I-370. The finding was made and described at `research/DIR-RESTATE-001-prereg002-mechanism.md:2652-2662` (§17.5) on 2026-09-14, during revision R-011 (dispatch S4-D-016); the log entry was never written. **Authored from the artifact, not from the citation** (§7.12).

`DATA-IMPL-012` §1 supplies three of the values transcribed into each vault's seal call; `instrument_identity` is not one of them. The prior single string named all four universe symbols on a vault that binds one pair — the same cardinality defect as I-340, in the adjacent field, four times over, inside a hashed spec. This seat's own words: *"The narrowing is a decomposition of the document's own existing string, and each vault's field list matches that vault's measured `columns` from `DATA-IMPL-012` §1. It is nonetheless authored rather than transcribed, and is labelled [inferred] rather than [measured] so no future reader mistakes it for Seat 9's measurement."* Ruling 001 §3.4 makes the field binding — a change to it retires the vault — so the error was not cosmetic and had to be fixed pre-seal or not at all.

**Resolution:** closed — narrowed per vault at revision R-011, labelled [inferred]; covered by `harness/tests/test_vault_seal_script.py::test_instrument_identity_is_narrowed_to_one_pair_per_vault`.
**Pattern tag:** `authored-not-transcribed-labelled-as-such` · `same-cardinality-defect-adjacent-field`

---

## I-345 · 2026-09-14 · The R-011 line-budget flag was first drafted from estimated figures in the slot reserved for a measurement, repeating the R-010/I-296 defect one revision later · Severity: LOW · Owner: director-of-research

**BACK-FILLED 2026-09-15** under the Principal's Option-B ruling on I-370. The finding was made and described at `research/DIR-RESTATE-001-prereg002-mechanism.md:2712-2715` (§17.8) on 2026-09-14, during revision R-011 (dispatch S4-D-016); the log entry was never written. **Authored from the artifact, not from the citation** (§7.12).

This seat's own words: *"R-011's line-budget flag was first drafted with estimated figures in the slot §7.12 reserves for a measurement, and the estimate for this section was 42% of its measured length — R-010's I-296 defect repeated one revision after it was filed. Corrected against `git diff --numstat` on the face of R-011"* [measured]. The corrected, measured figures given elsewhere in the R-011 revision block: `PREREG-002` 153 lines, `DIR-RESTATE` §17 151, payload 25, total 329 — 65% over the ~200 projection, with the §17 portion alone having been estimated at only 42% of its true measured length before the diff was taken.

**Resolution:** closed — corrected on the face of R-011 against a real `git diff --numstat`, with the overrun located and attributed to specific subsections rather than defended in aggregate.
**Pattern tag:** `estimate-in-a-slot-that-calls-for-a-measurement` · `same-defect-repeated-one-revision-later`
