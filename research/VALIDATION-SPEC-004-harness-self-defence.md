# VALIDATION-SPEC-004 — Harness self-defence: the registry and the vault defend themselves in code (I-095), and every dated clause is evaluated by something (I-135 / I-140 / I-153)

**Head of Quantitative Validation · Castellan Capital · 2026-08-12 · Dispatch S3-D-011 row 1**
**Red-first. Seat 9 implements. This document modifies no file under `harness/castellan/`.**

**Registry state at authoring [measured]: `book/registry.db` — 0 hypotheses / 0 trials / 1 event.
Unchanged by this dispatch. Suite at authoring [measured]: 271 passed / 4 failed / 275.**

---

## 0. THE TWO CONTROLS, ONE SENTENCE EACH

**ITEM 1.** `TrialRegistry` and `HoldoutVault` open **read-only by default** — the registry on a
SQLite `mode=ro` URI handle, the vault behind a guard on every method that touches `vault_dir` —
and a write requires an **explicit, typed, block-scoped grant** that writes its own first row into
the registry before any other write under it can happen.

**ITEM 2.** A **dated-clause evaluator** extracts every date literal, anchored formula and stated
span from a family's registered fields, resolves each against the sealed anchor `C`, and **exits
nonzero on any firing and on any inability to evaluate** — with no parameter, anywhere in its
signature, capable of silencing a finding.

---

## 1. SCOPE AND AUTHORITY

### 1.1 What this document does

Specifies both controls as binding numbered clauses (`R-` for Item 1, `E-` for Item 2), names which
Seat 9 implements mechanically and which route back to me, and files the tests, red today, that
grade them.

### 1.2 What this document does not do

- **No registration, no seal, no trial, no backtest, no vault touch.** `book/registry.db` reads
  0/0/1 when this is put down and must still read 0/0/1.
- **No `harness/castellan/` file is modified.** Every code shape below is a specification of what
  Seat 9 will write, quoted for precision, not a patch.
- **No Gate threshold moves.** R-15 and E-24 attach a *provenance precondition* to the overall
  verdict; they change no number in Charter §4.2. See §4.4 for why that is inside this seat's
  authority and not a §4 reserved act.
- **`research/PREREG-002-*` and `DIR-RESTATE-*` are untouched.** §12.5's 24-clause sweep is
  consumed as input; nothing is written back to it.
- **No ruling on I-153's C13(k).** This document specifies the checker that catches I-153's
  *class*. It does not rule I-153's *instance*, which remains owed by me. §13(3).

### 1.3 The projection, measured, and where it did not hold

The dispatch projected both items under **~800 authored lines**. **Measured on delivery: 857** — a
7% overrun, reported rather than hidden, and reported *after* the scope decision below, not
instead of it.

**The scope decision, stated rather than absorbed:** the evaluator specifies *that* a clause fired
and **never what a firing does**. Consequence semantics — terminate, downgrade to
ADMITTED-AS-EXPLORATORY, notify — the sponsor remediation workflow, and the document-side
(non-registry) clause surface are **deferred at a named boundary, E-25**. Without that cut this
document projected past 990 and the dispatch's split-and-price-as-two rule would have bound.

**What was not cut, because cutting it would have made the deliverable dishonest rather than
smaller:** everything the dispatch required of the evaluator — reads registered fields, evaluates
every clause against the store on invocation, exits nonzero on firing *or* inability, detects
formula-versus-literal divergence, direction-blind **by construction rather than by intent** — and
§4's honest account of what Item 1's grant prevents versus makes visible. **§4 is the section a
line budget would have eaten first and is the section this dispatch was actually about.**

**The CIO owns the pricing call on 844 against ~800.** This seat's view, offered and not decided: it
is one document, one owner, one implementer, one layer, and splitting it now would separate §4 from
the clauses §4 describes.

---

## 2. ITEM 1 · THE READ-ONLY CONSTRUCTION · R-1 … R-8

**Today [measured, `registry.py` L157–162]:**

```python
def __init__(self, path: str):
    self.path = path
    self.conn = sqlite3.connect(path)        # read-write. no mode. no uri.
    self.conn.executescript(SCHEMA)          # a write, on every construction
    self.conn.commit()                       # a write, on every construction
    self._migrate()                          # a write, on every construction
```

**Every handle this firm has ever taken on the registry has been a write handle, and three writes
happen before the caller has expressed any intention at all.** That is the surface I-095's remedy
closes.

> **R-1 · Read-only is the default and it is the constructor's default, not a caller convention.**
> ```python
> def __init__(self, path: str, *, allow_create: bool = False):
>     self.path = path
>     self._ro = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
>     self.conn = self._ro
>     self._grant = None
> ```
> `mode=ro` is the SQLite URI flag; it is enforced by the library, not by the harness, and it
> applies to the handle for its whole life.

> **R-2 · `executescript(SCHEMA)` and `_migrate()` leave `__init__`.** They move to the grant path
> (R-9, reason `MIGRATION`). Schema creation and schema migration are writes, they were always
> writes, and the only thing that made them invisible was that they happened before anyone looked.
> **This is the "sanctioned migrations" third of Sprint 2's external-state policy landing here.**

> **R-3 · A registry file that does not exist fails at construction, loudly, with a typed error.**
> `mode=ro` against a missing file raises `sqlite3.OperationalError: unable to open database file`.
> Seat 9 converts it:
> ```python
> raise RegistryNotInitializedError(
>     f"No registry at {path}. Creating a registry is a write act: construct with "
>     "allow_create=True inside a write_grant(reason='MIGRATION') block.")
> ```
> **It does not silently create one.** The failure mode this forecloses is a typo in a path
> producing a fresh empty registry that reads 0 trials — an N of zero that is not a measurement.

> **R-4 · An ungranted write raises `RegistryWriteNotGrantedError` at method entry, before any
> SQL.** `open_hypothesis`, `log_trial` and `log_event` each begin with `self._require_grant(...)`.
> The error names the method, the family, the reason vocabulary member the call would have needed,
> and the grant procedure. **Not at commit. Not at execute. At entry** — so the traceback points at
> the caller's line and not at a SQL string three frames down.

> **R-5 · `self.conn` remains the read-only handle whenever no grant is open, and this is the
> backstop, not the control.** A caller that reaches around the API —
> `registry.conn.execute("INSERT INTO trials ...")`, which nothing in Python prevents — receives
> `sqlite3.OperationalError: attempt to write a readonly database` **at the `execute`, not at the
> `commit`.** This is the dispatch's fourth settlement question and the answer is: **loudly, at
> execute.** SQLite refuses the statement; there is no dirty page to lose at commit time and no
> window in which the caller believes the write landed.
>
> **R-5 answers a question R-4 cannot.** R-4 is a guard in code the caller can decline to call.
> R-5 makes the guard non-bypassable *from inside the process*, because the handle itself has no
> write authority. The remaining path — a caller opening its own connection — is §4's subject and
> is not closed by anything here.

> **R-6 · An open grant swaps the handle and closing it swaps it back, including on exception.**
> On enter, a second connection is opened read-write and assigned to `self.conn`. On exit —
> `finally`, unconditionally — the read-write handle is committed if the block left no exception,
> rolled back if it did, closed, and `self.conn` is reassigned to `self._ro`. **A process that
> raises inside a grant does not keep write authority.**

