#!/usr/bin/env bash
# Castellan Capital -- Polymarket capture VPS install script.
# DATA-INFRA-002. Idempotent: safe to re-run after editing the .service/
# .timer files in this directory or after a `git pull` refreshes
# /opt/castellan/repo/harness.
#
# PREREQUISITE (a [PRINCIPAL] step, done BEFORE this script runs -- see
# the cutover runbook in research/DATA-INFRA-002-vps-capture-migration.md):
#   rsync -avz --delete ./harness/ root@<vps-ip>:/opt/castellan/repo/harness/
#   scp -r ./deploy/polymarket-capture-vps root@<vps-ip>:/opt/castellan/install/
#
# This script deliberately does NOT clone the firm's git repository onto
# the VPS and does NOT copy book/, research/, logs/, or agents/ -- only
# the harness/ package the capture script needs. Minimizes what a VPS
# compromise could expose: the code that runs public-API polls, and
# nothing about the firm's registry, hypotheses, or other data sources
# (DATA-INFRA-002 §1).
#
# Usage (on the VPS, as root):
#   bash /opt/castellan/install/install.sh

set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
    echo "must run as root (systemctl, apt, useradd)" >&2
    exit 1
fi

REPO_HARNESS=/opt/castellan/repo/harness
if [[ ! -f "${REPO_HARNESS}/castellan/loaders.py" ]]; then
    echo "ERROR: ${REPO_HARNESS} does not look like a harness checkout." >&2
    echo "Rsync harness/ to ${REPO_HARNESS} first -- see this script's header." >&2
    exit 1
fi

echo "== installing OS packages =="
apt-get update -qq
apt-get install -y -qq python3 python3-venv python3-pip ca-certificates rsync

echo "== creating unprivileged service user =="
if ! id -u castellan >/dev/null 2>&1; then
    useradd --system --create-home --home-dir /opt/castellan --shell /usr/sbin/nologin castellan
fi

echo "== creating directories =="
mkdir -p /opt/castellan/book/logs
mkdir -p /opt/castellan/venv

echo "== building/updating the venv =="
if [[ ! -x /opt/castellan/venv/bin/python3 ]]; then
    python3 -m venv /opt/castellan/venv
fi
/opt/castellan/venv/bin/pip install --quiet --upgrade pip
# Base harness deps only (numpy/pandas/scipy/cryptography/pyarrow) -- the
# polymarket capture path needs none of the optional [data] extras
# (yfinance/ccxt), which this VPS should never need to install.
/opt/castellan/venv/bin/pip install --quiet -e "${REPO_HARNESS}" certifi

echo "== fixing ownership =="
chown -R castellan:castellan /opt/castellan

echo "== installing systemd units =="
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "${SCRIPT_DIR}/castellan-polymarket-capture.service" /etc/systemd/system/
cp "${SCRIPT_DIR}/castellan-polymarket-capture.timer" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now castellan-polymarket-capture.timer

echo "== running one poll immediately to verify end-to-end =="
systemctl start castellan-polymarket-capture.service
sleep 3
systemctl status castellan-polymarket-capture.service --no-pager -l || true

echo
echo "== install complete =="
echo "Verify with:"
echo "  systemctl status castellan-polymarket-capture.timer"
echo "  tail -20 /opt/castellan/book/logs/polymarket-book.out"
echo "  bash ${SCRIPT_DIR}/health_check.sh"
