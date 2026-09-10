<p align="center">
  <a href="https://nika.sh">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://nika.sh/brand/nika-logo-dark.svg">
      <img src="https://nika.sh/brand/nika-logo-light.svg" alt="Nika" width="220">
    </picture>
  </a>
</p>

<h1 align="center">nika@nika</h1>

<p align="center">
  <strong>The plugin that teaches your agent the Nika workflow language: one Add, and it writes files it can audit before a token is spent and prove after.</strong><br>
  The marketplace <code>nika</code> for Claude Code, Codex, Grok Build, Cursor, Hermes and any MCP client · a byte-pinned mirror of the engine's own kit.
</p>

<p align="center">
  <a href=".claude-plugin/marketplace.json"><img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fsupernovae-st%2Fnika-plugins%2Fmain%2F.claude-plugin%2Fmarketplace.json&query=%24.plugins%5B0%5D.version&label=plugin&prefix=v" alt="plugin version"></a>
  <a href="https://github.com/supernovae-st/nika-plugins/actions/workflows/gate.yml"><img src="https://github.com/supernovae-st/nika-plugins/actions/workflows/gate.yml/badge.svg" alt="gate status"></a>
  <a href="https://github.com/supernovae-st/nika/releases/latest"><img src="https://img.shields.io/github/v/release/supernovae-st/nika?label=engine" alt="Engine release"></a>
  <a href="https://docs.nika.sh"><img src="https://img.shields.io/badge/docs-docs.nika.sh-8b8cf8.svg" alt="Documentation"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-AGPL--3.0-blue.svg" alt="AGPL-3.0"></a>
</p>

<p align="center">
  <a href="https://scorecard.dev/viewer/?uri=github.com/supernovae-st/nika-plugins"><img src="https://api.scorecard.dev/projects/github.com/supernovae-st/nika-plugins/badge" alt="OpenSSF Scorecard"></a>
  <a href="https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/supernovae-st/nika-plugins"><img src="https://archive.softwareheritage.org/badge/origin/https://github.com/supernovae-st/nika-plugins/" alt="Archived by Software Heritage"></a>
  <a href="https://skills.sh/supernovae-st/nika-plugins"><img src="https://skills.sh/b/supernovae-st/nika-plugins" alt="skills.sh listing"></a>
</p>

## Thirty seconds, no API key

The plugin invokes the `nika` binary; install it first (macOS and Linux). The
script path verifies the release `SHA256SUMS` before extracting and installs
to `~/.nika/bin`, no sudo:

```sh
brew install supernovae-st/tap/nika
# or: curl -LsSf https://nika.sh/install.sh | sh
nika --version
```

```
nika 0.118.7 (f3a31a6ee)
```

Then one Add in Claude Code (the other hosts are one section down). The host
prints its own confirmation:

```sh
claude plugin marketplace add supernovae-st/nika-plugins
claude plugin install nika@nika
```

From then on the session carries 4 skills, 3 subagents, 6 slash commands,
3 hooks and the read-only oracle `nika mcp`. Write `hello.nika.yaml`; the
`mock/echo` model rehearses with no key and no network:

```yaml
nika: hello
model: mock/echo
permits: {}
tasks:
  greeting:
    infer:
      prompt: "Say hello from the Nika plugin."
      max_tokens: 32
outputs:
  greeting: ${{ tasks.greeting.output }}
```

Ask the session « Validate hello.nika.yaml and repair every finding. » The
agent calls the oracle's `nika_check`. The same call by hand, over stdio, with
`jq` unwrapping the answer:

```sh
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"probe","version":"1"}}}' \
  '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"nika_check","arguments":{"workflow":"nika: hello\nmodel: mock/echo\npermits: {}\ntasks:\n  greeting:\n    infer:\n      prompt: \"Say hello from the Nika plugin.\"\n      max_tokens: 32\noutputs:\n  greeting: ${{ tasks.greeting.output }}\n"}}}' \
  | nika mcp | jq -r 'select(.id == 2) | .result.content[0].text'
```

