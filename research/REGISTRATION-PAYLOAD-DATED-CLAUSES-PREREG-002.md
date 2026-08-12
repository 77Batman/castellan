# REGISTRATION PAYLOAD — `dated_clauses` for `funding-carry-conditioning-002`

**The rows to be written to `VALIDATION-SPEC-004` E-5's `dated_clauses` table, produced as a payload
because prose is not registration.**

**Seat:** Director of Research (Seat 2) · **Date:** 2026-08-12 · **Dispatch:** S3-D-014, Task 2
**Discharges:** nothing. **Answers:** **I-164** (19 of 24 land `UNCOVERED`; the remedy is registration)
**Subject family:** `funding-carry-conditioning-002` · **Source of field text:** `PREREG-002` §21 at R-007
**Governing specification:** `research/VALIDATION-SPEC-004-harness-self-defence.md` §5–§8, E-1 … E-25
**Sweep this answers:** `DIR-RESTATE-001` §12.5, D-1 … D-24

> **THIS FILE WRITES NOTHING.** `dated_clauses` does not exist — `VALIDATION-SPEC-004`'s tests are red
> and Seat 9 has not implemented it. **This seat cannot write rows and does not.** It produces the rows
> to be written, in the same form and for the same reason as `REGISTRATION-PAYLOAD-PREREG-002.md`.
> `book/registry.db` reads **0 hypotheses / 0 trials** and must still read 0 / 0 when this is put down.

---

## 1. THE HEADLINE, BEFORE THE TABLES

**The register covers 10 of the 24 swept clauses. Fourteen are uncoverable and §5 names each and why.**

**And the 24 is the wrong denominator, which is the larger finding.** E-2 extracts **by literal form,
never by meaning**, over E-1's nine enumerated registry fields. Run against `PREREG-002` §21's actual
field text it yields **90 sites**, not 24 [measured — `research/work/extract_dated_sites.py`,
`research/work/dated_sites.txt`]. E-6 requires **every extracted site** to be claimed by exactly one
row or the run exits 4. **The coverage obligation is 90 rows, and 72 of them are for dates that are
not clauses at all** — revision stamps, satisfaction dates, commit dates, historical market facts.

**Three consequences follow, and the third is the one that matters:**

1. **`kind` has no member for 72 of the 90.** The closed vocabulary is `OBSERVATION | DEADLINE |
   PRECEDENT`. None describes *"R19 was written on 2026-08-10."* This is **I-166's first real hit**,
   arriving exactly as I-166 predicted — mid-task, with a deadline, and the cheap local action is to
   add one string. **This seat does not propose adding one. It proposes the document stop putting
   revision provenance inside hashed binding fields.**
2. **75 of the 90 sites FIRE on the first invocation.** E-10 row 4: `discharge_event_kind == ''` and
   `resolved_date ≤ T` ⇒ `FIRED`, unconditionally. 59 ISO sites carry past dates; 16 `FORMULA` sites
   resolve to bare `C`, which is the seal day and therefore `≤ T` at every later instant. **Nothing
   discharges a revision stamp, because there is no event that could.**
3. **Therefore `evaluate_gate1` returns `INSUFFICIENT-DATA` permanently.** E-24: a nonzero exit makes
   the Gate verdict INSUFFICIENT-DATA. Exit is the max over sites: `FIRED` (2), `DIVERGENT` (3) via
   E-14, and 4 if any site goes unclaimed. **This family cannot pass Gate 1 while its sealed prose
   fields carry their own revision history.** That is a document-side defect, it is this seat's, and
   the remedy is large: strip the revision apparatus out of six prose fields **before** the seal, and
   carry provenance in `model_prior_provenance` and in the document, which are where it belongs.

**All three are `[measured]` on already-extracted counts. No market data was touched and no trial ran.**

> ### **AND THE ROSTER IS ALREADY ONE REVISION STALE, WHICH IS THE POINT MADE AGAINST ITSELF.**
>
> §5's 90 rows are measured against **§21 as at R-006**. **R-007's own R38 insert — the Principal's
> ratification of I-153, which this dispatch was ordered to record in-field — adds 2 sites to
> `forward_kill_condition`** (one `ISO 2027-01-31`, one `FORMULA C + 187 days`), taking the obligation
> to **92** [measured, both canonicalizations]. **The register enumerates 90 of 92 and this seat states
> the gap rather than silently regenerating**, because the shape of the defect is more informative than
> a fixed number: **every conforming insert into a binding prose field creates new clause rows to
> write, and the register can never be finished while the field carries commentary.** Filed **I-178**.
> **This is §4.3 demonstrated on the document by the act of recording a Principal ruling in it.**

