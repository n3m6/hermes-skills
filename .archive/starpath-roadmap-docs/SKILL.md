---
name: starpath-roadmap-docs
description: Use when writing or committing a starpath docs/ file.
---

# Starpath docs: writing and committing a plan

Class of task: put a new document into the `starpath` docs tree — a roadmap or
closure plan, a spike/research plan, a runbook — and commit it without breaking the
doc gates. Repo: `~/repos/starpath` (`silentsea-xyz/starpath`). Read the root
`AGENTS.md` router first; it routes to `docs/house-rules.md` and then to the one
spec your task touches.

## Where each artefact belongs

- **Plans, specs, ADRs, registers, runbooks live in `starpath`.**
- **Spike code, fixtures, orchestration, CSVs and `FINDINGS.md` live in `mariner`**
  (`~/repos/mariner`, a sibling checkout). A starpath plan *plans* the work and
  cites mariner by path; it does not carry the results.
- Cite across repos as `mariner:<path>` in prose (`mariner:spikes/results/spike-x/FINDINGS.md`),
  not as a relative link that cannot resolve from the starpath tree.
- Authority is set by the status header, not by the folder: **Normative** (code must
  conform) / **Draft** / **Reference** / **Informative**. `docs/specs/inherited/` and
  `docs/specs/reference/` are imported copies with provenance headers — do not edit
  them into shape; a change there is a spec change.
- **A working plan authored in plan mode does not go inside the checkout.** An untracked file
  under `~/repos/starpath` makes the tree dirty, and the measured gates require a clean
  worktree (their source SHA is part of the evidence) while `check-doc-links.sh` also scans
  untracked files. Write it under the session workspace's `.hermes/plans/` and hand the user
  its absolute path; only documents meant to be committed go into the repo tree.
- **A phase plan that *is* meant to be committed belongs beside its milestone overview.** The
  overview owns the phase sequence and says where phase plans live — follow its own instruction
  (`docs/submissions/<milestone>/`) instead of inventing a directory.

## Always-on rules

1. **A plan is Informative and says so up front**: `**Status: Informative.**` plus a
   date, and one sentence naming what it does *not* amend — specification, ADR,
   obligation, constants, wire format. House rule 2 (a settled decision reopens only
   with a new measurement) means an Informative doc that reads like a spec change is a
   defect, not a style issue. Name the ADR whose reopening condition the work is *not*.
2. **Every number is cited to the file that owns it** — `docs/registers/measurements.md`,
   the ADR, the spec section, or the mariner findings file. Separate measured rows from
   derived rows in the same table, and never present arithmetic as measurement.
3. **Constants come from `packages/params`** (house rule 1) — a plan refers to them,
   never restates them, and a number that looks like a protocol constant does not go in
   a plan at all.
4. **Use the glossary's words** (house rule 9): epoch, chunk, chip, carrier, leaf, tree,
   root, bridge, wrap, tape, delta. Delivery labels in a plan are labels and must not
   become protocol vocabulary — say so in the doc.
5. **Run the doc gates before committing**, not after: they are in CI and a red pipeline
   blocks the merge.
   ```bash
   cd ~/repos/starpath
   ./scripts/check-doc-links.sh                 # every relative markdown link resolves
   ./scripts/check-roadmap-reference-policy.sh  # delivery-identifier policy
   ./scripts/check-acceptance-map.sh            # acceptance map stays consistent
   ./scripts/check-no-inline-constants.sh       # house rule 1, outside packages/params
   ```
   Two of the four can be **red at HEAD on files nobody in this task touched** — an
   active roadmap path, and a `spikes/*/src/*.rs` comment that inlines the 257-layer
   constant. Run all four, fix only your own findings, and report the rest.
   Run them **unpiped**: `./scripts/check-doc-links.sh | tail -5; echo $?` prints
   `tail`'s status, so a red gate reads green. Call the script alone or read
   `${PIPESTATUS[0]}`.
