---
name: gated-repo-workflow
description: "Use when reviewing, triaging, or executing gated repo work."
version: 1.0.0
author: Hermes Agent (curator)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [review, triage, planning, delegation, verification, repos]
    related_skills: [plan, gated-rust-workspace, starpath]
---

# Working on the owner's gated repos

One skill for the three things the owner asks about a repo that carries acceptance gates, registers
and plan documents: **orient** (what is this repo, how far along is it), **triage** (here is a report
of what went wrong), **execute** (run this approved phased plan through subagents). All three are one
discipline at different tempos: read the repo as the authority, answer verdict-first, and make every
claim re-derivable.

## When to use

- "What is repo X?" · "summarize repos X and Y and how they relate" · "how far along is this
  project?" · "what remains?" · "where does it stand against the requirements" → **Mode A**.
- A report of observed behaviour comes back — a playtest round, a bug report, a usability pass, a
  benchmark post-mortem — and the question is what to do about it → **Mode B**.
- An approved phased plan is handed over: "create subagents and complete each phase", "work through
  the phases", "run the plan" → **Mode C**.

Not for: writing the plan itself (the `plan` skill owns plan craft and plan-mode mechanics), a
build/verification task on a specific repo (that repo's own gate procedure), the language-level build
mechanics (`gated-rust-workspace`), or repo-specific knowledge (e.g. `starpath`).

## Rules that hold for all three modes

1. **Verdict first.** One short block — what is done and what is not, what the thing is and how the
   pieces relate, or what the real defect is — then the detail. Never open with a methodology
   paragraph or a list of what you read.
2. **Facts come from the tree at HEAD**, never from memory, a doc's prose, or a number quoted from a
   skill or an old note. Re-derive declared totals; header stamps, version numbers and char counts
   rot (a header can be a day older than the newest item under it).
3. **Word boundaries before claiming a concept is absent or present** (`rg -iw`, `\b`). A bare
   substring makes a count meaningless — "tribute" matches *contribute*, "reparation" matches
   *preparation* — so a hit count reported from one is a fabricated finding.
4. **Never infer a relationship, a cause or a pipeline from prose.** READMEs, ADRs and design docs
   are the least maintained text in any project; manifests, relative `path =` dependencies, fixture
   imports, build scripts and commit dates are the maintained facts. Where they disagree, the
   disagreement IS the finding — report it, do not silently repeat the doc.
5. **Label the axes.** Declared (decided / drafted / described) and measured (a command produced it)
   are different axes; say which one every figure came from. A tag census (`[DECIDED]`/`[OPEN]`) is a
   shape, not a percentage. Separate the kinds of "open": undecided is not decided-but-unbuilt, which
   is not built-and-awaiting-the-owner's-word.
6. **A symptom is not a diagnosis.** Reproduce before repairing; name the mechanism or write
   "unconfirmed — reproduce first". "No defect" is a valid, reportable outcome; inventing a fix to
   look productive is not.
7. **Assert absence from a captured run.** When the point is that the artifact no longer says
   something, keep the whole run's output in a file, count the quoted phrase (zero is the proof) and
   read the block that was complained about in full. Looking at a screen and concluding is not
   verification, and a line truncated while inspecting it hides the clause under test.
8. **A phrase you know printed can match nothing in a wrapped capture.** Terminal and report captures
   break at a column, so flatten whitespace before matching (save the output, then `search_files` it)
   or match one distinctive word. `search_files` answers in one of two shapes — `{matches: [...]}` or
   `{matches_text: "..."}` — so read both keys before concluding "no hits", and drop narrowing filters
   when a filtered call looks empty while the unfiltered one had hits.
9. **Register items before code.** Where the repo keeps an item register, Phase 0 creates the items so
   every later commit can cite the one it closes; nothing in a report is silently dropped or silently
   merged into another item.
10. **One baseline-moving change per commit.** Batched, "which change moved the number" becomes
    unanswerable — and that is exactly what the next phase's "unchanged" rests on. A presentation-only
    change must prove it changed nothing: the byte-identical fingerprint in the commit message, not a
    passing suite (a suite proves you did not break what it covers, not that the world did not move).
    A presentation change that renumbers an identifier the owner also types (row numbers, menu
    indexes, ids) additionally needs a test that every index still resolves to the object it named —
    no fingerprint can see a silently re-aimed habit.
11. **Commit locally; a push is a separate, asked-for action.** Never amend or force-push a commit
    already on the remote — amend before the push, follow-up commit after. Before telling a user who
    pulls the branch himself that a commit is up, ask the remote
    (`git ls-remote origin refs/heads/main`), never your local `origin/main`.
12. **Report your own writes only after they exist.** "Registered", "fixed", "committed" about a
    document or commit that does not yet exist is the same unverified claim you refuse from a
    subagent, and worse because the owner acts on it. If you catch yourself having said it early,
    correct it plainly and then make the write.
13. **A subagent's summary is a self-report.** Verify with the project's own command and read the
    numbers off your own run.
14. **Owner decisions are lettered and recommended-first.** Numbered, options (a)/(b)/(c), the
    recommended one FIRST with a one-clause why, so a terse reply (`1a 2b`, `ok`) works. An
    open-ended prose question gets deferred and the work stalls on it.
15. **Never implement a task the plan marks as awaiting the owner's ruling**, and never let a child do
    it either — children cannot ask questions, so a ruling-shaped task gets silently decided. "Built
    in part, question left in writing" is a correct outcome when the honest scope cannot close an item.
16. **A review does not run the build gate.** Cite the last recorded measurement with its date,
    commit and provenance (which command produced it) and say plainly you did not re-run it — "the
    numbers are as of that commit" is the honest version. Run the gate when the task is a build or a
    verification.
17. **Do not paraphrase a README back at its owner** — that is what the README is for. Orientation
    is: what it is, how it is built, how the pieces relate, and what is not what the docs claim.
18. **A repo-wide recursive grep at the project root can hang** on a large build tree — use the
    ripgrep-backed `search_files` (it respects ignore files) or scope to the source/doc directories.
19. **Read the artifact's own command surface before scripting probes at it** (`--help`, the CLI's help
    command, the module's command table). A guessed subcommand fails as "no verb matches", which reads
    like a missing feature rather than a typo, and costs a round trip.
20. **Offer fixes as separate opt-in commits.** A review reports; the owner decides what is written
    back. Name the exact edits you would make if he says yes.
21. **Never weaken a gate, guard, fixture or threshold to make it pass.** Regenerate a frozen fixture
    from its versioned generator, rename a delivery identifier to something semantic, or report the
    shortfall inside the deliverable's own numbering. A loosened budget, a skipped test or a disabled
    lint un-proves every earlier green and is a carve-out the owner rules on, never a local decision.

## Mode A — orientation and progress review (read-only)

Two questions, one method: "what is this repo and how do the repos relate" and "how far along is it and
what remains" are both read-only recon ending in a verdict-first report. Pull the latest, measure,
report — no writes, no refactors, no heavy verification runs.

- **Report the drift, always, as its own section.** The highest-value finding is usually stale
  bookkeeping rather than missing design or missing code: a version stamp older than the items under
  it, a declared total that does not reconcile with the list it summarises, a README declaring a
  sibling "frozen" while commits postdate the freeze, an item open in one place and ruled in another.
- **Prove dependency direction from manifests and code, never prose:**
  `grep -rn "<sibling>" --include=Cargo.toml .`, `find . -path ./.git -prune -o -iname '*<sibling>*' -print`.
  A relative `path = "../../../<sibling>/packages/x"` is the strongest evidence available — it proves a
  live build-time dependency and the expected on-disk layout. An inverted dependency is the most
  useful sentence in the report.
- **Progress:** read the plan spine whole (later rulings amend steps in place, so a step is not simply
  started-or-not), count the open items programmatically, read the measured-state file and the newest
  milestone doc, and walk the risk register marking each risk retired / holding / untouched with the
  evidence behind it. Measure volume against the design's own eventual target where volume is the
  honest answer; for a deliberate thin slice that ratio, not a step count, is the truthful remainder.
- **Report orientation-shaped, not summary-shaped:** one line per repo for what it is, a short layout
  line each, then the relationship as numbered mechanisms (origin→normative, live code dependency,
  division of labour, interface object), then discrepancies and caveats last.

Full method, the counting traps, and pitfalls: `references/orientation-and-progress-review.md`.

## Mode B — a defect report becomes grounded fixes

Anchor every quoted symptom in the code before planning anything (`grep -rn "<the quoted phrase>"` —
one call turns "the screen contradicts itself" into a file, a function and a mechanism). Then classify
each finding, because the class decides whether code may change at all:

| class | test | what it gets |
| --- | --- | --- |
| **Defect** | the code does not do what the spec/design already says | fix it; the record is the commit message |
| **Behaviour choice** | the code does something the spec never specified | a registered item, ruled by the owner BEFORE any code |
| **Open design question** | the report establishes X, not proof of Y | an item on the register, left open |
| **Trade-off already accepted** | the cost was ruled on knowingly | nothing; do not relitigate |

Where the repo's rule is "code may not silently redefine the design", shipping a behaviour *choice* as
a bug fix is the cardinal sin — and it is the easiest mistake to make, because a choice and a defect
look identical from the outside. Ask for the artifacts you do not have rather than reconstructing
them; name the authority for every disagreement (the component that owns the state is right, the
renderers are wrong); repro before repair for anything numeric or timing-dependent. Answer "what does
it actually do?" from the code path with file:line, separating what exists today from what is designed
and unbuilt — both halves belong in the reply.

Procedure, evidence rules, plan shape and anti-patterns: `references/defect-triage.md`. The recurring
mechanisms most of these reports turn out to be: `references/recurring-bug-classes.md`.

## Mode C — executing a phased plan through subagents

One subagent per phase, **sequentially**, when the phases share state (a schema bump, a register, a
document, the gate's own measured numbers) — each phase's baseline IS the previous phase's output. The
parent owns the bundle, the verification and the deviation ledger; the child reads the plan itself so
the parent does not have to hold the code in its own context. Do not collapse the plan into one long
agent run of your own.

- **Baseline first:** record whatever the project re-derives in one command (test count, fingerprint,
  artifact hashes, the gate's summary line) before dispatching. Every child's "this changed nothing"
  is checked against it, and a claim you cannot re-derive is a claim you can only believe.
- **Write the bundle** from `templates/delegation-bundle.md`: repo + branch + exact push command, the
  plan's absolute path AND which phase, the project skill to load first, the baseline values, the hard
  rules, the commit protocol, the report format. Every value in FULL — an unexpanded `<placeholder>`
  in the goal text is refused by the dispatch call, and one that slips through inside an illustrative
  format gets written literally into a committed file by a literal-minded child.
- **Verify every phase yourself before building on it:** `git log --oneline -8`, `git status -sb`, the
  project's gate into a log file, then grep that log for the hash and test lines the child reported.
  Expect the gate green and the numbers reported; a presentation-only phase must show the PREVIOUS
  phase's fingerprints, a state-moving phase new ones and why.
- **Keep a deviation ledger.** Children hit anchors that moved and make choices the plan did not
  anticipate; log every deviation, every task left undone and every defect the child surfaced — they
  are the best bug-finders in the loop because they read the neighbours of the line you sent them to.
  Close the list in one pass at the end rather than interrupting the sequence.
- **Iteration-cap death is an unfinished phase, not a lost one** — usually gate-green in the working
  tree but never committed. Read the diff yourself, re-run the gate, and commit/push in a message
  saying the orchestrator finished it after the phase's child ran out; then dispatch the remainder as a
  fresh child with the same bundle.
- **Final pass:** on the real tree, re-run the full gate, walk the ledger, fix what is fixable, then
  exercise the artifact end to end and read the lines the report complained about in that output;
  recompute anything the children only asserted; sweep the docs for the vocabulary the round deleted
  (zero hits in the code with one hit in a doc is the shape — correct each with an amendment marker
  beside the claim, not by rewriting the history around it).
- **Sizing:** budget ~5-8 minutes and a few dozen API calls per plan task; the number that actually
  bites is the call count (~250 regardless of task count), so cap a multi-item phase at ~4 tasks AND
  make commit-per-item a hard rule of the bundle.
- **Loop discipline:** while a child runs, do not poll its transcript — end the turn with a one-line
  status and act on the result when it arrives. `action='steer'` a drifting child; `action='stop'` one
  that is out of scope, rather than letting it finish work you will have to revert.

Full procedure and pitfalls: `references/phased-execution.md`.

## Support files

- `references/orientation-and-progress-review.md` — Mode A: per-repo identity, dependency direction,
  progress counts and their traps, the drift section to always report.
- `references/defect-triage.md` — Mode B: procedure, classification, evidence rules, plan shape,
  anti-patterns.
- `references/recurring-bug-classes.md` — the recurring bug mechanisms (symptom → mechanism → where to
  look) that most defect reports resolve to; check these before reading broadly.
- `references/phased-execution.md` — Mode C: bundle contents, verification, iteration-cap recovery,
  the final pass, sizing, pitfalls.
- `templates/delegation-bundle.md` — the child's `context` block, with the notes that save a round trip.
