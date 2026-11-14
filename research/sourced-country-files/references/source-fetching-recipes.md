# Source fetching recipes (per host)

Technique per host for the country/history research workflow. SKILL.md carries the always-on
rules (verify every URL, flag single-source claims, never fabricate a negative); this file
carries how to actually get the bytes and how to tell "absent" from "moved" from "rate-limited".

## Wikipedia: fetching a page

- **Raw wikitext is the workhorse:** `curl -s -A "Mozilla/5.0 (X11; Linux x86_64) research-bot" "https://en.wikipedia.org/w/index.php?title=${TITLE}&action=raw" -o pages/${TITLE}.wiki`. Batch several titles per call with `sleep 1` between fetches; check byte counts to spot failures.
- **Cite the rendered article URL in the deliverable**, never the raw endpoint. Wikitext is full of `{{templates}}` and `[[links]]` — that is fine, grep through it.
- **Redirects:** a tiny file (<200 bytes) or one starting `#REDIRECT [[X]]` means the title moved. Resolve with `api.php?action=query&titles=${TITLE}&redirects=1&format=json`, then re-fetch the canonical title. Watch URL-encoding for apostrophes (`Abul_A%27la_Maududi`).
- **Large pages (100KB+):** do not read whole — `grep -n -i -E "term1|term2"` then read the matched windows. Wikitext stores a whole paragraph on one line, so pipe a match through `cut -c1-400` before `head` or a dozen matches flood the context. Mid-size pages (10–40KB) can be read whole.

## Wikipedia: rate limits

- **Per-endpoint and aggressive.** Signature: a tiny (~1950–2090 byte) page starting `<!DOCTYPE html>` / "Wikimedia Error", or api.php replying "You are making too many requests to the API" while `index.php?title=X&action=raw` still works.
- Space raw-wikitext fetches 8–12s apart. `en.wikisource.org` has a **separate limiter** and takes bulk fetches freely — use it for primary texts. `en.m.wikipedia.org` returns 0 bytes when blocked (do not fall back to it); wikiwand.com is Cloudflare-walled.
- **`api.php` JSON has its own limiter whose signature is an EMPTY body → `JSONDecodeError`.** Treat that as rate-limit, not network failure, and re-sleep.
- **Heavy sessions outrun the spacing.** On a ~25-page batch individual titles still fail 3–4× even at 25s spacing: run stubborn retries as a background job with `sleep 20–30` and `notify_on_complete` rather than holding the turn.

## Wikipedia: 404 vs absent vs rate-limited

- **Read the Wikimedia Error body.** `Error: 404, Not Found` (title echoed in the page) = title moved/wrong, or **non-ASCII not percent-encoded**: `Halide_Edib_Ad%C4%B1var`, `%C4%B0smet_%C4%B0n%C3%B6n%C3%BC`, `Abd%C3%BClhamid_II`, `K%C3%A2z%C4%B1m_Karabekir` (Turkish `ı İ ö ü â`). The raw unencoded title 404s although the browser URL works. Fix the URL, don't sleep. A rate-limit message in the body = back off.
- **MISSING is proven by the extracts call:** `api.php?action=query&prop=extracts&exintro=1&explaintext=1&titles=<T>&format=json` — a `"missing":""` key means the article does not exist, an `extract` field means it does. `api/rest_v1/page/summary/<Title>` is a cheaper, less-limited existence probe. One `titles=` query can contradict a later one; the extracts call is authoritative.
- **`prop=extracts` caps:** `exchars` maxes at 1200 (a larger value fails the whole request); whole-article extracts force `exlimit=1` and silently return only the first title plus a `warnings` block. Lead-only sweeps (`exintro=1&explaintext=1&exlimit=20&redirects=1`) batch fine as a cheap identity/role/date pass and title resolver; whole-article plaintext is one title per call, ~2s apart.
- **Link text is a title hint.** When `[[Sayyid Muhammad Tabatabai]]` queries MISSING, try the exact variant other articles link (`[[Mirza Sayyed Mohammad Tabatabai]]`). Follow redirects — redirect targets are the encyclopedia's canonical spellings (`Mohammed Mossadegh` → `Mohammad Mosaddegh`).
- **Disambiguated titles: the plain title may be a different person.** `Edmund Ironside` is the 11th-century king; the 1921-coup general is `Edmund Ironside, 1st Baron Ironside`. After any fetch, verify with `grep -m4 -E "birth_date|death_date|Short description"` on the infobox.
- **Same surname ≠ same generation.** `Recollections of a Diplomatist` is by Sir Horace Rumbold's father (1829–1913), not the son (1869–1941); the two Louis Mallets (1823–1890 civil servant vs 1864–1936 ambassador to the Porte) are the same trap. Check the author's life dates against the figure's before citing a memoir.
- **No English article ≠ no sources.** Check other language editions — fr.wikipedia carries many MENA religious figures with full scholarly citations (e.g. Na'ini, with Hairi, *Shi'ism and Constitutionalism in Iran*, Brill 1977). Foreign-language reference lists are a fast way to verify ISBNs and page-level claims.