```
✔ clean — audited before a single token was spent · risk low
  1 task(s) · 1 wave(s) · permits {} · est out ≤$0.0000 ·          0 source(s) → 0 destination(s) · 1 model endpoint(s) · data internal
```

The guard hook runs the same audit in front of every `nika run` the agent
proposes; a file with live findings is refused, and the refusal carries the
findings so the agent repairs and re-checks by itself:

```sh
nika check hello.nika.yaml
```

```
 ✔ ORDER    no exec: sits downstream of a net-effecting task · unauthored content never reaches a shell
 ✔ PERMITS  literal + const: args fit the boundary · computed paths + symlinks are the RUN's verdict
 ✔ TRIFECTA no lethal trifecta over the declared permits: without a human gate
 ✔ JOURNEY internal · 0 sources · 0 destinations · 1 model endpoint · no secret reaches an external destination
 ✔ audited · 1 task · 1 wave · permits {} · est out ≤$0.0000 · 0 hints · risk low
 layers · valid ✔ · access ready ✔ · capacity fit ✔ · run ready ✔
```

## Why this building

- **Audited before it runs.** The oracle answers `nika_check` and
  `nika_explain` over MCP and the guard hook judges every `nika run` with
  `nika check`: the order of effects, the permits, the lethal trifecta, the
  journey of every secret, the cost floor. A red check never becomes a run.