> **R-7 · Grants do not nest.** Entering a grant while one is open raises
> `RegistryWriteGrantNestedError`. The property this protects: a function that takes a narrow grant
> cannot have its authority silently widened by a callee that takes a broader one, and a caller
> reading one `with` statement is reading the whole of the write authority in that block.

> **R-8 · The grant is scoped to the block, and that is the dispatch's second settlement question,
> answered with its reasons.** Not one operation: per-operation grants produce one grant record per
> logged trial, which drowns the very record the control exists to create, and force the token to
> live process-globally anyway because there is nowhere else to put it. Not a process lifetime: a
> script that legitimately needs one registration would hold write authority over every line it
> runs, including library code its author did not write, which is the exact "incidental write"
> property R-1 exists to remove. **The block is the narrowest scope that is simultaneously
> enforceable by the language and legible in the record.**

---

## 3. ITEM 1 · THE GRANT, AND HOW IT APPEARS IN THE RECORD · R-9 … R-18

*"The record shows" is the half of the Principal's ruling that makes this a control rather than a
speed bump. R-11 through R-15 are that half.*

> **R-9 · Signature.**
> ```python
> @contextmanager
> def write_grant(self, *, reason: str, dispatch: str, token: str | None = None):
> ```
> `token` defaults to `os.environ["CASTELLAN_REGISTRY_WRITE"]`; absent both, R-4's error. `reason`
> is a member of R-10's closed vocabulary. `dispatch` is the free-text dispatch identifier the
> brief supplies (e.g. `"S3-D-011 row 1"`). **All three are recorded in full.**

> **R-10 · `reason` is a closed vocabulary and it restricts which write methods the grant admits.**
>
> | `reason` | Admits | Refuses |
> |---|---|---|
> | `MIGRATION` | `executescript(SCHEMA)`, `_migrate`, `allow_create` | everything else |
> | `REGISTER_HYPOTHESIS` | `open_hypothesis`, `log_event` | `log_trial` |
> | `LOG_TRIAL` | `log_trial`, `log_event` | `open_hypothesis` |
> | `LOG_EVENT` | `log_event` | `open_hypothesis`, `log_trial` |
> | `VAULT_SEAL` | `log_event`, vault file writes under `seal()` | `open_hypothesis`, `log_trial` |
> | `VAULT_ACQUIRE` | `log_event`, vault file writes under `acquire_once()` | `open_hypothesis`, `log_trial` |
> | `GATE_VERDICT` | `log_event` | `open_hypothesis`, `log_trial` |
>
> A method call outside the open grant's row raises `RegistryWriteNotGrantedError` naming both the
> grant's reason and the reason the call needed. **A `reason` outside the vocabulary raises
> `RegistryWriteGrantMalformedError`; extending the vocabulary is a specification act and routes to
> me (§9.2).**
>
> **Why typing the grant is worth its cost, stated plainly because it is the one narrowing here
> that is real without authentication:** it does not stop anyone, but it means the record says not
> merely *that* a write happened under authority but *of what class* — and a grant taken to log a
> trial cannot register a hypothesis without a second, separately recorded grant naming that.

> **R-11 · New table `write_grants`. Created under the `MIGRATION` grant of R-16.**
> ```sql
> CREATE TABLE IF NOT EXISTS write_grants (
>     grant_id    INTEGER PRIMARY KEY AUTOINCREMENT,
>     token       TEXT NOT NULL,
>     reason      TEXT NOT NULL,
>     dispatch    TEXT NOT NULL,
>     argv        TEXT NOT NULL,       -- json.dumps(sys.argv)
>     pid         INTEGER NOT NULL,
>     opened_utc  REAL NOT NULL,
>     closed_utc  REAL,                -- NULL => the process died inside the grant
>     writes      INTEGER NOT NULL DEFAULT 0,
>     outcome     TEXT,                -- 'CLEAN' | 'EXC:<ExceptionClass>' | NULL
>     prev_hash   TEXT NOT NULL,
>     grant_hash  TEXT NOT NULL
> );
> ```

> **R-12 · The grant row is the first row written under its own grant.** On enter, before any
> caller statement executes, the read-write handle inserts the `write_grants` row. There is no
> ordering in which a write precedes the record of the authority it was made under. **The
> chicken-and-egg is resolved in the only direction that is auditable.**

> **R-13 · Chain.** `prev_hash` is the previous row's `grant_hash`, or 64 zeros for the first;
> `grant_hash = sha256(prev_hash || token || reason || dispatch || argv || repr(opened_utc))`,
> hex. **What this buys and what it does not is stated at §4.3, not here.**

> **R-14 · `grant_id` column on `hypotheses`, `trials` and `events`, set by every harness write.**
> A row inserted by anything that is not the harness — a `sqlite3` CLI statement, a caller's own
> `sqlite3.connect` — carries `grant_id IS NULL`. **That is an orphan, and orphan detection is the
> only part of this control that sees outside the process.**

> **R-15 · `audit_write_grants()`, a pure read on the read-only handle, and `evaluate_gate1` puts
> it on the face of every Validation Report.**
> ```python
> def audit_write_grants(self) -> dict:
>     """-> {"orphan_rows": {"hypotheses": [...], "trials": [...], "events": [...]},
>            "chain_intact": bool, "chain_head": str, "n_grants": int,
>            "unclosed_grants": [grant_id, ...], "migration_watermark": {...}}"""
> ```
> **Teeth, and they are the point of the whole item: a Gate 1 evaluation against a registry with
> any orphan row, a broken chain, or an unclosed grant returns `INSUFFICIENT-DATA` as the OVERALL
> verdict — not a FAIL of one criterion.** N is the denominator of every statistic in Charter Part
> IV; a registry that cannot account for how its rows arrived has not delivered an N, it has
> delivered an integer. My standing rule is that an unreconstructable N is INSUFFICIENT-DATA and
> never PASS, and orphan rows are exactly that condition arriving through a new door.
>
> The report carries `chain_head`, `n_grants`, and the orphan counts by table **whether or not they
> are zero** — a control that is only visible when it fires is a control nobody can confirm is
> running.

> **R-16 · The migration and its bounded amnesty.** `book/registry.db` predates R-11 and R-14; its
> **1 existing event row** [measured] cannot carry a `grant_id`. The `MIGRATION` grant that adds the
> columns records, in its own row, a `migration_watermark`: `MAX(rowid)` per table at migration
> time. `audit_write_grants` treats rows at or below the watermark as exempt and **reports the
> watermark on the face of the Gate report beside the orphan counts.** The amnesty is bounded to
> rows that already existed, recorded in the row that granted it, and **is not re-issuable** — a
> second `MIGRATION` grant may not raise a watermark, and an attempt raises
> `RegistryWriteGrantMalformedError`. Filed I-163.

> **R-17 · The vault takes the same default through the same grant.** `HoldoutVault`'s registry
> writes already route through `registry.log_event` and are covered by R-4 with no new code. Its
> **file** writes — `spec.json`, `payload.enc`, `verifier.json`, `acquisition_meta.json` — are not
> SQLite and get an explicit guard: `seal()`, `acquire_once()` and every method that opens a path
> under `vault_dir` for writing begins with `self.registry._require_grant("VAULT_SEAL")` or
> `("VAULT_ACQUIRE")` and raises `VaultWriteNotGrantedError` otherwise. `os.makedirs(vault_dir)` in
> `__init__` moves behind the same guard.

