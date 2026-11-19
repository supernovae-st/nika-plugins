<!-- SPDX-License-Identifier: Apache-2.0 -->
# Kimi Code CLI × Nika

Verified live 2026-07-31 · kimi-code 0.30.0 · nika 0.106.1.

[Kimi Code CLI](https://github.com/MoonshotAI/kimi-code) reads MCP servers
from `mcp.json` at two levels · user `~/.kimi-code/mcp.json` (shared across
projects) and project `.kimi-code/mcp.json` (same-named entries: project
wins). Binary first (`brew install nika-open/tap/nika`), then add the
read-only oracle to the user file:

```json
{
  "mcpServers": {
    "nika": { "command": "nika", "args": ["mcp"] }
  }
}
```

Or conversationally: `/mcp-config` in the TUI adds servers without
hand-editing JSON, and `/mcp` shows connection status.

## One trap worth naming

The legacy kimi-cli taught `kimi mcp add …` · **that subcommand does not
exist in kimi-code** (its command set is `login · acp · web · doctor ·
export · migrate · upgrade · provider · vis`). The file contract above is
the door. Their docs also warn that project-level stdio entries execute
when a session starts · trust-scope accordingly.

## The proof (deterministic · verified live)

A headless run emits one JSON object per line, tool calls included · the
oracle answering IS the receipt:

```sh
kimi -p "Call the mcp__nika__nika_canon tool with no arguments and stop." \
  --output-format stream-json
# → {"role":"assistant","tool_calls":[{"function":{"name":"mcp__nika__nika_canon", …}}]}
```

`kimi doctor` validates the config files (exit 0/1) · `/mcp` in the TUI
shows the live connection.

## The repo side

`nika init` writes the `.agents/skills` authoring skill · kimi-code scans
four skill tiers including project and user `.agents/skills/`, so the
skill is discovered as `/skill:nika-authoring` with zero extra wiring
(verified live: an ACP `session/new` lists it). AGENTS.md is NOT
auto-loaded by kimi-code today (upstream asks are open) · the skill and
the oracle carry the teaching.

Division of labor unchanged: Kimi orchestrates and writes code · Nika runs
the repeatable work as a checkable file with receipts (`nika check` before
· `--max-cost-usd` during · `nika trace verify` after).