6. **Commit locally; pushing is a separate, asked-for action.** Message shape is
   `docs(<area>): <what changed>` (`docs(roadmap):`, `docs(results):`, `docs(specs):`).
   These repos are private, carry per-repo deploy keys, and the work lands on `main` —
   a push is a publish. Offer it, do not assume it.
7. **Verify the write landed before saying it did.** `git show --stat --oneline HEAD`
   after a commit, and do not report a document as committed (or a skill as saved)
   on the strength of a plan to commit it. The reply must match tool output.
8. **A new `docs/results/` record is indexed in the same commit.** `docs/results/README.md`
   carries a `## Records` list; add the bullet there when you add the file, or the record is
   one nobody finds. The bullet names the topic, the date, and what was run — not a figure,
   which lives in the record itself.

## Procedure: a spike or research plan

1. **Find the neighbours.** `ls docs/roadmap/`, then read the closest existing plan
   end-to-end and mirror its skeleton — there is a house pattern, and matching it is
   most of the review. A ready skeleton is in `templates/spike-plan.md`.
2. **Recon what the plan acts on**, in this order: the obligation in
   `docs/registers/obligations.md` that owns the term; the ADR that settled the current
   approach and its reopening condition; the inherited spec section the work would
   amend; the measurements register for what is *already* measured. Anything already
   measured goes in a "must not be re-measured" table with its source, so the plan does
   not pay for it twice.
3. **Order the work cheapest-falsifier-first.** The house style is a first stage that
   can kill the whole idea in an afternoon (a ceiling computation, a paper comparison, a
   census re-read) before any gadget is built. Say out loud which stage can stop the
   work.
4. **Pre-register the gates and the decision rule**, including the prior you expect to
   fail. A plan whose gates were written after the numbers is indistinguishable from one
   fitted to them.
5. **State the layout and provenance**: which repo, which arm/command name, which CSV
   directory, the host record discipline, and that every measured row must be a verified
   proof. If third-party code is read or vendored, say which (house rule 8 needs a
   `PATCHES.md` for anything copied, with upstream commit and per-patch reason).
6. **Write what it does not decide**, as its own section: specs untouched, obligations
   still open, wire formats untouched, and the next measurement that does close them.
7. **Run the gates, fix, commit, verify** (rules 5–7).

## Procedure: a phase plan derived from a milestone overview

Class of task: a milestone overview lists phases with results, dependencies, and exit gates,
and one phase now needs its own implementable plan. The overview owns scope; your document
turns exactly one phase into ordered work.

1. **Read the phase section whole** before planning it — entry condition, work to cover, exit
   gate, handoff. Elaborate that phase; do not re-cut the sequence or absorb a neighbour's work.
2. **Re-verify the overview's baseline and environment claims against the live tree.** Compare
   the revision it records as its planning baseline with `git rev-parse HEAD`, check
   `git status --short --branch`, and re-check the toolchain and CI claims it relies on. An
   overview's baseline is a snapshot: by the time a phase is planned the tree has usually moved,
   and a claim about the pipeline or a tool version can be stale. Record the revision actually
   used, and put every discrepancy in the plan's context table instead of silently planning
   against the older state.
3. **Recon what already does the work**, in this order: the runner script and spec that own the
   path, the runbook section that owns the pinned prerequisites, and which of those pieces are
   development-only. Where the phase must reuse what an acceptance fixture already does, decide
   extraction versus duplication in the plan, name the fallback, and keep it away from
   assertions (see `starpath-validation`: never fork or weaken a gate).
4. **One task per 2–5 minutes of focused work**, each naming exact file paths, the command to
   run, its expected output, and a commit. Mark the long-running tasks as such, give their
   wall-clock budget from a recorded number, and say plainly that the budget is an estimate from
   that number rather than a measurement.
