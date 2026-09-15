# DATA-IMPL-013 — §15 STEP 2: F-002 LEG (0) THEN LEG (III)

**Dispatch S4-D-028 · Head of Data & Infrastructure · 2026-09-15**
**Scope: §15 step 2 only — the qualifying-bar floor, then the unconditioned benchmark `R_bench`. Nothing else was run.**

---

## 1. What this document is, and is not

This is a report of **one registered trial** against `funding-carry-conditioning-002`: F-002 leg (0) (the qualifying-sample floor) and leg (iii) (whether `R_bench` clears zero net of costs), computed on a single `castellan.run_backtest` call. **It is not a Gate 1 result, not a survival claim, and not a reason to expect the family passes.** Per `PREREG-002` §5.3 R7, leg (iii) "will almost certainly not fire, and this seat records now that its non-firing is worth nothing as evidence" — the family's entire falsification burden sits on legs (i) and (ii), which this dispatch does not run (held by the CIO, §15 hard stop 1).

---

## 2. Universe run, and how it was confirmed against the sealed field

**Ran:** `binance` spot `BTC/USDT`, `ETH/USDT` long, paired against `binanceusdm` perpetual `BTC/USDT:USDT`, `ETH/USDT:USDT` short. **SOL was not queried, not loaded, and appears nowhere in the panels below.**

**Confirmation method:** read `book/registry.db :: hypotheses.universe` for `funding-carry-conditioning-002` directly (read-only connection, not narrated from the pre-reg prose) [measured]. The sealed field's text is verbatim: *"UNIVERSE: BTC/USDT and ETH/USDT spot paired against BTC/USDT:USDT and ETH/USDT:USDT perpetuals... THERE IS NO SECONDARY UNIVERSE... REASON, per I-045: [SOL funding-formula break]."* This agrees with the brief and with `PREREG-002` §6.1 and §21. **No disagreement found between the sealed `universe` field and this dispatch's brief — nothing to stop and report on that count.**

`book/pit.db` was queried directly (read-only `SELECT`) to confirm the four series are the only ones touched: `binance`/`BTC/USDT`, `binance`/`ETH/USDT`, `binanceusdm`/`BTC/USDT:USDT`, `binanceusdm`/`ETH/USDT:USDT`, each 2,416 daily `close` observations, `2020-01-01T00:00:00Z` → `2026-08-12T00:00:00Z`, zero `NaN` gaps in `close` over that span [measured]. `SOL/USDT` and `SOL/USDT:USDT` remain on disk (per §6.1's own note that dropping SOL from the universe does not require dropping it from storage) and were never passed to any loader or to `run_backtest`.

---

## 3. The exact `run_backtest` call

```python
store = PITStore("book/pit.db")   # see §7 below — NOT opened via the URI the dispatch specified
C = pd.Timestamp("2026-09-15", tz="UTC")

spot = pit_price_panel(store, "binance", ["BTC/USDT", "ETH/USDT"], C)
perp = pit_price_panel(store, "binanceusdm", ["BTC/USDT:USDT", "ETH/USDT:USDT"], C)
prices = pd.concat([spot, perp], axis=1).dropna()
idx = prices.index[prices.index <= pd.Timestamp("2026-08-11")]  # settled-only; see §5
prices = prices.loc[idx]

funding = pit_funding_panel(store, "binanceusdm", ["BTC/USDT:USDT", "ETH/USDT:USDT"], C, idx)

weights = pd.DataFrame(0.0, index=idx, columns=prices.columns)
weights["BTC/USDT"] = 0.5;         weights["ETH/USDT"] = 0.5
weights["BTC/USDT:USDT"] = -0.5;   weights["ETH/USDT:USDT"] = -0.5
# constant every day: this IS the unconditioned R_bench, w(t) ≡ 1.0 hedge
# ratio per asset, equal capital weight across BTC and ETH (§5.1, §6.1)

cost_model = {
    "BTC/USDT": CRYPTO_SPOT_TAKER,       "ETH/USDT": CRYPTO_SPOT_TAKER,
    "BTC/USDT:USDT": CRYPTO_PERP_TAKER,  "ETH/USDT:USDT": CRYPTO_PERP_TAKER,
}  # §12.8: spot leg on CRYPTO_SPOT_TAKER, perp leg on CRYPTO_PERP_TAKER, never one model for both

reg = TrialRegistry("book/registry.db", allow_create=False)

res = run_backtest(
    prices, weights, cost_model, reg,
    family="funding-carry-conditioning-002",
    config={
        "step": "S15-step2: F-002 leg(0) then leg(iii)",
        "series": "R_bench",
        "description": "Unconditioned delta-neutral long-spot/short-perp "
                        "benchmark, constant notional w=1.0, equal-weight "
                        "BTC/ETH, daily rebalance inside turnover band, "
                        "net of full cost stack.",
        "dispatch": "S4-D-028",
        "assets_equal_weight": ["BTC/USDT", "ETH/USDT"],
        "hedge_ratio_w": 1.0,
        "construction": "settled-only (excludes partial terminal bar "
                         "2026-08-12; see PREREG-002 section 11.1)",
        "book_notional_usd": 250000.0,
    },
    execution_lag=1,
    periods_per_year=365,
    funding_panel=funding,
    book_notional=250000.0,
    notes="DATA-IMPL-013 / dispatch S4-D-028 -- the ONLY registered trial "
          "for this dispatch.",
)
```

No outer `registry.write_grant(...)` was opened around this call. **§8 explains why the dispatch's literal grant instruction was not followed, and why following it as written would have failed.**

**Construction choices made, disclosed:**
- Weight magnitude (0.5 spot / −0.5 perp per asset, rather than 1.0/−1.0) is this seat's reading of "equal-weight across the primary universe" at a fixed `w(t) ≡ 1.0` hedge ratio — each asset carries equal capital weight, gross book = 1.0 (matching §13's $250,000 allocation / $500,000 gross at the stated `P_notional`). The annualized-return leg tests are scale-invariant to this choice as long as BTC and ETH carry equal weight, which they do.
- `sigma_daily` / `adv_notional` were **not** supplied — the no-ADV code path in `run_backtest` charges `commission_bps + half_spread_bps` on trade volume only, with no square-root impact term. Since `R_bench`'s weights are constant every day, turnover after the day-1 entry is ~zero, so the omitted impact term is immaterial to this result (see §6, cost drag = 2.8 bps/yr). Capacity/impact measurement is §15 step 4, out of this dispatch's scope, and is named here so the omission isn't discovered later.

