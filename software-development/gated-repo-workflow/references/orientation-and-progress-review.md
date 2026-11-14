# Orientation and progress review — method and traps (Mode A)

Read-only recon that ends in a verdict-first report. Detail for the two questions: "what is this repo
and how do the repos relate", and "how far along is this project and what remains".

## Progress review: procedure

1. Pull the repo; note the commit you are measuring.
2. Read the plan spine whole, amendments included — later rulings amend steps in place, so a step's
   state is not simply started-or-not.
3. Count the open items programmatically; never trust a declared total.
4. Read the measured-state file and its placeholder list, and the newest milestone/plan document
   (which carries which sub-phases landed and which human step is still owed).
5. Measure volume where volume is the honest answer: content/data counts against the design's own
   eventual target. For a deliberate thin slice that ratio, not a step count, is the truthful "how
   much remains".
6. Walk the risk register, marking each risk retired / holding / untouched with the evidence behind
   it (a stored fixture, an ignored matrix run, an adopted threshold). "Which risks are still naked"
   is the answer to the question behind the question.
7. Write it in that order: verdict, requirements side, build side, remaining work in the plan's own
   order, risk ledger, drift found, the one human step owed.

### Counting a tracking doc — the traps

- Declared totals drift; re-derive them (count list-section lines by the doc's own convention).
- Items recorded as their own `## <title> (<ID>)` heading are NOT in the list — scan those headings
  separately and reconcile the two sets before quoting any number; a prefix-only scan silently
  undercounts the open set.
- Classify each item by the markers in its body (built / ruled / deferred / bare) and bucket by
  owning section via the doc's index table, so the report names subsystems, not a flat count.
- Header stamps, version numbers and char counts rot — re-read them, never cite them as current.

## Multi-repo orientation: method

1. **Locate and enumerate.** Check the local clones first (`ls -la` on each candidate path) — doc
   paths in one repo often point at another repo's *author's* layout, not yours. Read each repo's
   `README.md` **and** its `AGENTS.md`/`CLAUDE.md` if present: these are written as routers and are
   the cheapest orientation in the tree.
2. **Establish identity per repo:** `git remote -v`,
   `git log --pretty='%h %ad %s' --date=short -10`, file count. Remotes may use per-repo SSH host
   aliases (`github-<repo>`), so a plain `github.com` origin says nothing about ownership or grouping.
3. **Read the normative self-description** if the repo keeps one — an ADR index, a spec index, a
   roadmap DAG, the registers (`measurements`, `obligations`, `invariants`). That is what the repo
   says it *is*; a design doc or whitepaper in a sibling is the weaker source.
4. **Prove dependency direction from manifests and code, never from prose:**
   `grep -rn "<sibling>" --include=Cargo.toml .` / `--include=package.json`, and
   `find . -path ./.git -prune -o -iname '*<sibling>*' -print`. A relative
   `path = "../../../<sibling>/packages/x"` is the strongest evidence available — it proves a live
   build-time dependency and tells you the expected on-disk layout. An inverted dependency ("the
   research repo's spikes depend on the implementation repo's packages") is the most useful sentence
   in the report.
5. **Check claim-versus-commit divergence.** A README/ADR declaring a sibling "frozen" or "archived"
   is intent at a date; `git log` is the fact. If commits postdate the freeze, or the other repo's
   live roadmaps route work into it, report both and say which the program's own plans contradict —
   do not silently repeat the ADR.
6. **Find the concrete interface objects** — boundary codecs, fixture imports, cited-by-path
   references (`<repo>:spikes/results/...`, `include_bytes!(".../<sibling>/fixtures/...")`). One such
   artifact beats a paragraph of description and tells you which way data flows.
7. **Report orientation-shaped, not summary-shaped:** one line per repo for what it is, a short layout
   line each, then the relationship as numbered *mechanisms* (origin→normative, live code dependency,
   division of labour, interface object), then discrepancies and caveats last. Name the sibling
   explicitly in each mechanism rather than writing a joint narrative.

## Pitfalls

- A repo described as an archive may hold the newest commits — read `git log` dates before calling
  anything historical, and before accepting an ADR's freeze claim.
- The same repo appears under different names — a docs nickname, a directory name, a GitHub name, a
  wiki slug can all differ. Grep the concept names, not just the repo name, when hunting
  cross-references.
- Doc paths are the author's machine layout — translate `/home/<user>/src/<program>/<repo>` to the
  local checkout rather than reporting a foreign path as broken.
- Do not paraphrase the README back at the owner — that is what the README is for.
- A milestone, phase or plan document that is about to close needs something that says what it did and
  did not settle; a review reports and offers fixes as separate opt-in commits, never writes them in.