5. **Separate the three artefacts a phase produces.** Procedures go to `docs/runbooks/`,
   measurements to `docs/results/` (plus its README index bullet), and the schedule revision
   back into the overview as a dated block — the overview's own prose stays intact and its
   Informative status is not upgraded, because completing a phase is not a measurement of the
   system. A phase plan never carries a measured figure into prose as a decision rule.
6. **Leave the next phase a starting point**, and say which gates this phase cannot close
   (acceptance evidence, production claims, obligations). Gates, commit, verify (rules 5–7).

## Procedure: a spec change (ADR plus the amendment)

Trigger: a settled claim is wrong, or an inherited document needs its living copy
changed. Do not fix wording quietly — every such change moves through the same steps.

1. **Decide what kind of claim it is.** A *measurement* settles a decision (house rule
   2); an argument or a source reading does not. So a reading may correct a *reason* or
   a false *existence clause*, but it must not reverse a decision. When that is the
   case write the ADR's `Settled by` as an explicit judgement call and say in plain
   words that it is **not** a measurement — the ADR README requires a judgement call to
   say so rather than borrow the authority of a number.
2. **Add the ADR.** Take the next free number from `ls docs/adr/`, copy
   `docs/adr/template.md` (Status / Date / Settled by, Context, Decision, Consequences,
   Reopening — one page, prose over bullets where the reasoning matters), and add its
   row to the index table at the end of `docs/adr/README.md`. Supersede an existing ADR
   only when reversing it, and then mark the old one `Superseded by ADR-NNNN`. A
   single corrected clause gets a short `> **Corrected <date> by [ADR-NNNN](...):**`
   blockquote in the old ADR's body saying which part stands instead.
3. **Amend the living normative document.** An inherited spec's provenance header is
   where amendments are logged: append `> **Amended in starpath on YYYY-MM-DD:** …`,
   naming the ADR and what moved. New sections keep the document's own numbering. Never
   edit the body of `docs/specs/reference/`: a `Reference` snapshot records
   supersession by adding the superseded section to its "Already superseded here"
   provenance paragraph.
4. **Then the register.** Research is not a debt. If the register already lists the
   topic as explicitly out of scope, add a pointer to the corrected basis — do **not**
   invent an `O-N` obligation for it.
5. **Keep the proposer honest.** If a roadmap document proposed the change, move its
   status block to `**Applied YYYY-MM-DD**` and rewrite the section that described the
   proposal into a description of what landed, so the two documents cannot be read as
   contradicting each other.
6. **Gates, commit, verify** (rules 5–7). One commit may carry the ADR, the amendment,
   the snapshot annotation, the register pointer and the proposer update; name each in
   the message body.

A caution that generalises: **a gated conclusion does not move until its gate's own
condition is met.** When a normative note says a conclusion changes only after a census
or a measurement, correcting the letter is allowed and reversing the conclusion is not
— the change moves the *reason*, and the amended document should say so explicitly.

## Procedure: the obligations register (evidence, not obligation)

`docs/registers/obligations.md` is **Normative**, and an entry is a claim with a
status, not a container for findings. Four steps, in order:

1. **Read the entry whole before you characterise it** — the body *and* the
   `**Status:**` / `**Blocking:**` / `**Owner:**` line at the top. An entry whose prose
   still reads like an open gap is routinely already discharged elsewhere in the tree,
   and calling it open in a reply is a wrong fact the user will check. One entry cleanly:
   `awk '/^### O-6[^0-9]/,/^### O-7[^0-9]/' docs/registers/obligations.md`.
2. **Corroborating an obligation neither reopens nor discharges it.** Add a dated,
   bold-led paragraph (`**Corroborated YYYY-MM-DD by <what, with commit ids>.**`) after
   the existing prose, then state explicitly what did *not* move. Do not reword the
   obligation and do not rename its heading — other documents cite these anchors
   (`obligations.md#o-5-…`).
