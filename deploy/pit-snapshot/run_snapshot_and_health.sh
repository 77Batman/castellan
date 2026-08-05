#!/usr/bin/env bash
# Castellan Capital -- wrapper invoked by the pit-snapshot launchd job.
# DATA-INFRA-003. Runs the snapshot routine for all three book/*.db files,
# then the health check, and propagates a nonzero exit if either step
# reports a problem -- launchd's own per-job exit-status bookkeeping
# (visible via `launchctl list capital.castellan.pit-snapshot`) is then a
# second, independent place the firm can see a failure, alongside
# logs/capture/snapshot-failures.log and the per-db *.status.json files.
#
# [PRINCIPAL] Edit REPO_ROOT and PYTHON3 below if this machine's paths
# differ from the ones this script was written against (matches the
# existing capital.castellan.polymarket-book.plist convention).

set -uo pipefail

REPO_ROOT="/Users/<user>/projects/castellan-capital"
PYTHON3="/Library/Frameworks/Python.framework/Versions/3.13/bin/python3"

cd "${REPO_ROOT}" || exit 1

"${PYTHON3}" harness/scripts/snapshot_book.py --dest "$HOME/Library/Mobile Documents/com~apple~CloudDocs/castellan-backups"
SNAP_STATUS=$?

"${PYTHON3}" harness/scripts/check_snapshot_health.py --dest "$HOME/Library/Mobile Documents/com~apple~CloudDocs/castellan-backups"
HEALTH_STATUS=$?

if [[ "${SNAP_STATUS}" -ne 0 || "${HEALTH_STATUS}" -ne 0 ]]; then
    echo "pit-snapshot run: PROBLEM (snapshot exit=${SNAP_STATUS}, health exit=${HEALTH_STATUS})"
    exit 1
fi

echo "pit-snapshot run: OK"
exit 0
