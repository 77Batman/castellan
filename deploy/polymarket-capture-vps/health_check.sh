#!/usr/bin/env bash
# Castellan Capital -- Polymarket capture VPS health check. DATA-INFRA-002 §5.
#
# Run on the VPS directly, or remotely:
#   ssh <vps-host> bash /opt/castellan/install/health_check.sh
#
# Exits 0 if the timer is active, the last poll succeeded, and disk usage
# is below the warning threshold; nonzero otherwise, so this is usable as
# a monitoring check (cron + mail, or manual, at the operator's choice --
# nothing here schedules itself).

set -uo pipefail

STATUS=0
DISK_WARN_PCT=80
BOOK_DIR=/opt/castellan/book

echo "== timer status =="
if systemctl is-active --quiet castellan-polymarket-capture.timer; then
    echo "  active"
else
    echo "  NOT ACTIVE"
    STATUS=1
fi
systemctl list-timers castellan-polymarket-capture.timer --no-pager 2>/dev/null | sed -n '2p'

echo
echo "== last poll result =="
RESULT=$(systemctl show castellan-polymarket-capture.service --property=Result --value 2>/dev/null || echo "unknown")
LAST_RUN=$(systemctl show castellan-polymarket-capture.service --property=ActiveExitTimestamp --value 2>/dev/null || echo "unknown")
echo "  last exit result: ${RESULT}"
echo "  last active-exit:  ${LAST_RUN}"
if [[ "${RESULT}" != "success" && "${RESULT}" != "unknown" ]]; then
    echo "  WARNING: last run did not exit cleanly"
    STATUS=1
fi

echo
echo "== disk usage: ${BOOK_DIR} =="
if [[ -d "${BOOK_DIR}" ]]; then
    df -h "${BOOK_DIR}" | tail -1
    USE_PCT=$(df --output=pcent "${BOOK_DIR}" | tail -1 | tr -dc '0-9')
    du -sh "${BOOK_DIR}"/*.db 2>/dev/null || true
    if [[ -n "${USE_PCT}" ]] && [[ "${USE_PCT}" -ge "${DISK_WARN_PCT}" ]]; then
        echo "  WARNING: disk usage ${USE_PCT}% >= ${DISK_WARN_PCT}% -- see DATA-INFRA-002 §3"
        echo "  (retention policy decision, or a bigger volume, needed soon)"
        STATUS=1
    fi
else
    echo "  ${BOOK_DIR} does not exist -- has install.sh run?"
    STATUS=1
fi

echo
echo "== coverage (from this host's capture-only store) =="
VENV_PY=/opt/castellan/venv/bin/python3
REPORTER=/opt/castellan/repo/harness/scripts/report_polymarket_coverage.py
if [[ -x "${VENV_PY}" && -f "${REPORTER}" && -f "${BOOK_DIR}/pit_capture.db" ]]; then
    "${VENV_PY}" "${REPORTER}" --pit-db "${BOOK_DIR}/pit_capture.db" || STATUS=1
else
    echo "  cannot run coverage reporter (venv/reporter/store missing) -- has a poll run yet?"
fi

echo
echo "== recent log tail =="
tail -10 "${BOOK_DIR}/logs/polymarket-book.out" 2>/dev/null || echo "  no log yet"
if [[ -s "${BOOK_DIR}/logs/polymarket-book.err" ]]; then
    echo "  -- stderr is non-empty, last 10 lines: --"
    tail -10 "${BOOK_DIR}/logs/polymarket-book.err"
fi

echo
if [[ "${STATUS}" -eq 0 ]]; then
    echo "OK"
else
    echo "ISSUES FOUND -- see WARNING/NOT ACTIVE lines above"
fi
exit "${STATUS}"
