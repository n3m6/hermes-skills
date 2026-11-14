---
name: gated-rust-workspace
description: "Use when building a multi-crate Rust workspace with gates."
version: 1.2.0
author: Hermes Agent (curator)
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [rust, cargo, determinism, ci, workspace]
    related_skills: [gated-repo-workflow, starpath]
---

# Gated Rust workspaces

For repos where a wrong-but-compiling change must be caught by the build: a
simulation core that has to be bit-reproducible, a dependency budget, an ordered
phase table, a wire format. The user's Rust projects (starpath, mariner, wwx) all
have this shape. Worked example: `~/repos/wwx` — seven crates, a dependency-free
core, five guards and one gate script.

**The governing idea: a rule that matters gets a lint, a type, a test or a shell
guard — never a comment.** Every rule below exists because "we'll be careful" does
not survive a year of agent-written code.

## When to Use

- Building or extending a multi-crate Rust workspace where a wrong-but-compiling change must be caught by
  the build: a dependency budget, a bit-reproducible simulation core, an ordered phase table, a wire
  format.
- Adding a mechanic through every layer of such a workspace, or writing the guards, gate script and CI
  that hold its rules.
- Hitting a build or gate failure in one of these repos: a clippy lint under `-D warnings`, a
  borrow-checker error, a frozen fixture that moved, a determinism or dependency guard that fired.
- Answering "what happens when…" about a mechanic — from a captured run plus the code, never from the
  design docs.

Not for: reviewing or triaging a gated repo without build work (`gated-repo-workflow`), or a specific
repo's own validation and CI triage (`starpath`).

The cross-cutting discipline — verdict-first reporting, facts from the tree at HEAD, word boundaries
before claiming absence, commit-locally/push-separately, lettered owner decisions, never weakening a
gate — is `gated-repo-workflow`; apply it as written rather than re-deriving it here. What follows is
what a Rust workspace adds to it.

## Order of work

1. **Skeleton first, deepest crate first.** Workspace `Cargo.toml` with
   `[workspace.dependencies]`, `rust-toolchain.toml` pinning the channel, then the
   leaf crate (`core`), then the mid crates, then the edge crates (cli, server).
   Build after each crate lands, not at the end.
2. **Prove the registry is reachable before planning around crates.io:**
   `cargo new --lib /tmp/nettest && cargo add serde_json --manifest-path /tmp/nettest/Cargo.toml && cargo build --manifest-path /tmp/nettest/Cargo.toml`.
   A 403 on `crates.io` with a 200 on the index is normal; the fetch is what matters.
3. **Write the guards before the code they protect.** A guard added afterwards is a
   guard that has already been violated somewhere unlooked-at.
4. **Run the real thing, then document it.** `cargo build`, `cargo test`,
   `cargo clippy --workspace --all-targets -- -D warnings`, `cargo fmt --all`, and
   the binary itself. Docs are written from that output — never from intent. Then
   **read a full run's output end to end**, not just the green test summary: a screen
   dated from a lagging source, an ending printed before the screen it summarises, a
   menu offering choices the world refuses, and an advance overshooting the end are
   all invisible to assertions and obvious to a reader. Every number a doc or commit
   message quotes is copied from that output or read back out of the artifact file.
   - **Answer "what happens when…" questions from a captured run plus the code, never
     from the design docs.** Dump the run's records to a file (the CLI's `--ledger`
     style flag) and the terminal output to another, grep them for the exact detail
     strings the mechanic would write, and *count*. That is how you find a described
     path that never fires (an unpayable bill, a loss the docs promise) instead of
     describing the intent as if it were the behaviour.
   - **After a rule change, grep every doc that quotes a measured number** —
     fingerprints, hashes, percentages, test counts, line counts. One artifact moves
     for the change you made and another moves for a reason you were not looking at,
     and both are now wrong in three files.
5. **Gate script, then CI that calls the gate script.** No second list of steps.
6. **Commit with a structured message; stop there unless asked to push.** The
   standing instruction on these repos is *commit locally, do not push* (rule 11 of `gated-repo-workflow`) — a push is a
   separate, explicit request. Read the task's own wording first: when it says to leave
   the change in the working tree for review, that is *stricter* than the default and
   means no commit either. Equally, when the task approves a numbered plan of stages, that
   approval covers every stage to the end — gate, commit, and the push when one is asked for;
   stopping between stages to ask whether to continue is friction the plan already answered,
   so stop only at a milestone the plan itself names as a stopping point. Before reporting, run `git status` and reconcile it against
   what you believe you did — an edit under a path the task protects (a design doc, a
   vendored file) is reverted (`git checkout -- <path>` after saving the diff to the
   scratch dir) and reported with its content, never left in place. When it is asked for, check the remote is a
   fast-forward first (`git ls-remote origin`). Re-read `origin/main` before claiming
   "ahead N": a sibling agent or the owner can move it mid-session.
   - **Know where the artifact is actually run.** The owner works on his *own*
     machine and cannot see the lab host, so an unpushed fix is an undelivered fix:
     "run it from my tree" is not an instruction he can follow. When he is blocked on
     something and the block turns out to be a bug in what you just shipped, fix it,
     push it, and tell him to pull — that is the same request, not a new one. Never
     rewrite a commit that has already been pushed; a fix on top is a new commit.