---

## 2. THE ANCHOR, AND THE ONE THING THIS PAYLOAD CANNOT PUT AN INTEGER IN

**Anchor `C`** (E-4): `forward_window_start`, which `REGISTRATION-PAYLOAD-PREREG-002` §2.5 fixes as
`datetime.now(timezone.utc).date().isoformat()` at the instant of the call. **`C` is read, never
inferred** — this family supplies it, so the family is not `UNANCHORED`.

> ### **`source_offset` CANNOT BE FIXED IN ADVANCE, AND THE REASON IS A GAP, NOT A DIFFICULTY.**
>
> E-5 requires an integer `source_offset` and E-6 matches on `(field, source_offset)` exactly.
> **Nothing in the firm's documents defines the canonical string of a prose field.**
> `REGISTRATION-PAYLOAD-PREREG-002` §3 says only *"the text between `<field_name> = "` and its closing
> `"`"* in §21's fenced block. Read literally that includes the 37-column alignment indent on every
> continuation line; read as anyone intends, it does not. **Offsets differ between the two readings at
> 88 of the 90 sites** [measured]. A register that guesses wrong puts 88 rows at `DANGLING` and 88
> sites at `UNCOVERED` — **exit 4, from a whitespace convention.**
>
> **So this payload names a canonicalization-invariant identity — `(field, recognizer, matched_text,
> occurrence_ordinal)` — and both candidate offsets, and ships a generator.** The ordinals are stable
> across both readings [measured, asserted in `research/work/build_register.py`]. The integer is
> emitted by the generator against whatever string `open_hypothesis` actually receives.
> **The canonicalization itself is Validation's to fix and is filed as I-170.**

**One row's offset is unknowable even then.** `forward_window_start`'s value *is* the seal date, so its
single `ISO` site does not exist until the instant of the act. Its row is `(field=forward_window_start,
offset=0, date_expr="C")`, and `resolve("C") == parse(matched_text)` by construction, so it cannot
diverge. **E-8's `ANCHOR-STALE` — the spec's named D-8 case — therefore has nothing to bite on in this
family**, because the payload computes the anchor rather than carrying a literal. Filed **I-174**.

---

## 3. THE 24 SWEPT CLAUSES, MAPPED TO REGISTRY SITES

*Column 5 is the register's verdict on the clause, not the evaluator's verdict on a site.*
***"Registrable"* means only that an extracted site exists in an E-1 field that carries the clause.**
It does **not** mean a row can be completed: §5 marks 72 of the 90 rows `—/BLOCKED` for want of a `kind`
value, and some registrable clauses — D-23 above all — are historical facts used as rationale rather
than clauses that fire. **The two columns are answering different questions and are not in conflict.**

