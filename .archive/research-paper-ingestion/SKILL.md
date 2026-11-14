---
name: research-paper-ingestion
description: "Verify, fetch, convert, and file academic papers into a knowledge base (arXiv-focused)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Research, Arxiv, Papers, Ingestion, Verification, Knowledge-Base, Wiki]
    category: research
    related_skills: [arxiv, llm-wiki, grounded-citations, ocr-and-documents]
---

# Research Paper Ingestion

End-to-end pipeline for bringing an academic paper (arXiv or other) into a
knowledge base / wiki: **verify → fetch full text → convert → extract →
file → lint**. The verification step comes FIRST and is non-negotiable: this
skill exists because of a session where a paper was recommended from memory
("Data Infiltration: Poisoning Wikipedia…") and turned out to be unverifiable
after 10+ searches — no arXiv entry, no Semantic Scholar record, no web trace.

## When This Skill Activates

- User says "ingest this paper" / "add this paper to the wiki" / "read this paper"
- User provides a citation (title + authors + venue) that must be located
- Agent is about to recommend papers from memory for a KB — VERIFY FIRST
- Any full-text arXiv fetch that will be saved as a source document

## Step 0 — VERIFY the source exists (before fetching anything)

Never ingest — or recommend — a paper from memory. A citation (title, authors,
venue) is a *hypothesis*, not a fact. Verify with the arXiv API:

```python
# Title/author search (Atom XML):
curl "https://export.arxiv.org/api/query?search_query=ti:%22Exact+Title%22&max_results=5"
# By ID:
curl "https://export.arxiv.org/api/query?id_list=2302.10149"
# Parse with xml.etree; ns = {'a': 'http://www.w3.org/2005/Atom'}
```

**id_list verification gotchas (all hit in one session):**
- **Version-suffix trap:** the Atom `<id>` element is
  `http://arxiv.org/abs/2211.09110v3` — strip the trailing `v\d+` before
  matching against your ID list, or EVERY id_list lookup "fails" with a naive
  `split('/abs/')[-1]`.
- **Title-match, don't just presence-check.** A misremembered ID frequently
  resolves to a DIFFERENT real paper (session data point: 4 of 27 remembered
  IDs — OpenCompass, a GSM8K re-examination paper, Anthropic's Simple
  Benchmarks, a frontier-evals paper — pointed at unrelated astronomy and
  software-architecture papers). A wrong ID that returns 200 is the silent
  failure mode: verify the returned TITLE matches expectations, not merely
  that an entry exists.
- **Bulk-verify a candidate canon in one call:** `id_list=2211.09110,2009.03300,...`
  (comma-separated), then print id → title → date per entry. Cheaper than N
  searches and produces a compact table that makes mismatches obvious.
- **Software entities (harnesses, benchmark suites, tooling) live on GitHub,
  not arXiv:** verify repos via `https://api.github.com/repos/{owner}/{repo}`
  (description, stars, created_at; JSON `message` field on failures).
  Unauthenticated works for a handful of lookups.

Search patterns that work well:
- `ti:"exact phrase"` — title search (use quotes for multi-word titles)
- `au:LastName AND abs:keyword` — author + abstract keyword
- `all:"exact phrase"` — full-record search; good for distinctive phrases
- Try the plain arXiv full-text search UI as a second pass:
  `curl "https://arxiv.org/search/?searchtype=all&query=%22phrase%22" -H "User-Agent: Mozilla/5.0" | grep -oP 'arxiv\.org/abs/[0-9.]+' | sort -u`

**If the paper cannot be verified anywhere (arXiv API, arXiv full-text search,
Semantic Scholar, web search):**
1. **Do NOT fabricate content or ingest from memory.** A wiki's value is
   traceability; an unverifiable citation silently breaks that contract.