- **Sovereign by default.** The same file runs on local models (Ollama,
  llama.cpp, vLLM, or the binary's own `nika model serve`), on Mistral,
  Hugging Face, OpenAI, xAI, Anthropic and the rest of the engine's catalog;
  `mock/echo` rehearses with no key and no network.
- **Traced after.** Every run leaves a hash-chained trace; the
  `nika-debugging` skill and the `nika-debugger` subagent read it with
  `nika trace verify` and hand back the exact resume line. Running stays yours:
  the plugin proposes the command, you type it.
- **Pinned to the engine, proven against the release.** The bundle is a sha256-pinned
  mirror of the engine's own kit at the released tag; CI asserts every taught
  `nika` subcommand and every advertised `nika_*` tool against the released
  binary. The kit cannot drift from what ships.

## Pick your door

<p align="center">
  <a href="#thirty-seconds-no-api-key"><img src="https://img.shields.io/badge/Claude_Code-ff7a3c?style=for-the-badge" alt="Claude Code"></a>
  <a href="#codex"><img src="https://img.shields.io/badge/Codex-5b8cff?style=for-the-badge" alt="Codex"></a>
  <a href="#grok-build"><img src="https://img.shields.io/badge/Grok_Build-22d3ee?style=for-the-badge" alt="Grok Build"></a>
  <a href="#hermes-or-any-skillssh-client"><img src="https://img.shields.io/badge/Hermes-9fd0ff?style=for-the-badge" alt="Hermes"></a>
  <a href="#cursor"><img src="https://img.shields.io/badge/Cursor-0a1226?style=for-the-badge" alt="Cursor"></a>
  <a href="#everyone-else"><img src="https://img.shields.io/badge/every_other_client-5a6d8a?style=for-the-badge" alt="every other client"></a>
</p>

<p align="center">
  <sub>or <a href="#every-client-you-have-one-command"><code>npx plugins add supernovae-st/nika-plugins</code></a>: every client on the machine, one command</sub>
</p>

### Codex

```sh
codex plugin marketplace add supernovae-st/nika-plugins
codex plugin add nika@nika
```

<sub>Codex takes the skills, the commands, the hooks and the oracle. Its plugin
schema has no key for the 3 subagents or the 2 rules, so they ship in the
bundle and sit inert. Codex keeps one cached copy per plugin version and
refreshes it the next time you start <code>codex</code>.</sub>

### Grok Build

```sh
grok plugin marketplace add supernovae-st/nika-plugins
grok plugin install nika@nika --trust
```

<sub>Reads the Claude Code layout natively; <code>--trust</code> is what
activates the hooks and the MCP server. The live receipt:
<a href="integrations/grok-build/">integrations/grok-build</a>.</sub>

### Hermes, or any skills.sh client

```sh
npx skills add supernovae-st/nika-plugins
```

<sub>The kit-native delegation skill, listed live on
<a href="https://skills.sh/supernovae-st/nika-plugins">skills.sh</a>; Hermes
also takes it through <code>hermes skills tap add supernovae-st/nika-plugins</code>.</sub>

### Cursor

The Cursor marketplace manifest ships here (`.cursor-plugin/marketplace.json`,
the fullest one: rules, skills, agents, commands, hooks and the oracle), and
the portable `plugin.json` beside it. The local path is a copy of
`.agents/plugins/nika` into `~/.cursor/plugins/local/nika`, which
`scripts/update-mirrors.sh` keeps in sync.

Whatever the host, `nika init` equips the **repository**: the `AGENTS.md`
family, the authoring skill, the rules, the hooks and the MCP oracle. The
remaining skills and the `/nika:*` commands arrive with the plugin, from its
manifest, which is the host's own plugin system's job.

### Every client you have, one command

```sh
npx plugins add supernovae-st/nika-plugins
```

<sub>Vercel's installer detects which of Claude Code, Cursor, Codex, Grok
Build, Kimi Code, GitHub Copilot CLI and VS Code are on your machine
(<code>npx plugins targets</code> lists them) and installs to each through
that client's own plugin system. Add
<code>-t &lt;client&gt;</code> for one of them, <code>--scope project</code> to
keep it in the repo. <code>npx plugins discover supernovae-st/nika-plugins</code>
shows what it found before anything is written; replayed with
<code>plugins@1.3.4</code> on 2026-09-10:</sub>

```
◇  Found 1 local plugin(s)
│
│  nika  4 skills, 6 cmds, 3 agents, 2 rules, mcp  Author, debug, operate and m…
```

### Everyone else

opencode · Kimi Code · Gemini CLI · Zed · Cline · Copilot CLI · Amp · Warp and
the rest of [`clients.yaml`](clients.yaml): `nika init` equips the repo,
`nika wire <client>` wires the machine, and the read-only oracle rides any MCP
client. Every door on one page:
[docs.nika.sh/integrations/everywhere](https://docs.nika.sh/integrations/everywhere).
OpenClaude reads the Claude Code marketplace layout according to its source;
the dossier and its honest status live in
[integrations/openclaude](integrations/openclaude/).

### One-click doors

Where the client supports a one-click MCP install, one button wires the
read-only oracle, the oracle only: the full plugin still arrives through
your client's Add above (binary still required):

<p align="center">
  <a href="https://vscode.dev/redirect/mcp/install?name=nika&config=%7B%22command%22%3A%20%22nika%22%2C%20%22args%22%3A%20%5B%22mcp%22%5D%7D"><img src="https://img.shields.io/badge/VS_Code-install%20nika%20mcp-0098FF?style=for-the-badge&logo=githubcopilot" alt="Install in VS Code"></a>
  <a href="https://insiders.vscode.dev/redirect/mcp/install?name=nika&config=%7B%22command%22%3A%20%22nika%22%2C%20%22args%22%3A%20%5B%22mcp%22%5D%7D"><img src="https://img.shields.io/badge/VS_Code_Insiders-install%20nika%20mcp-24bfa5?style=for-the-badge&logo=githubcopilot" alt="Install in VS Code Insiders"></a>
  <a href="https://cursor.com/en/install-mcp?name=nika&config=eyJjb21tYW5kIjogIm5pa2EiLCAiYXJncyI6IFsibWNwIl19"><img src="https://cursor.com/deeplink/mcp-install-dark.svg" alt="Install MCP Server in Cursor"></a>
</p>

## Your first minute

See a workflow work before anything else: offline, zero keys, nothing written
(a scratch `HOME` stays empty after it):

```sh
nika try 01-hello
```

```
rehearsal: mock/echo answers by echoing the prompt — not a real answer · a real one: `--model <provider/model>` with its key, or `--access <seat>` (nika doctor lists them)
  🦋 nika · hello · 1 task
     permits ✓ declared boundary · default-deny

  ✔  greet  infer · mock/echo  1ms
  ── 1/1 done · unpriced (1 call) · elapsed 0.0s ─────────────────
    rehearsal. to own the file: nika new 01-hello
    said "mock(echo) · Say hello in French, in one sh…"
    rehearsal · a mock model echoed the prompt — not a real answer

  rehearsal: rehearsal. to own the file: nika new 01-hello
```

![nika try 01-hello renders the live DAG offline under the mock provider and seals the honest run card (a mock is unpriced, never free), then points at nika new to make the file yours · zero keys, nothing written, recorded against the released binary](media/try.gif)

*Recorded from `scripts/media/try.tape` against the released engine
(0.118.7) in a scratch `HOME`; every line on screen is the binary's own.*

## Your first real answer

`nika try` runs on a **mock** model: it proves the plumbing and echoes your
prompt back. Real work needs a real seat, and you have three. Pick one and
re-run with `nika run <file>`:

```sh
# 1 · Local, no key, no daemon: the binary serves the model itself
nika model pull unsloth/Qwen3-4B-Instruct-2507-GGUF   # size prints before downloading
nika model serve --model unsloth/Qwen3-4B-Instruct-2507-GGUF

# 2 · Local, via ollama, if you already run it
ollama serve                                          # then: model: ollama/qwen3.5:4b

# 3 · A cloud provider: one key, in your shell
export MISTRAL_API_KEY=…      # or HF_TOKEN · OPENAI_API_KEY · XAI_API_KEY · ANTHROPIC_API_KEY
```

`nika doctor` tells you which of the three this machine already has. Any
workflow runs on any of them: the seat is one line (`model:`) in the file, or
`--model <provider>/<name>` on the run.

Then paste one of these into your agent:

> Turn this repeatable task into a checked Nika workflow.

> Validate this .nika.yaml file and repair every finding.

> Diagnose this failed Nika run from its trace.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="media/loop-dark.svg">
    <img src="media/loop-light.svg" alt="The loop: you describe the job in plain words, the agent writes the .nika.yaml, nika check audits it before a token is spent, nika run stays yours to type, nika trace verify seals the receipt · the file is the repeatable part" width="100%">
  </picture>
</p>

The plugin proposes the command; you type it. Spend stops admitting new work
at the call that would cross the cap, the effect boundary is declared in the
file and reviewable in a diff, and every run leaves a hash-chained trace you
can verify afterwards:

<!-- engine hero pinned to the release tag it demonstrates · re-pin on lockstep bumps -->
![nika check audits the workflow (plan, permits, cost, secrets, types, the lethal-trifecta gate), then nika run executes it locally and seals the hash-chained trace · the audit-then-run story](https://raw.githubusercontent.com/supernovae-st/nika/v0.118.7/media/nika-hero.gif)

## What one Add installs

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="media/suite-dark.svg">
    <img src="media/suite-light.svg" alt="One Add installs the whole suite: 4 skills, 3 subagents, 6 commands, 3 hooks and the read-only oracle" width="100%">
  </picture>
</p>

| Component | What it does |
|---|---|
| `nika-authoring` skill | the author, check, repair loop, taught step by step |
| `nika-debugging` skill | run forensics: trace ls, show, outputs, verify · resume lines · surgical reruns |
| `nika-operating` skill | day-2 hardening: spend caps · permits · secrets · model swaps · CI goldens |
| `nika-migration` skill | convert scripts, CI jobs and prompt chains to workflows: mapping table + parity protocol |
| `nika-author` subagent | routes an intent to a template, fills the `# SLOT:` markers, loops `nika check` until rc=0; launching belongs to the conversation |
| `nika-debugger` subagent | root-causes a failed or paused run from its hash-chained trace, hands back the exact resume line |
| `nika-migrator` subagent | ports existing automation: inventory, native-first mapping, check loop, golden pin |
| `/nika:check` · `/nika:explain` · `/nika:new` | audit a file · explain a finding code · scaffold from a template |
| `/nika:trace` · `/nika:permits` · `/nika:doctor` | read a run's flight recorder · infer and paste the tightest permits boundary · diagnose this machine's Nika surface |
| session-context hook | a workspace with workflows greets the agent with the nika map at session start (Cursor and Claude Code dialects) |
| check-on-edit hook | every agent edit to a `*.nika.yaml` is audited immediately; findings land in the hook log, the edit is never blocked |
| guard-run hook | a `nika run` must pass `nika check` first; the deny carries the findings |
| language rule · delegation rule | the four verbs (`infer` · `exec` · `invoke` · `agent`) on `*.nika.yaml` · when to propose a workflow and which surface to reach for |
| MCP oracle | `nika_check` · `nika_inspect` · `nika_explain` · `nika_schema` · `nika_examples` · `nika_template` · `nika_canon` · `nika_catalog` · `nika_tools`; read-only by design: there is no run tool over MCP ([threat model](integrations/mcp/THREAT-MODEL.md)) |

The bundle's own README, mirrored from the engine, carries the hook laws
(comfort hooks degrade quietly, the run guard fails visible) and the macOS
GUI `PATH` note: [.agents/plugins/nika/README.md](.agents/plugins/nika/README.md).

## Proven where you work

Coverage is a machine-checked contract, not a claims list:
[`clients.yaml`](clients.yaml) is the client × component matrix, gated both
ways against the released binary (`scripts/check-clients-matrix.py`). The
proven rows, each with its deterministic receipt and the versions it was
measured on recorded in that file:

| Client | The receipt |
|---|---|
| **Claude Code** | the suite loads in-session: skills · subagents · `/nika:*` · hooks · the oracle |
| **Codex** | live install (plugin cache enabled) · the live marketplace page renders the interface block |
| **Grok Build** | `grok inspect --json` lists every component with its origin · `grok mcp doctor --json`: handshake OK ([fiche](integrations/grok-build/)) |
| **Kimi Code** | a stream-json run emits `tool_calls: mcp__nika__nika_canon`: the oracle loaded and called ([fiche](integrations/kimi-code/)) |
| **opencode** | `opencode mcp list` answers `✓ nika connected` ([fiche](integrations/opencode/)) |
| **Copilot CLI** | `copilot mcp get nika` answers · a headless `copilot -p` run calls the oracle and names the server |
| **Hermes / skills.sh** | the skill pack listed live ([skills.sh](https://skills.sh/supernovae-st/nika-plugins)) |
| **Any MCP client** | the containerized oracle answers `initialize` + `tools/list` on every CI run ([integrations/mcp](integrations/mcp/)) |

<sub>Listed across the ecosystem:
<a href="https://skills.sh/supernovae-st/nika-plugins">skills.sh</a> ·
<a href="https://claudepluginhub.com">ClaudePluginHub</a> ·
<a href="https://github.com/davila7/claude-code-templates">aitmpl.com</a> ·
<a href="https://github.com/SchemaStore/schemastore">SchemaStore</a> (<code>*.nika.yaml</code> in every IDE) ·
<a href="https://www.libhunt.com/r/nika">LibHunt</a> ·
<a href="https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/supernovae-st/nika">Software Heritage</a>
· every submission lives in <a href="listings.yaml"><code>listings.yaml</code></a>, verified on a cadence.</sub>

## Keeping the suite fresh

The binary moved and a kit stayed behind? `nika doctor` reads what each client
actually loads, names any kit lagging the binary's train and prints the exact
per-client fix. On a machine whose Cursor drop and Claude Code install lag the
released 0.118.7:

```sh
nika doctor --plain | grep -A1 '^! kit'
```

```
! kit        cursor plugin kit 0.110.0 lags the binary (0.118.7)
  fix: re-sync the local drop: scripts/update-mirrors.sh (nika-plugins checkout)
! kit        claude plugin kit 0.116.2 lags the binary (0.118.7)
  fix: claude plugin marketplace update nika, then claude plugin update nika@nika
```

Every surface invokes the binary and the plugin kits ride its release train,
but no surface updates another: brew never touches a plugin, a marketplace
never touches the binary. The gestures, per surface:

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="media/update-rungs-dark.svg">
    <img src="media/update-rungs-light.svg" alt="Updating: brew upgrade nika for the binary · then the two rungs for the Claude Code plugin: marketplace update, plugin update, restart" width="100%">
  </picture>
</p>

| Surface | Update gesture |
|---|---|
| Binary | `brew upgrade nika` |
| Claude Code plugin | `claude plugin marketplace update nika` **then** `claude plugin update nika@nika` (two rungs · restart after) |
| Codex plugin | `codex plugin marketplace upgrade nika` |
| Cursor local drop | `scripts/update-mirrors.sh` (rsync from this checkout) |
| Every surface at once (maintainers) | `scripts/update-mirrors.sh` (`--check` reports drift read-only, exit 1 on any) |

Drift is advisory (`nika doctor` warns, exit 0) and every fix line it prints
is copy-paste ready.

## Taking it back off

Same mechanisms, in reverse. The plugin comes off with one command per
client; the machine wiring is manual today, `nika wire` has no `--remove`,
and the table below is here so you do not have to go looking.

| Surface | Removal gesture |
|---|---|
| Claude Code plugin | `claude plugin uninstall nika@nika` **then** `claude plugin marketplace remove nika` |
| Codex plugin | `codex plugin remove nika@nika` **then** `codex plugin marketplace remove nika` |
| Grok Build plugin | `grok plugin uninstall nika` **then** `grok plugin marketplace remove nika` |
| Cursor local drop | delete `~/.cursor/plugins/local/nika` |
| One repo (`nika init`) | delete what it wrote: `.agents/`, `.cursor/`, `.github/copilot-instructions.md`, `.mcp.json`, `.vscode/settings.json`, `AGENTS.md`, `CLAUDE.md` and its `.gitignore`; `nika init` prints every file it creates and `git status` shows the whole list before you decide |
| One machine (`nika wire`) | delete the `nika` entry from the client's config (below), or the file if Nika created it |
| Binary | `brew uninstall nika`, or `rm -rf ~/.nika/bin` for the script install (models and traces live in `~/.nika/` too; remove the whole dir to take everything) |

`nika wire` only ever adds one `nika` server entry, and it names the exact
file before it writes: `nika wire detected --dry-run` previews the clients
this machine shows, `nika wire all --dry-run` previews every supported one.
Replayed in a scratch `HOME=/tmp/you` so the paths read as a fresh machine's:

```sh
HOME=/tmp/you nika wire all --dry-run --plain
```

```
dry-run · plan only · nothing written
+ would create cursor: /tmp/you/.cursor/mcp.json
+ would create vscode: ./.vscode/mcp.json
+ would create windsurf: /tmp/you/.codeium/windsurf/mcp_config.json
+ would create claude: /tmp/you/.claude.json
+ would create claude-desktop: /tmp/you/Library/Application Support/Claude/claude_desktop_config.json
+ would create cline: /tmp/you/.cline/data/settings/cline_mcp_settings.json
+ would create codex: /tmp/you/.codex/config.toml
+ would create continue: /tmp/you/.continue/mcpServers/nika.json — reload Continue (or re-save config.yaml) to pick it up
+ would create zed: /tmp/you/.config/zed/settings.json
+ would create opencode: ./opencode.json
+ would create hermes: /tmp/you/.hermes/config.yaml
+ would create gemini: /tmp/you/.gemini/settings.json
+ would create qwen: /tmp/you/.qwen/settings.json
+ would create lmstudio: /tmp/you/.lmstudio/mcp.json
+ would create junie: ./.junie/mcp/mcp.json
+ would create grok: /tmp/you/.grok/config.toml
+ would create antigravity: /tmp/you/.gemini/config/mcp_config.json
+ would create kimi: /tmp/you/.kimi-code/mcp.json
+ would create kiro: /tmp/you/.kiro/settings/mcp.json
+ would create copilot: /tmp/you/.copilot/mcp-config.json
+ would create amp: /tmp/you/.config/amp/settings.json
→ re-run without --dry-run to apply
```

![A fresh machine: nika wire all previews the MCP config for every agent client, one confirmation applies the sweep, then nika welcome confirms every editor wired, local models first, zero keys needed · the one-command wiring story, recorded against the released binary](media/wire-all.gif)

## How the pieces fit

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="media/layers-dark.svg">
    <img src="media/layers-light.svg" alt="Three layers: the engine supernovae-st/nika is the source of truth, mirrored byte-pinned into this repo, one Add per client · nika init equips one repository · nika wire wires one machine · nika-vscode is the IDE product, not a plugin" width="100%">
  </picture>
</p>

Three mechanisms, no overlap: the **plugin** teaches any agent the language
(per-agent) · **`nika init`** equips one repository (per-repo) · **`nika
wire`** configures one machine's clients (per-machine). The VS Code extension
is not a plugin: it is the full IDE surface, and on Cursor it nudges you to the
plugin for the agent side.

## Why a separate repo

`plugin marketplace add` clones its target. The engine repo carries the full
Rust workspace and media; this repo carries the plugin only, so the install
is instant. The bundle is mirrored verbatim from the engine's
[`.agents/plugins/`](https://github.com/supernovae-st/nika/tree/main/.agents/plugins)
at the released tag named in [`mirror.json`](mirror.json). A wording bug in a
mirrored skill is fixed in the engine repo and reaches the marketplace with the
next release; the daily `release-heal` workflow opens that re-sync PR.

## What's inside

```
.agents/plugins/marketplace.json      Codex marketplace manifest
.agents/plugins/nika/                 the plugin: one bundle, every host
  plugin.json · mcp.json              the portable Agent Plugins manifest + its MCP stanza
  .claude-plugin/plugin.json          Claude Code manifest (hooks wired)
  .codex-plugin/plugin.json           Codex manifest (interface block · try-now prompts)
  .cursor-plugin/plugin.json          Cursor manifest (rules · skills · agents · commands · hooks · MCP)
  .mcp.json                           the read-only oracle wiring: nika mcp
  skills/{nika-authoring,nika-debugging,nika-operating,nika-migration}/SKILL.md
  agents/{nika-author,nika-debugger,nika-migrator}.md
  commands/{check,explain,new,trace,permits,doctor}.md
  hooks/{claude,cursor}-hooks.json    session context · check-on-edit · guard-run, one file per dialect
  scripts/                            the hook scripts and their tests
  rules/{nika-workflow-language,nika-delegation}.mdc
  assets/nika-logo.png · README.md · CHANGELOG.md
.claude-plugin/marketplace.json       Claude Code marketplace manifest
.cursor-plugin/marketplace.json       Cursor marketplace manifest
clients.yaml                          the client × component matrix (the coverage SSOT)
skills/autonomous-ai-agents/nika/     the Hermes delegation skill (kit-native)
integrations/{grok-build,kimi-code,opencode,openclaude,mcp,aur}/
                                      per-client fiches · live-verified, version-pinned
integrations/description-bank.md      the words every listing copies
listings.yaml                         the public submissions ledger
mirror.json                           the drift contract (classes + sha256 pins)
scripts/                              the gates · resync-mirror.py · update-mirrors.sh · media/ tapes
```

Two content classes, one contract (`mirror.json`): **engine-mirror** files
are byte-identical projections of the engine repo, pinned by sha256 at the
engine SHA they were proven against: a pin mismatch means corruption (hard
fail), a newer engine release means a re-sync is due. **kit-native** files are
owned here and proven against the released binary instead: the gate asserts
every taught `nika <subcommand>` and every advertised `nika_*` tool actually
ships.

## Development proof

The same gates CI runs, replayed here against the released engine:

```sh
claude plugin validate .                          # the marketplace manifest
claude plugin validate .agents/plugins/nika       # the plugin manifest
NIKA_BIN=/absolute/path/to/nika python3 scripts/check-mcp-tools.py
NIKA_BIN=/absolute/path/to/nika python3 scripts/check-skill-commands.py
NIKA_BIN=/absolute/path/to/nika python3 scripts/check-clients-matrix.py
NIKA_BIN=/absolute/path/to/nika python3 scripts/check-dead-forms.py
python3 scripts/check-vocab.py
```

```
✔ Validation passed
✔ Validation passed
✓ README ⟺ nika mcp agree · 9 tools: nika_canon · nika_catalog · nika_check · nika_examples · nika_explain · nika_inspect · nika_schema · nika_template · nika_tools
✓ skills/autonomous-ai-agents/nika/SKILL.md · 9 taught subcommands ship; no known retired argv: catalog · check · doctor · explain · mcp · new · run · test · trace
✓ the client matrix holds (schema · manifests · counts · wire)
✓ no dead language forms across 30 kit-native teaching files
✓ vocabulary law holds across 38 tracked .md files
```

The pins, the versions and the upstream drift are judged in
[`gate.yml`](.github/workflows/gate.yml); the containerized oracle is built
from the release artifacts and probed in-container on every run.

## Add your client · ask for a workflow

You want to support Nika in your client? Copy the matching
[`integrations/`](integrations/) folder: each one is self-contained,
version-pinned, and gate-checked against the live binary. Missing a
workflow for your use case?
[Ask for one](https://github.com/supernovae-st/nika-plugins/issues/new?template=request-a-workflow.yml):
the answer ships as a checked file, receipts included.

<!-- city:map -->
## The city · where this repo sits

```text
📜 nika-spec ──── language law and conformance
    │
    ▼
⚙️ nika ───────── engine, admission, execution, receipts and schedules
    │
    ▼
🤖 nika-plugins ─ this door: the marketplace `nika`, the plugin `nika@nika`, the oracle `nika mcp`
    │
    ▼
🧩 agent hosts: Claude Code · Codex · Grok Build · Cursor · Hermes · any MCP client
```

This repository mirrors the engine's kit and carries the per-client wiring.
It is not authoritative for the workflow language.

All the buildings: [nika-spec](https://github.com/supernovae-st/nika-spec) ·
[nika](https://github.com/supernovae-st/nika) ·
[nika.sh](https://github.com/supernovae-st/nika.sh) ·
[nika-docs](https://github.com/supernovae-st/nika-docs) ·
[nika-client](https://github.com/supernovae-st/nika-client) ·
[nika-vscode](https://github.com/supernovae-st/nika-vscode) ·
[nika-plugins](https://github.com/supernovae-st/nika-plugins) ·
[gh-nika](https://github.com/supernovae-st/gh-nika) ·
[homebrew-tap](https://github.com/supernovae-st/homebrew-tap) ·
[nika-action](https://github.com/supernovae-st/nika-action) ·
[nika-actions-starter](https://github.com/supernovae-st/nika-actions-starter) ·
[nika-registry](https://github.com/supernovae-st/nika-registry) ·
[nika-estate](https://github.com/supernovae-st/nika-estate).
<!-- /city:map -->

## License

[AGPL-3.0-or-later](LICENSE), the engine's license, for the mirrored bundle.
The kit-native fiches and gate scripts carry an `SPDX-License-Identifier:
Apache-2.0` header; the two agent skill files carry MIT in their frontmatter.

## Security

Report vulnerabilities privately through
[GitHub security advisories](https://github.com/supernovae-st/nika-plugins/security/advisories/new);
the posture (nothing here executes on install, the mirror is pinned, the
oracle is read-only) is in [SECURITY.md](SECURITY.md).

## Contributing

Mirrored files are fixed upstream: file issues and PRs against
[supernovae-st/nika](https://github.com/supernovae-st/nika)
([CONTRIBUTING.md](https://github.com/supernovae-st/nika/blob/main/CONTRIBUTING.md)).
Kit-native files (`clients.yaml`, `integrations/`, `skills/`, `scripts/`) take
PRs here; [AGENTS.md](AGENTS.md) carries the two-class law. Docs:
[docs.nika.sh](https://docs.nika.sh).