| # | Site in the sweep | Date expression | Anchor | What fires | Premise true today? | Registrable? |
|---|---|---|---|---|---|---|
| D-1 | §14 condition precedent (prose) | `2026-08-11` | — | family → ADMITTED-AS-EXPLORATORY | **FALSE** — struck R-005, C1 discharged R-006 | **NO** — prose only; struck in-field at R29(b) |
| D-2 | `forward_kill_condition`, same clause in-field | `2026-08-11` | — | same, on the sealed string | **FALSE** — struck at R29(b) | **RESIDUE ONLY** — rows 77, 78 claim the strike record, not a live clause |
| D-3 | §14 observation date | `2027-01-31` | — | the whole of KC-002 | **FALSE** — conformed to `C + 187 days` at R32(b) | **NO** — prose only |
| D-4 | `forward_kill_condition` opening | **`C + 187 days`** | `C` | the whole of KC-002 | **TRUE** | **YES** — row 50 |
| D-5 | `forward_kill_condition`, computation window | `[C, C + 187 days]` | `C` | the computation's window | **TRUE** — conformed R32 | **YES** — rows 55, 56; row 58 is the struck literal |
| D-6 | `forward_kill_condition`, anti-reinterpretation cl. 3 | **`C + 187 days`** | `C` | successor-family boundary | **TRUE** — conformed R32 | **YES** — row 61; row 63 the struck literal |
| D-7 | `forward_kill_condition`, **clause 5, SILENCE IS A KILL** | **`C + 187 days`** | `C` | **AUTOMATIC TERMINATION** | **TRUE** — conformed R32, ratified §4 | **YES — rows 74, 76.** See §4.1: it extracts as bare `C` |
| D-8 | §11.4 R3 `forward_window_start` | `C` | `C` | the forward window's start | **TRUE** — conformed R33 | **YES, in its registry incarnation only** — the §11.4 prose copy is outside E-1 (E-25(3)) |
| D-9 | §11.4 R3 `forward_kill_condition` row | `C + 187 days` | `C` | restates D-3 | **TRUE** — conformed R33 | **NO** — prose only; the field carries D-4 |
| D-10 | `success_criteria`, KC-002 survival | **`C + 187 days`** | `C` | the success criterion's date | **TRUE** — conformed | **YES** — row 32 |
| D-11 | §10.5.2 Stage 2 `N_forward` | `2027-01-31` | — | the forward budget's span | **FALSE** | **NO** — §10.5.2 is not in any E-1 field |
| D-12 | §10.5.3 line item | `2027-01-31` | — | same | **FALSE** | **NO** — same |
| D-13 | §15 step 8 | `C + 187 days` | `C` | forward generation | **TRUE** | **NO** — §15 is not in any E-1 field |
| D-14 | §20.1 realistic seal date | `2026-08-11` | — | a dated commitment | **FALSE** — struck R36 | **NO** — prose only |
| D-15 | §11.3 earliest Gate 1, reading 1 | `C + 12 months` | `C` | Gate 1 schedule | **TRUE** — re-expressed R34 | **NO** — §11.3 is not in any E-1 field |
| D-16 | §11.3 reading 2 | `C + 4 years` | `C` | same | **TRUE** — re-expressed R34 | **NO** — same |
| D-17 | §11.3 reading 3 | `C + ~2.19 years` | `C` | same | **TRUE** — re-expressed R34 | **NO** — same |
| D-18 | §16, §17 rank 9, §22 row 6 | same three | `C` | same | **TRUE** — re-expressed R34 | **NO** — three further prose copies |
| D-19 | §11.1 in-sample span, **6.571 y** | `[2020-01-01, C]` | `C` | **MinBTL, DSR, the length criterion** | **TRUE as measured; R34's "understatement" label is STRUCK at R37 — see §4.2** | **PARTIAL** — rows 10, 11 claim the `universe` copy; **no `SPAN` site exists, so E-9 and E-21 never run** |
| D-20 | §11.1 ingest ceiling | `2026-07-28` | — | the `PITStore` ingest bound | **TRUE** — written formula-safe | **NO** — §11.1 is not in any E-1 field |
| D-21 | §7.1.1, K7's in-sample trigger | `2025-09-18` | — | K7's declaration + a 30-day `INSUFFICIENT-DATA` state | **TRUE** [cited — official] | **YES** — rows 19, 20 |
| D-22 | §14.1's quoted C-001 sentence | `2026-11-01` | — | nothing here | **n/a** — a quotation about KC-001 | **NO** — `2026-11-01` is absent from every E-1 field [measured] |
| D-23 | §6.1 / §9.1, SOL's structural break | `2022-11-09` | — | K4 / R3's universe decision | **TRUE** [measured] | **YES** — rows 13, 26, 28 |
| D-24 | §20 C8, *"same session, same UTC day"* | relative — **no date expression** | — | P7 | **TRUE** | **NO** — E-2 extracts nothing from a relative phrase; P7 evaluates it in code |

### **COVERAGE: 10 of 24.**

**Fully covered — 7:** D-4 · D-5 · D-6 · D-7 · D-10 · D-21 · D-23.
**Covered as residue only — 1:** D-2 (the clause is struck; the rows claim the strike record).
**Covered but with the governing mechanism absent — 2:** D-19 (no `SPAN` site ⇒ E-9/E-21 dead),
D-8 (in-field, but E-8 cannot fire because the anchor is computed, not carried).
**Uncoverable — 14:** D-1 · D-3 · D-9 · D-11 · D-12 · D-13 · D-14 · D-15 · D-16 · D-17 · D-18 · D-20 ·
D-22 · D-24.

**Thirteen of the fourteen are uncoverable for one reason: the clause lives in document prose that no
registry field carries.** That is **E-25(3)'s named gap**, stated by Validation in advance —
*"the remedy is that clauses must be registered, not that the checker must learn to read documents."*
**This seat agrees and states the cost: the remedy for those thirteen is not a row, it is moving the
clause into a binding field or striking it.** The fourteenth, D-24, is uncoverable because it has no
date expression at all and is already class (a) under P7 — **that one is fine and needs nothing.**

---

## 4. THE THREE FINDINGS THE MAPPING PRODUCED