2. Substitute a VERIFIED paper covering the same ground if one exists.
3. Record the unverified citation in the KB's `log.md` with a note.
4. Flag it on the relevant page (e.g. "could not be verified on arXiv — any
   claims from it are unverified").

Also verify user-provided venue claims when cheap (e.g. "ICLR 2026") — one web
search usually confirms or denies; record the confirmation in the log.

## Step 1 — Fetch full text

Preferred: `https://arxiv.org/html/{id}` (clean, structured). Not all papers
have a native HTML version (older ones 404) — **before settling for
abstract-only, try the ar5iv mirror `https://ar5iv.labs.arxiv.org/html/{id}`**,
which renders full text from the LaTeX source for nearly any paper with a
source tarball (session: HELM 2022 and MMLU 2020 both captured at full length
via ar5iv). Probe candidates with
`curl -sL -o /dev/null -w "%{http_code}" <url>` and take the first that
returns 200. Last resort: the abs page (`https://arxiv.org/abs/{id}`) for
abstract-level capture; note the fallback in the log.

**Stub detection (hit repeatedly — scan the WHOLE document, not the
head):** both arXiv native HTML and ar5iv can return *plausible-looking
stub pages* instead of 404s — arXiv prints `No HTML for '<id>'`, ar5iv
prints `Untitled Document` / `Conversion to HTML had a Fatal error and
exited abruptly` (some LaTeX sources break the converter). Stubs are large
enough to pass naive `len(raw) > 5000` checks, AND the visible marker can
sit past byte 3000 of the raw HTML (the stub's <head> is full of script/
style boilerplate). A "first ~500 chars of content" check silently passes
them — session: InterCode 2306.14898 and RepoBench 2306.03091 were both
saved as 15-line stubs that way and had to be re-captured. Reject by
scanning the FULL raw document AND the converted body (lowercased) for
`no html for`, `fatal error`, `untitled document`, and additionally require
the converted body to have real bulk (>~30 lines) before accepting.

**PDF fallback (when HTML and ar5iv both fail):** `arxiv.org/pdf/{id}` +
pypdf text extraction. On PEP 668 hosts use a throwaway venv:
`python3 -m venv /tmp/pdfvenv && /tmp/pdfvenv/bin/pip -q install pypdf`,
extract per page, join. This recovered the SWE-agent paper (2405.15793)
after native HTML and ar5iv both failed; the source_url then points at the
PDF.

**web_extract may be configured search-only** (e.g. DuckDuckGo backend — it
errors on any URL fetch). Don't build the pipeline on it: the curl +
stdlib `html.parser` converter in `scripts/fetch_arxiv.py` is the
dependency-free path for HTML, pypdf covers PDFs.

**Bot-blocked non-arXiv pages** (e.g. openai.com sits behind Cloudflare and
blocks BOTH curl and the browser): fetch via the r.jina.ai text proxy —
`curl -sL "https://r.jina.ai/<full-url>"` — which returns markdown. Strip
the leading `Title:` / `URL Source:` / `Markdown Content:` header lines
before saving (session: the SWE-bench Verified blog was captured this way
into `raw/articles/`). Verify the URL exists via web_search first — the
proxy follows redirects silently, so a 200 can mask a moved page. **If a
known blog/post URL 404s, search for an arXiv version of the same work**
(session: METR's "Measuring AI Ability to Complete Long Tasks" blog URL
was dead; the identical paper was arXiv:2503.14499).

**Live leaderboards / JS-rendered data (hit repeatedly):** leaderboard
sites (swebench.com, tbench.ai, frontierswe.com) render their tables
client-side — curl AND the r.jina.ai proxy return prose/nav only, with
NO table rows. Capture with the real browser: `browser_navigate` then
`browser_console` with
`[...document.querySelectorAll('table tbody tr')].map(r => [...r.querySelectorAll('td')].map(c => c.innerText.trim()).join(' | '))`.
Gotchas: (a) swebench.com/verified is prose-only — the table lives on the
main leaderboard page (swebench.com/); (b) filter dropdowns are native
`<select>`s — switch views by setting `select.value` and dispatching
`new Event('change', {bubbles:true})`, then re-extract after ~3s
(switching "mini-SWE-agent" → "All agents" revealed the product-level
entries); (c) rows carry their own submission dates — leaderboard data
lags the capture date; record both. Save snapshots as NEW dated raw
articles (raw/ is immutable — never overwrite an earlier snapshot; name
e.g. `swebench-verified-leaderboard-2026-08-09.md`), stamp the real
sha256 immediately (no placeholder hashes), and list the source in the
KB's WATCHLIST with a refresh cadence. Re-capturing an unchanged
leaderboard is a verification pass, not a new snapshot.

**GitHub / code-entity capture (default branch ≠ main — hit twice):** for
READMEs of software entities, `raw.githubusercontent.com/{owner}/{repo}/main/README.md`
can 404 when the default branch is `dev`/`master` (session: anomalyco/opencode
uses `dev`). Resolve first:
`curl -s https://api.github.com/repos/{owner}/{repo}` → `default_branch`,
and grab `stargazers_count`/`created_at`/`description` in the same call for
the entity page. Save READMEs verbatim (they're already markdown) into
`raw/articles/`. **Product-site capture:** JS-heavy marketing sites
(pi.dev-style, Next.js) still server-render real content — convert the HTML
like any other page, but require the CONVERTED body ≥~2000 chars or it's a
JS shell; extract the `<title>` and meta description, and grep the raw HTML
for `github.com/...` links to find the canonical repo.

**Rate limits:** arXiv ~1 req/3s; Semantic Scholar 429s hard at ~1 req/s
without a key — retry with backoff or skip S2 entirely (arXiv API + web
search is usually enough). Rapid back-to-back batches eventually return
empty XML (parse error `no element found`) — pace queries with `sleep(2)`
or split the list.

## Step 2 — Convert HTML → markdown

`web_extract` may not handle arxiv.org/html pages well; a stdlib converter
works. See `scripts/fetch_arxiv.py` for the full implementation. Key points:

- Strip `<script>/<style>`, convert headings/paragraphs/links/bold/italic
- **CRITICAL ToC gotcha:** arXiv HTML ToCs contain links in TWO forms —
  `[text](https://arxiv.org/html/...)` AND `[text](#S4.SS3)` anchor links.
  A strip regex that only matches the URL form leaves anchor-link lines in
  the body, which then pollute section extraction (every section search hits
  the ToC first). Strip BOTH forms:
  ```python
  lines = [l for l in lines if not re.match(r'^\s*\[[^\]]+\]\([^)]*#?S?\d', l)
           and not re.match(r'^\s*\[[^\]]+\]\(https://arxiv\.org/html/', l)]
  ```
- Save with raw frontmatter: `source_url`, `ingested: YYYY-MM-DD`,
  `sha256:` of the body (everything after the closing `---`). sha256 enables
  drift detection on re-ingest.
- **sha256 drift gotcha (hit on a PDF capture):** the wiki lint computes the
  hash over the exact bytes AFTER the closing `---\n` (its regex is
  `^---\n(.*?)\n---\n`), so a body that starts with a stray `\n` hashes
  differently from what the capture script stored — the file passes its own
  hash but fails the lint's. Save the body `text.strip()`-ed (no leading
  newline) and compute the hash over the same string you write. If lint
  flags drift on an existing raw, re-stamp: the FILE content is
  authoritative (it's the capture), recompute sha256 over `content[m.end():]`
  per the lint regex and rewrite the frontmatter hash — then re-lint.

## Step 3 — Extract the abstract and key sections

- Abstract extraction from converted HTML is brittle (the page has multiple
  "Abstract" occurrences, nav junk). **Prefer the arXiv API summary** — it is
  always clean:
  `https://export.arxiv.org/api/query?id_list={id}` → `<summary>` element.
- For key sections, search the converted body for section headings; if
  searches keep hitting ToC junk, re-apply the ToC strip from Step 2.
- Extract numbers verbatim (poison fractions, p-values, model sizes) — quote
  them exactly as printed; flag units that were mangled by math conversion
  (e.g. `0.005%percent0.005` means 0.005%).

## Step 4 — File into the KB

Follow the host KB's conventions (`llm-wiki` skill if it's a Karpathy wiki):
check existing pages BEFORE creating (search, don't guess); create entity +
concept + comparison pages as thresholds warrant; cross-link with `[[wikilinks]]`;
update index.md + log.md; provenance markers `^[raw/papers/file.md]` on
synthesis pages.

**Synthesis-currency rule (user's explicit standing instruction):** if the KB
has synthesis pages — a comparison table (e.g. `comparisons/poisoning-vectors-compared.md`)
and/or a tactics page (`tactics/`) — EVERY newly ingested paper must be
reflected in them, not just the concept/entity pages. Add a column/row to the
comparison, fold the paper's findings into the relevant tactics principles,
and bump both pages' `updated` date + sources frontmatter. The user has
repeated this instruction on every single ingest ("update the comparison and
add it to tactics") — treat it as a mandatory step, not an optional extra.
A paper that lands only in `concepts/` is half-ingested.

**Contested-content rule (validity challenges):** when a new source directly
challenges an already-ingested benchmark's validity (contamination/recall
studies, verifier audits), don't silently overwrite the old page — record
BOTH dated positions (the original claim AND the challenge, each with
sources and dates), set `contested: true` in the page's frontmatter so the
lint surfaces it for human review, and wikilink the challenge papers from
the challenged page. Session pattern: the SWE-Bench Illusion (2025),
ability-or-memory (2025), and DeepSWE's verifier audit (2026) were all
folded into `swe-bench.md` / `swe-bench-verified.md` /
`agentic-coding-evaluation.md` with both positions and `contested: true` —
the lint's advisory REVIEW SIGNALS then carry the debate to the user
instead of one side silently winning.

**Pitfall — prose ≠ wikilink:** mentioning an entity in prose does NOT create
a link. Every entity/concept you name in a page body must be `[[wikilinked]]`
or the lint will flag it as an orphan (hit repeatedly: entities mentioned in
bold text but not linked). Same for the index — every page listed, every
listed page exists.

## Step 5 — Lint and commit

Run the KB's lint (see `scripts/lint.py` — a complete 9-check wiki linter:
broken links, orphans, index completeness, frontmatter, tag taxonomy, page
size, source drift, log rotation, quality signals). Fix what it finds, then
commit + push. A lint pass that finds nothing on a fresh ingest is usually
wrong — it means the checker didn't run.

**Negative-test the linter before trusting a clean pass:** after a fresh
ingest, a green lint can mean "wiki is healthy" OR "checker silently broke"
(e.g. wrong LAYERS list, bad regex). Prove the checker actually fires by
injecting a deliberately broken page (a wikilink to `nonexistent-page-xyz`),
confirming the lint exits 1 with the expected findings, then removing the
test file:

```bash
printf -- '---\ntitle: Test\ncreated: 2026-08-08\nupdated: 2026-08-08\ntype: concept\ntags: [poisoning]\nsources: [raw/papers/x.md]\n---\n\nLink to [[nonexistent-page-xyz]]\n' > concepts/.__lint_test.md
python3 scripts/lint.py; echo "exit: $?"   # expect exit 1, broken-link finding
rm -f concepts/.__lint_test.md
```

If the linter passes on the broken page, fix the checker before fixing the
wiki. Also: a `tactics/` layer (if the KB has one) must be in the lint's
LAYERS list or its pages silently skip all checks. **Index page-count
header:** the `Total pages: N` line must match the filesystem — count with
`ls <dir>/*.md | wc -l`, don't trust the previous number (a string edit
silently failed once and the header drifted by 1 until the next full pass).

## Lead mining from curated lists (awesome-lists / companion repos)

Papers frequently arrive as "mine this repo" — an awesome-list or a
survey's companion repo of curated papers. This is a vetted lead source
(often by the same authors as an ingested paper); mine it systematically:

1. **Fetch + inspect the format first.** Repo READMEs via the GitHub API
   (`default_branch`, then raw README). Awesome-lists do NOT use plain
   `[title](url)` entries — the common format is
   `* **_Title_**, Authors, [![badge](img.shields.io/...)](https://arxiv.org/abs/XXXX) [![GitHub](...)](https://github.com/o/r)`.
   The arXiv URL lives in the **badge target**, not the link text; the
   title comes from `**_..._**`; badge-image links (img.shields.io) can
   dominate the link count (session: 284 of 307 links were badges) — parse
   `^\*\s+\*\*(.+?)\*\*,\s*(.+?),\s*(\[.*)$` per entry line and extract
   `arxiv.org/(abs|pdf|html)/<id>` from the badge targets.
2. **Dedupe against the KB before tiering:** match by arXiv ID against
   raw frontmatter AND by normalized title (lowercase, strip punctuation)
   against existing page titles. Report the already-covered count — it
   validates coverage (session: 13 of 275 were already ingested).
3. **Tier the remainder by relevance to the active project** (T1 =
   directly serves the goal, T2 = adjacent, T3 = out of scope now) and
   file the whole inventory as a `queries/` page with the tier tables.
4. **Treat mined titles as WORKING titles — verify each before ingest.**
   Curated lists carry pre-print working titles; `id_list` verification
   corrected one of ten (listed as "Configuring Agentic AI Coding Tools",
   actual: "Harness Engineering for Agentic AI Coding Tools"). Same rule
   as user-supplied citations: title-match the API response.
5. **Capture the list itself** as a dated raw article (it drifts; raw/ is
   immutable) + add a WATCHLIST row with a re-mine cadence.
6. Beware same-name different-benchmark collisions in mined lists
   (session: EvoCodeBench 2602.10171 vs already-ingested EvoCode-Bench
   2605.24110 — both valid; cross-link with a "do not conflate" note).

Full parsing recipe: `references/awesome-list-mining.md`.

## Batch ingestion

When ingesting N papers at once:
1. Verify all N first (one script, sequential with sleep for rate limits)
2. Fetch: for ~10+ sources run the capture as a BACKGROUND job
   (`terminal(background=true, notify_on_complete=true)` — foreground
   commands cap at 600s) and write synthesis pages (concepts/tactics from
   already-captured sources) while it runs; `process(action=wait)` to pick
   up the results
3. Extract all abstracts in one pass
4. Identify all entities/concepts ACROSS all sources before writing anything
5. **Plan inbound link coverage BEFORE writing pages** — decide which new
   pages link to each other and which existing pages get reciprocal links
   (or one hub page); lint orphan flags are cheaper to prevent than fix
6. **Slug = filename, or bulk-fix before linting** — a 43-paper wave once
   shipped 16 broken links purely from wikilinks pointing at *planned*
   slugs while files landed under different names
   ([[self-organizing-mas-continuous-sd]] → thebotcompany.md;
   [[req-to-architecture-hybrid-eval]] → r2abench.md;
   [[programming-with-pixels-se-computer-use]] → programming-with-pixels.md).
   Lock the slug list first and name files exactly those slugs; if names
   drift, run a bulk `[[old]] → [[new]]` replace across the cohort before
   the lint pass
7. **Mass waves: skeleton pages are acceptable** — for "mine ALL the
   coding-relevant papers" (43 in one wave), write ~20-line compact pages
   (overview from the abstract + 3-5 key facts + related links) for the
   bulk, and full-treat only the few the user is likely to cite. The raw
   holds full text for later deepening; skeletons keep a giant wave
   shippable in one session. State the depth choice in the log entry
8. Create/update pages in one pass, update index once, ONE log entry
9. Lint once at the end

## Product verification (software subjects, not papers)

Benchmark subject sets are often *software products* (agents, harnesses,
IDEs), not papers. Same verify-first discipline, different sources. Full
recipe + session detail: `references/product-verification.md`.

1. **Locate the canonical repo via web_search** (`<product> github`), then
   GitHub API for stars/created/license/default_branch; GitHub *search*
   API (`/search/repositories?q=...&sort=stars`) when the org is unknown.
   **Closed products have no repo** — capture the marketing site instead:
   JS-heavy sites still server-render; require converted body ≥~2000 chars
   or treat as a JS shell; grep raw HTML for `github.com/...` to find the
   real repo.
2. **Name collisions are common — disambiguate before writing anything.**
   Same-name projects from unrelated vendors appear constantly (session:
   simonyos/Z-CODE, an unrelated terminal assistant, vs Z.ai's ZCode ADE).
   Resolve via vendor + launch date + third-party corroboration (news,
   integration issues, community bridge repos that name the product).
3. **Routing eligibility is the benchmark-specific analysis:** grep the
   *captured* product sources for model-routing lines and classify
   vendor-locked vs BYO/endpoint-capable (session: 6 of 15 products were
   vendor-locked → only 9 could run the pinned model). Check the model
   provider's own docs for official integration pages (DeepSeek's
   api-docs documented Kilo Code — first-party eligibility evidence).
   Mark unverified eligibility as `[OPEN]` in the spec, don't assert.
4. **Page-writing conventions for products:** flag self-reported marketing
   claims explicitly ("10× faster" = marketing, not verified); disclose
   first-party status when the wiki's own tooling is a subject (Hermes
   page carries a conflict-of-interest note); record star counts as
   snapshot-dated and drifting.
