# DATA-IMPL-012 — the vault's three placeholder arguments, `funding-carry-conditioning-002`

**Seat:** Head of Data & Infrastructure · **Dispatch:** S4-D-015 · **Issue range:** I-330 … I-339
**Clears:** the executability half of I-325. **Touches:** nothing under `book/`, `harness/castellan/`,
`VALIDATION-*`, `REDTEAM-*`. No `open_hypothesis`, no `seal()`, no passphrase. Read-only against
`book/pit.db` (`file:...?mode=ro`) and read-only against `book/registry.db`.

## 0. The vault count — item 6 and the block's own comment are both wrong

`HoldoutVault.seal()` and `PITStore.set_holdout_ceiling()` each take one `dataset_id: str` per call,
and the D2 ceiling is looked up by exact `(source, symbol)` match, no wildcard
(`data.py` `_active_ceilings`, `WHERE source=? AND dataset_id=?`). One `seal()` call therefore
protects exactly one `(source, dataset_id)` pair — confirmed convention, not my invention:
`DATA-IMPL-001-p1-vault.md` §4(1), *"the vault's `dataset_id` argument is passed straight through as
`symbol`."* `book/pit.db`, read directly, holds **two symbols per source** in the BTC/ETH universe:

| source | symbol (= dataset_id) | fields present | rows |
|---|---|---|---|
| `binance` | `BTC/USDT` | close, high, low, open, volume | 2,416 (2020-01-01 → 2026-08-12) |
| `binance` | `ETH/USDT` | close, high, low, open, volume | 2,416 |
| `binanceusdm` | `BTC/USDT:USDT` | close, funding_rate, high, low, open, volume | 8,330 |
| `binanceusdm` | `ETH/USDT:USDT` | close, funding_rate, high, low, open, volume | 8,330 |

**C8 requires four vaults, not one and not two.** Item 6 ("the vault," singular) is wrong. The block's
own comment (`# a second vault for source="binanceusdm"`) is also wrong — it splits spot from perp but
not BTC from ETH within either source. `instrument_identity` as drafted spans two symbols per source in
one string; that is fine as prose, but `dataset_id`/the ceiling machinery cannot follow it, because a
single string cannot equal both `"BTC/USDT"` and `"ETH/USDT"`. **Filed I-330, HIGH.**

## 1. The three values, in `seal()`'s exact form — one row per vault

```python
dataset_id: str          # binding, exact
query_semantics: dict     # binding, exact
schema_fingerprint: dict  # binding, exact
```

**Vault A — `binance` / `BTC/USDT` (spot):**
```python
dataset_id = "BTC/USDT"
query_semantics = {
    "loader": "castellan.loaders.fetch_ccxt_ohlcv",
    "timeframe": "1d",
    "fields_requested": ["open", "high", "low", "close", "volume"],
    "date_bounds": {"since": "2020-01-01T00:00:00Z", "until": "cutoff C, open-ended forward"},
    "filter_predicates": "none beyond (exchange_id, symbol, timeframe); every bar ccxt returns "
                         "for that tuple since `since` is ingested unfiltered",
}
schema_fingerprint = {
    "columns": ["close", "high", "low", "open", "volume"],
    "dtypes": {"close": "float64", "high": "float64", "low": "float64",
               "open": "float64", "volume": "float64"},
}
```

**Vault B — `binance` / `ETH/USDT` (spot):** identical to A with `dataset_id = "ETH/USDT"`;
`query_semantics` and `schema_fingerprint` unchanged (same loader, same fields, same measured dtypes).

**Vault C — `binanceusdm` / `BTC/USDT:USDT` (perp + funding):**
```python
dataset_id = "BTC/USDT:USDT"
query_semantics = {
    "loaders": ["castellan.loaders.fetch_ccxt_ohlcv", "castellan.loaders.fetch_ccxt_funding"],
    "timeframe_ohlcv": "1d",
    "funding_native_cadence": "8h exchange settlement interval, via ccxt "
                              "fetch_funding_rate_history, not resampled",
    "fields_requested": ["open", "high", "low", "close", "volume", "funding_rate"],
    "date_bounds": {"since": "2020-01-01T00:00:00Z", "until": "cutoff C, open-ended forward"},
    "filter_predicates": "none beyond (exchange_id, symbol); every OHLCV bar and every funding "
                         "print ccxt returns for that tuple since `since` is ingested unfiltered",
}
schema_fingerprint = {
    "columns": ["close", "funding_rate", "high", "low", "open", "volume"],
    "dtypes": {"close": "float64", "funding_rate": "float64", "high": "float64",
               "low": "float64", "open": "float64", "volume": "float64"},
}
```