### 4.1 · **Clause 5 — the clause that terminates the family — extracts as a bare `C`.** *(I-171, HIGH)*

E-2's `FORMULA` pattern is `\bC\s*(?:[+-]\s*\d+\s*(?:day|month|year)s?)?\b` and is **case-sensitive as
specified**. Clause 5 as conformed at R32 reads *"on THE OBSERVATION DATE **C + 187 DAYS**"* — the unit
in capitals, because this document's emphasis convention is ALL CAPS. `DAYS` does not match `days?`,
the optional group fails, and the recognizer matches **bare `C`** at offset 7341. The same happens at
offset 6089 [both measured].

**Consequence.** The site's `matched_text` is `C`, resolving to the seal day; the clause row's
`date_expr` is `C + 187 days`, resolving 187 days later. E-12's divergence test fires only when
`matched_text` is an `ISO` literal, so it does **not** catch this. **E-14 does** — the field holds both
a `FORMULA` site and an `ISO` site (`2027-01-31`, offset 7381) whose resolved dates differ — so
`forward_kill_condition` returns `DIVERGENT` at both offsets and exits 3. **The control holds, by a
different clause than the one aimed at it, and only because the struck literal is still in the field.**

**Strip the struck literals from the field and E-14 has no `ISO` partner left, at which point clause 5
— the automatic-termination clause — is a bare `C` that resolves to the seal day and fires
immediately as `FIRED`.** The document is currently protected by its own uncorrected text. **That is
not a control.** Routed to Validation: the recognizer should be case-insensitive on the unit, or the
document must never capitalise a unit inside a binding field. **Neither is this seat's to decide.**

### 4.2 · **§11.1's span has no `SPAN` site, so E-21's proof case does not fire on the family it was written for.** *(I-172, HIGH)*

E-2's `SPAN` recognizer requires a **bracketed** interval in the same sentence as a quantity. The
in-sample span appears in a registry field exactly once, in `universe`:

> *"common span **2020-01-01 to C = 6.571 years**, zero gaps [measured]"*

**Unbracketed.** It extracts as two ordinary sites — `ISO 2020-01-01` and `FORMULA C` — and E-9's
recomputation never runs. The one bracketed interval that *is* in a registry field, `[2020-01-01, C]`
in `falsifier` at offset 137, sits in a sentence carrying no quantity, so it is not a `SPAN` site
either. **Across all nine E-1 fields there are zero `SPAN` sites** [measured].

**E-21 names §11.1's span as its required proof case and the whole of §7's direction-blindness
apparatus is built around it.** The apparatus is sound; **it has no site to act on in this family**,
because the stale figure lives in §11.1 — document prose — and its in-field twin is written without
brackets. **The remedy is one character-level document edit, not a spec change**, and it is this
seat's: `universe` should read `[2020-01-01, C] = 6.571 years`. **This pass does not make that edit,
because it changes a hashed binding-field string on a reading of a specification whose tests are red,
and the sponsor editing its own sealed text to satisfy a checker is the shape of act R32 was disclosed
at maximum volume for.** Put to C2.

### 4.3 · **Registering the document as it stands produces a permanent nonzero exit.** *(I-173, HIGH)*

75 of 90 sites `FIRED` on the first invocation; `DIVERGENT` at two more via E-14; `kind` unavailable
for 72. **The evaluator is correct and the document is wrong.** The remedy is document-side and this
seat owns it: **binding prose fields must carry the clause and not its editorial history.** Sizing it
honestly — six prose fields, roughly 35 revision-stamp insertions, every one of them currently inside
`prereg_sha256`'s domain — **this is a revision, not a conformance insert, and it is not funded in
this dispatch.** Named and left open rather than started.

---

## 5. THE ROWS

**Identity is `(field, recognizer, matched_text, ordinal)`. `off-D` is the dedented canonicalization,
`off-V` the verbatim; §2 records that the choice is Validation's and that 88 of 90 differ.**

**`kind` and `date_expr` are given for the 18 clause-bearing rows only.** The remaining 72 are marked
`—/BLOCKED`: they require a `kind` value that does not exist, and writing one of the three that do
exist would be a mislabel. **The count of 18 is `[inferred]` under a stated rule** — a site is
clause-bearing iff its sentence states something that happens or is required on or after its date —
**not `[measured]`, and this seat labels it so.**

