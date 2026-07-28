"""Holdout Vault — house rule 4, enforced physically.

The most recent HOLDOUT_FRACTION of each dataset is serialized, encrypted
with a key derived from a passphrase held by the Principal, and written
to disk. The plaintext never touches the research path. Opening requires
the passphrase, is logged permanently in the Trial Registry, and a second
open attempt raises and marks the vault RETIRED forever.

This converts "the holdout is sacred" from a promise into a property.
"""

from __future__ import annotations

import base64
import io
import json
import os
import time

import pandas as pd
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .registry import TrialRegistry

HOLDOUT_FRACTION_DEFAULT = 0.25


class HoldoutError(RuntimeError):
    pass


class HoldoutRetiredError(HoldoutError):
    """The vault was already opened once. It is permanently retired."""


def _derive_key(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt, iterations=200_000
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))


class HoldoutVault:
    """One vault per (dataset, family). Directory layout:

    vault_dir/
      meta.json      # cutoff date, fraction, rows, salt — public
      payload.enc    # encrypted holdout parquet bytes
    """

    def __init__(self, vault_dir: str, registry: TrialRegistry, name: str):
        self.dir = vault_dir
        self.registry = registry
        self.name = name
        os.makedirs(vault_dir, exist_ok=True)

    @property
    def _meta_path(self) -> str:
        return os.path.join(self.dir, "meta.json")

    @property
    def _payload_path(self) -> str:
        return os.path.join(self.dir, "payload.enc")

    def exists(self) -> bool:
        return os.path.exists(self._meta_path)

    # -- lock ----------------------------------------------------------

    def lock(
        self,
        df: pd.DataFrame,
        passphrase: str,
        fraction: float = HOLDOUT_FRACTION_DEFAULT,
    ) -> pd.DataFrame:
        """Split `df` (DatetimeIndex, sorted) at the holdout boundary.
        Encrypts and stores the most recent `fraction`; returns ONLY the
        in-sample portion. The caller never holds holdout plaintext.
        """
        if self.exists():
            raise HoldoutError(
                f"Vault '{self.name}' already exists; re-locking would "
                "allow choosing a favorable split. Refused."
            )
        if not df.index.is_monotonic_increasing:
            raise HoldoutError("Index must be sorted ascending by time")
        n = len(df)
        n_hold = max(1, int(round(n * fraction)))
        insample, holdout = df.iloc[: n - n_hold], df.iloc[n - n_hold :]

        salt = os.urandom(16)
        f = Fernet(_derive_key(passphrase, salt))
        buf = io.BytesIO()
        holdout.to_parquet(buf)
        with open(self._payload_path, "wb") as fh:
            fh.write(f.encrypt(buf.getvalue()))
        meta = {
            "name": self.name,
            "fraction": fraction,
            "n_total": n,
            "n_holdout": n_hold,
            "cutoff": str(insample.index[-1]),
            "holdout_start": str(holdout.index[0]),
            "holdout_end": str(holdout.index[-1]),
            "salt_b64": base64.b64encode(salt).decode(),
            "locked_utc": time.time(),
        }
        with open(self._meta_path, "w") as fh:
            json.dump(meta, fh, indent=2)
        self.registry.log_event(
            "holdout_locked",
            None,
            {"vault": self.name, **{k: meta[k] for k in
             ("cutoff", "holdout_start", "holdout_end", "n_holdout")}},
        )
        return insample

    # -- open (once) ---------------------------------------------------

    def _open_count(self) -> int:
        return len(
            [e for e in self.registry.events(kind="holdout_opened")
             if e["detail"].get("vault") == self.name]
        )

    def is_retired(self) -> bool:
        return self._open_count() >= 1

    def open_once(self, passphrase: str, opened_by: str) -> pd.DataFrame:
        """Decrypt and return the holdout. Exactly once, ever.

        The opening is logged before the data is returned; a second call
        raises HoldoutRetiredError and logs the violation attempt.
        """
        if not self.exists():
            raise HoldoutError(f"Vault '{self.name}' does not exist")
        if self.is_retired():
            self.registry.log_event(
                "holdout_second_open_attempt",
                None,
                {"vault": self.name, "by": opened_by},
            )
            raise HoldoutRetiredError(
                f"Vault '{self.name}' was already opened. It is retired; "
                "results derived from it after this point are invalid."
            )
        with open(self._meta_path) as fh:
            meta = json.load(fh)
        salt = base64.b64decode(meta["salt_b64"])
        f = Fernet(_derive_key(passphrase, salt))
        with open(self._payload_path, "rb") as fh:
            token = fh.read()
        try:
            raw = f.decrypt(token)
        except InvalidToken:
            raise HoldoutError("Wrong passphrase") from None
        # Log BEFORE returning plaintext: opening is irreversible.
        self.registry.log_event(
            "holdout_opened",
            None,
            {"vault": self.name, "by": opened_by, "opened_utc": time.time()},
        )
        return pd.read_parquet(io.BytesIO(raw))
