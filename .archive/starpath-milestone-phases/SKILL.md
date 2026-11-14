---
name: starpath-milestone-phases
description: Use when planning a starpath phase or authoring its docs.
---

# Starpath milestone phases

Class of task: the user drives `~/repos/starpath` as *milestones* made of *phases*. Each phase gets
its own plan document, its own exit gate, and its own dated result record; the milestone overview
stays the authority for scope. Environment, gates, dev stack, CI, and the browser-runtime mechanics
live in `starpath-validation` — this skill is the plan→execute→record workflow around them. Which plan
family a workstream belongs to, and where its state lives, is `references/server-side-plan-families.md`.

## Always-on rules

1. **The phase overview is the authority; a phase plan is a proposal.**
   `docs/submissions/<window>/<milestone>-plan.md` owns scope, sequencing, checks, and the schedule
   decisions. Quote its phase section, and never widen scope because something looks cheap.
2. **Recon order before writing anything:** the phase section → the previous phase's result record in
   `docs/results/` → the runbook's "Known gaps and owners" table (carryover debt lives there) → the
   governing spec / acceptance-map entry. Then **verify each claim against the tree**: a gap table is
   a snapshot, and the tree moves under it (ending a phase with `reset --yes` can delete the whole
   development root the next phase is meant to use).
3. **Cost claims must be measured, and the mechanism checked.** Never carry a measured figure to a
   situation it does not describe, and never promise a fast path without proving its precondition.
   Say "unknown" rather than reasoning from a number taken elsewhere.
4. **A phase plan cannot amend a protocol rule, constant, wire format, or gate.** New behaviour is
   resolved in the governing spec first; a plan that appears to need a spec change stops and raises
   it. If a plan does change a gate, it does so in its own "Decisions" section, in the strict
   direction, with the fallback if the owner rejects it.
5. **No fabricated completion.** A phase is complete when the integrated gate output exists plus a
   dated record — never because coding finished. A same-commit prebuilt run and a UI smoke check
   cannot advance recorded acceptance evidence; say so in the record.
6. **Plans and notes never go inside the checkout.** An untracked file in the repo counts as a dirty
   tree for the measured gates and is scanned by `check-doc-links.sh`. Session plans live in
   `.hermes/plans/`; evidence lives outside the repo.
7. **Grep for consumers before replacing an exported helper** (a fixture helper is typically imported
   by an operator tool, a `node --test` lane, and a runbook):
   `grep -rn '<name>' --include='*.mjs' --include='*.ts' --include='*.md' .` — update every consumer
   in the same task, or the tool breaks while its unit test still passes.
8. **Provenance dies on a squash; the tree hash is the durable handle.** When a work branch lands as
   one squashed commit, every short SHA and tag the records cite for that branch becomes unreachable
   (`git cat-file -t <sha>` fails, `git ls-remote --tags` is empty) while the pushed tree is intact.
   Before calling a candidate "the qualified one", match the record's recorded tree to a reachable
   commit (`git rev-parse <reachable-sha>^{tree}`) and pin the reachable SHA — a campaign pin has to
   resolve in the host's fresh clone. Report unreachable anchors as evidence-integrity debt the owner
   may want to fix (push the tag and objects), never as a footnote.

## Explaining a phase on request

"Examine Phase N — what needs to be done here?" is a read-and-answer turn, not a planning turn. Answer
shape the user expects: one-line verdict on what the phase *is* and what it gates · entry state
verified with paths and line anchors (what exists, what is still a placeholder, what the previous
phase deliberately deferred to this one) · each overview work item translated into what actually has
to be built, with the source fact that constrains it · decisions already fixed by the overview
separated from the forks still open, each with the alternative it rejects · the exit gate plus how
much of it can be proven on this host versus needing the owner at a keyboard · what the phase does NOT
establish · the record, overview-section, and gap-table updates it owes on closure. End with the
smallest set of owner decisions the plan needs. Do not write the plan file in an explanation turn, do
not start executing, and do not silently decide an open fork.

For a **"what do we do next?"** turn, three extra obligations:

- **Name the plan set you read, because the repo has two families that share the word "server".**
  Pick by the user's words before answering, and say which one you read plus how to redirect you. See
  `references/server-side-plan-families.md`.
- **A handoff's state is in its appended paragraphs, not its checkboxes.** Read the appendix ("completed
  <date>" / "outcome") and the newest `docs/results/` record for the workstream before believing an
  unchecked acceptance list; a plan document is edited incrementally and its checklist rots.
