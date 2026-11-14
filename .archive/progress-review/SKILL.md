---
name: progress-review
description: "Use when asked how far along a project is, or what remains."
version: 0.1.0
author: Hermes Agent (curator)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [review, planning, status-reporting]
---

# Progress review: how far along, and what remains

## When to Use

- The owner asks how far along a project is, how much remains, or where things stand
  against the requirements.
- He asks for a design or status review of a long-horizon project (a game design, an
  implementation roadmap, a milestone plan).
- A milestone, phase or plan document is about to close and something must say what it did
  and did not settle.

Not for a build/verification task (that is the repo's own gate procedure) and not for
writing the plan itself (that is the `plan` skill).

It is a **read-only measurement task**: pull the latest, measure, report. No writes, no
refactors, and no heavy verification runs unless he asks for them.

## Rules that make the answer right

1. **Verdict first.** One short block: what is done, what is not, the rough fraction,
   and why that fraction is the honest one. He asks design questions in that shape and
   skips preamble. Never open with a methodology paragraph or a list of what you read.
2. **"What remains" comes from the project's own plan document, never from memory.**
   Find the build order / roadmap / milestone list and read it at HEAD, then answer in
   ITS step numbers and ITS item ids, quoting the doc's own hand-off sentence for what is
   next. A plan reconstructed from memory is a plausible list that will not match the doc
   the owner checks it against.
3. **Two axes, labelled: declared vs measured.** Requirements/design side = what is
   decided, drafted or open. Build side = what is measured versus what is a placeholder
   (read the status/ledger file's own honest list, not the roadmap's optimism). Say which
   axis every figure came from; never blend them into one percentage.
4. **Separate the kinds of "open".** Undecided is not the same work as
decided-but-unbuilt, which is not the same as built-and-awaiting-the-owner's-word. A
   count that lumps them misstates what is left - the second and third kinds are cheap.
5. **Report the drift, always, as its own section.** The highest-value finding of a
   review is stale bookkeeping rather than missing design: a version stamp older than the
   items under it, a declared total that does not reconcile with the list it summarises,
   a hand-maintained prose block ("the three biggest unresolved things") overtaken by
   later work, an item still tagged open in one place and ruled in another, or a measured
   number quoted from a skill, comment or memory instead of re-read from the code.
6. **Do not run the build gate or re-derive hashes for a review.** Cite the last recorded
   measurement with its date, commit and provenance (which command produced it) and say
   plainly that you did not re-run it. Adding "the numbers are as of that commit" is the
   honest version, and it is what he wants; a verification run answers a question he did
   not ask. Run the gate when the task is a build or a verification.
7. **Offer fixes as separate opt-in commits.** The review reports; the owner decides what
   is written back. Name the exact edits you would make if he says yes.

## Procedure

1. Pull the repo, note the commit you are measuring.
2. Read the plan spine whole, amendments included - later rulings amend steps in place,
   so a step's state is not simply started-or-not.
3. Count the open items programmatically (python in `execute_code`); never trust a
   declared total.
4. Read the measured-state file and its placeholder list; read the newest milestone/plan
   document, which carries which sub-phases landed and which human step is still owed.
5. Measure volume where volume is the honest answer: content/data counts against the
   design's own eventual target. For a deliberate thin slice this ratio, not a step
   count, is the truthful "how much remains".
6. Walk the risk register, marking each risk retired / holding / untouched with the
   evidence behind it (a stored fixture, an ignored matrix run, an adopted threshold).
   "Which risks are still naked" is the answer to the question behind the question.
7. Write it in that order: verdict, requirements side, build side, remaining work in the
   plan's own order, risk ledger, drift found, the one human step owed.

## Counting a tracking doc (the traps)

- **Declared totals drift; re-derive them.** Items in a list section = lines matching
  `^<ID>\b` between that section's banner and the next banner - and check the section
  against the doc's own convention for what the total should include.
- **Items recorded as their own `## <title> (<ID>)` heading are NOT in the list.** Scan
  those headings separately and reconcile the two sets before quoting any number; a
  prefix-only scan silently undercounts the open set.
- **Classify each item by the markers in its body** (built / ruled / deferred / bare),
  and bucket them by owning section using the doc's own index table, so the report can
  say which subsystems the open work belongs to instead of giving a flat count.
- **Header stamps, version numbers and char counts rot** (a header can be a day older
  than the newest item under it). Re-read them; never cite them as current.
- A tag census (`[DECIDED]` / `[PROPOSED]` / `[OPEN]` per document) is a shape, not a
  completion percentage - say so when you use it.

## Worked example

The owner's game-design repo WWX: Shadow Wars is where this method is exercised most: the
register `docs/design/00-open-questions.md`, the build order `16.3` and risk register
`16.4` in `docs/design/16-production-scope-risks.md`, measured state `docs/status.md`.
The project-specific conventions - the register's own count convention, the permanent
`W-` item ids, and why a design review does not run the gate - live in the
`wwx-shadow-wars` skill. Read them there; do not infer them here.
