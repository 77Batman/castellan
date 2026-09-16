"""C-4 reproducibility probe (VALIDATION-SPEC-005 sec2.5 / sec7.3 test
C-4). Deterministic, pre-committed-seed-only: draws the primary
(permutation, L=30) cell's first 200 resample indices from
`SeedSequence(MASTER_SEED).spawn(8)[1]` (index 1 = permutation at L=30
per the spec's own spawn-index table) against a small synthetic w-array,
and prints ONLY the sha256 of the resulting index array as its last
stdout line -- run twice, in separate processes, from
`test_c4_reproducibility_two_processes_same_seed`, and the two hashes
must be identical.

Kept deliberately independent of `book/pit.db` (no PIT data needed to
prove seed reproducibility) so the test is fast and has no live-data
dependency.
"""
import hashlib
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "harness"))
from castellan import nullcal  # noqa: E402

PREREG_SHA256 = "e5ebd3a6db02b97955518bc70db3906918e702f9879d3ad9928223ad6d2a105f"
MASTER_SEED = int(PREREG_SHA256[:16], 16)


def main():
    ss = np.random.SeedSequence(MASTER_SEED)
    kids = ss.spawn(8)
    rng = np.random.default_rng(kids[1])  # index 1 = permutation, L=30
    T, L = 500, 30
    sigmas = np.stack([nullcal.circular_block_permutation_index(T, L, rng) for _ in range(200)])
    h = hashlib.sha256(sigmas.tobytes()).hexdigest()
    print(f"master_seed={MASTER_SEED}")
    print(h)


if __name__ == "__main__":
    main()