> **R-18 · The vault has one layer where the registry has two, and this is disclosed rather than
> papered over.** R-5's backstop is a property of the SQLite handle. There is no filesystem
> equivalent: a caller holding a vault object can call `open(vault._payload_path, "wb")` and the
> guard never runs, because the guard lives in methods the caller declined to use. **The registry's
> control survives a caller reaching around the API; the vault's does not.** Filed I-160. The
> mitigation that does exist is R-4: the vault cannot log its `holdout_sealed` / `holdout_acquired`
> events without a grant, so a file written around the guard is a vault whose **state machine**
> disagrees with its **directory** — `is_sealed()` reads True from the file while `state` reads
> UNSEALED from the events. **That divergence is detectable and Gate 1 already reads the event
> side.** It is a weaker property than R-5 and is labelled as one.

---

## 4. ITEM 1 · THE HONEST ANSWER — I-095's OWN TEST, TURNED ON I-095's REMEDY

*§4.7.3's test is not "is this control deterministic?" but **"name the path a real actor would
take, and show this control on it."** Applied to this specification, in the terms the dispatch
required.*

### 4.1 The paths a real actor would take

| # | Path | Does this control stop it? |
|---|---|---|
| **A1** | `python3 -c "import sqlite3; sqlite3.connect('book/registry.db').execute('INSERT INTO trials …'); …"` | **No.** A connection the harness did not issue has no guard on it and no `mode=ro` on it. |
| **A2** | `sqlite3 book/registry.db "INSERT INTO events …"` | **No.** Same, one layer further out. |
| **A3** | `export CASTELLAN_REGISTRY_WRITE=anything` then an ordinary harness call inside a grant | **No.** A seat that can run `python3` can set an environment variable. **The seat can mint its own grant.** |
| **A4** | `registry.conn.execute("INSERT …")` from inside a harness process, no grant open | **Yes** — R-5, at `execute`, `attempt to write a readonly database`. |
| **A5** | `registry.log_trial(...)` with no grant open | **Yes** — R-4, at method entry, typed. |
| **A6** | A grant taken for `LOG_EVENT` used to call `open_hypothesis` | **Yes** — R-10, typed refusal, and the record shows the grant that was taken. |
| **A7** | A write of any kind, followed by a claim that it was authorized | **No, and this is I-103**: `token` and `dispatch` are strings a seat writes about itself. |

**A3 is the honest centre of this section and the dispatch named it before I did.** The grant, if it
is an environment token, is mintable by the actor it governs. That is I-103 — *the harness cannot
authenticate anyone* — arriving in a new place, and it is filed again as I-161 rather than treated
as answered because it appears under a different name.

### 4.2 What this control prevents, in those terms

Three things, all in-process, all deterministic:

1. **Incidental writes.** After R-1/R-2, no code path writes the registry without a block that says
   it is writing. The three writes that happen today before the caller expresses any intention are
   gone. **Code that did not mean to write cannot.**
2. **Ungranted writes through any handle the harness issues** — R-4 at the API, R-5 at the handle.
   A caller inside a harness process cannot reach a write path by accident or by reaching around.
3. **Writes of a class the grant did not name** — R-10. A grant is not a general key.

### 4.3 What it makes visible without preventing, and what it detects

- **Visible, not prevented:** a deliberate write by a seat that mints its own token (A3). It runs.
  It is recorded — reason, dispatch, argv, pid, wall-clock — and the record is the forger's own
  strings. **The control converts "a write happened" into "a write of this class happened under
  this stated authority at this moment from this command line," and stops there.**
- **Detected, not prevented:** A1 and A2 leave `grant_id IS NULL` (R-14). Under R-15 the next Gate
  report on that registry reads **INSUFFICIENT-DATA**. This is the one part of the control that
  sees a path outside the harness process, and it works because the harness sets a column the
  outside path does not know to set.
- **Detected conditionally:** retro-insertion or edit of a `write_grants` row breaks R-13's chain —
  **but only against an independent copy of the head.** One exists and is not incidental:
  **`book/registry.db` is tracked in git** [measured — `git ls-files book/`], and A3 makes the repo
  the book of record, so every commit pins that session's chain head in history. **Rewriting the
  head therefore requires rewriting git history, which is a different and far more visible act than
  an INSERT.** Without that external witness the chain would be a hash a forger controls both ends
  of, and would be worth nothing; **it is worth exactly the difficulty of rewriting the repo.**

### 4.4 What it is not proof against, said in the terms the dispatch required

**A seat that decides to write can write.** It mints a token (A3), takes a well-formed typed grant,
performs the write through the harness, and the record shows a correctly-formed authorization it
issued to itself. Nothing in this specification, and nothing available at this firm's scale,
distinguishes that from the real thing.

**So, stated once, in the dispatch's own terms and to be quoted rather than paraphrased:**

> **The grant makes registry and vault writes DELIBERATE, TYPED, and ATTRIBUTABLE-BY-DECLARATION.
> It does not make them PREVENTED, and it does not AUTHENTICATE the declarant.**
>
> **It is proof against accident, against incidental writes by code that did not mean to write,
> against reaching around the API from inside the process, and against a raw-path write remaining
> invisible.**
>
> **It is not proof against a seat that decides to write and mints its own grant. That seat's write
> succeeds and its record reads correct.**

**And the labelling consequence, because the finding this remedies was a labelling failure.** The
`f54f9b9` status line was corrected once, at S3-D-009, to say the denies covered a path nobody uses.
**When this lands it needs a second line, and that line is not "registry and vault are
write-protected."** It is: *"registry and vault are read-only by default; writes require a typed,
block-scoped grant that records itself; raw-path writes are detected, not prevented; the grant is
attributable by declaration and authenticates nobody."* **A remedy for a misaimed control that is
itself described as more than it is would be I-095's successor**, and this seat would rather ship a
modest control described precisely. §13(1).

**On R-15 and the §4-reserved-act question, settled here rather than left to be raised:** attaching
INSUFFICIENT-DATA to a registry whose write provenance is broken **moves no threshold in Charter
§4.2** and adds no criterion to §4.4's table. It applies the Charter's existing rule — *"if N is
unknown or unreconstructable, the verdict is automatically INSUFFICIENT-DATA, never PASS"* (§Seat 3
standing constraints) — to a newly-detectable way for N's provenance to be unknown. That is inside
this seat's mandate. **It is disclosed anyway, as I-165**, because a rule that makes a whole report
INSUFFICIENT-DATA on a condition nobody has seen fire yet is exactly the kind of clause that should
be visible before it bites and not after.

---

## 5. ITEM 2 · THE DATED-CLAUSE EVALUATOR — CONSTRUCTION · E-1 … E-11

*Scope widened twice by ruling: **every dated clause** — kill conditions, condition precedents,
observation dates, deadlines of any kind. The Director's sweep (`DIR-RESTATE-001` §12.5) is useful
input and not a specification: **2 of 24 clauses evaluated by code, 3 class (b), 19 evaluated by a
reader noticing.** This evaluator's job is to make the 19 impossible.*

