---
name: primary-source-verification
description: "Verify historical/archival claims against primary texts: archive.org OCR mining, Wikipedia curl checks, PDF HEAD-checks, blocked-archive handling, and the sourced-dossier deliverable format."
version: 1.0.0
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Research, Verification, Primary-Sources, Archive.org, History, Dossiers]
    category: research
    related_skills: [grounded-citations, blocked-page-recovery]
---

# Primary Source Verification & Sourced Dossiers

When a research task involves historical, archival, or heavily-sourced claims,
the deliverable is only as good as the chain claim → primary text. This skill
captures the retrieval-and-verification recipes for going to the source
document itself instead of trusting a tertiary page's paraphrase. It
complements the (bundled) `grounded-citations` skill: that skill owns the
citation-ledger mechanics; this one owns HOW to locate, fetch, and verify the
primary texts, and the dossier structure that makes the result checkable.

## When to Use

- "Produce a thoroughly sourced country/actor/entity file" tasks (e.g.
  religion × politics × empire dossiers per country)
- Fact-checking a quote or date attributed to a 19th/20th-century book, treaty,
  report, or biography
- Any task where you must distinguish verified sources from unverified leads
  and the reader will check your work

## Core Workflow

1. **Inventory claims → identify the primary text for each.** For each load-
   bearing claim, name the primary document (book, treaty text, official
   report, contemporary press) that should carry it.
2. **Locate the primary text** (archive.org advancedsearch; Project Gutenberg;
   Wikimedia Commons for treaty PDFs; library catalog records).
3. **Verify the item is actually quotable** — confirm a text derivative exists,
   download it, grep the verbatim passage. A scan with no OCR text is not
   quotable; a search snippet is not page content.
4. **Cross-check every OCR'd digit** against a second source; flag
   discrepancies inline instead of silently choosing.
5. **Assemble the dossier** in the standard structure (below), with an explicit
   Unverified Leads section.

## Recipes

### Archive.org full-text OCR mining

```bash
# 1) Find scans by title
curl -s "https://archive.org/advancedsearch.php?q=title%3A%28word1+word2%29&fl%5B%5D=identifier&fl%5B%5D=title&fl%5B%5D=year&rows=20&output=json"
#    multiple titles: q=%28title%3A%28a+b%29+OR+title%3A%28c+d%29%29

# 2) Confirm a text derivative exists, then download the OCR
curl -s "https://archive.org/metadata/<identifier>"   # files[] must list *_djvu.txt / *_hocr_searchtext.txt.gz / .epub
curl -sL "https://archive.org/download/<identifier>/<file>_djvu.txt" -o page.txt

# 3) Mine for verbatim quotes
grep -n -i "phrase" page.txt
sed -n 'START,ENDp' page.txt    # context window
```

- **Multi-volume works have separate identifiers per volume** (e.g.
  `modernegypt00crom` vs `modernegypt0002earl_m9t0`) — check both.
- **TOC first:** grep the table of contents for chapter titles + page numbers
  to find the body range before deep-grepping (e.g. "CH. XXXVII YOUNG EGYPT
  228" → read around line that renders p. 228).
- **OCR quirks:** doubled spaces (fine — the verbatim matcher tolerates
  whitespace); `^` where an fi/fl ligature was ("f^rst"); **digit errors are
  the dangerous one** — a footnote digit can be wrong (Cromer's *Modern Egypt*
  says Abduh "died in 1906"; standard sources say 1905). Never trust an OCR'd
  digit alone; cross-check and flag.

### Wikipedia fact checks without a browser

```bash
curl -sL "https://en.wikipedia.org/wiki/<Title>" -o p.html
python3 - <<'PY'
import re, html
t = open('p.html').read(); t = re.sub(r'<[^>]+>', ' ', t)
t = html.unescape(t); t = re.sub(r'\s+', ' ', t)
for kw in ['keyword1', 'keyword2']:
    m = re.search(re.escape(kw), t)
    if m: print(t[max(0, m.start()-130):m.start()+280]); print('---')
PY
```

- Infobox life dates also appear in the page's category lists
  ("1849 births", "1905 deaths") — a fast date check.
- Fetch the page before quoting; search snippets support only what they
  literally say.

### PDF existence check

```bash
curl -sI <pdf-url> | head -5   # HTTP 200 + content-type: application/pdf = citable
```

### Cloudflare-blocked archival pages (qdl.qa, hansard.parliament.uk)

- Direct fetch → 403 "Just a moment...". The URL is still real if it came
  from a web_search result.
- Cite it WITH the caveat: "page located via search; direct fetch blocked
  (403)". **Never fabricate its contents.**
- Try alternates before giving up: Project Gutenberg, Wikimedia Commons,
  alternate PDF hosts, or openlibrary.org catalog records for
  publisher/year even when the text itself is blocked.

## Dossier Structure (the deliverable format)

For "thoroughly sourced country/actor file" tasks, write:

1. **Overview** — 4–6 sentences, no claims beyond what is sourced below.
2. **Key Figures** — per entry: dates, role, stance, relation-to-subject,
   `Sources:` line with URLs.
3. **Mechanisms / policies** — structural levers (treaties, missions,
   institutions), each with its own sources.
4. **Primary Sources (verified)** — each with URL/location and fetch caveats
   ("OCR text downloaded and quoted"; "direct fetch blocked (403)").
5. **Secondary Sources** — author, title, year, publisher/journal, URL if
   found; only list ones actually located this session.
6. **Unverified Leads** — explicitly marked: standard references not verified
   this session, anecdotal quotes, interpretive claims. The reader must be
   able to tell exactly what is NOT established.

Inline discipline: flag date discrepancies as
`[Note: source A says X; standard sources say Y]`; mark anecdotal quotes
`[unverified; reported in ...]`. The credibility of the file comes from the
unverified list being explicit, not from implying everything was checked.

## Pitfalls

- **Citing a scan you never opened.** Always confirm the `_djvu.txt` exists in
  metadata and grep the passage before listing the item as a verified source.
- **Trusting OCR'd digits.** Cross-check against a second source; flag
  discrepancies rather than picking one silently.
- **Treating search snippets as page content.** Fetch first.
- **Fabricating the contents of a blocked page.** A 403 URL cited with a
  caveat is honest; invented content is not.
- **Skipping the Unverified Leads section** — it is what makes the rest of the
  dossier trustworthy.

## Worked Example

Egypt 1882–1952 dossier (religion × British imperial rule): located Cromer's
*Modern Egypt* (1908) and Wingate's *Mahdism and the Egyptian Sudan* (1891) on
archive.org, downloaded the OCR, and quoted the canonical passages verbatim
("Islam cannot be reformed; that is to say, reformed Islam is Islam no
longer"); HEAD-verified the 1936 Anglo-Egyptian Treaty PDF on Wikimedia;
flagged Cromer's OCR'd footnote digit (Abduh d. 1906 vs standard 1905); cited
the Milner Report (qdl.qa) and the 1921 Hansard debate with explicit 403
caveats; delivered the 6-section dossier at
`research/<project>/<NN>-<country>.md`.
