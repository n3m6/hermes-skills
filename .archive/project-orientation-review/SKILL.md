---
name: project-orientation-review
description: "Use when asked what a repo is or how far a project is."
version: 1.0.0
author: Hermes Agent (curator)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [review, planning, status-reporting, orientation, repos]
    related_skills: [plan]
---

# Project and repo orientation review

Two questions, one method. "What is this repo, and how do the repos relate?" and "how far
along is this project, and what remains?" are both **read-only recon that ends in a
verdict-first report**. Pull the latest, measure, report — no writes, no refactors, and no
heavy verification runs unless the user asks for them.

## When to Use

- "What is repo X?" / "summarize repos X and Y and how they relate" — orientation before work
  in a multi-repo program, or after a gap away from one.
- "How far along is this project?" / "how much remains?" / "where do things stand against the
  requirements".
- A design or status review of a long-horizon project (a game design, an implementation
  roadmap, a milestone plan).
- A milestone, phase or plan document is about to close and something must say what it did and
  did not settle.

Not for: a build/verification task (that is the repo's own gate procedure), or writing the
plan itself (the `plan` skill).

## Rules that hold for every review

1. **Verdict first.** One short block — what is done and what is not, or what the thing is and
   how the pieces relate — then the detail. Never open with a methodology paragraph or a list
   of what you read.
2. **The facts come from the project's own files, never from memory or from doc prose.** "What
   remains" comes from the plan/roadmap read at HEAD, answered in ITS step numbers and item ids;
   what a repo *is* comes from its manifests, fixture paths and commit log, not from a sibling's
   README. A list reconstructed from memory is a plausible list that will not match the doc the
   owner checks it against.
3. **Never infer a relationship from prose.** Sibling descriptions are the least maintained
   text in any multi-repo program; manifests, relative `path =` dependencies, fixture imports
   and commit dates are the maintained ones. When they disagree, the disagreement is the finding.
4. **Report the drift, always, as its own section.** The highest-value finding is usually stale
   bookkeeping rather than missing design or missing code: a version stamp older than the items
   under it, a declared total that does not reconcile with the list it summarises, a README that
   declares a sibling "frozen" while commits postdate the freeze, an item still tagged open in
   one place and ruled in another, a measured number quoted from a skill or a memory instead of
   re-read from the code.
5. **Label the axes and never blend them.** Declared (decided / drafted / described) versus
   measured (what a command actually produced) are different axes — say which one every figure
   came from. A tag census (`[DECIDED]`/`[PROPOSED]`/`[OPEN]`) is a shape, not a percentage.
6. **Separate the kinds of "open".** Undecided is not decided-but-unbuilt, which is not
   built-and-awaiting-the-owner's-word. A count that lumps them misstates what is left — the
   second and third kinds are cheap.
7. **Do not run the build gate or re-derive hashes for a review.** Cite the last recorded
   measurement with its date, commit and provenance (which command produced it) and say plainly
   that you did not re-run it. Adding "the numbers are as of that commit" is the honest version.
   Run the gate when the task is a build or a verification.
8. **Offer fixes as separate opt-in commits.** The review reports; the owner decides what is
   written back. Name the exact edits you would make if he says yes.

## Progress review: how far along, what remains

**Procedure.**
1. Pull the repo; note the commit you are measuring.
2. Read the plan spine whole, amendments included — later rulings amend steps in place, so a
   step's state is not simply started-or-not.
3. Count the open items programmatically; never trust a declared total.
4. Read the measured-state file and its placeholder list, and the newest milestone/plan
   document (which carries which sub-phases landed and which human step is still owed).
5. Measure volume where volume is the honest answer: content/data counts against the design's
   own eventual target. For a deliberate thin slice that ratio, not a step count, is the
   truthful "how much remains".
6. Walk the risk register, marking each risk retired / holding / untouched with the evidence
   behind it (a stored fixture, an ignored matrix run, an adopted threshold). "Which risks are
   still naked" is the answer to the question behind the question.
7. Write it in that order: verdict, requirements side, build side, remaining work in the plan's
   own order, risk ledger, drift found, the one human step owed.

**Counting a tracking doc — the traps.**
- Declared totals drift; re-derive them (count list-section lines by the doc's own convention).
- Items recorded as their own `## <title> (<ID>)` heading are NOT in the list — scan those
  headings separately and reconcile the two sets before quoting any number; a prefix-only scan
  silently undercounts the open set.
- Classify each item by the markers in its body (built / ruled / deferred / bare) and bucket by
  owning section via the doc's index table, so the report names subsystems, not a flat count.
- Header stamps, version numbers and char counts rot (a header can be a day older than the
  newest item under it); re-read them, never cite them as current.

*Worked home:* the owner's game-design repo WWX: Shadow Wars (register
`docs/design/00-open-questions.md`, build order `16.3` and risk register `16.4` in
`docs/design/16-production-scope-risks.md`, measured state `docs/status.md`). Its own count
conventions, the permanent `W-` item ids and why a design review does not run the gate live in
the `wwx-shadow-wars` skill — read them there, do not infer them here.

## Multi-repo orientation: what each repo is, how they relate

**Method.**
1. **Locate and enumerate.** Check the local clones first (`ls -la` on each candidate path) —
   doc paths in one repo often point at another repo's *author's* layout, not yours. Read each
   repo's `README.md` **and** its `AGENTS.md`/`CLAUDE.md` if present: these are written as
   routers and are the cheapest orientation in the tree.
2. **Establish identity per repo:** `git remote -v`,
   `git log --pretty='%h %ad %s' --date=short -10`, file count. Remotes may use per-repo SSH
   host aliases (`github-<repo>`), so a plain `github.com` origin says nothing about ownership
   or grouping.
3. **Read the normative self-description** if the repo keeps one — an ADR index, a spec index, a
   roadmap DAG, the registers (`measurements`, `obligations`, `invariants`). That is what the
   repo says it *is*; a design doc or whitepaper in a sibling is the weaker source.
4. **Prove dependency direction from manifests and code, never from prose:**
   `grep -rn "<sibling>" --include=Cargo.toml .` / `--include=package.json`, and
   `find . -path ./.git -prune -o -iname '*<sibling>*' -print`. A relative
   `path = "../../../<sibling>/packages/x"` is the strongest evidence available — it proves a
   live build-time dependency and tells you the expected on-disk layout. An inverted dependency
   ("the research repo's spikes depend on the implementation repo's packages") is the most
   useful sentence in the report.
5. **Check claim-versus-commit divergence.** A README/ADR declaring a sibling "frozen" or
   "archived" is intent at a date; `git log` is the fact. If commits postdate the freeze, or the
   other repo's live roadmaps route work into it, report both and say which the program's own
   plans contradict — do not silently repeat the ADR.
6. **Find the concrete interface objects** — boundary codecs, fixture imports, cited-by-path
   references (`<repo>:spikes/results/...`, `include_bytes!(".../<sibling>/fixtures/...")`).
   One such artifact beats a paragraph of description and tells you which way data flows.
7. **Report orientation-shaped, not summary-shaped:** one line per repo for what it is, a short
   layout line each, then the relationship as numbered *mechanisms* (origin→normative, live code
   dependency, division of labour, interface object), then discrepancies and caveats last. Name
   the sibling explicitly in each mechanism rather than writing a joint narrative.

**Pitfalls.**
- A repo described as an archive may hold the newest commits — read `git log` dates before
  calling anything historical, and before accepting an ADR's freeze claim.
- The same repo appears under different names — a docs nickname, a directory name, a GitHub
  name, a wiki slug can all differ. Grep the concept names, not just the repo name, when hunting
  cross-references.
- Doc paths are the author's machine layout — translate `/home/<user>/src/<program>/<repo>` to
  the local checkout rather than reporting a foreign path as broken.
- Do not paraphrase the README back at the owner — that is what the README is for. Orientation
  is: what it is, how it is built, how the pieces relate, and what is not what the docs claim.

*Worked home:* SilentSea — `starpath` (implementation monorepo, normative home for
specs/ADRs/obligations/params) and `mariner` (research record holding the v2.x design docs and
the spike programme): the ADR said mariner was frozen, `git log` showed current work, and
mariner's spike manifests carried `path = "../../../starpath/packages/..."` dependencies plus
`include_bytes!` imports of starpath's fixtures — so the two repos are mutually dependent, with
measurements flowing mariner→starpath's registers and code/constants flowing starpath→mariner.
