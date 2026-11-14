# Server-side plan families, and where their state lives

Starpath carries several plan sets that all sound like "the server work". Pick the family from the
user's vocabulary before reading, and open the answer by saying which one you read.

## The two families

| The user's words | The plan set | Authority vs. state |
| --- | --- | --- |
| "server-side testing", "the server campaign", "paid validation", "G0" | `docs/roadmap/medium-validation-execution-plan.md` (§11 defines the G0–G7 execution order), `docs/roadmap/paid-validation-preparation-and-runner-remediation-plan.md`, the G0 rerun handoff in `docs/roadmap/`, `docs/runbooks/paid-validation-v2.md`; controller and task inventory in `scripts/server-validation/` (`manifest-v2.json`) | The plans are Informative and close nothing. Obligation status is `docs/registers/obligations.md`; semantic responsibility is the acceptance map. Workstream state is the newest `docs/results/` record plus the handoff's appended paragraphs. |
| "server rung", "TDX measurement", "O-1", "the bare-metal host" | `docs/runbooks/server-rung*.md` (plan, archived handoff, session record) | Deferred deployment sizing, operator-commissioned. There is no endpoint in the repository and the runbook forbids inferring or probing one; the production clause additionally needs a streaming prover the repo does not have. |

## Reading a campaign handoff

- The authority order is: acceptance map / obligation register → governing spec or ADR → the plan →
  the result records. A controller status, a control run, or a local qualification is deliberately
  narrower than the obligation it feeds.
- "Next" is almost never in the checklist. Read the appended status paragraphs and the newest
  `docs/results/` record for the stream; the checklist is written once and left behind.
- The four facts a report must keep separate: local preparation, configured no-work readiness,
  observed external readiness, completed live evidence. Conflating them is the standard overclaim.

## Campaign mechanics worth knowing before planning

- One generated task inventory drives the campaign; read `manifest-v2.json` rather than trusting a
  remembered count. It splits into a source/controller qualification suite (`ci`, the on-host G0) plus
  heavy-proving, O-10, O-11, O-34, O-5 and O-1-control suites and bundle-import tasks.
- G0 gates everything downstream: the host reruns its own qualification against the pinned candidate,
  and a clean service exit is not an outcome — every task including the qualification task must report
  passed. Failures are preserved, not relabelled or retried around.
- `resume` schedules the remaining tasks in the reviewed order and skips what already passed, so it is
  only valid on the *new* run: after a source change the old run is evidence, never a resume target.
- A partial campaign's reduced manifest is regenerated from the reviewed canonical manifest and then
  validated by the controller; never edit a retained run's manifest or data to produce it.
- Authorization boundaries: host provisioning, preflight, workload execution, testnet/transaction
  actions and device-quote capture each need explicit operator authorization for a supplied target;
  local preparation, bundle validation, unit tests and booking-readiness reports do not.

## Local versus where the evidence lives

Evidence roots are outside the checkout, and in practice on whichever machine ran the lane. Paths inside
records are that machine's home, so check existence on the current host before citing them; the heavy
local lanes and their result directories will not be present on the small dev host. When a record's
anchors are unreachable from the pushed repository, that is debt to surface to the owner.