| # | field | rec | matched_text | ord | off-D | off-V | tag | kind | date_expr |
|---:|---|---|---|---:|---:|---:|---|---|---|
| 1 | `statement` | ISO | `2020-01-01` | 1 | 483 | 742 | **IS-START** | **PRECEDENT** | `2020-01-01` |
| 2 | `statement` | FORMULA | `C` | 1 | 497 | 756 | **IS-END** | **PRECEDENT** | `C` |
| 3 | `mechanism` | ISO | `2026-08-04` | 1 | 904 | 1422 | PROV-MECH-1 | **—/BLOCKED** | `2026-08-04` |
| 4 | `mechanism` | ISO | `2026-08-04` | 2 | 3193 | 5006 | PROV-MECH-2 | **—/BLOCKED** | `2026-08-04` |
| 5 | `falsifier` | ISO | `2020-01-01` | 1 | 137 | 211 | **F002-IS-START** | **PRECEDENT** | `2020-01-01` |
| 6 | `falsifier` | FORMULA | `C` | 1 | 149 | 223 | **F002-IS-END** | **PRECEDENT** | `C` |
| 7 | `falsifier` | FORMULA | `C` | 2 | 4643 | 7307 | PROV-FALS-2 | **—/BLOCKED** | `C` |
| 8 | `falsifier` | ISO | `2026-08-11` | 1 | 4758 | 7496 | PROV-FALS-1 | **—/BLOCKED** | `2026-08-11` |
| 9 | `falsifier` | ISO | `2026-07-29` | 1 | 4832 | 7607 | PROV-FALS-1 | **—/BLOCKED** | `2026-07-29` |
| 10 | `universe` | ISO | `2020-01-01` | 1 | 184 | 258 | **UNIV-SPAN-START** | **PRECEDENT** | `2020-01-01` |
| 11 | `universe` | FORMULA | `C` | 1 | 198 | 309 | **UNIV-SPAN-END** | **PRECEDENT** | `C` |
| 12 | `universe` | ISO | `2026-08-04` | 1 | 274 | 422 | PROV-UNIV-1 | **—/BLOCKED** | `2026-08-04` |
| 13 | `universe` | ISO | `2022-11-09` | 1 | 677 | 1047 | PROV-UNIV-1 | **—/BLOCKED** | `2022-11-09` |
| 14 | `universe` | ISO | `2022-11-10` | 1 | 2522 | 3891 | PROV-UNIV-1 | **—/BLOCKED** | `2022-11-10` |
| 15 | `universe` | ISO | `2020-03-12` | 1 | 2938 | 4566 | PROV-UNIV-1 | **—/BLOCKED** | `2020-03-12` |
| 16 | `universe` | ISO | `2026-08-04` | 2 | 5621 | 8803 | PROV-UNIV-2 | **—/BLOCKED** | `2026-08-04` |
| 17 | `universe` | ISO | `2026-08-04` | 3 | 6175 | 9690 | PROV-UNIV-3 | **—/BLOCKED** | `2026-08-04` |
| 18 | `universe` | ISO | `2026-08-04` | 4 | 7756 | 12196 | PROV-UNIV-4 | **—/BLOCKED** | `2026-08-04` |
| 19 | `universe` | ISO | `2025-09-18` | 1 | 10371 | 16328 | **K7-TRIGGER** | **PRECEDENT** | `2025-09-18` |
| 20 | `universe` | ISO | `2025-09-18` | 2 | 10809 | 17025 | **K7-BLACKOUT** | **PRECEDENT** | `2025-09-18` |
| 21 | `universe` | ISO | `2026-08-04` | 5 | 11121 | 17522 | PROV-UNIV-5 | **—/BLOCKED** | `2026-08-04` |
| 22 | `universe` | ISO | `2026-08-10` | 1 | 11182 | 17620 | PROV-UNIV-1 | **—/BLOCKED** | `2026-08-10` |
| 23 | `universe` | ISO | `2026-08-05` | 1 | 13279 | 20938 | PROV-UNIV-1 | **—/BLOCKED** | `2026-08-05` |
| 24 | `universe` | ISO | `2026-08-04` | 6 | 17131 | 26936 | PROV-UNIV-6 | **—/BLOCKED** | `2026-08-04` |
| 25 | `universe` | ISO | `2026-08-04` | 7 | 18294 | 28728 | PROV-UNIV-7 | **—/BLOCKED** | `2026-08-04` |
| 26 | `universe` | ISO | `2022-11-09` | 2 | 18711 | 29367 | PROV-UNIV-2 | **—/BLOCKED** | `2022-11-09` |
| 27 | `success_criteria` | ISO | `2026-08-05` | 1 | 6 | 6 | PROV-SUCC-1 | **—/BLOCKED** | `2026-08-05` |
| 28 | `success_criteria` | ISO | `2022-11-09` | 1 | 758 | 1202 | PROV-SUCC-1 | **—/BLOCKED** | `2022-11-09` |
| 29 | `success_criteria` | FORMULA | `C` | 1 | 1669 | 2594 | PROV-SUCC-1 | **—/BLOCKED** | `C` |
| 30 | `success_criteria` | ISO | `2026-08-06` | 1 | 2657 | 4174 | PROV-SUCC-1 | **—/BLOCKED** | `2026-08-06` |
| 31 | `success_criteria` | ISO | `2026-08-10` | 1 | 3191 | 5041 | PROV-SUCC-1 | **—/BLOCKED** | `2026-08-10` |
| 32 | `success_criteria` | FORMULA | `C + 187 days` | 1 | 8383 | 13230 | **SC-KC002-SURVIVAL** | **OBSERVATION** | `C + 187 days` |
| 33 | `success_criteria` | ISO | `2026-08-04` | 1 | 9603 | 15116 | PROV-SUCC-1 | **—/BLOCKED** | `2026-08-04` |
| 34 | `success_criteria` | ISO | `2026-08-10` | 2 | 9711 | 15298 | PROV-SUCC-2 | **—/BLOCKED** | `2026-08-10` |
| 35 | `success_criteria` | ISO | `2026-08-05` | 2 | 10522 | 16590 | PROV-SUCC-2 | **—/BLOCKED** | `2026-08-05` |
| 36 | `success_criteria` | ISO | `2026-08-05` | 3 | 13289 | 20911 | PROV-SUCC-3 | **—/BLOCKED** | `2026-08-05` |
| 37 | `success_criteria` | ISO | `2026-08-10` | 3 | 14207 | 22347 | PROV-SUCC-3 | **—/BLOCKED** | `2026-08-10` |
| 38 | `success_criteria` | ISO | `2026-08-10` | 4 | 16836 | 26567 | PROV-SUCC-4 | **—/BLOCKED** | `2026-08-10` |
| 39 | `success_criteria` | ISO | `2026-08-10` | 5 | 19524 | 30883 | PROV-SUCC-5 | **—/BLOCKED** | `2026-08-10` |
| 40 | `success_criteria` | ISO | `2026-08-04` | 2 | 19770 | 31277 | PROV-SUCC-2 | **—/BLOCKED** | `2026-08-04` |
| 41 | `success_criteria` | ISO | `2026-08-04` | 3 | 20127 | 31893 | PROV-SUCC-3 | **—/BLOCKED** | `2026-08-04` |
| 42 | `success_criteria` | ISO | `2026-08-05` | 4 | 21051 | 33335 | PROV-SUCC-4 | **—/BLOCKED** | `2026-08-05` |
| 43 | `success_criteria` | ISO | `2026-08-04` | 4 | 22451 | 35475 | PROV-SUCC-4 | **—/BLOCKED** | `2026-08-04` |
| 44 | `success_criteria` | ISO | `2026-08-11` | 1 | 24373 | 38507 | PROV-SUCC-1 | **—/BLOCKED** | `2026-08-11` |
| 45 | `success_criteria` | ISO | `2026-08-11` | 2 | 25171 | 39786 | PROV-SUCC-2 | **—/BLOCKED** | `2026-08-11` |
| 46 | `success_criteria` | ISO | `2026-07-29` | 1 | 25193 | 39808 | PROV-SUCC-1 | **—/BLOCKED** | `2026-07-29` |
| 47 | `success_criteria` | ISO | `2026-07-29` | 2 | 26074 | 41207 | PROV-SUCC-2 | **—/BLOCKED** | `2026-07-29` |
| 48 | `success_criteria` | FORMULA | `C` | 2 | 26314 | 41595 | PROV-SUCC-2 | **—/BLOCKED** | `C` |
| 49 | `success_criteria` | ISO | `2026-08-11` | 3 | 26511 | 41903 | PROV-SUCC-3 | **—/BLOCKED** | `2026-08-11` |
| 50 | `forward_kill_condition` | FORMULA | `C + 187 days` | 1 | 27 | 27 | **KC-002-OBS-DATE** | **OBSERVATION** | `C + 187 days` |
| 51 | `forward_kill_condition` | FORMULA | `C` | 1 | 264 | 375 | PROV-FORW-1 | **—/BLOCKED** | `C` |
| 52 | `forward_kill_condition` | ISO | `2026-07-28` | 1 | 268 | 416 | PROV-FORW-1 | **—/BLOCKED** | `2026-07-28` |
| 53 | `forward_kill_condition` | ISO | `2027-01-31` | 1 | 287 | 435 | **KC-002-OBS-DRAFTED** | **OBSERVATION** | `C + 187 days` |
| 54 | `forward_kill_condition` | FORMULA | `C + 187 days` | 2 | 379 | 564 | **KC-002-OBS-GOVERNING** | **OBSERVATION** | `C + 187 days` |
| 55 | `forward_kill_condition` | FORMULA | `C` | 2 | 779 | 1223 | **KC-002-WINDOW-START** | **OBSERVATION** | `C` |
| 56 | `forward_kill_condition` | FORMULA | `C + 187 days` | 3 | 782 | 1226 | **KC-002-WINDOW-END** | **OBSERVATION** | `C + 187 days` |
| 57 | `forward_kill_condition` | ISO | `2026-08-11` | 1 | 802 | 1246 | PROV-FORW-1 | **—/BLOCKED** | `2026-08-11` |
| 58 | `forward_kill_condition` | ISO | `2027-01-31` | 2 | 827 | 1271 | PROV-FORW-2 | **—/BLOCKED** | `2027-01-31` |
| 59 | `forward_kill_condition` | FORMULA | `C ` | 1 | 3035 | 4774 | **KC-002-NO-POST-C-EXCL** | **PRECEDENT** | `C` |
| 60 | `forward_kill_condition` | ISO | `2026-08-05` | 1 | 3243 | 5093 | PROV-FORW-1 | **—/BLOCKED** | `2026-08-05` |
| 61 | `forward_kill_condition` | FORMULA | `C + 187 days` | 4 | 3764 | 5984 | **KC-002-CL3-BOUNDARY** | **DEADLINE** | `C + 187 days` |
| 62 | `forward_kill_condition` | ISO | `2026-08-11` | 2 | 3783 | 6003 | PROV-FORW-2 | **—/BLOCKED** | `2026-08-11` |
| 63 | `forward_kill_condition` | ISO | `2027-01-31` | 3 | 3804 | 6024 | PROV-FORW-3 | **—/BLOCKED** | `2027-01-31` |
| 64 | `forward_kill_condition` | ISO | `2026-08-05` | 2 | 3845 | 6102 | PROV-FORW-2 | **—/BLOCKED** | `2026-08-05` |
| 65 | `forward_kill_condition` | ISO | `2026-08-11` | 3 | 4733 | 7508 | PROV-FORW-3 | **—/BLOCKED** | `2026-08-11` |
| 66 | `forward_kill_condition` | FORMULA | `C + 187 days` | 5 | 4877 | 7726 | PROV-FORW-5 | **—/BLOCKED** | `C + 187 days` |
| 67 | `forward_kill_condition` | ISO | `2027-01-31` | 4 | 5021 | 7944 | PROV-FORW-4 | **—/BLOCKED** | `2027-01-31` |
| 68 | `forward_kill_condition` | ISO | `2026-07-28` | 2 | 5177 | 8211 | PROV-FORW-2 | **—/BLOCKED** | `2026-07-28` |
| 69 | `forward_kill_condition` | FORMULA | `C + 187 days` | 6 | 5189 | 8223 | PROV-FORW-6 | **—/BLOCKED** | `C + 187 days` |
| 70 | `forward_kill_condition` | ISO | `2027-01-31` | 5 | 5219 | 8253 | PROV-FORW-5 | **—/BLOCKED** | `2027-01-31` |
| 71 | `forward_kill_condition` | ISO | `2027-01-31` | 6 | 5237 | 8308 | PROV-FORW-6 | **—/BLOCKED** | `2027-01-31` |
| 72 | `forward_kill_condition` | FORMULA | `C` | 3 | 6089 | 9641 | PROV-FORW-3 | **—/BLOCKED** | `C` |
| 73 | `forward_kill_condition` | ISO | `2027-01-31` | 7 | 6668 | 10590 | PROV-FORW-7 | **—/BLOCKED** | `2027-01-31` |
| 74 | `forward_kill_condition` | FORMULA | `C` | 4 | 7341 | 11633 | **KC-002-CLAUSE-5** | **OBSERVATION** | `C + 187 days` |
| 75 | `forward_kill_condition` | ISO | `2026-08-11` | 4 | 7360 | 11689 | PROV-FORW-4 | **—/BLOCKED** | `2026-08-11` |
| 76 | `forward_kill_condition` | ISO | `2027-01-31` | 8 | 7381 | 11710 | **KC-002-CLAUSE-5-DRAFTED** | **OBSERVATION** | `C + 187 days` |
| 77 | `forward_kill_condition` | ISO | `2026-08-11` | 5 | 7916 | 12578 | PROV-FORW-5 | **—/BLOCKED** | `2026-08-11` |
| 78 | `forward_kill_condition` | ISO | `2026-08-11` | 6 | 8164 | 12974 | PROV-FORW-6 | **—/BLOCKED** | `2026-08-11` |
| 79 | `forward_kill_condition` | ISO | `2026-08-11` | 7 | 8436 | 13394 | PROV-FORW-7 | **—/BLOCKED** | `2026-08-11` |
| 80 | `forward_kill_condition` | ISO | `2026-07-29` | 1 | 8458 | 13416 | PROV-FORW-1 | **—/BLOCKED** | `2026-07-29` |
| 81 | `forward_kill_condition` | FORMULA | `C` | 5 | 9173 | 14612 | PROV-FORW-5 | **—/BLOCKED** | `C` |
| 82 | `forward_kill_condition` | FORMULA | `C` | 6 | 9428 | 15015 | PROV-FORW-6 | **—/BLOCKED** | `C` |
| 83 | `forward_kill_condition` | FORMULA | `C` | 7 | 9842 | 15651 | PROV-FORW-7 | **—/BLOCKED** | `C` |
| 84 | `forward_kill_condition` | FORMULA | `C` | 8 | 10249 | 16280 | PROV-FORW-8 | **—/BLOCKED** | `C` |
| 85 | `forward_kill_condition` | ISO | `2026-08-10` | 1 | 10404 | 16546 | PROV-FORW-1 | **—/BLOCKED** | `2026-08-10` |
| 86 | `forward_kill_condition` | ISO | `2026-08-10` | 2 | 12127 | 19305 | PROV-FORW-2 | **—/BLOCKED** | `2026-08-10` |
| 87 | `forward_kill_condition` | ISO | `2026-08-10` | 3 | 13113 | 20920 | PROV-FORW-3 | **—/BLOCKED** | `2026-08-10` |
| 88 | `forward_kill_condition` | ISO | `2026-07-29` | 2 | 13434 | 21426 | PROV-FORW-2 | **—/BLOCKED** | `2026-07-29` |
| 89 | `forward_kill_condition` | ISO | `2026-08-11` | 8 | 13763 | 21977 | PROV-FORW-8 | **—/BLOCKED** | `2026-08-11` |
| 90 | `forward_kill_condition` | FORMULA | `C` | 9 | 14241 | 22714 | PROV-FORW-9 | **—/BLOCKED** | `C` |

