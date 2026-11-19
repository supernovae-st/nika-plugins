#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
#
# update-mirrors.sh — every installed nika-kit surface, one gesture.
#
# The staleness ladder is per-client and easy to half-climb (a Claude Code
# install once sat THREE releases behind, silently, with a fresh clone right
# next to it — the clone had updated, the install had not). This script
# climbs every rung on every surface it finds, and says what it did:
#
#   binary       nika on PATH (brew is the writer)  upgrade when it lags the
#                                                   kit train (major.minor)
#   Cursor       ~/.cursor/plugins/local/nika        rsync from this repo
#   Claude Code  marketplace clone + install         BOTH rungs + restart note
#   Codex        marketplace clone (per-version cache refreshes on next run)
#
#   scripts/update-mirrors.sh            # update every surface found
#   scripts/update-mirrors.sh --check    # read-only: report drift, exit 1 if any
#
# A surface that is absent is skipped with a note, never an error — the
# script serves laptops with one client as well as the full triple. The
# binary rides the same contract: absent → note + install line, never an
# auto-install (the marketplaces never consented to placing system
# binaries; this script keeps that line even as an explicit gesture).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KIT="$ROOT/.agents/plugins/nika"
CHECK=0
[[ "${1:-}" == "--check" ]] && CHECK=1

repo_version="$(python3 -c "import json;print(json.load(open('$KIT/.claude-plugin/plugin.json'))['version'])")"
echo "kit at this checkout: $repo_version"
drift=0

surface_version() { # $1 = plugin.json path
  [[ -f "$1" ]] && python3 -c "import json;print(json.load(open('$1'))['version'])" 2>/dev/null || echo absent
}

# ── The binary first (every surface invokes it · brew is the writer) ──
# Compared at major.minor: the kit is cut per release train, patch
# releases ship binary-only, so patch drift is not a finding.
if command -v nika >/dev/null 2>&1; then
  bin_v="$(nika --version 2>/dev/null | tr -cd '0-9.')"
  IFS=. read -r r_maj r_min _ <<<"$repo_version"
  IFS=. read -r b_maj b_min _ <<<"${bin_v:-.}"
  if [[ -z "$b_maj" || -z "$b_min" ]]; then
    echo "· binary: nika answers no parseable version — skipped"
  elif (( b_maj == r_maj && b_min == r_min )); then
    echo "✔ binary: nika $bin_v (the $r_maj.$r_min train)"
  elif (( b_maj < r_maj || (b_maj == r_maj && b_min < r_min) )); then
    if [[ $CHECK -eq 1 ]]; then
      echo "✖ binary: nika $bin_v lags the kit train $repo_version — brew upgrade nika"; drift=1
    elif command -v brew >/dev/null 2>&1; then
      brew upgrade nika >/dev/null 2>&1 || true
      nv="$(nika --version 2>/dev/null | tr -cd '0-9.')"
      if [[ "$nv" == "$bin_v" ]]; then
        echo "✖ binary: brew moved nothing (still $nv) — the tap may not carry the $r_maj.$r_min train yet"
      else
        echo "✔ binary: nika $bin_v → $nv"
      fi
    else
      echo "✖ binary: nika $bin_v lags the kit train $repo_version and brew is absent — update via your install path (nika.sh)"
    fi
  else
    # The binary rides ahead: the stale side is THIS CHECKOUT, not brew.
    if [[ $CHECK -eq 1 ]]; then
      echo "✖ binary: nika $bin_v rides ahead of this checkout ($repo_version) — git pull, then re-run"; drift=1
    else
      echo "· binary: nika $bin_v rides ahead of this checkout ($repo_version) — git pull, then re-run"
    fi
  fi
else
  echo "· binary: nika absent — every surface invokes it (brew install nika-open/tap/nika)"
fi

# ── Cursor (local plugin dir · rsync is the only writer) ──────────────
CURSOR_DIR="$HOME/.cursor/plugins/local/nika"
v="$(surface_version "$CURSOR_DIR/.claude-plugin/plugin.json")"
if [[ "$v" == absent ]]; then
  echo "· cursor: no local plugin — skipped (marketplace installs self-manage)"
elif [[ "$v" == "$repo_version" && $CHECK -eq 1 ]]; then
  echo "✔ cursor: $v"
elif [[ $CHECK -eq 1 ]]; then
  echo "✖ cursor: $v (repo has $repo_version)"; drift=1
