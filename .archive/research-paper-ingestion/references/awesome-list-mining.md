# Awesome-List / Companion-Repo Lead Mining

Proven recipe from mining `ggjy/Awesome-Agent-Engineering` (companion to the
"From Question Answering to Task Completion" survey, arXiv:2606.20683) —
275 entries parsed, 270 arXiv IDs, 13 already in the KB, tiered queue filed
as a `queries/` page.

## Entry format (the trap)

Awesome-lists do NOT use plain `[title](url)` links. Typical line:

```
* **_Title_**, Author et al., [![arXiv](https://img.shields.io/badge/arXiv-24.07-red?labelColor=grey)](https://arxiv.org/abs/2407.xxxx) [![GitHub](https://img.shields.io/badge/GitHub-Code-white?logo=github)](https://github.com/o/r)
```

- The arXiv URL is the **badge target** (`](https://arxiv.org/abs/...)`)
  — NOT the visible link text (which is the shields.io image).
- The paper title is the `**_..._**` span; authors follow after the comma.
- Badge-image links can dominate: 284 of 307 links in the mined repo were
  `img.shields.io` images. A naive `[text](url)` regex finds almost nothing.

## Parsing (Python)

```python
import re
cur_cat = "?"
entries = []
for line in readme.splitlines():
    m = re.match(r"^#{1,3}\s+(.+)$", line)
    if m:
        cur_cat = m.group(1).strip(); continue          # category = ## header
    em = re.match(r"^\*\s+\*\*(.+?)\*\*,\s*(.+?),\s*(\[.*)$", line)
    if not em: continue
    title, authors, rest = em.group(1), em.group(2), em.group(3)
    aid = re.search(r"arxiv\.org/(?:abs|pdf|html)/([0-9]{4}\.[0-9]{4,5})", rest)
    gh  = re.search(r"github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)", rest)
    entries.append({"cat": cur_cat, "title": title, "authors": authors.strip(),
                    "id": aid.group(1) if aid else None, "github": gh.group(1) if gh else None})
```

## Dedupe against the KB

- Match by arXiv ID against raw frontmatter (`source_url` lines) AND
  `entities/*.md` + `concepts/*.md` titles.
- Normalize titles: `re.sub(r"[^a-z0-9 ]", "", title.lower())`.
- Report the already-covered count — it validates KB coverage.

## Tiering + filing

- Tier by relevance to the active project: T1 = serves the goal directly
  (for a benchmark project: eval methodology, validity, harness, product
  config), T2 = adjacent, T3 = out of scope (log, don't queue).
- File the full inventory as a `queries/<topic>-lead-inventory.md` page:
  mining stats + tier tables with IDs + usage notes. Link it from the
  survey/entity page that surfaced it (inbound link, no orphans).
- Capture the repo README itself as a DATED raw article + WATCHLIST row
  (re-mine cadence).

## Working titles — always verify before ingest

Curated lists carry pre-print working titles. `id_list` verification of
tier-1 (10 papers) corrected one: listed as "Configuring Agentic AI Coding
Tools", actual title "Harness Engineering for Agentic AI Coding Tools".
Same rule as user citations: title-match the arXiv API response, don't
presence-check.

## Same-name collisions

Mined lists can contain names that collide with already-ingested papers:
EvoCodeBench (2602.10171, inference-time self-evolution) vs EvoCode-Bench
(2605.24110, multi-turn iterative interactions) — different benchmarks.
Cross-link both pages with a "do not conflate" note instead of deduping
them away.
