# Security

## Reporting

Please report vulnerabilities privately via
[GitHub security advisories](https://github.com/nika-open/nika-plugins/security/advisories/new)
— not in public issues. You'll get an acknowledgment within 72 hours.

## What this repo is — and what installing from it runs

- **Teaching surfaces, not executables.** The skill and the packs are
  markdown instructions plus config stanzas; nothing here executes on
  install. The binary they teach (`nika`) is installed separately, from
  its own release pipeline, checksum-verified.
- **The mirror is pinned.** Engine-mirror files are byte-identical
  projections of `nika-open/nika`, pinned by sha256 in `mirror.json`
  — a hand-edit on this side is a hard CI failure, so what you install
  from here is what the engine repo reviewed.
- **Kit-native files are binary-truth-checked.** Every `nika`
  subcommand a skill teaches and every `nika_*` tool a pack advertises
  is asserted against the latest released binary in CI (plus a daily
  cron), so the teaching cannot silently drift from what ships.
- **The oracle the packs wire is read-only.** `nika mcp` validates and
  teaches; there is no execute tool over MCP. The threat model lives at
  [`integrations/mcp/THREAT-MODEL.md`](integrations/mcp/THREAT-MODEL.md).
- **Skills never self-persist.** No skill here instructs an agent to
  edit its host's own configuration — the class host scanners rightly
  hunt (hermes's skill-guard verified this repo's skill SAFE).

## Supported

The `main` branch is the only supported surface — marketplaces and taps
pull from it directly.