## Wikisource

- **Cite through the wikitext header for attribution.** For an anthology chapter the page author is the volume; the contributor lives in `{{header}}` (`| contributor = Eldon Gorst`).
- **Title case is exact** — `.../The_Empire_and_the_century/Lord_Cromer_in_Egypt` vs a `The_Empire_and_The_Century` guess that 404s. When a collection-page guess fails, enumerate real subpages: `api.php?action=query&list=allpages&apprefix=<Collection>/&aplimit=100&format=json`.
- **`Page:` namespace vs main.** A clean title can 404 while the scan lives at `Page:<Title>.pdf/N` (e.g. the 1928 Anglo-Transjordanian Agreement, Cmd 3488, on /1 and /2).
- **Treaties are often split:** `action=raw` on `Treaty_of_S%C3%A8vres` returns `{{header}}` plus subpage links — use `/All_parts` or fetch `/Part_I`, `/Part_IV`. Clause text goes through template params (`|clause1=…`) which strip article numbers, so grep content keywords ("Protection of Minorities", "Kurdistan") rather than "Article N", and confirm wording against the rendered page.
- **A 404 is a verified negative — record it.** The Faisal–Weizmann agreement is absent (use the web.archive.org UN text); the King-Crane full text is at `wwi.lib.byu.edu/index.php/The_King-Crane_Report`, not Wikisource.
- **En-dash titles** ("Sykes–Picot", "King–Crane", "McMahon–Hussein") use en-dashes; hyphen guesses 404 or redirect.

## archive.org

- **Discover:** `advancedsearch.php?q=<query>&fl[]=identifier&fl[]=title&fl[]=year&rows=10&output=json`, then `archive.org/metadata/<id>` for the exact filename, then the OCR text at `archive.org/download/<id>/<exact filename>_djvu.txt` (URL-encode spaces). Always `curl -sL` — downloads 302.
- **Verify existence via `metadata/<id>`** (HTTP 200 + JSON) and pull title/creator/date from that JSON. Public-domain scans download freely; lending-restricted items return HTTP 401 → cite `[META] lending-restricted, metadata verified` rather than failing.
- **Hits are noisy:** podcasts and compilations pollute results. Check `metadata/<id>` `files` for `.txt`/`.pdf` before treating a hit as a text source; if neither exists the item cannot be quoted.
- **Titles mislead — read the djvu text before citing "the report".** The League of Nations dossier `disturbances-august-1929` is mixed-language correspondence, not the Shaw Report (Cmd 3530), whose clean scan is a Wikimedia Commons djvu reached via the en.wikipedia File page.
- **Known-good finds for Mandate/Middle East work:** Aitchison's treaty collection Vol. XI (Darin 1915, Jeddah 1927, 1923 Hasa oil concession, Uqair/Mohammerah), Hurewitz *Diplomacy in the Near and Middle East*, Antonius *The Arab Awakening*, Dickson *Kuwait and Her Neighbours*, Philby *Saudi Arabia*, Kramer *Islam Assembled*, Shuster 1912, Curzon 1892, Gooch & Temperley Vol IV.

## British official records