5. **Comparison-matrix count changes:** when N subjects changes, grep the
   OLD count across the whole page — title, intro, verdict, sources list,
   and the spec's subject table (session: 9→15 touched 5+ locations).
   Rewrite the matrix table wholesale; per-cell patches drift.

## Benchmark run cost modeling

Estimating what a benchmark run costs at a model provider's list prices.
Recipe + worked example (deepseek-v4-flash): `references/benchmark-run-cost-modeling.md`.
Core: capture the pricing page (curl + tag-strip; `web_extract` may be
search-only), record input cache-miss / cache-hit / output per 1M tokens,
then model per-task-run cost with explicit token-band assumptions
(low/mid/high per task family) and a hit/miss/output split — report the
range, never a false-precision single number. Cache-hit price is often
50× cheaper than miss (output tokens then dominate the bill); flag
price-rise warnings from the page and snapshot it into the project docs.

## Pitfalls

- **Recommending papers from memory** — verify every paper you recommend or
  ingest; a confident-sounding citation can be entirely fictional
- **Wrong ID that resolves to a real paper** — title-match API responses; a
  200 with the wrong title is worse than a 404, because it looks verified
- **Fetching before verifying** — cheap to verify first; expensive to unwind
  a fabricated ingest
- **ToC anchor links surviving strip** — the `#S4.SS3` form, not just URLs
- **Abstract from converted HTML** — use the API summary instead
- **Prose mentions without wikilinks** — orphan pages; lint will catch it.
  Recovery: when lint flags an orphan, add reciprocal links from the new
  page's nearest neighbors (a `[[new-page]]` line in each related page's
  "Related" section) — don't just link out from the orphan. For big
  cohorts, create ONE hub page (a taxonomy / family-index page that
  wikilinks every member) so each new page gets inbound coverage in a
  single place; patch existing neighbors only for stragglers
