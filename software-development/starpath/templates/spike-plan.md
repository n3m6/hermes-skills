# <Subject> — spike plan and runbook

**Status: Informative.** This is an exploratory measurement plan. It is not a
specification, an architecture decision, an accepted measurement, or a source of
protocol constants. It does not amend `<spec>`; it does not reopen `<ADR>`; it does not
discharge `<O-N>`. The workstream labels below are delivery labels only and must not
become protocol vocabulary.

**Date:** <YYYY-MM-DD>.

## Why this spike exists

<The register's own statement of the gap, one paragraph, cited. Then the internal or
external trigger that makes it worth a spike now. Name what is already measured and what
is still open.>

<If a premise could kill the whole line of inquiry, state it here — what it is, which
spec line it rests on, and that the spike resolves it before building anything.>

## Reference materials

- `mariner:<arm path>` — the existing arm this one extends.
- `mariner:spikes/results/<spike>/` — the CSVs and findings it re-uses.
- `<starpath package path>` — the implementation the plan would change.
- `docs/specs/<spec>#<section>` — the normative section the work would amend.
- `docs/house-rules.md` — name the rules that bind this work (measurement reopening,
  layer ceiling, checked trace, transcript order, provenance, hiding).

## What is already measured, and must not be re-measured

| Quantity | Value | Source |
| --- | ---: | --- |
| <the numbers this spike must be read against> | | <spike-x / register> |

<State which units must never be divided by each other, and which figure is a summary
rather than an instrument.>

## Candidate arms

**Arm A — <the cheap arm>.** <What changes, what does not.>

**Arm B — <the structural alternative>.** <Pre-registered prior to falsify, and the
ceiling stage that can close it cheaply.>

**Arm C — <the out-of-scope option>.** <Measurement and price sheet only; the spec
changes it would force.>

**Arm D — control.** <Same-host, same-day baseline re-run plus the negative controls.>

## Work items

### 1. <Reconnaissance / premise check, read-only and pinned>
<Exact questions, exact source, deliverable.>

### 2. <The cheapest falsifier>
<The computation or census that can stop the spike, and what number stops it.>

### 3. <Build the surviving arm>
<Arm file, command name, CSV directory, differential against the control.>

### 4. <Hygiene: layers, hiding, transcript delta, corpus rows>

### 5. <Cost model at production shape — measured vs derived, separated>

## Gates and the pre-registered decision rule

- **Gate 1 — <marginal cost>.**
- **Gate 2 — <the gate that matters>.**
- **Gate 3 — <shape / row class>.**
- **Gate 4 — <soundness and binding>.**

<Decision rule written before the measurements; the expected-to-fail prior; what
adoption would require (ADR, spec, corpus, placement, code — in that order); and what
closing the line with a recorded number looks like.>

## What this spike does not decide

- It does not amend <spec> and does not touch `packages/params`.
- It does not reopen <ADR> (its own reopening condition is <...>).
- It does not close <O-N>.

## Measurement rows, layout, and provenance

<CSV directory under `mariner:spikes/results/`, arm file, host record discipline,
verified-proof rule, findings split, PATCHES.md if anything is vendored, and the verdict
copied forward into `docs/registers/measurements.md` as Informative.>

## Acceptance for this spike

- <the premise has a written answer with the spec lines it rests on>
- <the surviving arm has a matched, verified measurement, or the report says none
  survived>
- <layer count recorded; transcript delta and corpus rows named; hiding status stated>
- <every table separates measured from derived>

## Risks and pitfalls

- <the one about pricing a gadget by its constraint count / row class>
- <the one about exempting a cost because it lands outside the relation>
- <the one about inheriting a hiding property>

## Re-entry and follow-on

<If an arm passes: the fixed order. If none passes: where the verdict is recorded and
what stays open.>
