---
name: multi-repo-orientation
description: Use when asked what a repo is or how sibling repos relate.
---

# Multi-repo orientation

Use when the user asks "what is repo X", "summarize repos X and Y and how they relate", asks for orientation before work in a multi-repo program, or returns to a program after a gap. Separate repos in one program drift into describing each other inaccurately; the job is to report what is true now, not what the docs say about each other.

## Method

1. **Locate and enumerate.** Check the local clones first (`ls -la` on each candidate path) — the user works from checkouts, and doc paths in one repo often point at another repo's *author's* layout, not yours. Read each repo's `README.md` **and** its `AGENTS.md`/`CLAUDE.md` if present: these are written as routers and are the cheapest orientation in the tree.
2. **Establish identity per repo.**
   ```bash
   git remote -v
   git log --pretty='%h %ad %s' --date=short -10
   echo "files: $(git ls-files | wc -l)"
   ```
   Remotes may use per-repo SSH host aliases (`github-<repo>`), so do not assume a plain `github.com` origin means anything about ownership or grouping.
3. **Read the normative self-description**, if the repo keeps one: an ADR index, a spec index, a roadmap DAG, and the registers (`measurements`, `obligations`, `invariants`). That is where a repo states what it *is* as opposed to what it hopes; a design doc or whitepaper in a sibling repo is the weaker source.
4. **Prove the dependency direction from manifests and code — never from prose.**
   ```bash
   grep -rn "<sibling>" --include=Cargo.toml .
   grep -rn "<sibling>" --include=package.json .
   grep -rln "<sibling>" docs/ | head
   find . -path ./.git -prune -o -iname '*<sibling>*' -print
   ```
   Relative `path = "../../../<sibling>/packages/x"` entries are the strongest evidence available: they prove a live build-time dependency, and they tell you the expected on-disk sibling layout. A finding like "the research repo's spike crates depend on the implementation repo's packages" inverts the relationship the READMEs describe, and that inversion is the most useful sentence in the report.
5. **Check claim-versus-commit divergence.** A README or ADR that declares a sibling "frozen", "archived", or "nothing new is written there" is a statement of intent at a date. `git log` is the fact. If commits postdate the freeze, or the other repo's live roadmaps route work into it, report both and say which the program's own plans contradict. Do not silently repeat the ADR.
6. **Find the concrete interface objects.** Boundary codecs, fixture imports, and cited-by-path references (`<repo>:spikes/results/...`, `include_bytes!(".../<sibling>/fixtures/...")`) are where the relationship is mechanically enforced. One such artifact is worth more than a paragraph of description, and it also tells you which way data flows.
7. **Report orientation-shaped**, not summary-shaped: one line per repo for what it is; a short layout line each; then the relationship as numbered *mechanisms* (origin→normative, live code dependency, division of labour, interface object), then discrepancies and caveats last. Name the sibling explicitly in each mechanism rather than writing a joint narrative.

## Pitfalls

- **Never infer the relationship from doc prose.** Sibling descriptions are the least maintained text in any multi-repo program; manifests, fixture paths, and commit dates are the maintained ones. When they disagree, the disagreement is the finding.
- **A repo described as an archive may hold the newest commits.** Read `git log` dates before describing anything as historical, and before accepting an ADR's freeze claim.
- **The same repo appears under different names** — a docs nickname, a directory name, a GitHub name, and a wiki slug can all differ. Grep for the concept names, not just the repo name, when hunting for cross-references.
- **Doc paths are the author's machine layout.** Translate `/home/<user>/src/<program>/<repo>` style paths to the local checkout; do not report a path as broken when it is merely foreign.
- Do not paraphrase the README back at the user — that is what the README is for. Orientation is: what it is, how it is built, how the pieces relate, and what is not what the docs claim.

## Worked example

SilentSea (`starpath` = implementation monorepo, normative home for specs/ADRs/obligations/params; `mariner` = research record holding the v2.x design docs and the spike programme): the ADR said mariner was frozen, `git log` showed current source-opening work, and mariner's spike manifests carried `path = "../../../starpath/packages/..."` dependencies plus `include_bytes!` imports of starpath's frozen fixtures — so the two repos are mutually dependent, with measurements flowing mariner→starpath's registers and constants/code flowing starpath→mariner's spikes.