- **Stub pages that pass head-only checks** — scan the full raw + converted
  body for `no html for` / `fatal error` / `untitled document` markers, and
  require real body bulk before accepting a fetch
- **User-supplied citations can carry wrong IDs too** — a user-pasted
  "DevBench 2403.07772" resolved to a statistics paper (correct:
  2403.08604, benchmark artifact DevEval). Treat user-provided IDs as
  hypotheses, same as memory: title-match the API response
- **Not recording the unverifiable-citation incident** — log it so future
  sessions don't re-recommend the same phantom paper
- **Terminal heredoc + `&` in content** — appending wiki log text containing
  an ampersand (e.g. "Capture & Verification Conventions") via
  `cat >> log.md <<'EOF'` trips the terminal tool's backgrounding guard
  ("Foreground command uses '&' backgrounding") and rejects the whole
  command. Append via `write_file`/`patch`, or rephrase the text without `&`.
- **Python `glob` has no brace expansion** — `glob.glob("raw/papers/{a,b}*.md")`
  returns EMPTY (silent); list filenames explicitly when looping over
  specific papers for abstract extraction.
- **Leaderboard deep-links drift** — tbench.ai (Terminal-Bench, redirects
  from terminal-bench.ai): the home page shows the top-10 table but
  versioned leaderboard paths (e.g. `/leaderboard/terminal-bench/2.1`)
  can 404; grab the home-page table and note the version status (TB 2.1
  active / TB 3 shipped) instead of chasing the deep link.
