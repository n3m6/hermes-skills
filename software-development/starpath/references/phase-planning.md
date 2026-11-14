# Phase planning depth (starpath)

Depth for the "Phase planning & docs" half of the `starpath` skill. The always-on rules live there;
this file is the explain-a-phase turn, the full plan procedure, and the planning pitfalls.

## Explaining a phase on request

"Examine Phase N — what needs to be done here?" is a read-and-answer turn, not a planning turn. The
answer shape the user expects: one-line verdict on what the phase *is* and what it gates · entry
state verified with paths and line anchors (what exists, what is still a placeholder, what the
previous phase deliberately deferred to this one) · each overview work item translated into what
actually has to be built, with the source fact that constrains it · decisions already fixed by the
overview separated from the forks still open, each with the alternative it rejects · the exit gate
plus how much of it can be proven on this host versus needing the owner at a keyboard · what the
phase does NOT establish · the record, overview-section, and gap-table updates it owes on closure.
End with the smallest set of owner decisions the plan needs. Do not write the plan file in an
explanation turn, do not start executing, and do not silently decide an open fork.

For a **"what do we do next?"** turn, three extra obligations:

- **Name the plan set you read, because the repo has two families that share the word "server".**
  Pick by the user's words before answering, and say which one you read plus how to redirect you.
  See `server-side-plan-families.md`.
- **A handoff's state is in its appended paragraphs, not its checkboxes.** Read the appendix
  ("completed <date>" / "outcome") and the newest `docs/results/` record for the workstream before
  believing an unchecked acceptance list.
- **Split the remaining items into operator-gated and local, and say where "local" runs.** Host
  provisioning, preflight, workload execution, testnet actions and device capture need explicit
  authorization; local preparation, validation and booking-readiness reports do not. Check that the
  evidence paths a record cites actually exist on *this* host — heavy lanes often ran on the other
  machine and their `/home/<other-user>/...` roots will not resolve here.

End such a turn with the smallest owner decision set, including the schedule: a campaign competes
with the dated milestones in `docs/submissions/<window>/README.md`. State what the next step does NOT
establish — a green source/controller qualification run moves no obligation.

## Procedure

0. **Branch before reading.** `git fetch origin && git pull --ff-only`, then
   `git checkout -b abdulla/<topic-slug>` before touching the tree: this user opens one branch per
   work session and asks for it first. The branch name is provenance, not a required implementation
   branch; do the recon on it so the revision you read and the work you record agree.
1. Read the phase section of the overview; list its work items verbatim as the checkable spine.
2. Read the previous phase's result record and the runbook gap table; list the carryover items that
   tax this phase (each becomes a task or an explicit exclusion).
3. Verify those claims with read-only commands: file existence, `git log --oneline -25 -- <paths>`,
   `ls`, and symbol greps. Record where the tree disagrees with the documents — that disagreement is
   usually the phase's first real task.
4. **For a journey/UI phase, take the proven step sequence from the acceptance spec's fixture calls,
   not from product code.** The happy-path spec drives the real browser through named helpers
   (registration begin/resume, the epoch close between queueing and activation, funding, prepare /
   activate, evidence) in the order the product has to reproduce, together with the parameter
   derivations (a session bound computed as pinned chain-head time plus the params-owned validity
   bound). Cite those anchors — they are what makes a claim checkable. Copy the sequence and the
   parameter sources, never the transport: a fixture that authorizes over an unlocked-node RPC client
   is exactly what product code must not do.
5. **Grep for the WRITER of every value the phase says the environment publishes** — config field,
   address, artifact. A runbook phrase like "recorded once a session creates one" often describes a
   step that exists only inside the acceptance spec, so the published value is empty in the operator
   stack and a later phase's gate has no input.
6. Fix the decisions before writing tasks. For each real fork write choice + reason + rejected
   alternative; a decision deferred to implementation costs a rewrite.
7. Write the plan to `.hermes/plans/<date>_<time>-<slug>.md` (or the exact path the runtime supplies)
   and reply with what was planned plus the path, then offer execution (subagent-driven: one fresh
   child per task, spec review then quality review). Do not start executing in the planning turn.
8. Execute task-by-task, committing locally per task with `type(area): what changed`; never push
   unless asked.
9. Close the phase: dated record in `docs/results/<topic>-<date>.md` plus the README index row; a
   "Phase N result and measured re-estimate" section appended to the milestone overview; the runbook
   updated (close the gaps that closed, add the ones you found, each with an owner); and a numbered
   entry-point list for the next phase's plan.

## Pitfalls

- **A phase plan's fast path can depend on evidence-directory state.** A retained prebuilt layout,
  staged inputs, or a cached corpus is evidence, not supported tooling: record its provenance and
  prove it is still current (input hashes or an empty diff against the artifact inputs) before the
  plan relies on it, and give the cold-path fallback in the same task.
- **Trust the measure, not the vibe, for "is it hung".** A silent window on this host is usually
  compilation, epoch settlement, or proving. Check accumulated CPU on the child processes and the log
  tail.
- **The plan's quoted revision is not the revision it runs on.** State the revision actually used in
  the plan and again in the result record; the overview's "planning baseline" commit is usually older
  than the tree you measured.
- **A gate change hidden inside a feature task is a rejected plan.** Surface it as its own decision
  with the strictness argument and the alternative the owner might prefer.
- **Do not restate what the runbook already owns.** A phase plan adds decisions, tasks, and evidence;
  repeating the environment narrative makes two documents that drift apart.
- **Trace the next phase's exit gate back to a producing step before calling this phase scoped.** A
  gate that needs a fact no phase produces — an address nothing publishes, funding nobody performs,
  an artifact no task builds — is this phase's real first task or an escalation with a rejected
  alternative.
- **A test-only contract call never becomes product code.** When the reference path funds itself by
  minting a test-only token, the app does not grow that button; funding stays a documented operator
  step.
- **Product code changes can break the acceptance spec at bring-up.** Replacing a starter page moves
  the page title the spec asserts, so a regression fails with `caseCount: 0` before any case runs.
  Update the assertion deliberately, call it out in the result record as a reviewable change, and do
  not change any assertion the failure did not actually exercise.
- **Sub-second event-driven assertions in the acceptance spec are contention-sensitive.** A case that
  fails at the same index while something else is compiling or a duplicate runner is alive is a rerun
  signal, not a product regression: check for a live runner (`pgrep -af run-sdk-placement`) and rerun
  with the host otherwise idle before touching the spec.