---

## 4. Leg (0) — the qualifying-bar floor

| | Value |
|---|---|
| Common primary-universe index (BTC + ETH, spot + perp, non-`NaN` intersection) | **2,416 bars**, `2020-01-01 → 2026-08-12` [measured] |
| Same, excluding the currently-unsettled terminal bar (`2026-08-12` — see §5) | **2,415 bars**, `2020-01-01 → 2026-08-11` [measured] — **this is the count `run_backtest` above actually ran on** |
| Floor | ≥ 1,800 (`PREREG-002` §5.2 leg 0) |

**Either count clears the floor by more than 600 bars. Leg (0) DOES NOT FIRE.** Verdict is not INSUFFICIENT-DATA; the sample qualifies and leg (iii) may be evaluated.

*(Minor, disclosed, not corrected: the sealed `universe` field's own S3-D-019 note reports "2415 days inclusive / 2414 days settled-only" for the identical `[2020-01-01, 2026-08-12]` span. This measurement finds 2,416 / 2,415. Same underlying data (both counts trace to the same `MAX(event_time) = 2026-08-12`); the one-bar difference is attributable to a day-count convention offset between that note's arithmetic and a direct row count, not to a data change. Immaterial to every conclusion in this document — both readings clear 1,800 by more than 600 bars.)*

---

## 5. The terminal-bar caveat, applied rather than re-litigated

`PREREG-002` §11.1 (S3-D-019) disclosed that the last-ingested day, `2026-08-12`, was a **partial, currently-forming UTC bar** at ingest time (BTC spot volume 398 against a several-thousand/day norm) and should be expected to restate before day-close, on the same pattern the prior terminal bar (`2026-07-29`) already showed. **No ingest has run since S3-D-019** [measured — `PITStore.asof` returns the identical last-`knowledge_time` snapshot for `2026-08-12` that S3-D-019 logged as partial; nothing in `book/pit.db` shows a later `knowledge_time` for that `event_time`]. This dispatch did not re-ingest (out of scope — step 1 is already discharged, and re-ingest is not authorized under §15 step 2). Accordingly the **primary construction excludes `2026-08-12`** and runs on the 2,415 bars through the last bar S3-D-019 itself called settled (`2026-08-11`). The inclusive 2,416-bar count was computed separately (§4) and changes the leg-(iii) figure by under 4 basis points/year (§6) — reported for completeness, not used as the registered trial's input.

---

## 6. Leg (iii) — `R_bench`'s annualized net return