- **Semantic Scholar 429s** — don't build the workflow on it; use arXiv API
- **`exec(src, ns)` re-runs module-level code** — reusing a capture script
  by `exec(open(...).read(), ns)` executes any top-level loop when the
  script lacks a `__main__` guard (session: the METR re-capture silently
  re-fetched all 17 papers before the intended single capture ran).
  Idempotent overwrites are harmless but wasteful; put the batch loop
  behind `if __name__ == "__main__":` or a `main()` so exec-import only
  exposes functions
- **Patch anchors drift after earlier edits in the same wave** — in a
  multi-edit session, a "Related" section you patched an hour ago no
  longer matches the old_string you remember (session: swe-atlas,
  goal-directed, cursor patches failed on stale anchors; one bad patch
  even inserted a self-link `[[flare]]` and dropped lines). Read the
  CURRENT file content immediately before each patch in a link-wiring
  pass; check diffs after each patch; never patch a self-link into a
  page's own Related section.
- **Comparison-matrix subject counts appear in many places** — when a
  comparison grows (9 → 15 products), the old count lives in the title,
  intro, cluster analysis, verdict, AND sources list; grep for it before
  commit (lint doesn't catch prose-count drift, only broken links).

## Related

- `references/coding-agent-benchmark-canon.md` — verified arXiv IDs + tiers
  for the coding-agent evaluation canon (active user project: building a
  coding-assistant benchmark; harness-wiki). Includes the known-wrong-ID
  list so future waves don't re-verify from scratch.
- `references/product-verification.md` — verifying software products as
  benchmark subjects: repo location, name-collision resolution,
  vendor-locked vs BYO routing classification, marketing-claim flagging
  (session: six-product wave, 9/15 eligibility split).
- `references/benchmark-run-cost-modeling.md` — pricing-page capture and
  per-task-run cost model for fixed-model benchmark runs (cache hit/miss
  split, token bands, worked deepseek-v4-flash example).
- `references/awesome-list-mining.md` — parsing recipe for awesome-list /
  companion-repo lead mining (badge-target URLs, dedupe, tiering, working
  titles).
- `arxiv` skill — search/retrieval mechanics (bundled; this skill adds the
  verify-first discipline and full-text conversion it lacks)
- `llm-wiki` skill — the KB conventions this feeds (bundled)
- `grounded-citations` — per-claim provenance for deliverables
- `ocr-and-documents` — local PDF text extraction
