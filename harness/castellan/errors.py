"""Shared error types for the P-1 holdout regime (Validation Ruling 001).

Both ``holdout.py`` (the vault) and ``data.py`` (``PITStore``, which owns
the D2 ingest ceiling) need to raise and catch holdout-related errors
without importing each other, so the types live in their own module.
"""

from __future__ import annotations


class HoldoutError(RuntimeError):
    """Base class for all holdout-vault errors."""


class HoldoutRegimeError(HoldoutError):
    """The legacy fetch-then-lock / decrypt-then-open API is retired.

    Amendment P-1 (2026-07-28) forbids holding holdout plaintext before
    Gate 1. ``HoldoutVault.lock()`` and ``.open_once()`` violate that by
    construction and must not remain silently callable (Ruling 001, F1).
    """


class HoldoutAlreadySealedError(HoldoutError):
    """A vault's spec may be sealed exactly once (Ruling 001 A2)."""


class HoldoutSpecInvalidError(HoldoutError):
    """The spec failed validation at seal time (Ruling 001 A3)."""


class HoldoutSpecTamperedError(HoldoutError):
    """The spec on disk no longer matches the hash sealed at pre-registration
    (Ruling 001 D4 / A4 / C3)."""


class HoldoutRetiredError(HoldoutError):
    """The vault was already successfully acquired. It is permanently
    retired (Ruling 001 C2)."""


class HoldoutPassphraseError(HoldoutError):
    """No usable passphrase was supplied (Ruling 001 C4 / C9).

    See the implementation note (``research/DATA-IMPL-001-p1-vault.md``)
    for why this is a presence check at acquisition and a real
    cryptographic check only on re-read of an already-sealed payload.
    """


class HoldoutNotYetReachedError(HoldoutError):
    """Wall-clock has not reached the sealed cutoff C; there is nothing to
    acquire yet (Ruling 001 C5)."""


class HoldoutRetryUnauthorizedError(HoldoutError):
    """A further acquisition attempt was made after a failure, with no
    matching ``holdout_retry_authorized`` event (Ruling 001 C6)."""


class HoldoutAcquisitionFailedError(HoldoutError):
    """The injected fetch raised. The vault moves to ACQUISITION_FAILED and
    is NOT retired (Ruling 001 C6)."""


class HoldoutAcquisitionOverlapError(HoldoutAcquisitionFailedError):
    """Acquisition-side enforcement of the load-bearing property the legacy
    test protected: the fetched frame must contain nothing at or before the
    sealed cutoff C (``acquired.index.min() > C``). A ``HoldoutCeilingError``
    is *ingest*-side (rows already in ``pit.db``); this is the fetch-side
    twin that Validation Acceptance 001 found "enforced nowhere and asserted
    nowhere" (C-7 / R-F1/F2-4). Treated as a C6-class acquisition failure:
    the vault moves to ACQUISITION_FAILED, is NOT retired, and a further
    attempt requires ``holdout_retry_authorized``."""


class HoldoutSchemaMismatchError(HoldoutError):
    """The fetched frame does not match the sealed schema_fingerprint
    (Ruling 001 C10)."""


class HoldoutCeilingError(RuntimeError):
    """PITStore refused an ingest batch (or a ceiling mutation) that would
    cross, or bypass, a sealed holdout cutoff (Ruling 001 D2 / B3 / B5)."""
