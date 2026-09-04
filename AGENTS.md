# AGENTS.md — nika-plugins (the plugin marketplace mirror)

Vendor-neutral agent entry per the AGENTS.md convention (agents.md).

## What this repo is

The lean install surface for the Nika agent plugin — Claude Code and
Codex marketplaces both point here. It carries three things: the plugin
manifests (`.claude-plugin/` · the `.agents/` plugin tree), the
`nika-authoring` skill, and the MCP wiring for the read-only oracle.

## The ONE law — mirror.json is the drift contract

Every content file belongs to one of two classes, declared in
`mirror.json` (the SSOT the gate loops over — never a hardcoded list):

- **engine-mirror** (`.agents/plugins/nika/**`) — a **byte-identical
  mirror of the engine repo** (`supernovae-st/nika`, same paths) at the
  **released tag** `mirror.json.engine_ref` (the stable train · what
  `brew install` gives a user), pinned by sha256 at the engine SHA it was
  proven against — never `main`: the kit is teaching, and mirrored from
  main it taught the 0.109 language to 0.108.0 installs (2026-08-18).
  Found a wording bug in the authoring `SKILL.md`? **Fix it in the engine
  repo**, merge there; it reaches the marketplace with the next release
  (the release-heal moves the mirror to each new tag). A hand-edit on
  this side, or bytes that differ from the tag, is a pin mismatch → hard
  RED (corruption signal). A newer engine release than `engine_ref` is a
  WARNING on PRs and a loud failure on the daily cron (re-sync signal) —
  two different signals, never conflated.
- **kit-native** (`skills/**` — the Hermes delegation skill ·
  `integrations/**` — the per-client wiring packs) — owned HERE, not
  mirrored. Its proof is the SAME released binary the mirror follows: the gate asserts every
  `nika <subcommand>` it teaches ships in the latest release
  (`scripts/check-skill-commands.py`) and every advertised `nika_*` tool
  is served over the wire (`scripts/check-mcp-tools.py`).

Marketplace-specific files owned here: the manifests, `README.md`,
`scripts/`, `media/` (the hero/rungs SVG pairs + the tape-rendered gifs ·
teaching surfaces: their commands follow the same binary-truth gates),
the gate workflow, `mirror.json`, `listings.yaml` (every
external listing/submission registers there — pinned description from the
bank · cadence class · kill criterion >60d), and this file.

**External skill copies (parity watch).** The open submission
NousResearch/hermes-agent#61632 carries the kit-native Hermes skill
`skills/autonomous-ai-agents/nika/SKILL.md`. Refresh that exact fork file
with each kit-side change and verify its bytes and host-specific tests.
Resolve the PR's actual state and head before updating it; an old fork ref
is not a live upstream publication. The former watches
sickn33/agentic-awesome-skills#806 and davepoon/buildwithclaude#238 merged
on 2026-07-12 and 2026-07-14 respectively; their outcomes live in
`listings.yaml`. Updating a merged copy requires a new upstream change,
not a push to the settled submission branch. New copies name their source
file and any host-owned frontmatter at submit time.

## Load-bearing facts (verify in-repo · never from memory)

- The three plugin manifests MUST agree on one version (gate-checked).
- The README's advertised `nika_*` tool names MUST equal what the
  pinned `nika mcp` binary actually serves — asserted by
  `scripts/check-mcp-tools.py` against the live wire, never a
  remembered count.
- Counts live in the engine/spec canon; prose here stays count-free or
  gate-checked.

## Verify before any PR

```sh
python3 scripts/check-mcp-tools.py        # NIKA_BIN=… locally
python3 scripts/check-skill-commands.py   # kit-native skills vs the binary
python3 scripts/check-vocab.py            # the description-bank vocabulary law
# pins + upstream + manifest gates run in CI (.github/workflows/gate.yml)
```

## Concurrent sessions (the shared-checkout law)

Two agent sessions regularly hold this repo's ONE local checkout. Two
incidents in 24h (2026-07-11/12) wrote the law:

1. **Never commit in the shared checkout.** Another session can switch
   the branch between your edit and your commit — both bites landed on a
   sister feature branch. Ship via the git data API instead (blob → tree
   → commit → ref on a fresh branch), then PR.
2. **Re-parse every YAML you write, before it ships.**
   `python3 -c "import yaml; yaml.safe_load(open('listings.yaml'))"` costs
   one second; the broken-parse incident cost a sister session a repair
   commit. CI now gates the parse — do not rely on it discovering your
   break.
