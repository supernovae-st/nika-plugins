<!-- SPDX-License-Identifier: Apache-2.0 -->
# Threat model — the oracle & the trace chain

Plain statements, scoped to what the machinery proves. Nothing more.

## The oracle (`nika mcp`)

- **Read-only by design.** The tools validate, explain and teach; there is
  no execute/run tool over MCP. Execution requires the CLI.
- **Local stdio subprocess.** No listening port, no network egress of its
  own; it answers from the vendored spec and the workflow text a client
  passes it.
- **Tool outputs are data, not instructions.** A workflow file can contain
  hostile text; the oracle returns findings *about* it. Clients should
  treat everything inside a workflow as untrusted content.
- **No key values.** Provider keys are read by the CLI at run time; the
  oracle's answers never depend on, nor contain, a secret value.

## The trace chain (`nika trace verify`)

- **Chain consistency is not producer honesty.** Changing an event without
  updating its hash links breaks the chain. Recomputing an entire unkeyed
  chain can restore consistency, so compare its head with independently
  trusted evidence or verify a trusted seal. Even a valid signature does
  not prove the writer told the truth. Verification reads existing evidence;
  it cannot create a missing journal or seal an incomplete one.
- **Costs are list-rate estimates.** Unpriced calls have no measured USD
  amount. Do not turn absent pricing into a claim of free work or a guaranteed
  invoice ceiling; in-flight calls can also overshoot an admission-stop budget.

## What never happens

- No telemetry — neither surface phones home.
- No secret leaves your machine through the oracle.
- No workflow executes because an agent asked politely over MCP.
