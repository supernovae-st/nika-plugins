<!-- SPDX-License-Identifier: Apache-2.0 -->
# Skill Hub submission — prepared, NOT opened

Everything needed to open the `Gitlawb/openclaude-skills` PR lives here.
Submit only when external contribution is within the user's mandate and the
destination's contribution policy. This prepared pack is not a submitted PR.

Rules below were read from their `CONTRIBUTING.md`, `DECISIONS.md` and
`.maintainers/trust.json` on 2026-07-28. Re-read them at submission time —
a registry's rules move.

## Size the gesture first

| Signal (2026-07-28) | Value |
|---|---|
| `Gitlawb/openclaude` | 30,399★ · pushed same day |
| `Gitlawb/openclaude-skills` (the hub) | 11★ · 10 skills · last push 2026-05-27 |

The hub is a discovery surface, not the distribution. The plugin path in
[`README.md`](README.md) reaches OpenClaude users directly and needs no
one's approval. Spend the gesture if hub presence is worth it on its own
terms, not because it is the way in.

## The submission

1. Fork and clone `Gitlawb/openclaude-skills`, then `bun install`.
2. Copy [`SKILL.md`](SKILL.md) to `skills/nika-workflow/SKILL.md`.
3. Add a short `skills/nika-workflow/README.md` — every skill in the hub
   ships one beside its `SKILL.md`.
4. Validate: `bun run scripts/validate-skill.ts skills/nika-workflow/`
   (exit 0 clean · 1 errors · 2 warnings-only). Their scanner reads the
   body as agent-readable instructions and rejects hidden characters, HTML
   comments, fake role markers, injection wording, credential paths,
   exfiltration endpoints, external fetch helpers, encoded eval patterns
   and confirmation-bypass language. `SKILL.md` here was written against
   that list; the validator is still the judge.
5. Rebuild the registry: `bun run build:registry`. Commit the regenerated
   `registry.json` in the SAME PR — their CI fails a stale registry.
   Never hand-edit it.
6. Open the PR with their template: `?template=new_skill.md`.

## Non-negotiables in the PR

- **`trust: community`.** Their build FAILS a PR that self-declares
  `official` or `verified` without a matching `.maintainers/trust.json`
  entry. Promotion is theirs to make, in a later PR, and we never ask for
  it up front.
- **Disclose first-party**, in the PR body, in one plain line: *"Disclosure:
  I maintain Nika, the engine this skill drives."* Same disclosure we use
  on every other registry.
- **Describe OpenClaude as an open-source coding-agent CLI, and stop
  there** — in the skill, the README, the PR body and every follow-up
  comment. We integrate with that one tool, and claim no adjacency to
  anything else in the stack around it. That is the whole description.
- **Zero co-branding.** We are a skill in their hub, nothing more.

## Suggested PR body

> Adds `nika-workflow` — captures a repeated AI chore as a Nika workflow
> file: audited before it runs, cost-capped while it runs, hash-chain
> traced after.
>
> Nika is an open-source (AGPL) Rust engine. It is not a coding agent and
> does not overlap OpenClaude's job — it takes the chore that comes back
> every week (digest, triage, release notes, an ETL pass) out of the chat
> loop and into a file you can audit, budget and replay. The skill's
> procedure is the engine's own discipline: start from a template, declare
> the effect boundary, audit until clean, report output-cost estimates and unpriced input honestly,
> and complete execution only within the user's authorized scope and budget.
>
> `trust: community` per CONTRIBUTING. Validator run locally, registry
> regenerated in this PR.
>
> Disclosure: I maintain Nika, the engine this skill drives.

## After it merges (or closes)

Record the outcome in `listings.yaml` as a `submitted-pr` entry — created
at submission time, not before — with the pinned description from
`integrations/description-bank.md`, the normal cadence class, and the
60-day kill criterion.

Their `revocations.json` is a registry-level kill switch. Like every other
third-party registry we appear in, nothing load-bearing depends on it: the
tap, the direct URL and `npx` paths stay the truth.
