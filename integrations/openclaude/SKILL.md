---
name: nika-workflow
title: Nika Workflow
description: Captures a repeated AI chore as a Nika workflow file — audited before it runs, cost-capped while it runs, hash-chain traced after.
category: general
tags:
  - workflow
  - automation
  - cost-control
  - audit
  - local-first
trust: community
version: 0.1.1
license: MIT
author: ThibautMelen
tools_required:
  - Bash
---

# Nika Workflow

[Nika](https://nika.sh) is an open-source Rust engine that captures a
repeatable AI task as one plain-text `*.nika.yaml` file. The file is
audited before a single token is spent, runs against local or cloud
providers under a spend ceiling, and records a hash-chained journal you
can verify afterwards.

Use it for the work that repeats. Nika is not a coding agent and does not
compete with one: OpenClaude writes the code, Nika runs the chore that
comes back every week and hands you a receipt for it.

## Use this skill when

- The user describes a prompt or prompt chain they run more than once — a
  weekly digest, an inbox triage pass, a release-note draft — and wants it
  captured as something re-runnable.
- A shell or Python script in the repo calls a model API, or wraps HTTP,
  file and JSON plumbing around model output.
- The user asks for a hard spend ceiling on an AI task, or asks what a
  task will cost before it runs.
- The user needs a record of what an AI run actually did: a receipt, an
  audit trail, something a reviewer can check independently.
- A `*.nika.yaml` file is open or being written, or `nika check` reported
  a `NIKA-XXXX` finding that needs fixing.

## Do NOT use this skill when

- The user wants a one-off answer or a single tool call — answer directly,
  a workflow file is overhead.
- The user wants application code written, refactored or reviewed — that
  belongs to a coding skill.
- The task needs conversational back-and-forth mid-execution — workflows
  are non-interactive by design; a confirm gate asks one question, it does
  not hold a discussion.

## Procedure

1. Confirm the engine is present: `nika --version`. If it is missing, say
   so and stop — installing is the user's move
   (`brew install supernovae-st/tap/nika`, or the paths listed at
   nika.sh). Never improvise workflow YAML from memory.
2. Start from a skeleton, never a blank file. `nika new --from '?'` lists
   the embedded templates, `nika new --from <template> <file>.nika.yaml`
   writes one, and bare `nika try` lists complete runnable lessons.
3. Fill it in. The envelope opens with `nika: <kebab-case-name>` — that
   one key carries both the mark and the file's name, and there is no
   `workflow:` envelope key — plus a `tasks:` map keyed by task id.
   Exactly one verb per task: `infer` (a model call) · `exec` (a
   subprocess, whose `command:` is an argv list) · `invoke` (a builtin or
   MCP tool) · `agent` (a bounded multi-turn loop). Every value the file
   depends on is declared in one of three authorities: `inputs:` ·
   `const:` · `secrets:` — a deployment-supplied value is an `inputs:`
   entry with `required: false` and a `default:`.
4. Declare the boundary. `permits:` states what the workflow may touch,
   and an ABSENT block means zero authority — any effect without a grant
   is refused at check time. `nika check <file> --infer-permits` prints
   the tightest block the workflow actually needs; paste it in.
5. Audit before anything runs: `nika check <file>`. Exit 0 is clean, exit
   2 carries findings. Each finding names its task and the fix it wants;
   `nika check <file> --fix` applies the mechanical repairs. Decode an
   unfamiliar code with `nika explain NIKA-XXXX`. Loop until clean.
6. Report cost from the check output, never from a guess. `≤ $X` is a
   ceiling; `≥ $X FLOOR` means at least one task is unbounded, and you
   name why. A model running locally is unpriced compute — say unpriced,
   never free.
7. Hand the run to the user. Typing `nika run <file>` is their move; give
   them the line, with `--max-cost-usd <n>` when spend matters. An offline
   rehearsal costs nothing: `--model mock/echo`.
8. After a run that mattered, prove it. `nika trace verify <trace>` checks
   the hash-chained journal under `.nika/traces/`, and
   `nika trace evidence <trace>` exports a pack a reviewer can check without
   trusting you. Cite the trace, never a memory of the run.

## Examples

In scope: *"every Monday I paste a competitor changelog into a model and
ask what changed"* → capture it as a workflow with a fetch task, a bounded
`infer`, and a written report; audit it clean; hand over the run line.

In scope: *"this deploy script calls a model to draft the release note"* →
port the model call to `infer:`, the file writes to the `nika:write`
builtin, declare the permits, pin the behavior with
`nika test <file> --update`, and leave the old script for the user to
retire.

Out of scope: *"explain what this regular expression does"* → answer
directly; no file, no workflow.

Out of scope: *"refactor this module"* → a coding skill owns that. Nika
does not write application code.

## Self-check before responding

- Did `nika check` exit 0 on the exact file being handed over? If it did
  not, the file is not ready to hand over.
- Is the cost reported the way the audit reported it — a ceiling, or a
  floor with a named reason — with no local model described as free?
- Does the file declare a `permits:` block, or is the body genuinely pure
  compute and saying so with an empty one?
- Was the run proposed as a command line rather than executed?
- Is every credential referenced through the declared `secrets:` block,
  with no literal value written anywhere in the file?