**Vault D — `binanceusdm` / `ETH/USDT:USDT` (perp + funding):** identical to C with
`dataset_id = "ETH/USDT:USDT"`.

**Measurement, not description (§7.12):** every column/dtype above came from
`pd.read_sql(...).pivot_table(index="event_time", columns="field", values="value")` against the live
`book/pit.db`, one query per (source, symbol) pair, printed in full above — not copied from
`instrument_identity`'s prose in §21, which lists the fields but not their dtypes or column order.

**Caveat I cannot close myself:** `_schema_matches()` (`holdout.py`) does exact-order list equality
on `columns`. The order above is pandas' pivot-table default (alphabetical); it is **not** a guarantee
about what a not-yet-written Gate-1 `fetch()` will return. Whoever writes that function must match this
order byte-for-byte or a legitimate acquisition spuriously fails — a false operational block, not a
leak, but still a name-it-now problem while the fingerprint is about to freeze. **Filed I-334, MEDIUM.**

## 2. `dataset_id` — existing convention, not invented here

Convention exists and is cited, not proposed: `dataset_id` **is** the literal `symbol` string a loader
passes to `PITStore.ingest()` — `data.py` line 65's own comment (`dataset_id ... maps to symbol
above`), and `DATA-IMPL-001-p1-vault.md` §4(1). It is load-bearing, not cosmetic: `_enforce_holdout_ceiling`
looks up ceilings by the literal `symbol` argument future `ingest()` calls use, so a `dataset_id` that
does not exactly match that string (e.g. a firm-label composite like `"BTC-ETH-spot"`) would seal
successfully and then **never bind** — the D2 ceiling would silently protect nothing. This is why one
`dataset_id` cannot cover two symbols (§0).

## 3. `query_semantics` — filled to Ruling 001 §3.4's standard

§3.4 requires "fields requested, date bounds, filter predicates, expressed declaratively," and rules
that transport (URL, endpoint, pagination, API version, client library) is provenance-only and must
**not** be binding. Filled above for all four vaults on exactly that basis. Nothing in §3.4's list is
left unfillable. One thing worth stating plainly rather than assuming: `query_semantics` is **recorded**
in `spec.json` but **never read** by any harness code path — `acquire_once()` calls the caller-supplied
`fetch(spec)` callable, which may or may not actually consult `spec["query_semantics"]` to build its
request. There is no code that checks the fetch implementation against the sealed query. Enforcement is
human, at Gate 1 code review, comparing the two by eye. **Filed I-333, MEDIUM** — not a defect Ruling 001
asked to be automatic, but a declared-commitment-not-a-control fact the firm should hold before relying
on it.

## 4. `schema_fingerprint` — measured off `pit.db`, and what its own check does not catch

Values are in §1. The mechanism (§4.6 of the Charter's own "computed, not narrated" test, applied here):
`_schema_matches(df, fingerprint)` checks `fingerprint.get("columns")` against `df.columns` **only if
not None**, and iterates `fingerprint.get("dtypes") or {}` **only over the keys present**. A
`schema_fingerprint` that is non-empty but lacks the literal keys `"columns"`/`"dtypes"` — e.g.
`{"note": "todo"}` — passes `seal()`'s truthiness check (§5) and then, at Gate 1, `expected_cols` is
`None` (skip) and `expected_dtypes` is `{}` (skip): `_schema_matches` returns `(True, "")`
**unconditionally**, regardless of what the acquired frame actually contains. **Filed I-332, HIGH** —
stronger than "accepts `{}`": `seal()` does reject literal `{}` (§5), but any non-empty, wrong-shaped
dict defeats both the seal-time check and the one Gate-1 content check this field has.

## 5. What `seal()` does with an empty or placeholder value — the §4.7.2 test, run

```python
required = {"source": source, "dataset_id": dataset_id,
            "instrument_identity": instrument_identity,
            "query_semantics": query_semantics, "schema_fingerprint": schema_fingerprint}
for fname, fval in required.items():
    if not fval:
        raise HoldoutSpecInvalidError(f"seal() requires a non-empty '{fname}'")
