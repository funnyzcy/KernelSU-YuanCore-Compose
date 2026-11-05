#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 YuanCore contributors
#
# Publish the yuancore branch to YOUR OWN GitHub repository.
# Upstream stays reachable as `upstream`; your fork becomes `origin`.
# Nothing is pushed in --dry-run mode.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash tools/yuancore_publish.sh [--dry-run] <your-repo-url>

Example:
  bash tools/yuancore_publish.sh --dry-run git@github.com:YOURNAME/KernelSU-YuanCore.git
  bash tools/yuancore_publish.sh          https://github.com/YOURNAME/KernelSU-YuanCore.git

Before running: create an EMPTY repository on GitHub (do NOT initialise it
with README / LICENSE / .gitignore). Then this script will:
  1. run tools/yuancore_prepublish_check.py  (blocks on any finding)
  2. rename the official `origin` to `upstream`
  3. point `origin` at your repository
  4. push -u origin yuancore
EOF
}

DRY=0
URL=""
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1 ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "Unknown option: $1" >&2; usage; exit 1 ;;
    *) URL="$1" ;;
  esac
  shift
done
if [ -z "$URL" ]; then usage; exit 1; fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PY="${PYTHON:-python}"

echo "==> pre-publication hygiene check"
"$PY" tools/yuancore_prepublish_check.py || {
  echo "==> BLOCKED: fix the failures above before publishing." >&2
  exit 1
}

run() {
  if [ "$DRY" -eq 1 ]; then
    echo "  [dry-run] $*"
  else
    echo "  $*"
    "$@"
  fi
}

echo "==> remote layout"
if git remote | grep -qx upstream; then
  echo "  upstream already configured"
elif git remote | grep -qx origin; then
  run git remote rename origin upstream
else
  run git remote add upstream https://github.com/tiann/KernelSU.git
fi

if git remote | grep -qx origin; then
  run git remote set-url origin "$URL"
else
  run git remote add origin "$URL"
fi

echo "==> branch"
BRANCH="$(git branch --show-current)"
if [ "$BRANCH" != "yuancore" ]; then
  echo "  WARNING: current branch is '$BRANCH', expected 'yuancore'" >&2
fi

echo "==> push"
run git push -u origin yuancore

echo "==> done"
if [ "$DRY" -eq 1 ]; then
  echo "    upstream : https://github.com/tiann/KernelSU.git (would be)"
  echo "    origin   : $URL (would be; no remote was changed)"
else
  echo "    upstream : $(git remote get-url upstream 2>/dev/null || echo '(missing)')"
  echo "    origin   : $(git remote get-url origin 2>/dev/null || echo '(missing)')"
fi
echo "    next     : set the GitHub repo description to mention UNOFFICIAL FORK"
echo "               and keep README-YuanCore.md / NOTICE linked from the repo about box."