3. **Name the kind of evidence inside the record.** Source reading, a diff of somebody
   else's tree, an unmerged branch, an unmeasured projection: each gets its own clause,
   so a later reader cannot mistake it for a measurement (house rule 2). A comparison
   that was never executed says so in the entry.
4. **Adjudicate a divergence, do not just report it.** When a peer's implementation
   differs from ours, decide which of *defect here* / *defect there* / *capability they
   declined* it is, and write that down. "They differ" is not a finding.

## Pitfalls

- **The delivery-identifier policy is enforced in paths *and* prose.**
  `scripts/check-roadmap-reference-policy.sh` rejects the shapes `M1`–`M4`,
  `S1`–`S9`, `P1`–`P8`, `C1`–`C6`, `U1`–`U3`, `H1`–`H4`, `OC1`/`OC2` as standalone
  tokens in any tracked file **except `docs/roadmap/archive/`** — and the same shapes
  anywhere in a path or filename. Only the S-series is matched case-insensitively; the
  others are uppercase-only, so a lower-case vendor name (`p3-schnorr`) passes while
  `P3` does not. Dot-separated forms (`L.2`) survive, bare ones do not. The cheap escape
  is to name work items and arms descriptively (`sigagg`, `premise`, `ceiling`,
  `recursion`) instead of by letter+digit.
- **A gate can already be red at HEAD on a file you did not touch.** When your own file
  is clean, do not "fix" the other one: count its blast radius (`search_files` for the
  filename) and report it. Renaming someone's in-flight plan is not a side effect of
  adding a document.
- **Repo-wide `grep -rn <pattern> .` at the starpath root hangs** on the build tree
  (`target/` holds gigabytes of artifacts). Use `search_files` (ripgrep-backed, respects
  ignore files) or scope the path to `docs/`, `packages/`, `scripts/`. The same applies
  to `find`.
- **Doc links are checked; anchors and external URLs are not.** A relative link must
  resolve from the file that holds it. The `docs/specs/inherited/` and
  `docs/specs/reference/` exemptions are conditional on their provenance header — do not
  add a file there without one. A link to a file you *intend* to add later fails the gate
  now: add the target in the same commit, or describe it as prose (`the date-stamped record
  in docs/results/`) until it exists.
- **Do not restate a register figure as a plan constant.** Measured figures are
  Informative and host-specific; a plan that turns one into a decision rule creates the
  second home for a number that house rule 1 exists to prevent.
- **An out-of-scope register entry is not an obligation.** The obligations register's
  "Explicitly out of scope" list exists so those items are "not mistaken for
  oversights". Adding an `O-N` for one contradicts the register's own design; a pointer
  keeps it truthful instead.
- **Do not invent the spike's letter or number.** Existing plans reference spikes by
  letter (`spike-j`, `spike-n`) from the mariner archive; a new spike's identity is
  better carried by a descriptive name, which also keeps the identifier policy satisfied.
- **Several edits to one file in one turn can race.** Independent tool calls in a single
  turn may execute concurrently, so a second `patch` computed against pre-first-patch
  text fails or duplicates. For a same-file group, do the edits **sequentially inside one
  `execute_code` call** (`from hermes_tools import patch`) and read the file back once
  afterwards — that call is also where the gates belong, before any commit.
- **A cross-repo file cannot be linked, only cited.** The doc-link gate reads
  `[text](path)` as a path relative to the file that holds it, so a link-shaped mention
  of something inside another checkout fails, and so does a `..` target (a directory is
  not a file). Write `mariner:<path>` or plain text instead.

## Support files

- `templates/spike-plan.md` — the section skeleton to copy for a new spike/research
  plan (status header, why, reference materials, already-measured table, arms,
  work items, gates and decision rule, what it does not decide, layout, acceptance,
  risks, re-entry).
- `references/peer-fork-comparison.md` — how to diff a peer's public fork of a
  dependency we vendor, and what a corroboration or divergence paragraph must contain.
  Read it before writing evidence about somebody else's implementation into the record.