```
(`holdout.py` lines 345–356, read directly.)

| Input | Result |
|---|---|
| `dataset_id=""` | raises `HoldoutSpecInvalidError` |
| `dataset_id="<the ingested dataset identifier>"` (the literal placeholder text) | **passes silently** — non-empty string, no format check against real symbols |
| `query_semantics={}` | raises `HoldoutSpecInvalidError` |
| `query_semantics="<the exact query, per Ruling 001 section 3.4>"` (a string, not a dict — signature says `dict` but there is no `isinstance` check anywhere in `seal()`) | **passes silently** |
| `schema_fingerprint={}` | raises `HoldoutSpecInvalidError` |
| `schema_fingerprint={"note": "todo"}` (non-empty, wrong shape) | **passes `seal()`, and later passes `acquire_once()`'s content check too** — §4 |

**Answer to the dispatch's framing directly:** `seal()` does **not** accept `query_semantics={}` — it
raises. The vault's provenance guarantee is nonetheless class (c) — a declared commitment, not a
control — for a narrower and more precise reason than emptiness: the only thing enforced is
*truthiness*, never *type* or *shape*, and for `schema_fingerprint` the one shape-dependent check that
exists (`_schema_matches`, at Gate 1, once) degrades to "nothing to check" on exactly the kind of
plausible-looking placeholder a rushed sealer would type. `query_semantics` has no shape check anywhere,
ever (§3). `dataset_id` has no check beyond non-empty, ever, and its correctness is load-bearing (§2).
Per GATES.md §4.7.2's own test — name the field the harness reads — the field the harness reads for all
three is `bool(value)`, nothing else, at seal time.

## 6. State at close

`book/registry.db`: **0 hypotheses / 0 trials**, `write_grants` **1 row** (`grant_id=1`, `MIGRATION`,
`CLEAN`) — read before and after this dispatch, unchanged; no grant opened, no write attempted.
`book/pit.db`: read-only (`?mode=ro`); no ingest, no ceiling, no vault directory created.
`book/vaults/`: unchanged, `.gitkeep` only.

## 7. Issues filed

| # | Sev | Finding |
|---|---|---|
| I-330 | HIGH | C8 requires **four** vaults (one per `(source, symbol)` pair), not one (item 6) or two (the block's own comment) |
| I-331 | HIGH | `seal()` validates `dataset_id`/`query_semantics`/`schema_fingerprint` for non-emptiness only, never type or structural content — the provenance guarantee for all three is class (c) until (partially) Gate 1 |
| I-332 | HIGH | `_schema_matches()` treats a non-empty `schema_fingerprint` lacking `"columns"`/`"dtypes"` as "nothing to check," returning `True` unconditionally — defeats the one Gate-1 content check this field has |
| I-333 | MEDIUM | `query_semantics` is recorded but never read by any harness code path; its only enforcement is human review at Gate 1 comparing the sealed spec against the `fetch()` implementation |
| I-334 | MEDIUM | `schema_fingerprint`'s `columns` check is exact-order; the order measured here is a pandas pivot artifact, not a guarantee about a not-yet-written Gate-1 `fetch()`'s output order |
| I-335–I-339 | — | unused |

## 8. Line budget

Comparator `DATA-IMPL-011`: 117 lines [measured]. Projection: ~110. **Measured, this document: 191
lines [`wc -l`]. Overrun, flagged, not trimmed.** The overrun is structural, not padding: the true vault count is
4, not the 1–2 the dispatch anticipated, which alone quadruples §1's content against a single-vault
draft; each of the two additional harness-behavior findings (§4, §5) is demonstrated against actual code
rather than asserted, per the same discipline `DATA-IMPL-011` §9 already established for this seat.
Cutting either would mean asserting a failure mode without having read the function that produces it.

## 9. Files

- `research/DATA-IMPL-012-vault-arguments.md` — this document
- Read, not edited: `research/PREREG-002-crypto-funding-basis.md` (§21), `research/REGISTRATION-PAYLOAD-PREREG-002.md` (§5, §6), `research/VALIDATION-RULING-001-holdout-regime.md` (§3.4), `reference/GATES.md` (§4.7.2), `reference/TEMPLATES.md` (§7.12), `research/DATA-IMPL-001-p1-vault.md` (§4)
- Read, not edited: `harness/castellan/holdout.py`, `harness/castellan/data.py`
- Read-only queries: `book/pit.db`, `book/registry.db`
