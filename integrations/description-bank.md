<!-- SPDX-License-Identifier: Apache-2.0 -->
# Description bank — the words every listing copies

One truth, three lengths per surface. Submissions (MCP directories, awesome
lists, marketplaces) copy from HERE — never improvise a description in a PR
form. Rules: name **verifiable capabilities** (check · cost floor · traces ·
receipts), never "AI workflow tool"; no counts (they drift — the gate checks
tool names against the live binary instead); local-first examples; the words
"standard", "framework", "blockchain" and "attested" do not appear.

## One line (≤160 chars — awesome lists, directory taglines)

> Nika — intent-as-code for AI workflows: author a reviewable DAG in YAML,
> audit cost/permits **before** running, keep tamper-evident traces after.

## Three lines (MCP directories, marketplace cards)

> Nika is a workflow language for AI — one file, four verbs, one Rust
> binary. Its MCP server is a read-only oracle: agents validate workflows
> (`nika_check`, `nika_explain`) and learn the language (schema, templates,
> examples, catalogs) without executing anything. Running stays on the CLI,
> budget-capped and trace-verified — inspect freely, execute deliberately.

## Ten lines (README sections, submission long-forms)

> Nika turns repeatable AI work into files you can run, review, diff and
> share. A workflow is a `.nika` DAG — LLM steps, shell steps, tool
> calls — statically checkable before a single token is spent: `nika check`
> audits the schema, the DAG, the cost floor (unpriced is never $0), the
> secret flows and the effect permits. Runs are budget-capped
> (`--max-cost-usd`) and leave a tamper-evident trace (`nika trace verify`).
> Agents meet it through the surfaces they already read: `AGENTS.md` and a
> repo skill (`nika init`), a read-only MCP oracle (`nika mcp`), and a
> GitHub Action that posts the plan with receipts on every PR. Local-first:
> the mock and Ollama paths need no API key. Engine AGPL-3.0-or-later ·
> spec and SDK Apache-2.0.

## Per-surface first lines (when the form asks "what is this?")

| surface | lead |
|---|---|
| MCP directories | the three-line block (the oracle IS the listing) |
| awesome-mcp lists | one line + `read-only oracle: validate + learn, no execution` |
| skills registries | `Author → check → repair loop for Nika workflows — teaches agents to write valid .nika, never invent syntax` |
| GitHub Action marketplace | `Plan with receipts: check verdict, honest cost floor, permits and the DAG on every PR — static, zero secrets` |
| Hermes/agent catalogs | `The deterministic workflow worker: Hermes orchestrates, Nika runs repeatable work budget-capped with verifiable receipts` |
| product directories (AlternativeTo · SaaSHub · LibHunt) | `Declarative AI pipelines as plain files — the audit before the run, the receipt after. Single static binary, local models first-class, no cloud required` |
| self-hosted directories | `Self-hosted by construction: one binary, your models (Ollama · llama.cpp · vLLM), plain-text workflows and traces on your disk — nothing phones home, telemetry off by default` |
| newsletters (devtools editorial) | `nika check is CI for AI pipelines: it reads the workflow file and prints the DAG, an honest cost floor, secret flows and permissions — before a single token is spent` |
| newsletters (AI-engineering) | `Agents write the workflow, the engine keeps it honest: typed outputs, budget caps, did-you-mean fixes at check time, and a hash-chained trace any reviewer can re-verify` |
| package registries (AUR · nixpkgs · distro) | `Workflow language + engine for AI pipelines — author .nika, statically audit (cost/permits/secrets), run on any LLM provider, verify the trace. Single static Rust binary` |
| static-analysis / linter lists | `A static analyzer for AI workflows: schema, DAG order, cost bounds, secret-flow and permission escapes caught before execution — findings carry codes and machine-applicable fixes` |
| VS Code extension showcases | `The .nika cockpit: check-as-you-type diagnostics from the real engine, a live DAG canvas that runs and replays workflows, cost inlays before a token is spent` |

### Alternative-to anchors (comparison sites — honest pairings only)

State what differs, never "better than". Anchors that hold: **n8n / Windmill /
Kestra** (visual-or-server orchestrators → nika is file-first, one binary, no
server) · **GitHub Actions for AI steps** (nika adds the static audit + local
runs) · **plain Python scripts + API keys** (the real incumbent — nika adds
check, budget caps, receipts). Anchors that DON'T hold (never claim): Airflow
at data-platform scale · Temporal durability · LangGraph/CrewAI agent
frameworks (different seat: they orchestrate agents, nika runs the
repeatable slice — link how-nika-compares instead).

Companion: `listings.yaml` (every live submission registers there with its
pinned description + cadence + kill criterion — see AGENTS.md).
