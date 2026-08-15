<!-- SPDX-License-Identifier: Apache-2.0 -->
# OpenClaude × Nika

Read from source 2026-07-28 · `Gitlawb/openclaude` (TypeScript · MIT ·
30,399★ · pushed the same day) · nika 0.106.0.

[OpenClaude](https://github.com/Gitlawb/openclaude) is an open-source
coding-agent CLI that runs against OpenAI-compatible APIs, Gemini, GitHub
Models, Ollama and other backends from one terminal-first workflow.
Division of labor, same as everywhere else: OpenClaude writes code; Nika
runs the repeatable work as a checkable file with receipts.

## The short path — this kit installs as-is

OpenClaude's plugin loader reads the **Claude Code marketplace layout**.
Two things in their source say so:

- `src/utils/plugins/schemas.ts` — the marketplace `path` field is
  documented as *“defaults to `.claude-plugin/marketplace.json`”*.
- `src/commands/plugin/parseArgs.ts` — the same verbs Claude Code uses:
  `marketplace add|remove|update|list`, and `install <plugin>@<marketplace>`.

This repo already ships `.claude-plugin/marketplace.json`, so it is already
shaped as an OpenClaude marketplace — no OpenClaude-specific port:

```sh
npm install -g @gitlawb/openclaude       # the client
brew install supernovae-st/tap/nika      # the binary the plugin invokes

openclaude plugin marketplace add supernovae-st/nika-plugins
openclaude plugin install nika@nika
openclaude plugin marketplace update nika   # later: pull a new kit version
```

One Add gets the whole bundle: 4 skills (author · debug · operate ·
migrate), 3 subagents, 5 commands, the delegation rule, the three seatbelt
hooks and the read-only MCP oracle.

**Honest status — read before quoting this.** The lines above are derived
from their published source, not from a live install on this machine. The
layout parity is verified; the round trip is not. Anyone who runs it and
sees `nika` listed under `plugin marketplace list` has PROVEN it, and this
paragraph becomes a date and a version instead of a caveat.

What the bundle's two halves each carry is worth knowing before you debug a
missing piece — and this part IS probed here, against `nika mcp` 0.106.0 on
this machine. The oracle serves nine `nika_*` tools over `tools/list` and
declares no other capability: `prompts/list` answers `-32601`. So the five
`/nika:*` commands are read from the plugin manifest, never from MCP — a
client that loaded the MCP stanza alone gets validation and no commands.

## The project scaffold — works with no plugin at all

`nika init` writes `AGENTS.md`, the editor rules and the authoring skill
into the repo. Any agent that reads a repo brief picks up the house law
from there: author → `nika check` → run budget-capped → `nika trace verify`.

```sh
nika init
```

That scaffold carries the language floor, which matters because a session
writing its first `.nika.yaml` from memory lands on retired shapes: the
envelope is nine keys and closed, values are classified across
`inputs:` · `const:` · `secrets:` (the older catch-all blocks
refuse at PARSE), and an absent `permits:` block is ZERO authority rather
than unrestricted — `NIKA-AUTH-006`. Every one of those is caught by
`nika check` before a token is spent, and `--fix` / `--infer-permits`
print the repair.

Two OpenClaude-specific facts worth knowing when you wire things by hand:

- It keeps its own config under `~/.openclaude` and `~/.openclaude.json`,
  and **ignores `CLAUDE_CONFIG_DIR`** (`OPENCLAUDE_CONFIG_DIR` is the knob).
- Their migration guidance is to copy the `.claude` files you authored into
  the matching `.openclaude` location — so a project already equipped for
  Claude Code carries over by copy, not by rewrite.

## The Skill Hub — a second, smaller door

`Gitlawb/openclaude-skills` is a curated registry (`skills/<name>/SKILL.md`
+ a generated `registry.json`, install via
`openclaude skills install gitlawb/<name>`). [`SKILL.md`](SKILL.md) in this
folder is written to their shape and validator rules, ready for the
submission described in [`SUBMISSION.md`](SUBMISSION.md).

Size it honestly before spending the gesture: at the 2026-07-28 read the
hub carried 10 skills, 11 stars, and no push since 2026-05-27. The plugin
path above reaches far more users; the hub is a discovery surface, not the
distribution.

## The open probe

`nika wire <client>` does not yet carry an `openclaude` target. Where
OpenClaude expects a user-level MCP server stanza to live (inside
`~/.openclaude.json`, or a project file) was not settled by this read —
that is the one question to answer before adding the target.
