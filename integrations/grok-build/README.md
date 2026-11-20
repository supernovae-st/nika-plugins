<!-- SPDX-License-Identifier: Apache-2.0 -->
# Grok Build × Nika

Verified live 2026-07-30 · grok 0.2.117 · nika 0.106.1 · kit 0.106.0.

[Grok Build](https://docs.x.ai/build/overview) reads Claude Code
marketplaces, plugins, skills, MCPs, agents, hooks and instruction files
natively (xAI's own compatibility contract) · so this kit installs
UNPORTED, the full bundle in one add:

```sh
grok plugin marketplace add nika-open/nika-plugins
grok plugin install nika@nika --trust
```

`--trust` is load-bearing, not ceremony: without it grok refuses the
install outright (plugins can run hooks, MCP servers and skills on your
machine), and trust is also what activates the plugin's hooks and MCP.
The refusal message teaches the exact re-run.

## Zero-config on a Claude Code machine

On a machine that already runs the Nika plugin in Claude Code, grok picks
up the marketplace and the components from the Claude surfaces on its own.
Two facts we verified live so you don't have to:

- `grok plugin marketplace add …` answered `already configured` before we
  ever taught grok about it · it had read the marketplace from the
  machine's Claude Code settings.
- Components dedup by name and a grok-side install takes priority ·
  `grok inspect` listed every nika component exactly once, from
  `~/.grok/installed-plugins/`, on a machine that also carries the Claude
  Code install.

## What loads (all verified via `grok inspect --json`)

- the 4 skills · authoring · debugging · operating · migration
- the 6 `/nika:*` commands · check · explain · new · trace · permits · doctor
- the 3 subagents · `nika:nika-author` · `nika:nika-debugger` · `nika:nika-migrator`
- the hook file (session map · check-on-edit · guard-run · claude dialect,
  registered as a unit)
- the read-only MCP oracle · 9 tools · no execution by design
  ([threat model](../mcp/THREAT-MODEL.md))

## The deterministic checks (no model call · CI-able)

```sh
grok inspect --json      # every component with its origin path
grok mcp doctor --json   # nika: command found · server started · handshake OK · 9 tools discovered
```

Trust those two outputs, not a model's enumeration. Our live doctor run:
`command found /opt/homebrew/bin/nika` · `server started 0.0s` ·
`handshake OK protocol 2025-06-18` · `9 tools discovered`.

## Optional native presence

The project `.mcp.json` shipped by the kit is read natively. For a
machine-level stanza in grok's own dialect:

```toml
# ~/.grok/config.toml
[mcp_servers.nika]
command = "nika"
args = ["mcp"]
```

## Caveats worth encoding in your rollout

- Plugins stay OFF until enabled · a plugin's hooks and MCP stay inactive
  until trusted.
- Enterprise deployments can require pinned-commit installs
  (`[marketplace] require_sha = true`) · release tags satisfy it.
- Grok enforces version floors at startup · pin deliberately in CI.

Then `nika init` in the repo · grok reads the `AGENTS.md` family and the
`.agents/skills` authoring skill natively, which is what makes the oracle
useful. Running stays yours: `nika check` before, `--max-cost-usd` during,
`nika trace verify` after.