**`forward_window_start` — row 91, and it is not in the table because it does not exist yet:**
`(field='forward_window_start', ordinal=1, offset=0, recognizer=ISO, matched_text=<the seal date>,
tag='C-ANCHOR', kind='OBSERVATION', date_expr='C', discharge_event_kind='hypothesis_sealed')`.

**`horizon` and `forward_window_min_length` contribute zero sites** [measured]. `horizon` names no
date; `12.0` matches no recognizer.

---

## 6. WHAT THIS PAYLOAD DOES NOT DO

- **No registry write. No `open_hypothesis`. No seal. No vault.** `dated_clauses` does not exist.
- **No trial, no number from market data.** The only figures are counts of regex matches over a
  markdown file and one span arithmetic reported at `PREREG-002` §11.1 R37.
- **No `harness/` file touched, no `VALIDATION-*` document touched, no `book/` artifact written**
  beyond a read-only `SELECT` against `book/pit.db` for the R37 span. No test run. No suite state
  reported. `test_h7` / `test_h8` not approached. No commit.
- **No binding field value changed.** `trial_budget = 47`, `n_inherited = 7`, unmoved.
- **`model_prior_provenance` is a binding field and is NOT in E-1's enumerated scope**, so its dated
  provenance claims are covered by nothing. Filed **I-175**, LOW — the gap is real and the direction
  is benign, since provenance is where dates *should* live.
- **C13(k) is not ruled here.** Validation holds I-153's instance and the alternative — the drafted
  literal `2027-01-31` and a shortened window — is live. **If Validation takes it, rows 74 and 76 and
  D-7's mapping change, and this payload is reissued.**

---

*Director of Research · Castellan Capital · 2026-08-12 · dispatch S3-D-014*
*Trial budget ZERO. `book/registry.db` reads **0 hypotheses / 0 trials** and must still read 0 / 0.*