## The guards

Implementations to copy: `references/guards.md`. Stored golden fixtures, and the gate
step that replays them: `references/stored-fixtures.md`. When a mechanic carries a
recurring bill, the failure path and the order the money is spent in — which is a
mechanic, not an implementation detail — are in `references/paid-commitments.md`.

| Rule to protect | Guard |
| --- | --- |
| The core stays dependency-free | `tools/check-deps.sh` greps its manifest; CI fails on any dependency |
| No floats, no hash-ordered maps, no clock, no IO in the sim | `tools/check-determinism.sh` greps the crate's sources, plus `clippy::float_arithmetic` denied |
| Layer boundaries | A test that **parses every `Cargo.toml`** against an explicit allowed-dependency table and names the offending crate |
| An ordered phase table cannot be reordered carelessly | A runtime contract guard: a phase sees only the stores it declares, and a store an earlier phase **read without writing** cannot be mutated later in the tick |
| The whole thing still works | `tools/gate.sh` — format check, clippy at `-D warnings`, the guards, tests, validation, one full end-to-end run |

Two properties worth copying: the gate script is the *only* definition of "passing"
(`.github/workflows/ci.yml` runs `bash tools/gate.sh` and nothing else), and the
allowed-dependency table lives in the test — docs summarise it, never duplicate it.

## Scaffolding workflow that works

Generate a workspace's files in batches from a Python script rather than hand-writing them one tool call
at a time — the script template, the match-count discipline and the nested-JSON anchoring trap are in
`references/scaffolding-workflow.md`. The rules that hold: **run the generator, then patch what it
generated** (an edit against a path the script has not created yet fails with `Failed to read file`);
**every replacement verifies its match count** and prints a failure rather than silently doing nothing;
and the real bugs surface at `cargo build` / `cargo test` — that pass is part of the deliverable, not an
interruption.

## Adding a mechanic through every layer

A workspace of this shape is one straight line — content → session → core ← projection ← protocol →
cli — and a new mechanic travels it in one direction; work from the inside out and the tree compiles at
every step. Full sweep (the four-places problem for an authored value, the store checklist, the
version-bump list): `references/adding-a-mechanic.md`.

Rules that hold every time:

- **Types first, then the boundary, then the test.** Types and the monthly pass as its own module in the
  systems directory, registered from the phase that already owns the subject; then the wire DTO and every
  version bump; then a negative control — the same world *without* the mechanic produces none of its
  effects, or the test cannot tell the mechanic apart from something else doing it.
- **A mechanic is a pass inside a phase, never a new row in the ordered phase table.** The table is the
  tick order, and its contract guard is what keeps each phase's reads and writes legal.
- **Sweep every extension point in one pass** — the RNG purpose enum, the balance struct, the ledger
  kinds, the belief provenance, the context and config structs, the state-hash tag — because each is a
  place the compiler will otherwise find later.
- **One authored value lands in four places and the compiler only names three.** Miss the validator's
  authored-vs-chosen list and the *runtime* content check fails; miss the session's mapping and it does
  not compile; and the new value moves the content fingerprint even though no rule moved.
- **Content is often already authored for the mechanic you are about to build** — an applier's "unbuilt
  effect" arm is the project's own list of mechanics the data model promises and the code has not
  delivered.
- **A precondition the design's data model cannot express is a question for the owner, not a local
  decision**, and a design statement the build falsifies is a finding to register — not something to
  code around.
- **Search the test tree for the config literal before running** (`search_files`, or `grep -rn "Config {"`).
  One new field on the shared config or
  context breaks every hand-built fixture; asking whether the value belongs to an entity or to the world
  is what avoids that cost in the first place.
- **Draws: append, never insert or renumber** (purposes are permanent ids keyed into every stored
  stream), draw only when the mechanic is live, derive the draw's entity from what the draw is about,
  and let an ordered map give you the ordering.

## Interface legibility (often the actual deliverable)

The definition of done usually includes *a human can tell what happened and why*. That is a build
requirement, not polish. Full cases, worked numbers and the catalogue/fog detail:
`references/interface-legibility.md`.

- **A renderer with a cap silently drops the rest.** Find where the interface slices the list, and
  prove visibility from a captured run — never by reading the code path that writes the record.
- **The interface must be able to answer "why".** Give a coerced outcome its own value, or a reason
  carried beside the state at the moment it is written; and publish the rule's own verdict (a read-only
  core function sharing the constants the world itself tests) instead of recomputing the rule in the
  projection, which drifts. Show preconditions, never a guess the draw may contradict.
