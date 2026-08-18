#!/usr/bin/env bash
# version-coherence.sh — the 0.x law across every live install surface.
#
# Doctrine: the whole constellation rides 0.x until the readiness-gated
# 1.0.0 launch; ONLY the nine-key language envelope is frozen. This
# guard catches two drift classes:
#   1. a satellite artifact tagging itself 1.x before the launch
#   2. an install surface quoting a version that is not the latest release
# Runs in the monthly listings ritual (see listings.yaml policy.ritual);
# read-only, exit 1 on any RED.
set -euo pipefail

UA="nika-version-coherence (contact@supernovae.studio)"
fail=0
say() { printf ' %s\n' "$*"; }

latest="$(curl -fsSLI -o /dev/null -w '%{url_effective}' https://github.com/supernovae-st/nika/releases/latest)"
latest="${latest##*/tag/v}"
say "engine latest release · ${latest}"

# ── 1 · the 0.x law on satellites (any 1.x tag before launch = RED) ─────
# Exception pending operator ruling: nika-action shipped v1.0.x before the
# 0.x law was voiced (2026-07-12). GitHub Actions convention pins by major
# tag (@v1) and retagging breaks external pinners — flagged ⚠, never
# auto-fixed. New 1.x tags anywhere else stay RED.
for repo in gh-nika nika-action nika-vscode nika-client nika-plugins; do
  tag="$(curl -fsSLI -o /dev/null -w '%{url_effective}' "https://github.com/supernovae-st/${repo}/releases/latest" 2>/dev/null || true)"
  tag="${tag##*/tag/}"
  case "$tag" in
    v1.* | 1.*)
      if [ "$repo" = "nika-action" ]; then
        say "⚠ ${repo} ${tag} — pre-law 1.x (Actions major-tag convention · operator ruling pending)"
      else
        say "✖ ${repo} latest tag ${tag} — the constellation is 0.x until the launch"
        fail=1
      fi
      ;;
    "" | *releases*) say "· ${repo} — no release tag (fine)" ;;
    *) say "✔ ${repo} ${tag}" ;;
  esac
done

# ── 2 · install surfaces quote the latest engine release ────────────────
brew_v="$(curl -fsSL -H "User-Agent: $UA" https://raw.githubusercontent.com/supernovae-st/homebrew-tap/main/Formula/nika.rb | sed -n 's/.*version "\(.*\)".*/\1/p' | head -1)"
if [ "$brew_v" = "$latest" ]; then say "✔ brew formula ${brew_v}"; else
  say "✖ brew formula ${brew_v} ≠ latest ${latest}"
  fail=1
fi

if [ -f "$(dirname "$0")/../integrations/aur/PKGBUILD" ]; then
  aur_v="$(sed -n 's/^pkgver=//p' "$(dirname "$0")/../integrations/aur/PKGBUILD")"
  if [ "$aur_v" = "$latest" ]; then say "✔ aur PKGBUILD ${aur_v}"; else
    say "⚠ aur PKGBUILD ${aur_v} ≠ latest ${latest} (bump before/at publish)"
  fi
fi

# ── 3 · the known-drift ledger (RED until the operator ceremony lands) ──
#
# `?n=1000` is load-bearing: the registry paginates at 100 by default, and
# this repository's first page is entirely pre-Diamond tags. Without it the
# check read 100 of 189 tags, never saw 0.107.0, and reported « ghcr serves
# only pre-Diamond tags » about a registry that was carrying the current
# release the whole time (caught 2026-08-02). A gate that cries wolf gets
# read as noise, which costs more than the check is worth.
ghcr_tags="$(curl -fsSL "https://ghcr.io/token?scope=repository:supernovae-st/nika:pull" | python3 -c "import json,sys; print(json.load(sys.stdin)['token'])" | xargs -I{} curl -fsSL -H "Authorization: Bearer {}" "https://ghcr.io/v2/supernovae-st/nika/tags/list?n=1000" | python3 -c "import json,sys; print(' '.join(json.load(sys.stdin).get('tags') or []))" || true)"
case " $ghcr_tags " in
  *" $latest "*) say "✔ ghcr carries ${latest}" ;;
  "  ") say "· ghcr — no tags visible (skip)" ;;
  *)
    say "✖ ghcr does not carry ${latest} — the brouillon-latest drift (payloads §14)"
    fail=1
    ;;
esac

if [ "$fail" -eq 0 ]; then say "✔ version coherence GREEN"; else say "✖ version coherence RED"; fi
exit "$fail"