else
  rsync -a --delete "$KIT/" "$CURSOR_DIR/"
  chmod +x "$CURSOR_DIR"/scripts/*.sh 2>/dev/null || true
  echo "✔ cursor: $v → $(surface_version "$CURSOR_DIR/.claude-plugin/plugin.json")"
fi

# ── Claude Code (TWO rungs: the clone, then the install) ──────────────
# Rung 2 IS probeable: installed_plugins.json is the install rung of
# record (the cache retains old version dirs — the JSON, not a dir
# listing, says what sessions load). The prior claim that it was not
# probeable read-only died empirically 2026-07-29.
claude_install_version() {
  [[ -f "$HOME/.claude/plugins/installed_plugins.json" ]] &&
    python3 -c 'import json,os
p = os.path.expanduser("~/.claude/plugins/installed_plugins.json")
print(json.load(open(p))["plugins"]["nika@nika"][0]["version"])' 2>/dev/null || echo absent
}
if command -v claude >/dev/null 2>&1; then
  CLAUDE_CLONE="$HOME/.claude/plugins/marketplaces/nika/.agents/plugins/nika/.claude-plugin/plugin.json"
  v="$(surface_version "$CLAUDE_CLONE")"
  iv="$(claude_install_version)"
  if [[ "$v" == absent && "$iv" == absent ]]; then
    echo "· claude: plugin not installed — skipped (claude plugin install nika@nika)"
  elif [[ "$v" == "$repo_version" && "$iv" == "$repo_version" && $CHECK -eq 1 ]]; then
    echo "✔ claude: $v (both rungs)"
  elif [[ $CHECK -eq 1 ]]; then
    echo "✖ claude: clone $v · install $iv (repo has $repo_version)"; drift=1
  else
    claude plugin marketplace update nika >/dev/null 2>&1 || true       # rung 1: the clone
    claude plugin update nika@nika >/dev/null 2>&1 || true              # rung 2: the install
    niv="$(claude_install_version)"
    if [[ "$niv" == "$repo_version" ]]; then
      echo "✔ claude: install $iv → $niv — restart the session to load it"
    else
      echo "✖ claude: install did not reach $repo_version (still $niv) — claude plugin install nika@nika, then restart"
    fi
  fi
else
  echo "· claude: CLI absent — skipped"
fi

# ── Codex (TWO rungs too: the clone, then the per-version cache the
#    sessions load — the cache refreshes on the next codex run) ────────
codex_cache_version() {
  local d names=()
  for d in "$HOME/.codex/plugins/cache/nika/nika"/*/; do
    [[ -d "$d" ]] || continue
    d="$(basename "$d")"
    [[ "$d" =~ ^[0-9]+\.[0-9]+(\.[0-9]+)?$ ]] && names+=("$d")
  done
  ((${#names[@]})) && printf '%s\n' "${names[@]}" | sort -t. -k1,1n -k2,2n -k3,3n | tail -1
}
if command -v codex >/dev/null 2>&1; then
  CODEX_CLONE="$HOME/.codex/.tmp/marketplaces/nika/.agents/plugins/nika/.claude-plugin/plugin.json"
  v="$(surface_version "$CODEX_CLONE")"
  cv="$(codex_cache_version)"
  [[ -n "$cv" ]] || cv=absent
  if [[ "$v" == absent && "$cv" == absent ]]; then
    echo "· codex: plugin not installed — skipped (codex plugin add nika@nika)"
  elif [[ "$v" == "$repo_version" && "$cv" == "$repo_version" && $CHECK -eq 1 ]]; then
    echo "✔ codex: $v (both rungs)"
  elif [[ "$v" == "$repo_version" && $CHECK -eq 1 ]]; then
    echo "✔ codex: clone $v · cache $cv — a codex run refreshes the cache"
  elif [[ $CHECK -eq 1 ]]; then
    echo "✖ codex: clone $v · cache $cv (repo has $repo_version)"; drift=1
  else
    codex plugin marketplace upgrade nika >/dev/null 2>&1 || true
    echo "✔ codex: clone $v → $(surface_version "$CODEX_CLONE") · cache $cv refreshes on the next codex run"
  fi
else
  echo "· codex: CLI absent — skipped"
fi

if [[ $CHECK -eq 1 ]]; then
  if [[ $drift -eq 0 ]]; then
    echo "no drift"
  else
    echo "drift detected — run scripts/update-mirrors.sh"
    exit 1
  fi
fi