> **E-1 · The evaluator reads the registry and nothing else.** Its inputs are the family's
> `hypotheses` row, its `hypothesis_sealed` shadow copy, its `dated_clauses` rows (E-5), and the
> `events` table. **It never opens a document.** A finding cannot be argued away with a section the
> evaluator did not read, and — the direction that matters more — **the evaluator cannot be handed
> a curated view of the text.** The fields in scope are enumerated, not sampled:
> `statement`, `mechanism`, `falsifier`, `universe`, `horizon`, `success_criteria`,
> `forward_window_start`, `forward_kill_condition`, and the numeric
> `forward_window_min_length`.

> **E-2 · Extraction is by literal form, never by meaning.** Three recognizers, applied to every
> field in E-1, each producing zero or more sites:
>
> | Recognizer | Pattern (specification, Seat 9 may compile it as it likes) | Example |
> |---|---|---|
> | `ISO` | `\b\d{4}-\d{2}-\d{2}\b` | `2027-01-31` |
> | `FORMULA` | `\bC\s*(?:[+-]\s*\d+\s*(?:day|month|year)s?)?\b` | `C + 187 days`, bare `C` |
> | `SPAN` | a bracketed interval `\[\s*(<ISO>\|C)\s*,\s*(<ISO>\|C)\s*\]` occurring in the same sentence as a quantity `\b\d+(?:\.\d+)?\s*(?:day\|month\|year)s?\b` | `[2020-01-01, C]` … `6.571 years` |
>
> **No natural-language understanding is attempted anywhere in this evaluator.** That is a design
> constraint, not a limitation being apologised for: a checker that decides what a sentence *means*
> is a checker whose findings are arguable, and an arguable finding is one a sponsor negotiates.

> **E-3 · A clause site is `(family, field, source_offset, matched_text, recognizer, sentence)`.**
> `source_offset` is the character offset of the match within the field's text — the stable
> identity a `dated_clauses` row claims. `sentence` is the maximal run between sentence terminators
> containing the match, truncated to 400 characters, and is **reported for the reader and consumed
> by nothing.**

> **E-4 · The anchor `C` is read, never inferred.** `C` = `forward_window_start` if it parses as an
> ISO date, else the UTC calendar date of the family's `hypothesis_sealed` event. **`C` is never
> re-derived from prose, never taken from a parenthesis, and never defaulted to today.** A family
> with neither is `UNANCHORED`: every `FORMULA` and every `SPAN` site containing `C` returns
> `UNANCHORED`, which is an inability verdict (E-19), and the run exits nonzero.

> **E-5 · New table `dated_clauses` — the structured form a clause must take to be evaluable.**
> ```sql
> CREATE TABLE IF NOT EXISTS dated_clauses (
>     clause_id            INTEGER PRIMARY KEY AUTOINCREMENT,
>     family               TEXT NOT NULL REFERENCES hypotheses(family),
>     tag                  TEXT NOT NULL,     -- sponsor's label, e.g. 'KC-002 clause 5'
>     field                TEXT NOT NULL,     -- one of E-1's enumerated fields
>     source_offset        INTEGER NOT NULL,  -- claims exactly one E-3 site
>     kind                 TEXT NOT NULL,     -- OBSERVATION | DEADLINE | PRECEDENT
>     date_expr            TEXT NOT NULL,     -- an ISO literal or an anchored formula
>     discharge_event_kind TEXT NOT NULL,     -- '' means nothing discharges this
>     sealed_utc           REAL NOT NULL,
>     grant_id             INTEGER            -- R-14
> );
> ```
> `kind` is closed. Rows are written under a `REGISTER_HYPOTHESIS` grant, hashed as
> `clauses_sha256` over the canonical JSON of all rows for the family in `clause_id` order, and
> sealed as a `dated_clauses_sealed` registry event. **Accessor and writer names are fixed at
> §10.1 and are not the implementer's to choose**, because the tests bind them.
>
> **`dated_clauses` is deliberately NOT a binding field of the pre-registration.** Adding it to
> `_BINDING_FIELDS` would change `prereg_sha256`'s domain and make every existing seal an
> amendment. It carries its own hash and its own sealed event instead. **The two hashes are
> independent and both are reported.**

> **E-6 · COVERAGE — every extracted site must be claimed by exactly one clause row.** Match on
> `(field, source_offset)`.
>
> | Condition | Verdict |
> |---|---|
> | claimed by exactly one row | proceed to E-7 |
> | claimed by no row | `UNCOVERED` |
> | claimed by two or more rows | `AMBIGUOUS` |
> | a clause row claiming an offset no site occupies | `DANGLING` |
>
> **All four of the non-proceeding cases are inability-to-evaluate and exit nonzero.** This is the
> clause that converts *"19 of 24 evaluated by nothing"* from an audit finding into a run that
> fails. **The evaluator does not decide that an unclaimed date is harmless; it declines to
> evaluate it and says so with a nonzero exit.** A sponsor's only routes are to structure the
> clause or to strike it — both pre-seal, both cheap, and both visible.

> **E-7 · Resolution.** For each covered site, resolve the *clause row's* `date_expr` to a UTC
> calendar date: an ISO literal resolves to itself; a `FORMULA` resolves against `C` by exact day
> arithmetic (`C + 187 days`, no month-length ambiguity for day units; `+N months` uses calendar
> month addition with end-of-month clamping, stated so two implementations cannot disagree).