- **Split the remaining items into operator-gated and local, and say where "local" runs.** Host
  provisioning, preflight, workload execution, testnet actions and device capture need explicit
  authorization; local preparation, validation and booking-readiness reports do not. Check that the
  evidence paths a record cites actually exist on *this* host — heavy lanes often ran on the other
  machine and their `/home/<other-user>/...` roots will not resolve here.

End such a turn with the smallest owner decision set, including the schedule: a campaign competes with
the dated milestones in `docs/submissions/<window>/README.md`. State what the next step does NOT
establish — a green source/controller qualification run moves no obligation.

## Plan shape the user expects

Section order: Goal (one sentence) · Current context/assumptions (revision actually used, host and
toolchain, what already exists and must not be rebuilt) · Architecture (2–3 sentences) ·
**Decisions fixed by this plan** · Layout/provenance table · Scope and non-goals · Tasks ·
Tests/validation summary · Risks, tradeoffs, open questions · exit-gate mapping · handoff to the next
phase.

- **Decisions name the alternative they reject.** One line each: the choice, the reason, the rejected
  option. A reviewer can then overrule one decision without unpicking the rest, and an implicit fork
  is what turns into a mid-phase rewrite (how configuration reaches the app, which asset path, which
  guard, whether to add a dependency).
- **Non-goals are explicit and include the next phase's work.** "Do not start X to compensate for an
  unfinished gate" prevents the classic overrun.
- **Task template:** Objective · Files (exact paths, create vs modify) · numbered steps with the exact
  command **and its expected output** · full TDD cycle for code tasks (write the failing test → run it
  and read the failure → implement minimally → run it green → lint → commit with the exact message) ·
  complete copy-pasteable code for every new file. A zero-context implementer must never guess.
- **Flag the tasks that are not 2–5 minutes with `[LONG]`** and say to start them detached in
  tmux/`setsid` while the other tasks proceed; give the fallback path if the fast path's precondition
  is missing.
- **State what the phase does NOT establish** in both the plan and its result record. This user reads
  the negative space: it is the difference between a demonstration and an acceptance claim.
- Reference the repository's own exceptions rather than inventing process: CI is
  `workflow_dispatch`-only, so the local gate sweep *is* the gate set, and the doc gates plus the
  package lanes must be run **unpiped** (a piped gate reports the pipe's status and reads green when
  it is red).

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
   bound). Cite those anchors in the answer — they are what makes a claim checkable. Copy the sequence
   and the parameter sources, never the transport: a fixture that authorizes over an unlocked-node RPC
   client is exactly what product code must not do.
5. **Grep for the WRITER of every value the phase says the environment publishes** — config field,
   address, artifact. A runbook phrase like "recorded once a session creates one" often describes a
   step that exists only inside the acceptance spec, so the published value is empty in the operator
   stack and a later phase's gate has no input.
6. Fix the decisions before writing tasks. For each real fork write choice + reason + rejected
   alternative; a decision deferred to implementation costs a rewrite.
7. Write the plan to `.hermes/plans/<date>_<time>-<slug>.md` (or the exact path the runtime
   supplies) and reply with what was planned plus the path, then offer execution (subagent-driven:
   one fresh child per task, spec review then quality review). Do not start executing in the
   planning turn.
8. Execute task-by-task, committing locally per task with `type(area): what changed`; never push
   unless asked.
9. Close the phase: dated record in `docs/results/<topic>-<date>.md` plus the README index row; a
   "Phase N result and measured re-estimate" section appended to the milestone overview; the runbook
   updated (close the gaps that closed, add the ones you found, each with an owner); and a numbered
   entry-point list for the next phase's plan.

## Authoring starpath docs (specs, ADRs, registers, results)

Class of task: put a document into the `starpath` docs tree — a roadmap/closure plan, a
spike or research plan, an ADR, a spec amendment, or an obligations-register entry — and
commit it without breaking the doc gates. Read the root `AGENTS.md` router first, then the
one spec the task touches.

- **Where each artefact belongs.** Plans, specs, ADRs, registers and runbooks live in
  `starpath`; spike code, fixtures, orchestration, CSVs and `FINDINGS.md` live in the
  sibling `mariner` checkout. Cite cross-repo as `mariner:<path>` — a cross-repo file cannot
  be a relative link, because the doc-link gate reads `[text](path)` as a path relative to
  the file that holds it.
- **Authority is set by the status header, not the folder.** Normative (code must conform)
  / Draft / Reference / Informative. `docs/specs/inherited/` and `docs/specs/reference/`
  are imported copies with provenance headers — a change there is a spec change.
