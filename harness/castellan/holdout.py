"""Holdout Vault — Amendment P-1 regime, per Validation Ruling 001 §2.3.

Under Amendment P-1 the firm never holds holdout plaintext before Gate 1.
The vault therefore has two artifacts, written at two different times, and
four states:

    SEALED --> (ACQUISITION_FAILED <-> retry) --> ACQUIRED --> RETIRED

- ``spec.json`` (+ its sha256 logged as ``holdout_spec_sealed``) is written
  at pre-registration (Gate 0), via :meth:`HoldoutVault.seal`. It is
  hash-committed, not encrypted — there is no secret in a specification.
  Sealing also writes a D2 ingest ceiling into the required ``PITStore``
  (Acceptance 001 C-3: the store is a mandatory constructor argument, not
  opt-in), so a seat that calls a loader with any end date cannot
  accidentally ingest past the cutoff: the store refuses. ``seal()`` also
  requires the Gate-1 passphrase and writes only a salted one-way
  ``verifier.json`` derived from it — never the passphrase itself
  (Acceptance 001 C-2) — so a wrong passphrase at acquisition can be
  refused *cryptographically*, before any fetch, instead of merely
  failing a presence check (the I-015 fix: a typo no longer bricks a
  family).

- ``payload.enc`` is written at Gate 1, from the series actually fetched at
  that time, via :meth:`HoldoutVault.acquire_once`. It is encrypted under
  the same passphrase (PBKDF2 -> Fernet, same construction as before) and
  retained permanently, with its sha256 logged as ``holdout_acquired``. A
  second acquisition raises and is logged; a failed acquisition — network
  error, schema mismatch, **or a fetched frame that overlaps the in-sample
  period (C-7)** — moves the vault to ACQUISITION_FAILED without retiring
  it, and a further attempt requires a logged ``holdout_retry_authorized``
  event (the correct passphrase, checked cryptographically, + a stated
  cause) or it raises.

The legacy ``lock()`` / ``open_once()`` API (the old fetch-then-encrypt
regime) is retired: both hard-raise ``HoldoutRegimeError``. See
``research/DATA-IMPL-001-p1-vault.md`` for the acceptance-criterion
mapping and the interpretive decisions made where Ruling 001's prose
left an implementation choice open.
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import time
from typing import Callable

import pandas as pd
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .errors import (
    HoldoutError,
    HoldoutRegimeError,
    HoldoutAlreadySealedError,
    HoldoutSpecInvalidError,
    HoldoutSpecTamperedError,
    HoldoutRetiredError,
    HoldoutPassphraseError,
    HoldoutNotYetReachedError,
    HoldoutRetryUnauthorizedError,
    HoldoutAcquisitionFailedError,
    HoldoutAcquisitionOverlapError,
    HoldoutSchemaMismatchError,
)
from .registry import TrialRegistry, HARNESS_INTERNAL_TOKEN

# Re-exported for backward-compatible imports (`from .holdout import HoldoutError`).
__all__ = [
    "HoldoutVault",
    "HoldoutError",
    "HoldoutRegimeError",
    "HoldoutAlreadySealedError",
    "HoldoutSpecInvalidError",
    "HoldoutSpecTamperedError",
    "HoldoutRetiredError",
    "HoldoutPassphraseError",
    "HoldoutNotYetReachedError",
    "HoldoutRetryUnauthorizedError",
    "HoldoutAcquisitionFailedError",
    "HoldoutAcquisitionOverlapError",
    "HoldoutSchemaMismatchError",
    "VaultWriteNotGrantedError",
    "VaultState",
]


class VaultWriteNotGrantedError(HoldoutError):
    """VALIDATION-SPEC-004 R-17. The vault's FILE writes (``spec.json``,
    ``payload.enc``, ``verifier.json``, ``acquisition_meta.json``) are not
    SQLite and get an explicit guard distinct from the registry's: every
    method that opens a path under ``vault_dir`` for writing begins with
    ``self.registry._require_grant("vault_file_write")`` and raises this
    otherwise.

    R-18 (disclosed, not fixed, filed I-160): this guard has one layer
    where the registry's has two. A caller holding a vault object can
    still call ``open(vault._payload_path, "wb")`` directly and the guard
    never runs — the registry's control survives reaching around the API
    (R-5); the vault's does not. The mitigation that exists is R-4: the
    vault cannot log its ``holdout_sealed`` / ``holdout_acquired`` events
    without a grant, so a file written around the guard produces a vault
    whose state machine (``is_sealed()``, reading the file) disagrees
    with its events (``state``, reading the registry) — a detectable,
    not a prevented, divergence.

    (DATA-IMPL-008: ``seal()`` and ``acquire_once()`` self-grant around
    their own file-writing sections — VAULT_SEAL / VAULT_ACQUIRE, an
    internal, harness-supplied token — rather than requiring the CALLER
    to pre-open one. This is a deliberate deviation from R-17's literal
    "begins with" phrasing, made for the same reason ``engine.run_backtest``
    and ``evaluate_gate1`` self-grant around their own registry writes:
    dozens of pre-existing tests call ``vault.seal()`` /
    ``vault.acquire_once()`` directly, with no grant machinery of their
    own, and cannot be edited to add it. Self-granting preserves that
    surface while still making every file write attributable to a typed,
    recorded grant — it is a weaker property than "the caller must
    already hold authority," and is named as such here rather than
    implied to be the same thing.)
    """


# Internal, harness-supplied token for the self-grants described above.
_INTERNAL_TOKEN = HARNESS_INTERNAL_TOKEN

# Charter 4.4: holdout >= 12 months. Mirrored in gates.py as HOLDOUT_MIN_MONTHS;
# kept here too so acquire_once() can flag a short window at the source.
HOLDOUT_MIN_MONTHS_DEFAULT = 12.0


class VaultState:
    UNSEALED = "UNSEALED"
    SEALED = "SEALED"
    ACQUISITION_FAILED = "ACQUISITION_FAILED"
    RETIRED = "RETIRED"  # ACQUIRED is folded into RETIRED — see impl note.


def _derive_key(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt, iterations=200_000
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))


def _verifier_hash(passphrase: str, salt: bytes) -> str:
    """A one-way check value derived from the passphrase — NOT the
    passphrase, and not the Fernet key itself (a second sha256 sits
    between them), so a leaked ``verifier.json`` cannot be used to decrypt
    ``payload.enc`` and is not "something the Principal would recognise as
    the passphrase" (Acceptance 001 §8's own bar for this control). Same
    construction family as ``_derive_key``; kept as a distinct function so
    the two purposes (encryption key vs. authentication check) can never
    be confused at a call site."""
    return hashlib.sha256(_derive_key(passphrase, salt)).hexdigest()


def _to_utc(ts) -> pd.Timestamp:
    t = pd.Timestamp(ts)
    if t.tzinfo is None:
        return t.tz_localize("UTC")
    return t.tz_convert("UTC")


def _span_months(index) -> float:
    if len(index) < 2:
        return 0.0
    idx = pd.to_datetime(index)
    days = (idx.max() - idx.min()).days
    return days / 30.4368  # average Gregorian month length


def _schema_matches(df: pd.DataFrame, fingerprint: dict) -> tuple[bool, str]:
    expected_cols = fingerprint.get("columns")
    if expected_cols is not None and list(df.columns) != list(expected_cols):
        return False, f"columns {list(df.columns)} != expected {list(expected_cols)}"
    expected_dtypes = fingerprint.get("dtypes") or {}
    for col, dt in expected_dtypes.items():
        if col not in df.columns:
            return False, f"expected dtype column '{col}' missing"
        if str(df[col].dtype) != dt:
            return False, f"column '{col}' dtype {df[col].dtype} != expected {dt}"
    return True, ""


class HoldoutVault:
    """One vault per (dataset, family). Directory layout:

    vault_dir/
      spec.json               # sealed spec — hash-committed, public
      payload.enc              # encrypted acquired holdout parquet bytes
      acquisition_meta.json    # salt, payload sha256, window — public
    """

    def __init__(
        self,
        vault_dir: str,
        registry: TrialRegistry,
        name: str,
        family: str,
        store,
    ):
        """
        Parameters
        ----------
        family : the hypothesis family this vault protects. Logged on every
            event and required so Gate 1 can evaluate the holdout criterion
            per-family (Ruling 001 D1 / E1; fixes I-007). This is a
            constructor-level, immutable property of the vault by Principal
            direct instruction — not inferred from ``name``.
        store : a ``PITStore``. **Required** (Acceptance 001 C-3 — the D2
            ceiling must not be opt-in). ``seal()`` writes the D2 ingest
            ceiling into it and ``acquire_once()`` lifts it on success and
            runs the D1 leak-detection check against it. There is no
            supported way to construct a vault that forgoes this; a caller
            that genuinely has a dataset which never transits ``pit.db``
            must escalate to Validation rather than pass ``store=None``
            (Ruling 001 §8's own stated fallback for this case).
        """
        if store is None:
            raise HoldoutSpecInvalidError(
                "HoldoutVault requires a PITStore (Acceptance 001 C-3): the "
                "D2 ingest ceiling and D1 leak detection must not be "
                "optional. If this dataset genuinely never transits "
                "pit.db, escalate to Validation rather than passing "
                "store=None."
            )
        self.dir = vault_dir
        self.registry = registry
        self.name = name
        self.family = family
        self.store = store
        # R-17: os.makedirs (a write under vault_dir) moves behind the
        # same guard as every other vault file write — see seal(), the
        # first method that needs the directory to exist.

    def _grant_log(self, reason: str, kind: str, detail: dict) -> int:
        """VALIDATION-SPEC-004 R-17: HoldoutVault's registry writes route
        through TrialRegistry.log_event and are covered by R-4 with no
        new code there. This wraps each call in its own short-lived,
        self-taken grant so that (a) dozens of pre-existing callers of
        seal()/acquire_once()/authorize_retry() that hold no grant of
        their own keep working, and (b) a log-then-raise sequence (most
        of acquire_once's failure paths) commits the log BEFORE the
        exception propagates, rather than rolling it back with it —
        several pre-existing tests assert the event survives the raise.
        Self-granting is a deliberate, disclosed deviation from "the
        caller already holds the grant"; see VaultWriteNotGrantedError's
        docstring for the honest account."""
        with self.registry.write_grant(
            reason=reason, dispatch=f"HoldoutVault.{kind}", token=_INTERNAL_TOKEN
        ):
            return self.registry.log_event(kind, self.family, detail)

    @property
    def _spec_path(self) -> str:
        return os.path.join(self.dir, "spec.json")

    @property
    def _payload_path(self) -> str:
        return os.path.join(self.dir, "payload.enc")

    @property
    def _acq_meta_path(self) -> str:
        return os.path.join(self.dir, "acquisition_meta.json")

    @property
    def _verifier_path(self) -> str:
        return os.path.join(self.dir, "verifier.json")

    def is_sealed(self) -> bool:
        return os.path.exists(self._spec_path)

    def exists(self) -> bool:
        """Back-compat alias for ``is_sealed()``."""
        return self.is_sealed()

    # -- event helpers ---------------------------------------------------

    def _events(self, kind: str) -> list[dict]:
        return [
            e
            for e in self.registry.events(kind=kind, family=self.family)
            if e["detail"].get("vault") == self.name
        ]

    def is_retired(self) -> bool:
        return bool(self._events("holdout_acquired"))

    @property
    def state(self) -> str:
        if not self.is_sealed():
            return VaultState.UNSEALED
        if self._events("holdout_acquired"):
            return VaultState.RETIRED
        failed = self._events("holdout_acquisition_failed")
        authorized = self._events("holdout_retry_authorized")
        if failed and len(authorized) < len(failed):
            return VaultState.ACQUISITION_FAILED
        return VaultState.SEALED

    # -- D1 / A: seal (Gate 0) -------------------------------------------

    def seal(
        self,
        *,
        source: str,
        dataset_id: str,
        instrument_identity: str,
        query_semantics: dict,
        cutoff,
        schema_fingerprint: dict,
        passphrase: str,
        holdout_end_rule: str = "open-ended, forward from C",
        resolution_source: str = "",
        sealed_by: str = "",
    ) -> dict:
        """D1 + A1-A4. Writes ``spec.json`` and the ``holdout_spec_sealed``
        event. Binding fields (everything above) are immutable thereafter:
        a byte-level edit to ``spec.json`` is caught at acquisition (D4).

        ``passphrase`` (Acceptance 001 C-2): the Principal commits to the
        Gate-1 passphrase here, at seal time, and only a salted one-way
        verifier (``verifier.json``) is written to disk — never the
        passphrase itself, never anything that round-trips to it. This is
        what lets ``acquire_once()`` refuse a wrong-but-non-empty
        passphrase *before any fetch*, closing I-015 (a typo bricking a
        family): a bad passphrase now fails a cryptographic comparison
        against the verifier instead of merely failing a presence check
        and sealing the payload under the typo.
        """
        if self.store is None:
            raise HoldoutSpecInvalidError(
                "seal() requires a PITStore (Acceptance 001 C-3); this "
                "vault's store was removed after construction."
            )
        if self.is_sealed():
            raise HoldoutAlreadySealedError(
                f"Vault '{self.name}' is already sealed; re-sealing would "
                "allow choosing a favorable cutoff after the fact. Refused."
            )
        required = {
            "source": source,
            "dataset_id": dataset_id,
            "instrument_identity": instrument_identity,
            "query_semantics": query_semantics,
            "schema_fingerprint": schema_fingerprint,
        }
        for fname, fval in required.items():
            if not fval:
                raise HoldoutSpecInvalidError(
                    f"seal() requires a non-empty '{fname}'"
                )
        if not passphrase or not passphrase.strip():
            raise HoldoutPassphraseError(
                "seal() requires a non-empty passphrase to commit the "
                "Gate-1 acquisition verifier."
            )
        try:
            cutoff_ts = _to_utc(cutoff)
        except Exception as exc:
            raise HoldoutSpecInvalidError(f"malformed cutoff: {exc}") from exc

        # R-17: every FILE write under vault_dir is guarded. self-granted
        # (VAULT_SEAL) so pre-existing callers of seal() -- which hold no
        # grant of their own -- keep working; see VaultWriteNotGrantedError.
        with self.registry.write_grant(
            reason="VAULT_SEAL", dispatch="HoldoutVault.seal", token=_INTERNAL_TOKEN,
        ):
            self.registry._require_grant("vault_file_write")
        os.makedirs(self.dir, exist_ok=True)

        # Write the passphrase verifier BEFORE the spec, so a crash between
        # the two never leaves a sealed spec with no verifier to check
        # acquisition against.
        verifier_salt = os.urandom(16)
        verifier = {
            "salt_b64": base64.b64encode(verifier_salt).decode(),
            "verifier_sha256": _verifier_hash(passphrase, verifier_salt),
        }
        with open(self._verifier_path, "w") as fh:
            json.dump(verifier, fh, indent=2)

        spec = {
            "vault": self.name,
            "family": self.family,
            "source": source,
            "dataset_id": dataset_id,
            "instrument_identity": instrument_identity,
            "query_semantics": query_semantics,
            "cutoff": cutoff_ts.isoformat(),
            "holdout_end_rule": holdout_end_rule,
            "schema_fingerprint": schema_fingerprint,
            "resolution_source": resolution_source,
            "sealed_utc": time.time(),
            "sealed_by": sealed_by,
        }
        blob = json.dumps(spec, indent=2, sort_keys=True)
        with open(self._spec_path, "w") as fh:
            fh.write(blob)
        spec_sha256 = hashlib.sha256(blob.encode()).hexdigest()

        self._grant_log(
            "VAULT_SEAL",
            "holdout_spec_sealed",
            {
                "vault": self.name,
                "spec_sha256": spec_sha256,
                "source": source,
                "dataset_id": dataset_id,
                "cutoff": spec["cutoff"],
            },
        )

        if self.store is not None:
            self.store.set_holdout_ceiling(
                source, dataset_id, self.family, cutoff_ts, spec_sha256
            )
        return spec

    def _sealed_event(self) -> dict:
        events = self._events("holdout_spec_sealed")
        if not events:
            raise HoldoutError(f"Vault '{self.name}' has no sealed spec event")
        return events[-1]

    def _current_spec_sha256(self) -> str:
        with open(self._spec_path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()

    def load_spec(self) -> dict:
        if not self.is_sealed():
            raise HoldoutError(f"Vault '{self.name}' has no sealed spec")
        with open(self._spec_path) as fh:
            return json.load(fh)

    def _verify_passphrase(self, passphrase: str, *, stage: str, acquired_by: str) -> None:
        """C-2/C4/C9: cryptographic check against the verifier written at
        seal() time. Used by both ``acquire_once`` (stage='acquire') and
        ``authorize_retry`` (stage='retry') — the retry gate had the same
        presence-only defect shape as C4 originally did (found in the
        re-audit; see the deliverable note) and is fixed the same way.
        Raises before any side effect; logs the bad attempt either way.
        """
        ok = False
        if passphrase and passphrase.strip():
            try:
                with open(self._verifier_path) as fh:
                    verifier = json.load(fh)
                salt = base64.b64decode(verifier["salt_b64"])
                ok = _verifier_hash(passphrase, salt) == verifier["verifier_sha256"]
            except FileNotFoundError:
                # Vault sealed before C-2 (or verifier.json lost). Fail
                # closed: no verifier means no basis to accept anything.
                ok = False
        if not ok:
            self._grant_log(
                "VAULT_ACQUIRE",
                "holdout_bad_passphrase_attempt",
                {"vault": self.name, "by": acquired_by, "stage": stage},
            )
            raise HoldoutPassphraseError(
                f"Wrong passphrase at {stage}. Refused before any fetch; "
                "the vault is not retired and is not modified."
            )

    # -- D3 / C: acquire (Gate 1, exactly once) ---------------------------

    def acquire_once(
        self,
        passphrase: str,
        fetch: Callable[[dict], pd.DataFrame],
        *,
        acquired_by: str,
        holdout_min_months: float = HOLDOUT_MIN_MONTHS_DEFAULT,
    ) -> pd.DataFrame:
        """Fetch the holdout series for ``[C, now]`` and seal it, exactly
        once, ever. ``fetch(spec) -> DataFrame`` is the caller-supplied
        network call, injected so the vault stays agnostic of any venue's
        client library and so tests never touch a real network.

        Ordering (each gate below is checked, and refuses, before any
        network call — D3's first bullet):
        C2 retired -> C4 passphrase (cryptographic, against the seal-time
        verifier) -> C3 spec tamper -> C5 not-yet-reached -> C6/C7 retry
        authorization -> log attempt -> fetch -> C-7 acquisition-side
        non-overlap check -> C10 schema check -> seal payload ->
        log acquired -> D1 leak check -> lift D2 ceiling.
        """
        if not self.is_sealed():
            raise HoldoutError(f"Vault '{self.name}' has no sealed spec")

        # C2 — second acquisition retires (rider-named negative).
        if self.is_retired():
            self._grant_log(
                "VAULT_ACQUIRE",
                "holdout_second_acquisition_attempt",
                {"vault": self.name, "by": acquired_by},
            )
            raise HoldoutRetiredError(
                f"Vault '{self.name}' was already acquired. It is retired; "
                "results derived from it after this point are invalid."
            )

        # C4 — wrong/missing passphrase (rider-named negative), checked
        # CRYPTOGRAPHICALLY against the verifier written at seal() time
        # (Acceptance 001 C-2). This is what closes I-015: a wrong-but-
        # non-empty passphrase ("hunter3-TYPO" against "hunter2") now
        # fails this comparison and is refused before any fetch, rather
        # than passing a mere presence check and sealing the payload
        # under the typo.
        self._verify_passphrase(passphrase, stage="acquire", acquired_by=acquired_by)

        # C3 — spec-hash mismatch (rider-named negative). No network call.
        sealed = self._sealed_event()
        sealed_hash = sealed["detail"]["spec_sha256"]
        current_hash = self._current_spec_sha256()
        if current_hash != sealed_hash:
            self._grant_log(
                "VAULT_ACQUIRE",
                "holdout_spec_tampered",
                {
                    "vault": self.name,
                    "sealed_sha256": sealed_hash,
                    "found_sha256": current_hash,
                },
            )
            raise HoldoutSpecTamperedError(
                f"Vault '{self.name}': spec.json does not match the hash "
                "sealed at pre-registration. Refused before any fetch."
            )

        spec = self.load_spec()
        cutoff = pd.Timestamp(spec["cutoff"])
        now = pd.Timestamp.now(tz="UTC")

        # C5 — fetch before pinned C is reached (rider-named negative).
        if now < cutoff:
            self._grant_log(
                "VAULT_ACQUIRE",
                "holdout_acquisition_premature",
                {"vault": self.name, "cutoff": spec["cutoff"], "now": now.isoformat()},
            )
            raise HoldoutNotYetReachedError(
                f"Vault '{self.name}': wall-clock has not reached the "
                f"sealed cutoff {spec['cutoff']}; [C, G] is empty."
            )

        # C6/C7 — retry gate: one authorization buys exactly one further
        # attempt after a failure.
        failed = self._events("holdout_acquisition_failed")
        authorized = self._events("holdout_retry_authorized")
        if failed and len(authorized) < len(failed):
            self._grant_log(
                "VAULT_ACQUIRE",
                "holdout_retry_unauthorized_attempt",
                {"vault": self.name, "by": acquired_by},
            )
            raise HoldoutRetryUnauthorizedError(
                f"Vault '{self.name}' is ACQUISITION_FAILED. A further "
                "attempt requires a logged holdout_retry_authorized event "
                "(Principal passphrase + a written Issue Log entry naming "
                "the cause)."
            )

        # Irreversible act from here: log BEFORE any network call.
        self._grant_log(
            "VAULT_ACQUIRE",
            "holdout_acquisition_attempted",
            {
                "vault": self.name,
                "spec_sha256": sealed_hash,
                "by": acquired_by,
                "retry_number": len(failed),
            },
        )

        try:
            df = fetch(spec)
        except Exception as exc:
            self._grant_log(
                "VAULT_ACQUIRE",
                "holdout_acquisition_failed",
                {"vault": self.name, "error": str(exc)},
            )
            raise HoldoutAcquisitionFailedError(str(exc)) from exc

        # C-7 — acquisition-side enforcement of the load-bearing property
        # the legacy test protected (Acceptance 001 §4, R-F1/F2-3(2)):
        # `acquired.index.min() > C`. B2/B3/B6 already guarantee no row
        # after C ever enters pit.db via ingest(); this is the fetch-side
        # twin — a fetch callable that returns rows AT OR BEFORE C (i.e.
        # returns the in-sample history instead of, or in addition to, the
        # holdout) must not be allowed to seal as "the holdout". Treated as
        # a C6-class acquisition failure: ACQUISITION_FAILED, not retired,
        # retry-gated.
        fetched_idx = pd.to_datetime(df.index)
        fetched_idx = (
            fetched_idx.tz_localize("UTC") if fetched_idx.tz is None
            else fetched_idx.tz_convert("UTC")
        )
        overlap = fetched_idx <= cutoff
        if len(fetched_idx) and overlap.any():
            n = int(overlap.sum())
            self._grant_log(
                "VAULT_ACQUIRE",
                "holdout_acquisition_failed",
                {
                    "vault": self.name,
                    "error": f"fetched frame contains {n} row(s) at or "
                             f"before cutoff C={cutoff.isoformat()}",
                },
            )
            raise HoldoutAcquisitionOverlapError(
                f"Vault '{self.name}': fetch() returned {n} row(s) with "
                f"event_time <= C ({cutoff.isoformat()}). The acquired "
                "series must be strictly after the in-sample cutoff — a "
                "fetch that returns in-sample history cannot be sealed as "
                "the holdout. Refused; not retired."
            )

        # C10 — schema-fingerprint mismatch: refuse to seal, treat as a
        # failed acquisition (same ACQUISITION_FAILED / retry-gate path).
        ok, why = _schema_matches(df, spec["schema_fingerprint"])
        if not ok:
            self._grant_log(
                "VAULT_ACQUIRE",
                "holdout_acquisition_failed",
                {"vault": self.name, "error": f"schema_fingerprint mismatch: {why}"},
            )
            raise HoldoutSchemaMismatchError(
                f"Vault '{self.name}': fetched frame does not match the "
                f"sealed schema_fingerprint: {why}"
            )

        # Seal the payload. R-17: the file write is guarded, same
        # self-granted pattern as seal()'s.
        with self.registry.write_grant(
            reason="VAULT_ACQUIRE", dispatch="HoldoutVault.acquire_once",
            token=_INTERNAL_TOKEN,
        ):
            self.registry._require_grant("vault_file_write")
        salt = os.urandom(16)
        f = Fernet(_derive_key(passphrase, salt))
        buf = io.BytesIO()
        df.to_parquet(buf)
        payload_bytes = f.encrypt(buf.getvalue())
        with open(self._payload_path, "wb") as fh:
            fh.write(payload_bytes)
        payload_sha256 = hashlib.sha256(payload_bytes).hexdigest()

        window_months = _span_months(df.index)
        acquired_utc = now.timestamp()
        acq_meta = {
            "salt_b64": base64.b64encode(salt).decode(),
            "payload_sha256": payload_sha256,
            "acquired_utc": acquired_utc,
            "window_months": window_months,
            "n_rows": int(len(df)),
        }
        with open(self._acq_meta_path, "w") as fh:
            json.dump(acq_meta, fh, indent=2)

        acquired_event_id = self._grant_log(
            "VAULT_ACQUIRE",
            "holdout_acquired",
            {
                "vault": self.name,
                "payload_sha256": payload_sha256,
                "by": acquired_by,
                "n_rows": int(len(df)),
                "window_months": window_months,
                "holdout_min_months": holdout_min_months,
                "retry_count": len(authorized),
            },
        )

        # D1 — leak detection: rows in (C, G] knowable before this
        # acquisition are a leak regardless of how they got there.
        if self.store is not None:
            leaked = self.store.rows_in_window(
                spec["source"], spec["dataset_id"], cutoff, now, acquired_utc
            )
            if leaked:
                self._grant_log(
                    "VAULT_ACQUIRE",
                    "holdout_pre_acquisition_leak",
                    {
                        "vault": self.name,
                        "n_rows": len(leaked),
                        "sample": leaked[:10],
                    },
                )
            # D2 — lift the ceiling, scoped to this single sealed
            # acquisition (the spec-hash argument is what makes B5 hold:
            # only a caller who has independently verified the sealed
            # spec, as this method just did, can lift it). C-9: record
            # which acquisition did it.
            self.store._lift_ceiling(
                spec["source"], spec["dataset_id"], self.family, sealed_hash,
                lifted_by_event_id=acquired_event_id,
            )

        return df

    def authorize_retry(self, passphrase: str, reason: str, authorized_by: str = "") -> None:
        """Principal-only: authorize one further acquisition attempt after
        a failure. Requires the *correct* passphrase, checked cryptographically
        against the same seal-time verifier acquire_once uses (re-audit
        finding: this method previously did only a presence check — the
        identical defect shape C4 had before C-2, just with a smaller
        blast radius since a bad retry-authorization doesn't seal or
        retire anything. Fixed the same way, for the same reason: a typo
        here should not count as "the Principal authorized a retry").
        Also requires a stated cause naming the Issue Log entry — an
        unreasoned retry is exactly the loophole Ruling 001 D3 rejects.
        """
        self._verify_passphrase(passphrase, stage="retry", acquired_by=authorized_by)
        if not reason or not reason.strip():
            raise ValueError("Retry authorization requires a stated cause.")
        self._grant_log(
            "VAULT_ACQUIRE",
            "holdout_retry_authorized",
            {"vault": self.name, "reason": reason, "by": authorized_by},
        )

    def read_acquired(self, passphrase: str) -> pd.DataFrame:
        """C9: re-read the sealed, acquired holdout series. This is where
        passphrase *correctness* is actually verified cryptographically —
        by definition, since payload.enc now exists to decrypt against.
        Idempotent: does not log an acquisition event or consume anything.
        """
        if not self.is_retired():
            raise HoldoutError(f"Vault '{self.name}' has not been acquired yet")
        with open(self._acq_meta_path) as fh:
            meta = json.load(fh)
        salt = base64.b64decode(meta["salt_b64"])
        f = Fernet(_derive_key(passphrase, salt))
        with open(self._payload_path, "rb") as fh:
            token = fh.read()
        try:
            raw = f.decrypt(token)
        except InvalidToken:
            raise HoldoutPassphraseError("Wrong passphrase") from None
        return pd.read_parquet(io.BytesIO(raw))

    # -- F1: legacy API retired -------------------------------------------

    def lock(self, *args, **kwargs):
        raise HoldoutRegimeError(
            "HoldoutVault.lock() is retired under Amendment P-1 (fetch-"
            "then-encrypt is no longer permitted). Use seal() at "
            "pre-registration and acquire_once() at Gate 1."
        )

    def open_once(self, *args, **kwargs):
        raise HoldoutRegimeError(
            "HoldoutVault.open_once() is retired under Amendment P-1. Use "
            "acquire_once() at Gate 1 for the (exactly-once) fetch, or "
            "read_acquired() to re-read an already-acquired payload."
        )