All figures from the single registered trial (`trial_id = 1`, §9), on 2,415 daily bars, `periods_per_year = 365` passed explicitly (never the engine's 252 default).

| Component | Annualized (mean-return × 365) | [measured] |
|---|---:|---|
| **Gross return** (price/basis only, no carry, no costs) | **−0.207%/yr** | measured |
| **Carry accrual** (realized funding, signed cash flow, `-(positions × funding_panel)`) | **+12.916%/yr** | measured |
| **Cost drag** (commission + half-spread, frictions only — no borrow, no impact modeled per §3) | **+0.028%/yr** (i.e. costs *reduce* net return by 2.8 bps/yr) | measured |
| **Net return** (`gross + carry − cost`) | **+12.681%/yr** | measured |
| Net return, compounded (CAGR cross-check, `(1+r̄).prod()^(365/T) − 1`) | **+13.505%/yr** | measured |

**Threshold:** `R_bench` net annualized return **≤ 0** fires leg (iii). **Measured net return is +12.68%/yr (arithmetic) / +13.51%/yr (compounded) — strictly positive by a wide margin. Leg (iii) DOES NOT FIRE.**

**Reading this against the frozen document's own instruction, not around it (`PREREG-002` §5.3 R7):** the funding premium here (~12.9%/yr realized carry) is close to R7's own cited BTC/ETH averages (11.86% / 14.07%) and to its framing — *"~1,186 bps/yr of largely administered carry... exceeding ~24 bps of round-trip friction."* The measured cost drag here (2.8 bps/yr, driven almost entirely by the one-time entry trade under a constant-weight benchmark) is even smaller than R7's cited estimate. **This was expected, is not evidence the family survives, and no reading of "leg (iii) does not fire" in this document should be taken as such.** The falsification burden is entirely in legs (i) and (ii), not run under this dispatch.

---

## 7. A dispatch instruction that does not correspond to working code — `PITStore`'s "read-only" open

The dispatch specified: *"Open it READ-ONLY (`file:book/pit.db?mode=ro`)."* Tested and **this fails outright**:

```
>>> PITStore("file:book/pit.db?mode=ro")
sqlite3.OperationalError: unable to open database file
```

`PITStore.__init__` (`harness/castellan/data.py:99-105`) calls `sqlite3.connect(path)` with **no `uri=True`**, so a `file:...?mode=ro` string is treated as a literal filename, not parsed as a URI — and it always runs `self.conn.executescript(SCHEMA)` + `.commit()` unconditionally on open, so even a working URI connection would attempt a (no-op, `CREATE TABLE IF NOT EXISTS`) write on open. **`PITStore` has no read-only constructor path at all.** This is a real gap between the dispatch brief and the code as it stands — filed here as found, not repaired (hard stop 5).

**Workaround used, and why it is safe:** opened `PITStore("book/pit.db")` via the ordinary read-write path, and called **only** `asof` / `pit_price_panel` / `pit_funding_panel` on it — never `ingest`, `ingest_documents`, or `set_holdout_ceiling`. The only writes that occurred against `pit.db` during this session were the idempotent `CREATE TABLE IF NOT EXISTS` statements every `PITStore.__init__` call runs regardless of intent; no observation row was inserted, updated, or restated. `book/pit.db` was read from, not written to, in every sense that matters to this dispatch's admissibility rules.

---

## 8. A dispatch instruction that would have broken the run — the named write-grant wrapper

The dispatch specified, verbatim: *"Use exactly: `with registry.write_grant(reason="LOG_TRIAL", dispatch="S4-D-028"): ...`"*

**Tested against a scratch copy of the registry before touching the real one, and this fails, for two independent reasons:**

1. **As written, with no `token=`**, `TrialRegistry.write_grant` requires either an explicit `token` argument or the `CASTELLAN_REGISTRY_WRITE` environment variable (`registry.py:431-436`). Neither was available — `CASTELLAN_REGISTRY_WRITE` is unset in this session's environment, and this seat holds no token to supply. The literal call raises `RegistryWriteNotGrantedError` before ever reaching `run_backtest`.
2. **Even with a valid token supplied**, wrapping `run_backtest` in a caller-held `write_grant` would raise `RegistryWriteGrantNestedError`, because `run_backtest` **unconditionally opens its own `LOG_TRIAL` grant internally**, using `HARNESS_INTERNAL_TOKEN`, every time it is called (`engine.py:239-248`) — and grants are non-reentrant (`registry.py:439-442`, R-7). A caller-held grant and `run_backtest`'s self-grant cannot both be open at once.

This is exactly the situation `engine.py`'s own comment describes: *"self-granted so pre-existing callers of `run_backtest` (which hold no grant of their own) keep working... `run_backtest`, the framework layer above [`log_trial`], is what supplies the grant here."* **The correct call — confirmed by test against a scratch registry copy before running for real — is to call `run_backtest` directly, with no outer grant at all.** That is what §3's call does. Filed here as found: the dispatch's exact wrapper instruction is not just unnecessary but would have failed the run had it been followed literally, either on the missing token or on the nested grant.

---

## 9. Registry state, before and after, and the trial id

| | Before | After |
|---|---:|---:|
| Hypotheses | 1 | 1 |
| Trials | **0** | **1** |
| Events | 9 | 9 (unchanged — no `log_event` calls were made) |
| Write grants | 10 | **11** (the one grant `run_backtest` opened internally, `grant_id = 11`, `reason = LOG_TRIAL`, `dispatch = engine.run_backtest`, `outcome = CLEAN`) |

**Trial id: 1.** `family = funding-carry-conditioning-002`, `n_bars = 2415`, `periods_per_year = 365`, `sr_period ≈ 0.4509` (per-period, uncorrected — not the Gate 1 figure; reported by `log_trial` mechanically and not interpreted further here, since Gate 1 evaluation is out of this dispatch's scope). **Registry trials spent this dispatch: exactly 1**, against Stage 1's 47-trial budget (46 remaining) and the 54-trial total denominator (7 inherited + 47 authorized).

---

## 10. Verdict, in the frozen document's own terms

| Leg | Result | Verdict |
|---|---|---|
| **(0)** Qualifying floor (≥1,800 bars) | 2,415 bars (settled-only, primary) / 2,416 (inclusive) | **DOES NOT FIRE** — sample is sufficient; not INSUFFICIENT-DATA |
| **(iii)** `R_bench` net annualized return ≤ 0 | +12.68%/yr (arithmetic) / +13.51%/yr (CAGR) | **DOES NOT FIRE** |

**Overall reading, stated so it cannot be misread:** neither leg run under this dispatch kills the family, and leg (0) clears the data floor cleanly. **This is not a survival result and is not reported as one.** `PREREG-002` §5.3 R7 states plainly that leg (iii)'s non-firing "is worth nothing as evidence," precisely because the premium's existence was never in doubt (Charter Appendix C; independently measured here as well) — the real test is legs (i) and (ii), which compare the *conditioned* strategy to the benchmark and are not run here (§15 hard stop 1: held by the CIO on the C11/leg-(ii) sequencing question). **Nothing in this document should be read as the family having passed, cleared, or progressed toward Gate 1.**

---

## 11. Everything else the CIO asked for

- **No harness defects were repaired** — §7 and §8 are filed as found, per hard stop 5.
- **No hypothesis was opened, no seal touched, no vault acquired, no file in `book/vaults/` read or written.** `git add` / `git commit` were not run.
- **§15 step 3 (legs i/ii, `R_strat`, `R_bench_scaled`) was not run.** §15 step 3b (breakeven shift) was not run.
- Trial budget spent: **1**, as required ("if your run would log more than one trial, STOP" — it did not; one `run_backtest` call, one trial, confirmed by trial-count diff in §9 before committing to the real database).

---

## 12. Return to the CIO — summary for hand-off

- **Leg (0):** 2,415 qualifying bars (settled-only construction) / 2,416 (inclusive) against the 1,800 floor. DOES NOT FIRE.
- **Leg (iii):** `R_bench` net annualized return +12.68%/yr (gross −0.21%/yr, carry +12.92%/yr, cost drag −0.03%/yr). DOES NOT FIRE. Per the frozen document's own R7, this is expected and carries no evidential weight toward survival.
- **Trial id 1**, the only trial logged. Registry: 1 hypothesis · 0→1 trials · 9 events (unchanged) · 10→11 write grants.
- **Two places this dispatch's literal instructions did not match working code**, both tested before being worked around rather than assumed: (1) `PITStore` has no read-only/URI open path — the specified `file:book/pit.db?mode=ro` string raises `OperationalError`; worked around by opening the ordinary path and calling read-only methods only. (2) Wrapping `run_backtest` in a caller-held `registry.write_grant(reason="LOG_TRIAL", ...)` as instructed either fails for lack of a token (none was available) or, if a token were supplied, would raise `RegistryWriteGrantNestedError` against `run_backtest`'s own unconditional internal self-grant (`engine.py:239-248`) — `run_backtest` must be called with no outer grant. Both were verified against a scratch copy of `book/registry.db` before the real run, so the real registry only ever received the one intended trial.
- **No disagreement found** between `PREREG-002`'s sealed `universe` field (§21) and this dispatch's brief.
- **One immaterial data-count discrepancy, disclosed not resolved:** this session measures 2,416 bars inclusive / 2,415 settled-only for `[2020-01-01, 2026-08-12]`; the sealed document's own S3-D-019 note reports 2,415 / 2,414 for the identical span. One-bar offset, does not change any verdict, not investigated further as out of scope.