- **TNA Discovery deep links return HTTP 202** (session content negotiation) — 202 means the record resolves; cite it and note "(HTTP 202)". Confirm via the API: `discovery.nationalarchives.gov.uk/API/search/records?sps.searchQuery=<terms>&sps.resultsPageSize=5` → `records[]` each with `id`, `reference` (`FO 633`, `PRO 30/57/3/10`, `KCLMA Allenby`, `MSS Afr s 1170`), `title`.
- **The Discovery API intermittently returns HTTP 500 HTML.** When it does, mine `/details/r/<id>` URLs out of Wikipedia citation lists (articles cite TNA heavily: `CAB 24/271/3` → `/details/r/D7730874`; Milner Mission → `/details/c/F262414`) and verify those return 202. Discovery is the union catalogue for UK private-paper collections (Cromer FO 633, Kitchener PRO 30/57, Allenby KCLMA, Killearn/Lampson MSS Afr s 1170, Wingate at Durham).
- **Historic Hansard API fetches when the modern site is gated:** `hansard.parliament.uk` returns 403 to curl (Cloudflare), but `api.parliament.uk/historic-hansard/commons/<yyyy>/<mmm>/<dd>/<topic>` (e.g. `.../commons/1939/may/23/palestine`, the 1939 White Paper debate) returns 200 with quotable text. Cite the API URL and note the modern-site caveat; Wikipedia citation lists carry the correct slugs.
- **OpenLibrary verifies print/secondary books** without a scan: `openlibrary.org/search.json?q=<plain space-separated terms>&fields=key,title,first_publish_year,author_name&limit=4` → `/works/OL…W` keys, then live-check `https://openlibrary.org/works/OL…W` (200). Field-syntax queries (`title:(x) AND creator:(y)`) return empty/error docs. Check OL before declaring a published memoir unlocatable (Killearn Diaries: absent from archive.org entirely, present on OL).
- **Cross-check dates against the London Gazette** or other official records cited inside articles (knighthood dates) rather than trusting article prose.

## Other reliable verbatim hosts

- **Avalon Project (avalon.law.yale.edu):** plain static HTML, no JS wall — Balfour Declaration and the 1939 White Paper both fetch cleanly.
- **UNISPAL modern scheme:** `un.org/unispal/document/auto-insert-<id>/` (1930 Wailing Wall Commission = auto-insert-183716). The old `domino.un.org/UNISPAL.NSF/...` links are dead; find the slug via search, don't guess the id.
- **ECF (content.ecf.org.il) and COJS (cojs.org):** clean Mandate-era primary PDFs (Mandate text, Hope Simpson Cmd 3686, Passfield Cmd 3692, 1922 White Paper, Shaw excerpts).
- **FCDO treaties (treaties.fcdo.gov.uk):** full UK treaty-series PDFs, article by article — better than any summary (Jeddah 1927, Cmd. 2951: Art. 1 independence, Art. 3 hajj, Art. 9 voids Darin 1915).
- **National Security Archive (nsarchive.gwu.edu, nsarchive2.gwu.edu):** HTTP 200, extracts fine with html2text; posts unredacted documents with IDs and FRUS refs (e.g. 2 Sep 1953 FO memo "Persia: Political Review of the Recent Crisis", NARA RG 59 788.00/9-253; CIA "The Battle for Iran"). Cite the briefing page + document ID, and note what stays redacted as an `[UNVERIFIED]` lead.
- **Project Gutenberg / Gutenberg Australia** for public-domain full text and verbatim quotes (*Seven Pillars of Wisdom* at gutenberg.net.au).
- **Foreign-ministry sites** (e.g. mfa.gov.tr) host official treaty texts verbatim — good cross-check for annexes like the 1923 population-exchange convention.

## Non-Wikipedia HTML, PDFs, and walls

- **Strip HTML with the bundled script:** `python3 scripts/html2text.py page.html -k "5,000" -k "Article 1"` prints context windows around exactly the terms you need — it beats grepping raw HTML and works on any static host.
- **PDFs:** `curl -s -L -A "Mozilla/5.0" "<url>" -o doc.pdf`, then `pdftotext -layout doc.pdf doc.txt` (poppler-utils). Journal PDFs often download from `article/download/<id>` URLs (e.g. AJISS "Caliphate Question").
- **JS-rendered pages yield nothing to curl.** If html2text reports NO MATCH on a plausible page (e.g. palquest.org), record "JS-rendered, not curl-extractable" and find the same document on another host (UNISPAL, Wikisource, archive.org).
- **Cloudflare-gated archives (qdl.qa, iranicaonline.org)** defeat curl *and* browser — don't burn turns. Cite `[BLOCKED] verified via search snippet / independent corroboration`; Iranica entry URLs stay citable with the article slug (`iranicaonline.org/articles/anglo-russian-convention-of-1907-...`), verified through the citing article.

## Final sweep

- Before finishing, extract **every** URL from the deliverable and HTTP-check the lot in one batch loop printing `code url`. That is the verification ledger for the Method note, and it catches the typos the per-item checks missed.
