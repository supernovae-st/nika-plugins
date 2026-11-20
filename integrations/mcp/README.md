<!-- SPDX-License-Identifier: Apache-2.0 -->
# Wiring the Nika MCP oracle (any client)

The engine serves a read-only MCP oracle over stdio: agents validate
workflows and learn the language without executing anything. One stanza,
every client:

```yaml
# YAML-config clients (hermes, …)
mcp_servers:
  nika:
    command: nika
    args: [mcp]
    timeout: 120
```

```json
{ "mcpServers": { "nika": { "command": "nika", "args": ["mcp"] } } }
```

`nika wire <client>` writes the stanza for you where supported — at 0.124.0
the targets are cursor · vscode · windsurf · claude · claude-desktop · cline
· codex · continue · zed · opencode · hermes · gemini · qwen · lmstudio ·
junie · grok · antigravity · kimi · kiro · copilot · amp. `nika wire
detected --dry-run` previews the clients this machine shows, `nika wire
detected` wires them, and `wire all` is the advanced sweep. `nika wire --help`
prints the live list; per-client pages with exact file paths:
https://docs.nika.sh/integrations/mcp-clients

Docker hosts (directory checkers, sandboxed runners): [`Dockerfile`](Dockerfile)
builds the oracle from the release artifacts (SHA256SUMS-verified, multi-arch
amd64/arm64) — `docker build -t nika-mcp . && docker run -i --rm nika-mcp`
speaks stdio JSON-RPC, introspection-probed in-container.

MCPB is a historical distribution lane, not a current release promise.
Engine `v0.99.0` shipped two `.mcpb` bundles; later releases do not ship
`.mcpb` assets or `MCPB.sha256`, and the registry manifest that named them
lives on only in git history. Install the engine through Homebrew or a
verified release archive, then use `nika wire <client>`; Docker hosts can use
the verified image recipe above, and registry clients the npm package below.

## From the MCP Registry (npm)

[`server.json`](server.json) is the oracle's entry in the official MCP
Registry, `io.github.nika-open/nika`. It names one package, `@nika-open/nika`
on npm: the TypeScript SDK, whose `nika` bin hands the arguments it receives
to the native engine npm installs alongside it (macOS and glibc Linux, arm64
and x64, Node.js 22 or later). A client that installs from the registry
launches the same read-only oracle over stdio, `<version>` being the one
`server.json` names:

```sh
npx -y @nika-open/nika@<version> mcp
```

### Publishing a version

The registry accepts the package only when the npm version `server.json`
names declares `"mcpName": "io.github.nika-open/nika"` in its `package.json`.
A publication takes three steps:

1. Release the SDK with that field, so `@nika-open/nika@<version>` is on npm.
2. Merge a pull request that sets both `version` fields of `server.json` to
   that version (the gate holds them equal).
3. Dispatch the workflow from `main`:
   `gh workflow run mcp-registry.yml -R nika-open/nika-plugins --ref main`.

[`mcp-registry.yml`](../../.github/workflows/mcp-registry.yml) runs only on
dispatch. It refuses to publish unless that npm version exists and claims
this server name, installs `mcp-publisher` at a pinned release after checking
its checksum and its Sigstore bundle, validates the manifest with the
registry, logs in with GitHub OIDC (no stored secret) and publishes.

## What the oracle serves

Nine tools over `tools/list`, re-asserted against the live wire on every
gate run (`scripts/check-mcp-tools.py` asks the binary, never a remembered
list):

| Tool | Answers |
|---|---|
| `nika_check` | is this workflow valid — the same audit as the CLI |
| `nika_inspect` | its anatomy: tasks · verbs · waves · cost · permits |
| `nika_explain` | one `NIKA-XXXX` code: cause · category · fix-form |
| `nika_schema` | the envelope JSON Schema (nine keys · closed) |
| `nika_examples` | the embedded example set |
| `nika_template` | a template skeleton to start from |
| `nika_canon` | the canonical registry (verbs · builtins · providers) |
| `nika_catalog` | provider/model ids · capabilities · required env vars |
| `nika_tools` | the builtins an `invoke` reaches without any MCP server |

At 0.124.0, `initialize` advertises the `tools` and `prompts` capabilities.
`prompts/list` serves five prompts, `check`, `explain`, `compile`, `trace` and
`permits`, the same jobs as five of the plugin's six `/nika:*` commands. The
sixth, `/nika:doctor`, and the skills, subagents and hooks come only from the
plugin manifests, in the clients that read one. Wire the oracle for
validation; install the plugin for the rest. Probe it yourself in one line:

```sh
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"probe","version":"1"}}}' \
  '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
  '{"jsonrpc":"2.0","id":3,"method":"prompts/list","params":{}}' | nika mcp
```

## The read-only posture (why there is no run tool)

Inspection is safe to hand an agent; execution is not. The oracle answers
*is this valid · what will it cost · what is the syntax* — running stays on
the CLI, where `--max-cost-usd`, effect permits and the trace live. An agent
that wants to run a workflow shells out to `nika run` under your terminal's
permissions, visibly, like any other command you'd review.

Companions in this folder: [`server.json`](server.json), the MCP Registry
manifest described above; [`Dockerfile`](Dockerfile), the verified image
recipe; and [`THREAT-MODEL.md`](THREAT-MODEL.md), which states plainly what
the oracle and the trace chain do and do not prove.