> **E-8 · Anchor staleness.** If `forward_window_start` holds an ISO literal and the family's
> `hypothesis_sealed` event falls on a different UTC calendar date, the site returns
> `ANCHOR-STALE`. **This is the sweep's D-8** — `forward_window_start = 2026-07-28 (= C; the seal is
> intended for today)`, false since 2026-08-04 and carried through four revisions.

> **E-9 · Span recomputation.** For each `SPAN` site: resolve both interval endpoints (E-7),
> recompute the quantity in the stated unit — years as `(end − start).days / 365.2425`, months as
> `/ 30.4368` (the constant `holdout.py` already uses), days exactly — and compare to the stated
> quantity. `|recomputed − stated| > max(0.005 × stated, 1 day-equivalent)` returns
> `SPAN-DIVERGENT`. **The comparison is on absolute difference and the verdict does not consult the
> sign.** §8.3.

> **E-10 · Firing, evaluated at invocation against the store.** For each covered site, with
> `T` = the as-of instant (E-22):
>
> | Condition | Verdict |
> |---|---|
> | `resolved_date > T` | `PENDING` |
> | `resolved_date ≤ T` and a registry event of kind `discharge_event_kind` exists for this family with `created_utc ≤ end of resolved_date` | `DISCHARGED` |
> | `resolved_date ≤ T` and no such event | **`FIRED`** |
> | `discharge_event_kind == ''` and `resolved_date ≤ T` | **`FIRED`** — unconditionally |
>
> The mechanics are identical across `OBSERVATION`, `DEADLINE` and `PRECEDENT`; only the sponsor's
> reading of what firing *means* differs, and that reading is E-25's boundary.

> **E-11 · The empty `discharge_event_kind` is `SILENCE IS A KILL`, made explicit and made a
> registration act.** A clause nothing can discharge is registrable — the firm has one, in
> PREREG-002's clause 5 — but registering it means writing `''` into a column, deliberately, under
> a grant, in a row that is hashed and sealed. **It is no longer a sentence inside a paragraph
> inside a hashed string.** The evaluator then fires it on its date, every invocation, forever,
> which is what the clause says it does.

---

## 6. ITEM 2 · FORMULA-VERSUS-LITERAL DIVERGENCE · E-12 … E-15

*I-153's doctrine, binding: **"a dated clause instantiated from a formula must seal as the formula
or carry its instantiation assumptions."** PREREG-002 clause 5 declared **"the drafted date is not
binding — the formula is"** and then named a literal that, at any seal after 2026-07-28, terminates
the family with certainty. The evaluator must detect that class.*

> **E-12 · The divergence test, and it is one comparison.** For every covered site whose
> `matched_text` is an `ISO` literal: if `resolve(clause.date_expr) ≠ parse(matched_text)`, the
> site returns **`DIVERGENT`**, reporting both dates, the anchor `C` used, and the field and offset
> of each.
>
> **Worked against I-153, which is the whole point of the clause.** Site: `forward_kill_condition`,
> the literal `2027-01-31` inside clause 5. Its clause row's `date_expr` is `C + 187 days`, because
> the field's own opening sentence says the formula governs. At any `C` later than 2026-07-28,
> `resolve("C + 187 days") > 2027-01-31`, the two disagree, and the site returns `DIVERGENT` with a
> nonzero exit **on the first invocation after registration** — which, under E-24, is before any
> Gate 1 verdict can read anything else.

> **E-13 · A prose disclaimer is not a reconciliation. Only equal values are.** A field that
> contains a sentence declaring which of its two dates governs — *"the DRAFTED DATE IS NOT BINDING —
> the formula is"* — still returns `DIVERGENT`. **This is specified explicitly because PREREG-002's
> field carried exactly that sentence and clause 5 fired anyway.** The sentence told a reader which
> value to prefer; it did not remove the other value from a hashed string, and a hashed string is
> what gets sealed. **The evaluator has no code path that reads a governing-clause declaration,
> which is what makes E-13 enforced rather than promised.**

> **E-14 · Intra-field cross-check.** Independently of E-12, if a single field contains both a
> `FORMULA` site and an `ISO` site whose resolved dates differ, that field returns `DIVERGENT` at
> **both** offsets. This catches the case where the sponsor's clause rows are internally consistent
> with each other and the *field* is not — the sweep's D-4 against D-5/D-6/D-7, three literals
> contradicting the opening of the same string.

> **E-15 · Post-seal, a divergence is an escalation and never a repair.** `dated_clauses` for a
> sealed family is immutable; a change requires a successor family declaring `predecessor_family`,
> exactly as the pre-registration freeze already requires. **A divergence found post-seal routes to
> Validation.** The reason is I-153's own shape: **the conformance that removed a certain kill ran
> in the family's favour**, and a sponsor editing a clause that terminates its own family is the
> shape of act this firm exists to distrust. Pre-seal it is a draft edit and cheap. Post-seal it is
> mine.

---

## 7. ITEM 2 · DIRECTION-BLINDNESS, ENFORCED RATHER THAN INTENDED · E-16 … E-21

*The requirement is binding and its reason is measured: **the sweep found 15 of 24 clauses carrying
false premises, and §11.1's span — the one stale figure running FOR the family — survived four
revision passes.** The CIO recorded the asymmetry as: stale dates that cost the firm get found;
stale dates that favour it survive. **A checker a sponsor would be relieved to see pass is not
direction-blind.** Five mechanisms follow; none of them is a promise.*

> **E-16 · The verdict vocabulary contains no favourable member.** Closed set:
> `PENDING`, `DISCHARGED`, `FIRED`, `DIVERGENT`, `SPAN-DIVERGENT`, `ANCHOR-STALE`, `UNCOVERED`,
> `AMBIGUOUS`, `DANGLING`, `UNANCHORED`. **There is no `OK`, no `WAIVED`, no `SUPPRESSED`, no
> `BENIGN`, no `IN-FAMILY-FAVOUR`.** There is no field anywhere in the finding record in which a
> direction could be written, so there is no field a later reader could filter on.

> **E-17 · No suppression parameter exists, and a test enforces the signature rather than trusting
> it.** The entry point takes `(registry, family=None, as_of=None)` and nothing else.
> `test_dce_17` asserts, via `inspect.signature`, that no parameter name of the evaluator or of any
> public function in its module matches
> `(?i)ignore|skip|allow|waive|suppress|exempt|except|only|severity|priority`.
> **This is the clause that makes E-16 hold under maintenance pressure**: the natural first request
> after this lands will be a way to silence one finding, and the request will arrive with a good
> reason. The answer is that the *document* changes, not the checker's configuration, and a test
> refuses the alternative at collection time.

> **E-18 · No severity, no ranking, one consequence class.** Every finding carries the same weight;
> the evaluator emits no ordering by impact and no per-finding priority. **All ten verdicts other
> than `PENDING` and `DISCHARGED` exit nonzero.** A finding cannot be de-prioritized because there
> is no priority to set.

> **E-19 · Report order is `(family, field, source_offset)`, never verdict order.** `test_dce_19`
> builds a fixture whose clause rows are inserted in a permuted order and whose findings span
> several verdicts, and asserts the emitted order is offset order. **The shape of the report
> encodes nothing about direction or severity**, so a reader skimming the top of the output is not
> being shown the sponsor-relevant findings first.

> **E-20 · The mirror-pair obligation, and it is enforced at collection.** Every fixture in
> `test_dated_clause_evaluator.py` whose divergence runs **against** the family is named
> `fx_<name>_against` and **must** have an arithmetic mirror `fx_<name>_for` constructed so the
> same magnitude of error runs **in the family's favour**. `test_dce_20` reads the fixture module
> with `inspect.getmembers`, asserts the pairing is total in both directions, and asserts for every
> pair that **the verdict and the exit code are identical.** A fixture added without its mirror is
> a test failure, not a review comment.

> **E-21 · The proof case is §11.1's span, and it is a required test.** The stated `6.571 years`
> over `[2020-01-01, C]` is **measured to 2026-07-28 and understated at every later `C`** — the one
> stale figure the four revision passes did not catch, precisely because catching it would have
> cost the family nothing. `test_dce_21` registers that exact span with `C` at a later date and
> asserts **`SPAN-DIVERGENT`, exit 3** — and its mirror overstates the span by the identical number
> of days and asserts the identical verdict and the identical exit code. **If the evaluator returns
> anything other than the same answer twice, it is not direction-blind and this test says so.**

---

## 8. ITEM 2 · EXIT CODES, INVOCATION, AND THE NAMED BOUNDARY · E-22 … E-25

> **E-22 · Exit codes, on the pattern the merge script proved** (`0` clean / `1` usage / nonzero
> distinct code per substantive finding class):
>
> | Code | Condition |
> |---|---|
> | `0` | every site `PENDING` or `DISCHARGED` |
> | `1` | usage or I/O — registry absent, family unknown, malformed `--as-of` |
> | `2` | any site `FIRED` |
> | `3` | any site in the divergence set — `DIVERGENT`, `SPAN-DIVERGENT`, `ANCHOR-STALE` |
> | `4` | any site in the inability set — `UNCOVERED`, `AMBIGUOUS`, `DANGLING`, `UNANCHORED` |
>
> **The exit code is the maximum over sites and the ordering is 4 > 3 > 2 > 0, with the reason
> stated because it is not obvious:** this seat ranks *epistemic state*, not *consequence*, because
> consequence is E-25's boundary and this evaluator does not evaluate it. **Inability to evaluate
> outranks a known firing** — a firing is a fact the firm has, and an unevaluable clause is a fact
> the firm does not have. **Every site is printed at every exit code**; the code is a summary, never
> a filter.

> **E-23 · Nonzero is nonzero.** No caller may branch on the specific code to proceed —
> *"only a 3, so continue"* is forbidden to the Friday ritual, to any script that shells out, and to
> any seat reading the output. The code exists to tell a reader **which** class to look at first,
> not **whether** to look. Binding on `STANDING-ORDER-002` §6, which is where this evaluator retires
> the class-(b) label it currently carries.

> **E-24 · Invocation, and the interlock with Item 1.**
> ```
> python3 harness/scripts/evaluate_dated_clauses.py [--registry-db PATH] [--family F] [--as-of ISO]
> ```
> **The evaluator writes nothing.** It opens the registry through R-1's read-only default, takes no
> grant, and its artifact is stdout plus an exit code, pasted into the ritual record. This is not
> an accident of design: a checker that writes to the store it is checking is a checker with an
> authority it does not need, and **Item 1 and Item 2 compose here — the read-only default is what
> lets the evaluator run with no grant at all.** `--record`, if Seat 9 is later asked for it,
> requires a `LOG_EVENT` grant and is not in this specification.
>
> **Gate teeth:** `evaluate_gate1` runs the evaluator for the family under evaluation. **A nonzero
> exit makes the Gate verdict `INSUFFICIENT-DATA`** and the evaluator's full finding table is
> reproduced in the Validation Report, unfiltered.
>
> **`--as-of` is a suppression vector and is handled as one.** An as-of earlier than the family's
> seal date is **refused, exit 1**. Any as-of other than wall-clock stamps **`AS-OF OVERRIDE`** on
> the header and on **every line** of the report, and `evaluate_gate1` never passes one. This is
> mitigation by marking, not by prevention, and it is filed as I-162 rather than described as
> closed.

> **E-25 · THE NAMED BOUNDARY — what this specification deliberately does not cover.**
>
> 1. **The consequence of a firing.** The evaluator reports **that** a clause fired and **never
>    what a firing does.** Termination, downgrade to ADMITTED-AS-EXPLORATORY, notification: not
>    evaluated, not stored in `dated_clauses`, not inferred from `kind`. **A checker that executed
>    consequences would be deciding a family's fate from a regex**, and the firm's answer to
>    "who terminates a family" is not a column.
> 2. **The sponsor remediation workflow.** What a sponsor does with an `UNCOVERED` finding, and in
>    what document, is the Director's and is not here.
> 3. **The document-side clause surface.** The evaluator reads the registry (E-1). A dated clause
>    living only in `PREREG-002` §11.4's R3 table — the sweep's D-8/D-9 — is caught **only insofar
>    as the corresponding registry field carries it.** Prose that never reaches a registered field
>    is outside this control, and that is a real gap, stated rather than hidden: **the remedy is
>    that clauses must be registered, not that the checker must learn to read documents.**
> 4. **Multi-family portfolio sweep** beyond iterating registered families with identical
>    per-family mechanics.

---

## 9. WHAT SEAT 9 IMPLEMENTS MECHANICALLY VS. WHAT ROUTES BACK

### 9.1 Mechanical — implement as written, no consultation

| Clauses | Why mechanical |
|---|---|
| **R-1 … R-8** | One URI string, three method-entry guards, one context manager with a `finally`, one nesting flag. Every error type and its message content is stated. |
| **R-9 … R-14** | One table DDL given in full, one column on three tables, one closed vocabulary table, one sha256 over a stated concatenation in a stated order. |
| **R-15 / R-16** | A stated return dict, four SQL counts, one watermark comparison, four report fields. |
| **R-17** | A guard call at the head of the vault methods that already exist. |
| **E-2 / E-3 / E-7 / E-9** | Three regexes given, one offset tuple, day/month/year arithmetic with the constants named (`365.2425`, `30.4368`, end-of-month clamping stated). |
| **E-5 / E-6** | One table DDL given in full and a four-way join outcome given as a table. |
| **E-8 / E-10 / E-12 / E-14** | Date equality comparisons against stated inputs, and one event-existence query. |
| **E-16 / E-18 / E-19 / E-22** | A closed verdict set, a sort key, a max over a stated code table. |
| **E-24** | One argparse front end, one refusal condition, one header stamp. |

### 9.2 Judgment calls — route back to me before implementing

| Trigger | Why it is not the implementer's |
|---|---|
| **A `reason` needed that is outside R-10's vocabulary.** | Extending the vocabulary is a specification act. Do not add a member to make a script run. The request itself tells me a write class exists that I did not anticipate. |
| **Any real family whose `dated_clauses` cannot claim every extracted site** (E-6). | That is a sponsor problem surfacing as an implementation problem. Do not add a wildcard claim, a `covers_all` flag, or an offset range. |
| **Any proposal to make an `UNCOVERED` finding exit 0** — including "only when the site is in `statement`", "only when the date is in the past", or "only during migration". | This is E-6's whole content and the first request that will arrive. The answer is no and the request is a finding. |
| **Any proposal for a suppression, allow-list, or severity parameter** (E-17). | Same, one layer up, and `test_dce_17` refuses it mechanically so the conversation happens before the code. |
| **A `kind` outside `{OBSERVATION, DEADLINE, PRECEDENT}`.** | Closed by E-5. A fourth kind is a specification act. |
| **Any request to exempt the vault from R-17 because file guards are awkward.** | I-160 already records that the vault's control is weaker than the registry's. Making it weaker still is mine. |
| **Any request to grandfather rows above R-16's watermark.** | The amnesty is bounded and non-re-issuable by construction. |
| **Any test in either new test file that cannot be met as specified.** | Ruling 004 §11's standing term, which binds me as hard as Seat 9: escalate in writing, do not amend. It has caught a Validation-authored defect three times this sprint (I-058, I-070, I-065). |

---

## 10. TEST INVENTORY AND THE INTENDED RED STATE

Two new files. **Seat 9 does not modify any test in either file under any circumstances.**

**`harness/tests/test_registry_write_grant.py`** — 19 tests, **19 red today [measured]**.

| ID | Property | Grades |
|---|---|---|
| `test_rwg_01` | a fresh `TrialRegistry(path)` holds a `mode=ro` handle | R-1 |
| `test_rwg_02` | opening a SQLite file carrying none of the registry's tables does **not** create them, and construction succeeds against a filesystem-read-only file | R-2 |
| `test_rwg_03` | a missing path raises `RegistryNotInitializedError` and creates no file | R-3 |
| `test_rwg_04` | `log_trial` with no grant raises `RegistryWriteNotGrantedError` **before** any SQL runs | R-4 |
| `test_rwg_05` | ditto `open_hypothesis`, `log_event` | R-4 |
| `test_rwg_06` | `registry.conn.execute("INSERT …")` with no grant raises at **execute**, not commit | R-5 |
| `test_rwg_07` | a grant admits its own write and the row lands | R-6 |
| `test_rwg_08` | on normal exit the handle reverts to read-only; a subsequent write raises | R-6 |
| `test_rwg_09` | on exception inside the block the handle reverts and the write is rolled back | R-6 |
| `test_rwg_10` | nesting raises `RegistryWriteGrantNestedError` | R-7 |
| `test_rwg_11` | absent token and absent env var raises; env var alone suffices | R-9 |
| `test_rwg_12` | a `LOG_EVENT` grant refuses `open_hypothesis`, naming both reasons | R-10 |
| `test_rwg_13` | an out-of-vocabulary `reason` raises `RegistryWriteGrantMalformedError` | R-10 |
| `test_rwg_14` | the `write_grants` row is the lowest-rowid write of its own grant | R-12 |
| `test_rwg_15` | the chain verifies across three grants; editing row 2 breaks it | R-13 |
| `test_rwg_16` | a raw `sqlite3.connect` INSERT yields `grant_id IS NULL` and `audit_write_grants` reports it as an orphan | R-14 / R-15 |
| `test_rwg_17` | `evaluate_gate1` on a registry with one orphan returns **overall INSUFFICIENT-DATA** and prints `chain_head` and orphan counts **even when zero** | R-15 |
| `test_rwg_18` | a second `MIGRATION` grant cannot raise the watermark | R-16 |
| `test_rwg_19` | `VaultWriteNotGrantedError` exists and `HoldoutVault.seal()` opens with the guard. **R-18 / I-160 is deliberately NOT tested as a prevention**, because it is not one: a caller holding a vault object can open `vault._payload_path` directly and the guard never runs. A test asserting a property the design does not have would be worse than the gap it hid | R-17 / R-18 |

**`harness/tests/test_dated_clause_evaluator.py`** — 26 functions / 28 collected items,
**27 red today [measured]**. The one green is `test_dce_20`, the mirror-pair meta-test, which grades
this file's own discipline rather than the harness and is correctly green from the moment it is
written — it turns red the first time a fixture is added without its mirror.

| ID | Property | Grades |
|---|---|---|
| `test_dce_01` | every field in E-1 is scanned; a date in `mechanism` is found | E-1 |
| `test_dce_02` | the three recognizers find ISO, formula and span sites at correct offsets | E-2 / E-3 |
| `test_dce_03` | `C` comes from `forward_window_start`, else the seal event; never from prose | E-4 |
| `test_dce_04` | a family with neither returns `UNANCHORED`, exit 4 | E-4 |
| `test_dce_05` | an unclaimed site returns `UNCOVERED`, exit 4 | E-6 |
| `test_dce_06` | two rows claiming one offset return `AMBIGUOUS`; a row claiming no site returns `DANGLING` | E-6 |
| `test_dce_07` | `C + 187 days` resolves by exact day arithmetic; `+N months` clamps end-of-month | E-7 |
| `test_dce_08` | a `forward_window_start` literal differing from the seal date returns `ANCHOR-STALE` | E-8 |
| `test_dce_09` | a past date with no discharge event returns `FIRED`, exit 2 | E-10 |
| `test_dce_10` | a discharge event at or before the date returns `DISCHARGED`, exit 0 | E-10 |
| `test_dce_11` | a discharge event **after** the date still returns `FIRED` | E-10 |
| `test_dce_12` | empty `discharge_event_kind` fires unconditionally on its date | E-11 |
| **`test_dce_13`** | **I-153 reproduced**: `date_expr = "C + 187 days"`, literal `2027-01-31`, `C = 2026-08-12` → `DIVERGENT`, exit 3 | E-12 |
| **`test_dce_14`** | **the same fixture with the governing sentence *"the drafted date is not binding — the formula is"* verbatim in the field → still `DIVERGENT`** | E-13 |
| `test_dce_15` | one field carrying a formula and a contradicting literal returns `DIVERGENT` at both offsets | E-14 |
| `test_dce_16` | the verdict vocabulary contains no favourable member (module constant asserted equal to E-16's set) | E-16 |
| `test_dce_17` | **signature test** — no parameter matches the suppression regex | E-17 |
| `test_dce_18` | no finding record carries a severity or priority field | E-18 |
| `test_dce_19` | permuted insertion yields offset-ordered output | E-19 |
| `test_dce_20` | **mirror-pair meta-test** — the `fx_*_against` / `fx_*_for` pairing is total in both directions | E-20 |
| `test_dce_20b` | **×3, parametrized** — each pair returns the identical verdict **and** the identical exit code by direction | E-20 |
| **`test_dce_21`** | **§11.1's span** — `[2020-01-01, C]` stated `6.571 years` at a later `C` → `SPAN-DIVERGENT`, exit 3, identically to its overstating mirror | E-9 / E-21 |
| `test_dce_22` | a run containing both a `FIRED` and an `UNCOVERED` site exits **4**, not 2 | E-22 |
| `test_dce_23` | the evaluator takes no grant and the registry's event count is unchanged by a run | E-24 |
| `test_dce_24` | `--as-of` below the seal date raises; an override stamps `AS-OF OVERRIDE` on the render | E-24 |
| `test_dce_25` | a nonzero clause evaluation makes the Gate verdict `INSUFFICIENT-DATA` and the code is on the report | E-24 |

### 10.1 The names these tests bind — Seat 9 must use exactly these

| Name | Where | Shape |
|---|---|---|
| `RegistryNotInitializedError`, `RegistryWriteNotGrantedError`, `RegistryWriteGrantNestedError`, `RegistryWriteGrantMalformedError` | `castellan.registry` | exception classes |
| `VaultWriteNotGrantedError` | `castellan.holdout` | exception class |
| `TrialRegistry.write_grant(*, reason, dispatch, token=None)` | `castellan.registry` | context manager |
| `TrialRegistry.audit_write_grants()` | `castellan.registry` | R-15's dict, with `orphan_rows` keyed by table (lists of rowids; the Gate report's twin field carries **counts**) |
| `TrialRegistry.register_dated_clause(*, family, tag, field, source_offset, kind, date_expr, discharge_event_kind)` | `castellan.registry` | write, `REGISTER_HYPOTHESIS` grant |
| `TrialRegistry.dated_clauses(family)`, `TrialRegistry.seal_dated_clauses(family)` | `castellan.registry` | read; and the `clauses_sha256` seal of E-5 |
| `castellan.dated_clauses` | new module | `VERDICTS` (frozen set), `extract_clause_sites(field, text)`, `resolve_date_expr(expr, C)`, `evaluate_dated_clauses(registry, family=None, as_of=None)` |
| report object | returned by `evaluate_dated_clauses` | `.findings` (each with `.family .field .source_offset .matched_text .recognizer .verdict .detail .sentence`), `.exit_code`, `.anchor_C`, `.as_of_override`, `.render()` |
| `ValidationReport` additions | `castellan.gates` | `write_grant_chain_head`, `write_grant_chain_intact`, `write_grant_orphan_rows`, `dated_clause_exit_code` |

**Measured state on delivery of this specification: 272 passed / 50 failed / 322** — 271/4/275
before, plus 47 collected items of which **46 are red** and one (`test_dce_20`) is green by design.
**Intended state after Seat 9's implementation: 318 passed / 4 failed / 322** — the 4 being the
pre-existing failures and nothing else. Those 4
(`test_G2_oos_index_calendar_span_used_and_reported`, `test_mbs_12`, `test_h7`, `test_h8`) are
unrelated to this specification, already filed (I-076 and the I-078 class), and **are not
addressed, touched, or counted as this spec's** — they remain failing after Seat 9's work and their
count is quoted separately at every checkpoint so the two sets never merge.

---

## 11. LEAKAGE AUDIT

Run on this specification itself, per my standing obligation. **This document produces no
performance number**, so criteria 1–7 have no signal to attach to; they are answered anyway because
an unrun audit is not a passed audit.

| # | Check | Finding |
|---|---|---|
| 1 | any field filtering on `event_time` rather than `knowledge_time` | **n/a** — no price or fundamental field is read. E-10's discharge test filters on `events.created_utc`, which is a `knowledge_time` by construction: it is when the event was *written*, not when the fact became true. |
| 2 | restated fundamentals | **n/a** — no fundamentals. |
| 3 | survivorship contamination | **n/a** — no universe. |
| 4 | retroactive split/dividend adjustment | **n/a** — no prices. |
| 5 | same-bar fill | **n/a** — no fills. |
| 6 | purged k-fold with 1% embargo where standard k-fold was used | **n/a** — no CV. |
| 7 | argmax rather than plateau centroid | **n/a** — no parameter surface. **E-9's tolerance (`0.5%` or one day-equivalent) is the only free constant in this document; it is stated in the clause, not tuned, and no fixture selected it.** |
| 8 | **was the holdout consulted, in any form, before this evaluation** | **NO.** `book/vaults/` holds only `.gitkeep` [measured] and was not opened, read, listed for content, or referenced. R-17 specifies a guard on vault methods and **runs none of them.** No `HoldoutVault` was constructed. No passphrase exists in this session. |

**One leakage-adjacent property this specification creates rather than audits, stated here because
it belongs nowhere else:** E-24 makes the dated-clause evaluator a **read-only** consumer of the
registry. A checker that wrote to the store it checks could, in principle, discharge a clause by
running — and that is an information leak from the evaluation into the thing evaluated. **It is
foreclosed by construction, not by discipline.**

---

## 12. ISSUES FILED · I-160 … I-166

| ID | Title | Sev | Owner |
|---|---|---|---|
| **I-160** | The vault's write guard has one layer where the registry has two — a caller holding a vault object can write `vault_dir` around the guard, and only the state/directory divergence detects it (R-18) | **MEDIUM** | quant-validation → Seat 9 |
| **I-161** | I-103 recurs at the write grant: a seat that can run `python3` can mint its own token, so the grant is attributable by declaration and authenticates nobody (§4.1 A3, §4.4) | **MEDIUM** | quant-validation → Principal (disclosure; **no fix requested**) |
| **I-162** | `--as-of` is a suppression vector on a checker specified to have none; mitigated by refusal below the seal date and by an `AS-OF OVERRIDE` stamp on every line — **marking, not prevention** (E-24) | **MEDIUM** | quant-validation |
| **I-163** | R-16's migration amnesty is permanent for the 1 pre-existing event row in `book/registry.db`, which will carry `grant_id IS NULL` forever; bounded by watermark, recorded in the granting row, non-re-issuable | **LOW** | quant-validation → Seat 9 |
| **I-164** | Under E-6, **19 of PREREG-002's 24 dated clauses land `UNCOVERED`** — the evaluator's first real run against that family is an **exit 4, not an exit 0**, and that is the correct answer, recorded now so it is not read as a regression when it happens | **MEDIUM** | director-of-research |
| **I-165** | R-15 and E-24 make a whole Gate report `INSUFFICIENT-DATA` on conditions outside §4.4's criterion table (write-provenance breakage; a nonzero clause evaluation). Inside this seat's mandate (§4.4 of this document), **disclosed because a rule that voids a report should be visible before it fires** | **MEDIUM** | quant-validation → Principal (disclosure) |
| **I-166** | R-10's `reason` vocabulary and E-5's `kind` vocabulary are closed and will be hit by real work; the route-back is specified (§9.2) but the first hit will arrive as schedule pressure | **LOW** | quant-validation |

**Not filed and deliberately so:** the 4 pre-existing suite failures. They are I-076's and the
I-078 class's, they are open, and re-filing them under new numbers would inflate this dispatch's
finding count with someone else's work.

---

## 13. ADDRESSED TO THE PRINCIPAL

**1 · The `f54f9b9` status line needs a second correction when this lands, and I am naming its text
now so it is not written by whoever ships the code.** S3-D-009 corrected it once, to say the denies
covered a path nobody uses. The line after this fix is **not** "registry and vault are
write-protected." It is:

> *Registry and vault are read-only by default. Writes require a typed, block-scoped grant that
> records itself in the registry. Raw-path writes are detected, not prevented. The grant is
> attributable by declaration and authenticates nobody.*

**A remedy for a misaimed control, described as more than it is, would be I-095's successor.**

**2 · R-15 has teeth that will be felt before they are appreciated.** A registry carrying one orphan
row — one raw `sqlite3` INSERT by any seat, at any time, for any reason — makes **every subsequent
Gate report INSUFFICIENT-DATA** until it is explained. That is the correct rule and I am not
softening it. It is also an operational consequence the firm has not lived with before, and the
first time it fires it will fire on a Friday. **The Principal should know the rule exists before it
costs a Gate evaluation, which is why it is I-165 and why it is here.**

**3 · I-153's C13(k) ruling is still owed by me and this document does not discharge it.** This
specification builds the checker that catches I-153's *class* (E-12, E-13, `test_dce_13`,
`test_dce_14`). It does not rule on I-153's *instance* — whether PREREG-002 seals `C + 187 days` or
the literal `2027-01-31` as drafted. **That ruling runs in the family's favour either way it is
argued and is therefore not the sponsor's; it remains mine and remains outstanding.** It should not
be read as answered because a checker for its class now exists.

---

## 14. WHAT CLOSES AND WHAT DOES NOT

**Closes on Seat 9's implementation and a green suite:** I-095 (the code-layer remedy the Principal
ruled at S3-D-009), and **I-135**'s standing finding that no harness path evaluates a kill condition
on any date for any family. `STANDING-ORDER-002` §6 item 2 (dated-clause review) reverts from class
(b) to class (a); §6 item 3 (I-095 gap review) retires.

**Does not close:** I-103 / I-161 — no fix is requested and none is proposed. I-153's instance.
I-160's vault asymmetry, which is disclosed and accepted rather than remedied. E-25's boundary:
consequence semantics, remediation workflow, and the document-side clause surface remain
unaddressed and are named as such.

**Verified at close [measured]:** `book/registry.db` — 0 hypotheses / 0 trials / 1 event. No
`harness/castellan/` file modified. `book/vaults/` untouched. No `research/PREREG-002-*` or
`DIR-RESTATE-*` file touched. No backtest, no hypothesis, no trial, no commit.

---

*Head of Quantitative Validation · Castellan Capital · 2026-08-12 · Dispatch S3-D-011 row 1.*
*Red-first. Trial budget ZERO. The prior is guilt.*
