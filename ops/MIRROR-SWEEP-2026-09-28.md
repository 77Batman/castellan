# MIRROR SWEEP · 2026-09-28

**Scope:** S5-D-001, Execution & Operations seat (generic-agent workaround I-372, one Sonnet unit).
**Method:** `git ls-files` (265 tracked files) and `git log --format='%H %s%n%b'` (202 commits, full
messages) swept for the six categories below. **Report only — nothing changed, nothing deleted,
nothing redacted in place.** No secret value is reproduced here; each finding gives file, line, and
the CLASS of thing found, value redacted.

**Disposition authority:** the Principal. This seat has no `git commit`, `git add`, remote, or delete
access under this dispatch's hard stops, and would not exercise it here regardless.

---

## Severity summary

| Severity | Count | Categories |
|---|---:|---|
| HIGH | 0 | — |
| MEDIUM | 2 | book/vaults/*/spec.json tracked and unexcluded (§6) · HARNESS_INTERNAL_TOKEN hardcoded literal (§3) |
| LOW | 3 | Principal's local account name in tracked paths (§4) · named mirror recipient in a tracked file (§4) · unrelated side-project bundled in the tree (§5) |
| CLEAN | 2 | VPS address (§1) · WRDS identifiers/artifacts (§2) |

---

## 1 · VPS address — CLEAN

No literal hostname, IP address, or `user@host` for the capture box was found in any tracked file or
any commit message. Every reference to the box uses a placeholder: `<droplet-ip>`, `<vps-host>`, or
the shell variable `$DROPLET` (never assigned a literal value in a tracked file).

Checked: `deploy/polymarket-capture-vps/*`, `research/DATA-INFRA-002-vps-capture-migration.md`,
`harness/castellan/capture_merge.py`, `harness/scripts/*capture*.py`, `logs/DECISION_RECORD.md`,
`logs/ISSUE_LOG.md`, and a full-tree regex sweep for IPv4-shaped strings (excluding version numbers,
`0.0.0.0`, `127.0.0.1`) — no hits. Commit messages report VPS coverage percentages and event
timestamps (e.g. "VPS 98.43% over 865h") but never an address.

## 2 · WRDS identifiers and metadata artifacts — CLEAN

Exactly one hit for "WRDS" in the entire tracked tree and commit history: `logs/DECISION_RECORD.md`
line 7478, inside the Principal's own S5-D-001 exclusion-list instruction (*"WRDS identifiers and any
WRDS metadata artifact"*) — i.e. the category name itself, not an identifier. No WRDS username,
library name, table name, or downloaded metadata file exists anywhere in the tracked tree or in any
commit message.

## 3 · Credentials of any kind — CLEAN, with two items to disclose

No password, API key value, private key block, `.env` file with populated values, or connection
string was found in any tracked file or commit message. `ops/watchtower/.env.example` is tracked and
declares four variable **names** only (`OPENAI_API_KEY=`, `PINECONE_API_KEY=`, `PINECONE_INDEX=`,
`N8N_ENCRYPTION_KEY=`) with no values — this is a template, clean. `ops/watchtower/.claude/settings.json`
is tracked and actively **denies** reading `.env` files and printing the relevant env vars — a control,
not a leak.

Two items disclosed for the Principal's own judgment, neither an exploitable secret:

- **MEDIUM · `harness/castellan/registry.py:121`** — `HARNESS_INTERNAL_TOKEN = "<hardcoded literal>"`.
  Class: a fixed, non-secret sentinel string used by the harness itself to authorize its own internal
  registry writes (contrasted with `CASTELLAN_REGISTRY_WRITE`, a caller-supplied dispatch-id string,
  also never a secret — see `harness/castellan/registry.py`'s own docstring, "Never a secret"). It
  authenticates nothing outside this repo and is required in source for the harness to run. Flagged
  because it is a literal matching the word "token," not because it grants access to anything external.

- **MEDIUM · `book/vaults/*/verifier.json` (4 files)** — Class: a salt + one-way SHA-256 hash used to
  verify the Principal's Gate-1 holdout passphrase without storing it. **Already on the Principal's own
  exclusion list** (`logs/DECISION_RECORD.md:7478`), and correctly so: I-369 (already filed, open) records
  that this is a single salted SHA-256 rather than a password-hardening KDF, which is an offline-crackable
  construction if published. This sweep did not find any additional occurrence of these values outside
  the four `verifier.json` files themselves.

## 4 · Personal information — LOW, two items

Not clean, but nothing found rises above LOW: no third-party real name, no personal email address
(the only email-shaped strings in the tree are `r1@example.invalid` … `r4@example.invalid` placeholders
in `ops/watchtower/template-audit/pass2/`), no phone number.

- **LOW · the Principal's own local machine account name in tracked file paths.** The string
  `<user>` (the Principal's local macOS account, distinct from "the Principal" or "Datis" as
  used deliberately in `FUND_CHARTER.md`/`CLAUDE.md`) appears embedded in absolute file paths in eleven
  tracked files, incidentally rather than deliberately — e.g. `deploy/pit-snapshot/run_snapshot_and_health.sh:16`,
  `deploy/pit-snapshot/capital.castellan.pit-snapshot.plist` (multiple lines), `logs/capture/polymarket-book.err`
  (Python tracebacks), `logs/ISSUE_LOG.md:7906`, `research/DATA-IMPL-011-checklist-grant-step.md:117`,
  `research/work/extract_dated_sites.py:14,130`, and six log files under
  `ops/watchtower/template-audit/pass2/runs/`. This is the Principal's own identifier, not a third
  party's, and its presence is a byproduct of local paths captured in error output and launchd plists
  rather than a deliberate disclosure. Distinct from the deliberate, already-public "Datis" in the
  Charter text, which this seat does not treat as a finding.

- **LOW · the mirror's named recipient appears in a tracked file.** `logs/DECISION_RECORD.md:7472`
  (the S5-D-001 entry that dispatched this sweep) names "a CIBC trading-technology reviewer" as the
  mirror's intended reader. This is already committed, in a file this dispatch may not edit, and will
  be visible in the mirror to the person it names. Recorded here only so the Principal sees it named
  plainly before tonight's publish.

## 5 · Stray personal notes and commit messages that read badly — CLEAN, one contextual observation

All 202 commit subject lines and a full-text scan of commit bodies for informal/frustration language
were reviewed. Every hit from an automated profanity/frustration-word scan was a false positive
(substring matches of "ugh" inside "though"/"through"). Commit messages are uniformly dense and formal,
in the repository's own house style — including messages that are sharply self-critical
(*"I-100 INCIDENT: R-4 locks the firm out of its own registry"*, *"S4-D-031 result: THE FEASIBILITY GATE
DID NOT CLOSE"*) — which this seat reads as the firm's documented candor, not as something that reads
badly to an outside reader. No personal notes, drafts, or scratch commentary outside the firm's own
register were found.

**One contextual observation, not a secrets finding:** `ops/watchtower/` (74 tracked files) is a
separate, Charter-governed program — an n8n-template security audit, with its own decision-record
entries (`S3-D-004`, `S3-D-007` in `logs/DECISION_RECORD.md`) — bundled in this repository but
unrelated to Castellan's trading operations. Nothing secret was found in its 74 tracked files (checked
directly, including its run logs and API-interaction transcripts). Flagged only so the Principal can
decide whether a trading-technology reviewer should see an unrelated security-research program in the
same mirror; this is a scope question, not a leak.

## 6 · What is tracked under `book/` beyond `*/verifier.json`

The Principal's exclusion list names `*/verifier.json`. Everything else currently tracked under `book/`:

| Path | Content | Assessment |
|---|---|---|
| `book/book.db` | Paper book — cash, positions, orders/executions/trades tables | Book of record (Charter A3); the artifact the mirror exists to show. Currently USD 10,000,000 cash, zero positions, zero of each blotter row. |
| `book/registry.db` | Trial registry — hypotheses, trials, events, write_grants, dated_clauses | Book of record; no credential material found on inspection. |
| `book/polymarket_universe.json` | Market universe bookkeeping (31.7 KB) | No credentials found. |
| `book/polymarket_merge_state.json` | Capture-merge watermark timestamps | No credentials found. |
| `book/.gitkeep`, `book/vaults/.gitkeep` | Empty placeholders | Inert. |
| **`book/vaults/*/spec.json` (4 files)** | **Not on the named exclusion list.** Per-vault holdout metadata: cutoff date, dataset id, query semantics (date bounds, fields, loader), schema fingerprint, `sealed_by`, `sealed_utc`. **No passphrase or cryptographic material** — but does disclose the exact holdout cutoff (`2026-09-15`) and window definition in the clear. | **MEDIUM — flagged under §6 specifically because the Principal's list did not name it.** Whether disclosing the holdout's exact boundary before Gate 1 is acceptable is a call this seat is not positioned to make; recorded so the Principal makes it deliberately rather than by omission. |
| `book/vaults/*/verifier.json` (4 files) | Already covered at §3/§6 lead — on the exclusion list. | Excluded, correctly. |

No other file or directory under `book/` is tracked.

---

## What this sweep did not do

Did not inspect the working tree's currently-uncommitted changes (`book/polymarket_universe.json`,
`logs/DECISION_RECORD.md`, `logs/ISSUE_LOG.md`, `logs/capture/polymarket-book.{err,out}` all show
modifications as of this session) beyond what `git ls-files`/`git log` already surfaced — those diffs
are pre-mirror working state, not yet committed history, and this sweep's mandate was tracked files and
commit messages. If the Principal commits before mirroring, a second pass over the new diff is cheap
insurance.

Did not open `book/book.db` or `book/registry.db` row-by-row beyond the queries reported above (cash,
position/order/execution/trade counts; table list) — a full dump was judged unnecessary given both are
databases of the firm's own governed state, not free-text fields where a stray secret could hide, and
the Principal's exclusion list did not ask for one.

## Findings filed

One finding from this seat, filed against the dispatch brief's own citation rather than a repository
defect — see the return to the CIO for detail. Filed as **I-397, LOW** (`logs/ISSUE_LOG.md`).