- **A plan is Informative and says so up front** (`**Status: Informative.**` plus a date),
  naming what it does *not* amend — specification, ADR, obligation, constants, wire format.
  House rule 2 means an Informative doc that reads like a spec change is a defect.
- **Every number is cited to the file that owns it** (measurements register, the ADR, the
  spec section, the mariner findings file); constants come from `packages/params` (house
  rule 1) and are referred to, never restated. Separate measured rows from derived rows.
- **A working plan authored in plan mode does not go inside the checkout** — an untracked
  file makes the tree dirty and the measured gates require a clean worktree. Session plans
  live in `.hermes/plans/`; only documents meant to be committed go into the repo tree, and
  a phase plan that is meant to be committed belongs beside its milestone overview.
- **Run the doc gates before committing, unpiped:**
  ```bash
  ./scripts/check-doc-links.sh                 # relative markdown links resolve
  ./scripts/check-roadmap-reference-policy.sh  # delivery-identifier policy
  ./scripts/check-acceptance-map.sh            # acceptance map stays consistent
  ./scripts/check-no-inline-constants.sh       # house rule 1, outside packages/params
  ```
  Two can be **red at HEAD on files nobody in this task touched** — run all four, fix only
  your own findings, and report the rest. Run them unpiped: `check-doc-links.sh | tail -5`
  prints `tail`'s status, so a red gate reads green.
- **Commit locally; pushing is a separate, asked-for action.** Message shape
  `docs(<area>): <what changed>`. These repos are private, carry per-repo deploy keys, and
  land on `main` — a push is a publish; offer it, don't assume it.
- **Verify the write landed** before saying it did (`git show --stat --oneline HEAD`), and
  index a new `docs/results/` record in `docs/results/README.md` in the same commit.

The four authoring procedures — spike/research plan, spec change (ADR + amendment),
obligations register, and the delivery-identifier policy — are distilled in
[references/docs-authoring.md](references/docs-authoring.md). A ready spike-plan skeleton is
[templates/spike-plan.md](templates/spike-plan.md); how to diff a peer's fork of a
dependency we vendor is [references/peer-fork-comparison.md](references/peer-fork-comparison.md).

## Pitfalls

- **A phase plan's fast path can depend on evidence-directory state.** A retained prebuilt layout,
  staged inputs, or a cached corpus is evidence, not supported tooling: record its provenance and
  prove it is still current (input hashes or an empty diff against the artifact inputs) before the
  plan relies on it, and give the cold-path fallback in the same task.
- **Trust the measure, not the vibe, for "is it hung".** A silent window on this host is usually
  compilation, epoch settlement, or proving. Check accumulated CPU on the child processes and the log
  tail; the recorded wall-clock figures are in `starpath-validation`.
- **The plan's quoted revision is not the revision it runs on.** State the revision actually used in
  the plan and again in the result record; the overview's "planning baseline" commit is usually older
  than the tree you measured.
- **A gate change hidden inside a feature task is a rejected plan.** Surface it as its own decision
  with the strictness argument and the alternative the owner might prefer.
- **Do not restate what the runbook already owns.** A phase plan adds decisions, tasks, and evidence;
  repeating the environment narrative makes two documents that drift apart, and the runbook is the
  one that must stay true.
- **Trace the next phase's exit gate back to a producing step before calling this phase scoped.** A
  gate that needs a fact no phase produces — an address nothing publishes, funding nobody performs,
  an artifact no task builds — is this phase's real first task or an escalation with a rejected
  alternative. Deferring it means the phase that fails on it also has to replan.
- **A test-only contract call never becomes product code.** When the reference path funds itself by
  minting a test-only token, the app does not grow that button — the package's own instructions
  forbid importing test-only entry points into `src/`, so funding stays a documented operator step.
  Check where the step sits in the reference order before claiming the gate needs it: a deposit that
  lands after activation is outside the activation gate.
- **Product code changes can break the acceptance spec at bring-up.** Replacing a starter page moves
  the page title the spec asserts, so a regression fails with `caseCount: 0` before any case runs.
  Update the assertion deliberately, call it out in the result record as a reviewable change, and do
  not change any assertion that the failure did not actually exercise.
- **Sub-second event-driven assertions in the acceptance spec are contention-sensitive.** A case that
  fails at the same index while something else is compiling or a duplicate runner is alive is a rerun
  signal, not a product regression: check for a live runner (`pgrep -af run-sdk-placement`) and rerun
  with the host otherwise idle before touching the spec.
