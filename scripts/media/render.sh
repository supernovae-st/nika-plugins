#!/usr/bin/env bash
# render.sh — render a kit tape against the real released binary in a
# sandboxed HOME (/tmp/you). Sibling of the engine's render-tape.sh ·
# same honesty contract: every command is real, every line of output is
# the binary's own. Usage: bash scripts/media/render.sh [tape-name]
#   NIKA_BIN    the engine to record (default: the nika on PATH)
#   TRANSCRIPT  also write the final screen, as text, to this file
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
NAME="${1:-wire-detected}"
TAPE="$ROOT/scripts/media/$NAME.tape"
[ -f "$TAPE" ] || { echo "no tape at $TAPE" >&2; exit 1; }
command -v vhs >/dev/null || { echo "vhs not installed (brew install vhs)" >&2; exit 1; }
NIKA="${NIKA_BIN:-$(command -v nika || true)}"
[ -n "$NIKA" ] && [ -x "$NIKA" ] || { echo "nika not found (set NIKA_BIN)" >&2; exit 1; }

# The sandbox the tapes enter: a fresh fake home, a git-initialized demo
# project, and the engine to record.
rm -rf /tmp/you
mkdir -p /tmp/you/demo /tmp/you/bin
git -C /tmp/you/demo init -q -b main
ln -s "$NIKA" /tmp/you/bin/nika
HOME=/tmp/you /tmp/you/bin/nika --version >/dev/null || {
  echo "the engine must answer under the sandbox HOME (a proxy may need NIKA_BIN)" >&2
  exit 1
}

if [ "$NAME" = "wire-detected" ]; then
  # What `nika wire detected` reads as presence: the settings files the
  # clients keep. Cursor already holds another MCP server, which the wiring
  # must keep; Claude Code's file is fresh; the project has a VS Code file.
  mkdir -p /tmp/you/.cursor /tmp/you/demo/.vscode
  printf '%s\n' '{' '  "mcpServers": {' \
    '    "filesystem": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "."] }' \
    '  }' '}' > /tmp/you/.cursor/mcp.json
  echo '{}' > /tmp/you/.claude.json
  echo '{}' > /tmp/you/demo/.vscode/mcp.json
fi

# shell.zsh, sourced by tapes that use it: a fresh HOME, the engine first on a
# short PATH (no agent CLI for the engine to probe), no credential variables,
# no keychain. The engine prints a home-isolation notice when stderr is a
# terminal and HOME is not the account home; its stderr reaches the screen
# through a pipe here, so that notice (it names the sandbox) stays out, as the
# engine's own media captures keep it out. stdout is still the terminal, and
# the exit code is the engine's own.
cat > /tmp/you/shell.zsh <<'EOF'
export HOME=/tmp/you TMPDIR=/tmp NIKA_KEYCHAIN=off
export PATH=/tmp/you/bin:/usr/bin:/bin
unset -m '*API_KEY*' '*_TOKEN*' '*SECRET*' 2>/dev/null
setopt interactive_comments
nika() {
  setopt localoptions nomultios
  local code
  { command nika "$@" 2>&1 1>&3 3>&- | { grep -v '^nika: home isolation:' >&2 || true; }; code=${pipestatus[1]}; } 3>&1
  return $code
}
cd /tmp/you/demo
EOF

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK" /tmp/you' EXIT
cp "$TAPE" "$WORK/$NAME.tape"
[ -z "${TRANSCRIPT:-}" ] || printf 'Output %s.txt\n' "$NAME" >> "$WORK/$NAME.tape"
(cd "$WORK" && vhs "$NAME.tape")
[ -z "${TRANSCRIPT:-}" ] || cp "$WORK/$NAME.txt" "$TRANSCRIPT"

mkdir -p "$ROOT/media"
OUT="$ROOT/media/$NAME.gif"
if command -v gifsicle >/dev/null; then
  gifsicle -O3 --lossy=40 "$WORK/$NAME.gif" -o "$OUT"
else
  cp "$WORK/$NAME.gif" "$OUT"
fi
SIZE_MB=$(du -m "$OUT" | cut -f1)
[ "$SIZE_MB" -le 8 ] || { echo "✖ $OUT is ${SIZE_MB}MB (budget 8MB)" >&2; exit 1; }
echo "→ $OUT (${SIZE_MB}MB · budget 8MB)"
