"""Holdout Vault — Amendment P-1 regime, per Validation Ruling 001 §2.3.

Under Amendment P-1 the firm never holds holdout plaintext before Gate 1.
The vault therefore has two artifacts, written at two different times, and
four states:

    SEALED --> (ACQUISITION_FAILED <-> retry) --> ACQUIRED --> RETIRED

- ``spec.json`` (+ its sha256 logged as ``holdout_spec_sealed``) is written
  at pre-registration (Gate 0), via :meth:`HoldoutVault.seal`. It is
  hash-committed, not encrypted — there is no secret in a specification.
  Sealing also writes a D2 ingest ceiling into the paired ``PITStore`` (if
  one is supplied), so a seat that calls a loader with any end date cannot
  accidentally ingest past the cutoff: the store refuses.

- ``payload.enc`` is written at Gate 1, from the series actually fetched at
  that time, via :meth:`HoldoutVault.acquire_once`. It is encrypted under
  the Principal's passphrase (PBKDF2 -> Fernet, same construction as
  before) and retained permanently, with its sha256 logged as
  ``holdout_acquired``. A second acquisition raises and is logged; a
  failed acquisition moves the vault to ACQUISITION_FAILED without
  retiring it, and a further attempt requires a logged
  ``holdout_retry_authorized`` event (Principal passphrase + a stated
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
    HoldoutSchemaMismatchError,
)
from .registry import TrialRegistry

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
    "HoldoutSchemaMismatchError",
    "VaultState",
]

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
        store=None,
    ):
        """
        Parameters
        ----------
        family : the hypothesis family this vault protects. Logged on every
            event and required so Gate 1 can evaluate the holdout criterion
            per-family (Ruling 001 D1 / E1; fixes I-007). This is a
            constructor-level, immutable property of the vault by Principal
            direct instruction — not inferred from ``name``.
        store : an optional ``PITStore``. If given, ``seal()`` writes the D2
            ingest ceiling into it and ``acquire_once()`` lifts it on
            success and runs the D1 leak-detection check against it. A
            vault constructed without a store still works (spec sealing,
            acquisition, tamper/retry logic) but forgoes the ceiling
            enforcement and leak detection — callers that skip this are
            choosing to forgo the compensating control the ruling
            considers "the ruling's most important element" and that
            choice should not be made silently in production use.
        """
        self.dir = vault_dir
        self.registry = registry
        self.name = name
        self.family = family
        self.store = store
        os.makedirs(vault_dir, exist_ok=True)

    @property
    def _spec_path(self) -> str:
        return os.path.join(self.dir, "spec.json")

    @property
    def _payload_path(self) -> str:
        return os.path.join(self.dir, "payload.enc")

    @property
    def _acq_meta_path(self) -> str:
        return os.path.join(self.dir, "acquisition_meta.json")

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
        holdout_end_rule: str = "open-ended, forward from C",
        resolution_source: str = "",
        sealed_by: str = "",
    ) -> dict:
        """D1 + A1-A4. Writes ``spec.json`` and the ``holdout_spec_sealed``
        event. Binding fields (everything above) are immutable thereafter:
        a byte-level edit to ``spec.json`` is caught at acquisition (D4).
        """
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
        try:
            cutoff_ts = _to_utc(cutoff)
        except Exception as exc:
            raise HoldoutSpecInvalidError(f"malformed cutoff: {exc}") from exc

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

        self.registry.log_event(
            "holdout_spec_sealed",
            self.family,
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
        C2 retired -> C4 passphrase presence -> C3 spec tamper ->
        C5 not-yet-reached -> C6/C7 retry authorization -> log attempt ->
        fetch -> C10 schema check -> seal payload -> log acquired ->
        D1 leak check -> lift D2 ceiling.
        """
        if not self.is_sealed():
            raise HoldoutError(f"Vault '{self.name}' has no sealed spec")

        # C2 — second acquisition retires (rider-named negative).
        if self.is_retired():
            self.registry.log_event(
                "holdout_second_acquisition_attempt",
                self.family,
                {"vault": self.name, "by": acquired_by},
            )
            raise HoldoutRetiredError(
                f"Vault '{self.name}' was already acquired. It is retired; "
                "results derived from it after this point are invalid."
            )

        # C4 — wrong/missing passphrase (rider-named negative). There is no
        # ciphertext yet to test correctness against at first acquisition
        # (see the implementation note): this is a presence gate, not a
        # cryptographic check. The cryptographic check is read_acquired().
        if not passphrase or not passphrase.strip():
            self.registry.log_event(
                "holdout_bad_passphrase_attempt",
                self.family,
                {"vault": self.name, "by": acquired_by, "stage": "acquire"},
            )
            raise HoldoutPassphraseError(
                "A non-empty Principal passphrase is required to acquire."
            )

        # C3 — spec-hash mismatch (rider-named negative). No network call.
        sealed = self._sealed_event()
        sealed_hash = sealed["detail"]["spec_sha256"]
        current_hash = self._current_spec_sha256()
        if current_hash != sealed_hash:
            self.registry.log_event(
                "holdout_spec_tampered",
                self.family,
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
            self.registry.log_event(
                "holdout_acquisition_premature",
                self.family,
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
            self.registry.log_event(
                "holdout_retry_unauthorized_attempt",
                self.family,
                {"vault": self.name, "by": acquired_by},
            )
            raise HoldoutRetryUnauthorizedError(
                f"Vault '{self.name}' is ACQUISITION_FAILED. A further "
                "attempt requires a logged holdout_retry_authorized event "
                "(Principal passphrase + a written Issue Log entry naming "
                "the cause)."
            )

        # Irreversible act from here: log BEFORE any network call.
        self.registry.log_event(
            "holdout_acquisition_attempted",
            self.family,
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
            self.registry.log_event(
                "holdout_acquisition_failed",
                self.family,
                {"vault": self.name, "error": str(exc)},
            )
            raise HoldoutAcquisitionFailedError(str(exc)) from exc

        # C10 — schema-fingerprint mismatch: refuse to seal, treat as a
        # failed acquisition (same ACQUISITION_FAILED / retry-gate path).
        ok, why = _schema_matches(df, spec["schema_fingerprint"])
        if not ok:
            self.registry.log_event(
                "holdout_acquisition_failed",
                self.family,
                {"vault": self.name, "error": f"schema_fingerprint mismatch: {why}"},
            )
            raise HoldoutSchemaMismatchError(
                f"Vault '{self.name}': fetched frame does not match the "
                f"sealed schema_fingerprint: {why}"
            )

        # Seal the payload.
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

        self.registry.log_event(
            "holdout_acquired",
            self.family,
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
                self.registry.log_event(
                    "holdout_pre_acquisition_leak",
                    self.family,
                    {
                        "vault": self.name,
                        "n_rows": len(leaked),
                        "sample": leaked[:10],
                    },
                )
            # D2 — lift the ceiling, scoped to this single sealed
            # acquisition (the spec-hash argument is what makes B5 hold:
            # only a caller who has independently verified the sealed
            # spec, as this method just did, can lift it).
            self.store._lift_ceiling(
                spec["source"], spec["dataset_id"], self.family, sealed_hash
            )

        return df

    def authorize_retry(self, passphrase: str, reason: str, authorized_by: str = "") -> None:
        """Principal-only: authorize one further acquisition attempt after
        a failure. Requires a passphrase (presence, per the C4 rationale
        above) and a stated cause naming the Issue Log entry — an
        unreasoned retry is exactly the loophole Ruling 001 D3 rejects.
        """
        if not passphrase or not passphrase.strip():
            raise HoldoutPassphraseError("Retry authorization requires a passphrase.")
        if not reason or not reason.strip():
            raise ValueError("Retry authorization requires a stated cause.")
        self.registry.log_event(
            "holdout_retry_authorized",
            self.family,
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
