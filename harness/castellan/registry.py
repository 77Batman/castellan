"""Trial Registry — the denominator of everything.

House rule 3: every backtest run increments the trial counter for its
hypothesis family. This module makes that a property of the code path
rather than a promise: `engine.run_backtest` refuses to run without a
registry handle, and every run writes its config hash, full net return
series, and per-period Sharpe here. N and the cross-sectional Sharpe
dispersion that DSR needs are then computed from the registry, never
self-reported.

The registry also holds the permanent event log: hypothesis
pre-registrations, holdout lock/open/retire events, and gate verdicts.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass

import numpy as np

from .stats import sharpe_period

SCHEMA = """
CREATE TABLE IF NOT EXISTS hypotheses (
    family        TEXT PRIMARY KEY,
    statement     TEXT NOT NULL,
    mechanism     TEXT NOT NULL,
    falsifier     TEXT NOT NULL,
    universe      TEXT NOT NULL,
    horizon       TEXT NOT NULL,
    success_criteria TEXT NOT NULL,
    trial_budget  INTEGER NOT NULL,
    created_utc   REAL NOT NULL,
    predecessor_family TEXT,
    holdout_classification TEXT,
    forward_window_start TEXT,
    forward_window_min_length REAL,
    forward_kill_condition TEXT,
    model_prior_provenance TEXT,
    published_signal_haircut_applied REAL,
    n_inherited   INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS trials (
    trial_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    family        TEXT NOT NULL REFERENCES hypotheses(family),
    config_json   TEXT NOT NULL,
    config_hash   TEXT NOT NULL,
    returns_blob  BLOB NOT NULL,
    n_bars        INTEGER NOT NULL,
    periods_per_year INTEGER NOT NULL,
    sr_period     REAL,
    notes         TEXT,
    created_utc   REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    event_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    kind          TEXT NOT NULL,
    family        TEXT,
    detail_json   TEXT NOT NULL,
    created_utc   REAL NOT NULL
);
"""


def _hash_config(config: dict) -> str:
    return hashlib.sha256(
        json.dumps(config, sort_keys=True, default=str).encode()
    ).hexdigest()[:16]


# Ruling 001 §5 P2 (Acceptance 001 P-series) — the pre-registration's
# binding field set, named exhaustively. Everything in this list is hashed
# into `prereg_sha256`; anything NOT in this list (created_utc, etc.) is
# provenance-only and outside the hash. The last six require the R1/R3/R4
# columns added in the SCHEMA migration below (I-018).
_BINDING_FIELDS = [
    "family", "statement", "mechanism", "falsifier", "universe", "horizon",
    "success_criteria", "trial_budget", "predecessor_family",
    "holdout_classification", "forward_window_start",
    "forward_window_min_length", "forward_kill_condition",
    "model_prior_provenance", "published_signal_haircut_applied",
    # C-001 §3.0 / H-3a: a declared denominator that is not sealed is not
    # a denominator (PREREG-001 H1). Binding means it is hashed into
    # `prereg_sha256`, shadow-copied into `hypothesis_sealed`, and a
    # change to it after seal is an amendment, not an update.
    "n_inherited",
]

_HOLDOUT_CLASSIFICATIONS = {"FORWARD", "HISTORICAL"}


def _binding_dict(fields: dict) -> dict:
    """Project an arbitrary field dict down to exactly the binding set,
    in a stable key order, so two dicts built from different call sites
    (a live DB row vs. a proposed registration) hash identically iff
    every binding field agrees."""
    return {k: fields.get(k) for k in _BINDING_FIELDS}


def _binding_hash(fields: dict) -> str:
    """P1: sha256 over canonical (sort_keys=True, UTF-8) JSON of the
    binding field set."""
    blob = json.dumps(_binding_dict(fields), sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


@dataclass
class FamilyStats:
    """The registry contract fixed by Validation, Gate 0 001 §3.0.

    ``n_trials`` is THE denominator every Part IV statistic consumes.
    ``n_inherited`` and ``n_logged`` are its two components, reported
    separately so a report can never launder an [inferred] declaration
    into a bare, [measured]-looking integer (H-12)."""
    family: str
    n_trials: int       # = n_inherited + n_logged
    n_inherited: int    # = Sum n_inherited(chain) — declared, phantom, no returns
    n_logged: int        # = Sum COUNT(*) trials(chain) — real, with returns
    trial_budget: int
    sr_period_std: float | None
    sr_period_mean: float | None
    sr_period_best: float | None


class PreRegistrationError(RuntimeError):
    """Raised when a trial is logged against an unregistered hypothesis."""


class PreRegistrationAmendedError(RuntimeError):
    """P3: re-calling ``open_hypothesis`` for an existing family with any
    differing binding field. Under D-006's pre-registration freeze the
    binding fields are immutable after sealing; amend by opening a
    successor family via ``predecessor_family``, not by re-registering the
    same family. Byte-identical re-registration remains idempotent and
    does not raise (see P3's second branch)."""


class InheritedCountDoubleCountError(ValueError):
    """H-5b / D-011 §3 (I-031): a successor's declared ``n_inherited`` is
    >= its predecessor chain's already-summed ``n_trials``.

    ``family_stats`` sums the predecessor chain transitively (F4 / H-5a).
    A successor that declares ``n_inherited`` at or above that running
    total is re-declaring trials the chain summation already counts —
    the exact double-count the naive reading of KC-001 clause 3 produces
    (F-5 / I-031), which the Principal's D-011 restatement assigns to
    "the registry's transitive summation" alone. A genuine new search
    larger than the entire predecessor chain is a Validation escalation,
    not a silent registration — this exception IS that escalation path."""


class TrialRegistry:
    def __init__(self, path: str):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.executescript(SCHEMA)
        self.conn.commit()
        self._migrate()

    def _migrate(self) -> None:
        """Add columns introduced after a DB may already have been created.
        SQLite's ``CREATE TABLE IF NOT EXISTS`` does not retrofit an
        existing table, so pre-existing registry.db files (this firm has
        one at book/registry.db, currently with zero families per D-001)
        need this to pick up new columns."""
        cols = [r[1] for r in self.conn.execute("PRAGMA table_info(hypotheses)")]
        additions = [
            ("predecessor_family", "TEXT"),
            # R1/R3/R4 (Ruling 002; binding per D-006) — I-018: without
            # these columns no family can be pre-registered with its
            # binding fields at all.
            ("holdout_classification", "TEXT"),
            ("forward_window_start", "TEXT"),
            ("forward_window_min_length", "REAL"),
            ("forward_kill_condition", "TEXT"),
            ("model_prior_provenance", "TEXT"),
            ("published_signal_haircut_applied", "REAL"),
            # I-027 / C-001 §3.0 / H1: the declared-but-unenforced
            # denominator. `book/registry.db` predates this column too
            # (H-1) — CREATE TABLE IF NOT EXISTS will not add it to an
            # existing table, only ALTER TABLE does.
            ("n_inherited", "INTEGER NOT NULL DEFAULT 0"),
        ]
        changed = False
        for name, sqltype in additions:
            if name not in cols:
                self.conn.execute(f"ALTER TABLE hypotheses ADD COLUMN {name} {sqltype}")
                changed = True
        if changed:
            self.conn.commit()

    # -- hypotheses ----------------------------------------------------

    def open_hypothesis(
        self,
        family: str,
        statement: str,
        mechanism: str,
        falsifier: str,
        universe: str,
        horizon: str,
        success_criteria: str,
        trial_budget: int,
        predecessor_family: str | None = None,
        holdout_classification: str | None = None,
        forward_window_start: str | None = None,
        forward_window_min_length: float | None = None,
        forward_kill_condition: str | None = None,
        model_prior_provenance: str | None = None,
        published_signal_haircut_applied: float | None = None,
        n_inherited: int = 0,
    ) -> None:
        """Gate 0 pre-registration, with sealed integrity (Acceptance 001
        P-series, closing the D-006 rider's gap: "the pre-registration is
        currently a tamper-evident *promise*, not a tamper-evident
        *payload*").

        ``predecessor_family`` (Ruling 001 §3.3, F4): closes the "abandon
        and re-pre-register with a later C" loophole in the pinned-cutoff
        rule. If set, the researcher has seen the predecessor's results;
        those trials happened and stay in the denominator — see
        :meth:`family_stats` and :meth:`returns_matrix`, both of which sum
        transitively across the chain.

        ``holdout_classification`` / ``forward_window_*`` / R4 fields
        (Ruling 002 R1/R3/R4, made binding by D-006; I-018): a
        ``HISTORICAL`` classification requires the forward-window
        falsifier fields (R3) — a historical holdout cannot deliver the
        "unseen data" property on its own, and R3 is the substitute the
        firm accepted for that.

        P1: on first registration, computes ``prereg_sha256`` over the
        canonical JSON of the binding field set (P2) and logs it, with a
        full shadow copy of every binding field, as a ``hypothesis_sealed``
        event in the append-only ``events`` table — a full copy, not a
        pointer to the mutable row.

        P3: re-calling with an existing family and ANY differing binding
        field raises :class:`PreRegistrationAmendedError` and logs
        ``hypothesis_amendment_refused`` naming the differing fields.
        Byte-identical re-registration remains idempotent and logs
        nothing — this is what keeps the method safe to call unconditionally
        at the top of a research script.

        ``n_inherited`` (I-027 / C-001 §3.0; H1-H14): the prior search
        attributable to THIS family and not already carried by its
        predecessor chain — declared, phantom, no return series (H-6b:
        none may be synthesised to compensate). Must be a non-negative
        int (H2). Binding (H-3a): sealed, hashed, and an amendment
        attempt if changed post-seal (H-3b). ``family_stats`` sums it
        transitively across ``predecessor_family`` (H-5a); a successor
        declaring ``n_inherited`` at or above its predecessor chain's own
        running total double-counts under that summation and is refused
        with :class:`InheritedCountDoubleCountError` (H-5b) — the
        Principal's D-011 non-overlap restatement of KC-001 clause 3
        (I-031), mechanised.
        """
        for name, val in [
            ("statement", statement),
            ("mechanism", mechanism),
            ("falsifier", falsifier),
        ]:
            if not val or not val.strip():
                raise ValueError(f"Pre-registration requires a non-empty {name}")
        if predecessor_family is not None and self.hypothesis(predecessor_family) is None:
            raise ValueError(
                f"predecessor_family '{predecessor_family}' is not itself "
                "a registered hypothesis"
            )
        # H2: n_inherited must be a non-negative int. `isinstance(x, int)`
        # already excludes float (3.7 is refused) but not bool (a bool IS
        # an int in Python), so bool is excluded explicitly.
        if not isinstance(n_inherited, int) or isinstance(n_inherited, bool):
            raise ValueError(
                f"n_inherited must be a non-negative int, got {n_inherited!r}"
            )
        if n_inherited < 0:
            raise ValueError(
                f"n_inherited must be >= 0, got {n_inherited}"
            )
        # H-5b / D-011 §3 (I-031): the non-overlap rule. `family_stats`
        # sums the predecessor chain transitively, so a successor's own
        # `n_inherited` must be strictly less than the predecessor
        # chain's already-summed `n_trials` — otherwise the chain is
        # counted once by summation and again by the successor's own
        # declaration. Guarded on chain_total > 0 so an ordinary
        # successor of a predecessor that has itself run/declared
        # nothing (chain_total == 0) is not blocked from declaring its
        # own honest n_inherited (including 0, the common case).
        if predecessor_family is not None:
            chain_total = self.family_stats(predecessor_family).n_trials
            if chain_total > 0 and n_inherited >= chain_total:
                raise InheritedCountDoubleCountError(
                    f"n_inherited={n_inherited} declared for family "
                    f"'{family}' is >= predecessor chain total "
                    f"n_trials={chain_total} for '{predecessor_family}'. "
                    "family_stats sums the predecessor chain "
                    "transitively; declaring n_inherited at or above the "
                    "chain's own total double-counts it (D-011 §3 / "
                    "I-031, the non-overlap reading of KC-001 clause 3). "
                    "A genuine new search larger than the entire chain "
                    "is a Validation escalation, not a silent "
                    "registration."
                )
        if holdout_classification is not None and holdout_classification not in _HOLDOUT_CLASSIFICATIONS:
            raise ValueError(
                f"holdout_classification must be one of {_HOLDOUT_CLASSIFICATIONS} "
                f"or None, got {holdout_classification!r}"
            )
        if holdout_classification == "HISTORICAL":
            # R3: a HISTORICAL holdout requires a pre-registered forward-
            # window falsifier — the substitute for the property a
            # historical holdout cannot deliver on its own.
            for name, val in [
                ("forward_window_start", forward_window_start),
                ("forward_window_min_length", forward_window_min_length),
                ("forward_kill_condition", forward_kill_condition),
            ]:
                if not val:
                    raise ValueError(
                        "A HISTORICAL holdout_classification requires "
                        f"'{name}' (Ruling 002 R3): a historical holdout "
                        "cannot deliver 'unseen data' on its own, and R3's "
                        "forward-window falsifier is the firm's substitute."
                    )

        proposed = {
            "family": family, "statement": statement, "mechanism": mechanism,
            "falsifier": falsifier, "universe": universe, "horizon": horizon,
            "success_criteria": success_criteria, "trial_budget": int(trial_budget),
            "predecessor_family": predecessor_family,
            "holdout_classification": holdout_classification,
            "forward_window_start": forward_window_start,
            "forward_window_min_length": (
                None if forward_window_min_length is None else float(forward_window_min_length)
            ),
            "forward_kill_condition": forward_kill_condition,
            "model_prior_provenance": model_prior_provenance,
            "published_signal_haircut_applied": (
                None if published_signal_haircut_applied is None
                else float(published_signal_haircut_applied)
            ),
            "n_inherited": int(n_inherited),
        }

        existing = self.hypothesis(family)
        if existing is not None:
            # P3: any differing binding field is an amendment attempt, not
            # an update — the freeze has no "edit" verb.
            existing_binding = _binding_dict(existing)
            proposed_binding = _binding_dict(proposed)
            differing = [k for k in _BINDING_FIELDS if existing_binding.get(k) != proposed_binding.get(k)]
            if differing:
                self.log_event(
                    "hypothesis_amendment_refused", family,
                    {"differing_fields": differing},
                )
                raise PreRegistrationAmendedError(
                    f"Family '{family}' is already pre-registered; binding "
                    f"field(s) {differing} differ from the sealed "
                    "pre-registration. The pre-registration is frozen "
                    "(D-006) — open a successor family via "
                    "predecessor_family to change these, do not re-register "
                    "the same family."
                )
            return  # byte-identical: idempotent, no event

        self.conn.execute(
            "INSERT INTO hypotheses (family, statement, mechanism, "
            "falsifier, universe, horizon, success_criteria, trial_budget, "
            "created_utc, predecessor_family, holdout_classification, "
            "forward_window_start, forward_window_min_length, "
            "forward_kill_condition, model_prior_provenance, "
            "published_signal_haircut_applied, n_inherited) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                family, statement, mechanism, falsifier, universe, horizon,
                success_criteria, int(trial_budget), time.time(),
                predecessor_family, holdout_classification,
                forward_window_start, proposed["forward_window_min_length"],
                forward_kill_condition, model_prior_provenance,
                proposed["published_signal_haircut_applied"],
                proposed["n_inherited"],
            ),
        )
        self.log_event(
            "hypothesis_registered", family,
            {"statement": statement, "predecessor_family": predecessor_family},
        )
        # P1: seal — full shadow copy of the binding fields + their hash,
        # in the append-only events table.
        prereg_sha256 = _binding_hash(proposed)
        self.log_event(
            "hypothesis_sealed", family,
            {**_binding_dict(proposed), "prereg_sha256": prereg_sha256},
        )
        self.conn.commit()

    def verify_prereg(self, family: str) -> dict:
        """P4/P6: compare the LIVE ``hypotheses`` row's binding fields
        against the hash sealed at pre-registration time. This is the A4
        analogue for the pre-registration: a raw ``UPDATE hypotheses SET
        ...`` is detected here, because the sealed event carries a full
        shadow copy of the binding fields, not a pointer to the row that
        was just mutated.

        Returns a dict with keys ``sealed`` (bool — False means P6: no
        ``hypothesis_sealed`` event exists, e.g. a family that predates
        this schema), ``match`` (bool | None), ``differing_fields``
        (list[str]), ``sealed_sha256``, ``live_sha256``, and
        ``sealed_created_utc`` (for P7's day-granularity comparison against
        the holdout cutoff C).
        """
        sealed_events = self.events(kind="hypothesis_sealed", family=family)
        if not sealed_events:
            return {
                "sealed": False, "match": None, "differing_fields": [],
                "sealed_sha256": None, "live_sha256": None,
                "sealed_created_utc": None,
            }
        sealed = sealed_events[-1]
        sealed_detail = sealed["detail"]
        sealed_hash = sealed_detail.get("prereg_sha256")
        live = self.hypothesis(family)
        if live is None:
            return {
                "sealed": True, "match": False,
                "differing_fields": ["<family row no longer exists>"],
                "sealed_sha256": sealed_hash, "live_sha256": None,
                "sealed_created_utc": sealed["created_utc"],
            }
        live_binding = _binding_dict(live)
        live_hash = _binding_hash(live_binding)
        sealed_binding = _binding_dict(sealed_detail)
        differing = [k for k in _BINDING_FIELDS if live_binding.get(k) != sealed_binding.get(k)]
        return {
            "sealed": True,
            "match": live_hash == sealed_hash,
            "differing_fields": differing,
            "sealed_sha256": sealed_hash,
            "live_sha256": live_hash,
            "sealed_created_utc": sealed["created_utc"],
        }

    def predecessor_chain(self, family: str) -> list[str]:
        """All ancestor families, nearest first, following
        ``predecessor_family`` transitively. Cycle-safe."""
        chain: list[str] = []
        seen = {family}
        cur_fam = family
        while True:
            hyp = self.hypothesis(cur_fam)
            pred = hyp.get("predecessor_family") if hyp else None
            if not pred or pred in seen:
                break
            chain.append(pred)
            seen.add(pred)
            cur_fam = pred
        return chain

    def hypothesis(self, family: str) -> dict | None:
        cur = self.conn.execute(
            "SELECT * FROM hypotheses WHERE family=?", (family,)
        )
        row = cur.fetchone()
        if row is None:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))

    # -- trials --------------------------------------------------------

    def log_trial(
        self,
        family: str,
        config: dict,
        net_returns: np.ndarray,
        periods_per_year: int,
        notes: str = "",
    ) -> int:
        if self.hypothesis(family) is None:
            raise PreRegistrationError(
                f"Family '{family}' has no Gate 0 pre-registration. "
                "Register the hypothesis (statement, mechanism, falsifier) "
                "before running any backtest."
            )
        r = np.asarray(net_returns, dtype=np.float32)
        sr = sharpe_period(r)
        cur = self.conn.execute(
            "INSERT INTO trials (family, config_json, config_hash, "
            "returns_blob, n_bars, periods_per_year, sr_period, notes, "
            "created_utc) VALUES (?,?,?,?,?,?,?,?,?)",
            (
                family,
                json.dumps(config, sort_keys=True, default=str),
                _hash_config(config),
                r.tobytes(),
                int(r.size),
                int(periods_per_year),
                None if np.isnan(sr) else float(sr),
                notes,
                time.time(),
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def family_stats(self, family: str) -> FamilyStats:
        """C-001 §3.0: n_trials = Sum n_inherited(chain) + Sum logged(chain).

        n_inherited sums each family's OWN declared seed transitively
        across the predecessor chain (H-5a) — never re-declared by a
        successor (H-5b enforces this at registration time). n_logged is
        the real, run-trial count with a return series; sigma_SR/mean/
        best are computed from those real trials ONLY (H-6a/H-6b/H-6c) —
        no phantom row is ever synthesised for a seeded family, so DSR's
        cross-sectional dispersion input is never corrupted by a
        fabricated series."""
        hyp = self.hypothesis(family)
        budget = int(hyp["trial_budget"]) if hyp else 0
        families = [family] + self.predecessor_chain(family)
        placeholders = ",".join("?" * len(families))
        cur = self.conn.execute(
            f"SELECT sr_period FROM trials WHERE family IN ({placeholders})",
            families,
        )
        srs = [row[0] for row in cur.fetchall() if row[0] is not None]
        n_logged = self.conn.execute(
            f"SELECT COUNT(*) FROM trials WHERE family IN ({placeholders})",
            families,
        ).fetchone()[0]
        n_inherited = 0
        for fam_name in families:
            fam_hyp = self.hypothesis(fam_name)
            if fam_hyp is not None:
                n_inherited += int(fam_hyp["n_inherited"] or 0)
        if len(srs) >= 2:
            arr = np.array(srs)
            std, mean, best = (
                float(arr.std(ddof=1)),
                float(arr.mean()),
                float(arr.max()),
            )
        else:
            std = mean = best = None
        n_logged = int(n_logged)
        n_trials = n_inherited + n_logged
        return FamilyStats(family, n_trials, n_inherited, n_logged, budget,
                           std, mean, best)

    def returns_matrix(self, family: str) -> np.ndarray:
        """(T, N) matrix of all logged trial return series, truncated to
        the shortest common length from the end (most recent bars).

        Pools transitively across ``predecessor_family`` (F4): DSR's N
        comes from :meth:`family_stats`, which is already transitive: this
        keeps PBO/CSCV's return matrix consistent with the same N rather
        than silently drawing on a different trial set."""
        families = [family] + self.predecessor_chain(family)
        placeholders = ",".join("?" * len(families))
        cur = self.conn.execute(
            f"SELECT returns_blob, n_bars FROM trials WHERE family IN "
            f"({placeholders}) ORDER BY trial_id",
            families,
        )
        rows = cur.fetchall()
        if not rows:
            return np.empty((0, 0))
        series = [
            np.frombuffer(blob, dtype=np.float32) for blob, _ in rows
        ]
        t_min = min(s.size for s in series)
        return np.column_stack([s[-t_min:] for s in series]).astype(float)

    def trial_returns(self, family: str) -> list[np.ndarray]:
        """VALIDATION-SPEC-002 R-10 -- each logged trial's return series
        at its OWN full length, transitive across ``predecessor_family``
        in the same way :meth:`returns_matrix` already is.

        :meth:`returns_matrix` truncates every column to the SHORTEST
        common length, so one 20-bar logged trial collapses the entire
        family's return matrix to 20 bars (I-062) -- silently degrading
        PBO/CSCV today. Consumed by the VIF family term, that truncation
        would drop every series below R-5's ``T >= 32`` floor and
        evaporate the family term entirely -- a one-line attack. This
        accessor exists so the VIF never consumes that truncation."""
        families = [family] + self.predecessor_chain(family)
        placeholders = ",".join("?" * len(families))
        cur = self.conn.execute(
            f"SELECT returns_blob FROM trials WHERE family IN "
            f"({placeholders}) ORDER BY trial_id",
            families,
        )
        return [
            np.frombuffer(blob, dtype=np.float32).astype(float)
            for (blob,) in cur.fetchall()
        ]

    # -- events / verdicts --------------------------------------------

    def log_event(self, kind: str, family: str | None, detail: dict) -> int:
        cur = self.conn.execute(
            "INSERT INTO events (kind, family, detail_json, created_utc) "
            "VALUES (?,?,?,?)",
            (kind, family, json.dumps(detail, default=str), time.time()),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def events(self, kind: str | None = None, family: str | None = None) -> list[dict]:
        q = "SELECT event_id, kind, family, detail_json, created_utc FROM events WHERE 1=1"
        args: list = []
        if kind:
            q += " AND kind=?"
            args.append(kind)
        if family:
            q += " AND family=?"
            args.append(family)
        out = []
        for row in self.conn.execute(q + " ORDER BY event_id", args):
            out.append(
                {
                    "event_id": row[0],
                    "kind": row[1],
                    "family": row[2],
                    "detail": json.loads(row[3]),
                    "created_utc": row[4],
                }
            )
        return out

    def close(self):
        self.conn.close()