- **A screen may only read what the observer is entitled to know.** Reading the world store from a
  display path is a fog leak through the interface; read the belief store, render an unheld reading as
  unknown, and give any judgement resting on it a third answer — "cannot say yet".
- **If no channel produces the reading the screen needs, the missing channel is a mechanic, not a
  display bug** — fill it with a registered producer, never from the world store.
- **A filter that is too tight reads as a rule.** Probe the engine by hand before writing a design
  story: if the world records the command, the defect is in the interface's catalogue.
- **A new block prints when it is the news of the interval just run**, with a reprint command and a
  self-stated age; where a draw resolves the mechanic, say outright it cannot separate preparation from
  luck, and drop any estimate the model does not support.

## Documents the repo owes itself

- `AGENTS.md` at the root as a **router** (what to read for which task), plus one
  short `AGENTS.md` per crate: what it is, its rules, its commands, what is stubbed.
- `docs/status.md` carries the **measured** state (test count, hashes, gate output)
  and an explicit "what is a deliberate placeholder" list. Keep the counts there and
  nowhere else: duplicated numbers in an always-loaded skill go stale and then
  contradict the code.
- **The definition-of-done test file is also the build's remaining-work list.** Where
  the suite pins an absence (see the section below), those tests name exactly what is
  left to build. To locate where a sliced build actually stands, read four things
  before planning anything: `docs/status.md`, the build brief, the acceptance test
  file, and the design's deliverable-order section. Grep for the `count == 0`
  assertions — they are a to-do list the project maintains for you.
- A section for invented mechanisms. Where the code needed a rule nobody decided, the
  doc names it as invented and asks for sign-off. **Never present an invented
  mechanism as designed.**
- The framing that makes the docs useful: the repo can be wrong about its domain and
  still be correct about itself.

## Acceptance you cannot meet yet

A definition of done written before the code exists will contain items the current
build cannot reach. Do not quietly narrow them, and do not skip them:

- **Assert the absence, and make the absence fail loudly.** Write the test so it
  asserts what *is* true plus the count that must be zero, with a comment naming what
  would have to exist for the real item to hold and saying the test must be replaced
  the day it lands. A `count == 0` assertion is a live tripwire; a skipped test is a
  hole that reads as coverage.
- **Assert the reachable half with a difference, not a shrug.** Where a criterion has
  a strict form and a weak form, assert the weak one *and* the distinguishing fact
  (losses of your own > 0, losses by an opponent == 0), so the gap between them is
  stated in the test rather than left for a reader to notice.
- **Report the shortfall inside the deliverable's own numbering.** Say which numbered
  items hold and which do not — in the test, in `docs/status.md`, and in the final
  message. "All tests pass" while a numbered item is unreachable is the failure mode
  this rule exists to prevent.
- **When the design pairs a machine half with a human half** (questions only the owner
  can answer, a verdict only a person can give), print them at the end of the run and
  hand the owner the exact command that plays it. The decisions *you* need while
  building go to him the same way: numbered, options lettered (a)/(b)/(c), the
  recommended one FIRST and carrying a one-clause why, so a terse reply works
  (`1a 2b`, `ok`). He answers in bulk and terse, so an open-ended prose question gets
  deferred and the build stalls on it; a lettered one gets answered in one line.

## Traps

Rust/cargo/clippy and file-editing traps that cost a build round-trip — `E0502`/`E0592`, a
`-D warnings` failure on code that reads fine, `cargo fmt` moving your patch anchors, the write-time
lint lie: `references/tooling-traps.md`. Traps that are about *behaviour* rather than a build — stock
thresholds, guard width, tick/phase and store contracts, fixture arithmetic, CLI buffering, seed
searching: `references/simulation-traps.md`. These four hold everywhere:

- **Do not add a second validator, a second gate, or a second architecture check.**
  One implementation, run by CI, by a human and by an agent, or the definitions of
  "valid" and "passing" start to differ.
- **The allowed-dependency table is a budget, not an obstacle.** Adding a dependency to
  a crate the table does not list fails a test that names the crate and the dependency.
  Check the table before adding one; the intended fix is usually to build on what the
  crate may already name — a CLI allowed `serde_json` but not `serde` writes its file
  format by hand over `serde_json::Value`, which reads better at a failure than a derive
  would anyway. Widening the table to fit code you just wrote is the wrong direction.
- **Label a screen from the authoritative clock, not from a derived projection.** A
  view that carries "values as of the last tick" lags the sim, so reading a date off it
  printed a month's dispatch under the previous month's date. Take time from the
  session or sim clock and compute calendar labels there.
- **A finished background run reports the tree as it was when it started.** A
  build/test notification can arrive after the error it names was already fixed;
  confirm against the current tree, or re-run the check, before telling the user
  something failed.
