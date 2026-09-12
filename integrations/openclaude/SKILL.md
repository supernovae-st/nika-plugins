---
name: nika-workflow
title: Nika Workflow
description: Author or port repeatable AI work into checked .nika.yaml workflows. Use for workflow artifacts and their diagnosis, not ordinary coding or one-off answers.
category: general
tags:
  - workflow
  - automation
  - cost-control
  - audit
  - local-first
trust: community
version: 0.1.2
license: MIT
author: ThibautMelen
tools_required:
  - Bash
---

# Nika Workflow

Use [Nika](https://nika.sh) through the host's Bash tool to capture repeatable
AI work in a `*.nika.yaml` artifact. Nika is an AGPL-3.0-or-later workflow engine;
this MIT-licensed skill teaches the public 0.118.7 contract. The host owns the
user's intent and authorization. A check gives evidence; engine and host gates
still control execution.

## Scope and discovery

Use this skill when the user wants to author, port, check or diagnose a workflow.
For an ordinary code edit or one-off answer, use the corresponding host tool.
A workflow is useful when repeatable work has defined inputs, outputs and a
failure policy; do not create one merely because a task uses several steps.

Identify the installed release with `nika --version`. If absent, complete setup
already authorized in the request or report the missing prerequisite and the
installation route at https://nika.sh. Use `nika doctor` when setup needs
diagnosis. Do not assume a model or host capability from its product name.

Read the existing file and callers before creating a replacement. For a new
shape, `nika new '?'` lists templates and `nika new <template> <file>.nika.yaml`
creates one. Resolve exact syntax from `nika spec --schema`, `nika catalog`,
`nika catalog --tools` and the matching release's
[authoring guide](https://github.com/supernovae-st/nika/blob/v0.118.7/.agents/plugins/nika/skills/nika-authoring/SKILL.md).
Read examples for unresolved structures, not a fixed quota before every edit.

## Author and validate

- Use `nika: <id>` and a `tasks:` map. Each task has exactly one verb:
  `infer`, `exec`, `invoke` or `agent`. Prefer native tools to shell glue;
  `exec.command` is an argv list. Bound inference and adaptive loops explicitly.
- Caller values belong in `inputs:`, fixed values in `const:`, credentials in
  `secrets:` with declared `egress:` sinks. Bind task data through `with:`;
  use `after:` for ordering without data. Never put credential values in files,
  arguments or reports.
- Declare `permits:` from the intended effects. Missing grants give zero
  authority; pure compute declares `permits: {}`. Review the proposal from
  `nika check <file> --infer-permits` against the user's scope before applying
  it. A diagnostic does not justify widening authority.
- Check the final file with `nika check <file> --json --native-strict`, including
  the intended model override. Read the exit status and the distinct `clean`,
  `native_strict_clean` and `paid_ready` verdicts. A paid-ready file can still
  fail another check. For composition, inspect coverage and child findings.
- Repair causes using `nika explain NIKA-XXXX`; `--fix` handles supported
  mechanical repairs whose diff should be inspected. Continue until the
  requested artifact checks clean or a concrete dependency/decision blocks it.

## Execution and evidence

Complete execution when already requested and authorized, preserving inputs,
model, effect scope, spend limits and existing human gates. Use
`nika run <file> --max-cost-usd <authorized-cap>` with the actual checked values.
Do not answer a human gate from generic run permission. Preserve the host's
session identifier for long work; before retrying an interrupted call, reconcile
its process, recorded trace, outputs and possible partial effects.

`--model mock/echo` changes envelope inference only. Task-pinned models, tools,
network calls, subprocesses and writes remain real. Rehearse only within an
isolated authorized boundary. `nika test <file> --update` supports a restricted
simulated plane that refuses network, subprocess and write effects; use it only
for workflows that fit that plane. Effecting migrations need controlled artifact
comparisons. Retire a source script only after parity and caller migration cover
its behavior and removal is authorized.

The checker estimates output-token cost, not the complete invoice. Input billing
may be unpriced; local compute is unpriced, never free. Metered caps stop new
admissions after crossing the budget, while already admitted calls can overshoot.
Unknown prices must remain unknown.

Use `nika trace show <trace>`, `nika trace outputs <trace>` and
`nika trace verify <trace>` for the identified run. Report the actual proof tier:
an intact chain is distinct from lifecycle completion or producer honesty.
Recording is enabled by default, but missing or incomplete recording does not
prove that execution never started or that no effects occurred. Export
`nika trace evidence <trace>` when an auditor pack is requested.

## Completion

Return the artifact, actual check verdict and remaining blockers. If execution
was requested, inspect the produced outputs against expected results and report
the real exit status, metered cost or unknowns, exact trace and verified tier.
A check is not a run receipt; a static port is not parity. Do not stop at a plan
or unchecked first draft when the remaining work is authorized.
