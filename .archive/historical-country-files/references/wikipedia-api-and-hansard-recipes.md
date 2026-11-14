# Wikipedia API & Historic Hansard recipes (figure clusters)

Condensed from the UK-part 11c session (British India policymakers,
Chelmsford→Mountbatten, Montagu→Hoare, O'Dwyer/Dyer), Sep 2026. Complements
`archive-org-wikisource-recipes.md`: that file covers books/statutes; this one
covers biography extraction and parliamentary debates.

## 1. Wikipedia plain-text extracts, batched (11 figures ≈ 2 minutes)

Goal: pull dated decisions for many figures WITHOUT streaming 10+ full
articles into model context. Fetch once to disk, grep locally.

```bash
# one title per request, ~10s spacing, tracked background job
f() { curl -s "https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1&format=json&formatversion=2&redirects=1&titles=$1" -o "pages/ukc_$2.json"; sleep 10; }
f "Frederic_Thesiger,_1st_Viscount_Chelmsford" chelmsford
f "Louis_Mountbatten,_1st_Earl_Mountbatten_of_Burma" mountbatten
# ... one line per figure; run via terminal(background=true, notify_on_complete)
```

Then convert + inventory in one python pass (read JSON files, write
`p['query']['pages'][0]['extract']` to `.txt`, print `title` + char count),
and grep the `.txt` files for decision-bearing terms with context
(`electorate|communal|Khilafat|Simla|Award|Rowlatt|Muslim|Jinnah|...`). Read
only short files whole.

Traps:
- **`redirects=1` redirects silently.** `3_June_Plan` came back as
  'Partition of India' (87k chars) — fine as content, but always compare the
  returned `pages[0].title` to the requested title so coverage claims are
  accurate.
- **Extract length varies wildly** (6.7k for Edwin Montagu vs 89k for Wavell).
  A short extract is lead-only, not evidence the article lacks the topic.
  Supplement with targeted anchor pages (below) when an entry is thin.
- **~10s spacing**: earlier sessions found tiny/empty responses = rate limit.
  Also expect occasional 429s on any later bulk re-check; a single retry after
  a pause returns 200.
- `curl | python3` pipes trip the terminal security scanner — write JSON to
  files, parse in a separate call.

### Anchor pages that pin dates cheaply (India cluster, worked)
- `Rowlatt_Act` — passed 18 Mar 1919, in force 21 Mar 1919; Satyapal/Kitchlew
  arrests 10 Apr 1919; Baisakhi gathering 13 Apr 1919.
- `Montagu–Chelmsford_Reforms` — report 1918 (Cd 9109) → Government of India
  Act 1919; diarchy mechanics.
- `Simla_Conference` — Wavell Plan announced 14 Jun 1945; conference opened
  25 Jun 1945; League 'sole representative of Indian Muslims' claim scuttled it.
- `Communal_Award` — MacDonald's award 16 Aug 1932; Depressed Classes clause
  (para 9); Akali/Sikh seat arithmetic.
- `Partition of India` — Mountbatten Plan press conference 3 Jun 1947;
  religious-bloc votes in Punjab/Bengal assemblies, NWFP+Sylhet referendums;
  14–15 Aug 1947 independence.
- `Indian_Independence_Act_1947` on legislation.gov.uk:
  https://www.legislation.gov.uk/ukpga/Geo6/10-11/30/contents/enacted

## 2. Historic Hansard: live-fetchable, but the slug must be exact

The old 'hansard is Cloudflare-gated' assumption is WRONG for direct debate
pages — via curl they return HTTP 200 with the correct `<title>`:

- https://api.parliament.uk/historic-hansard/commons/1920/jul/08/army-council-and-general-dyer
  ('ARMY COUNCIL AND GENERAL DYER', 8 July 1920 — the Dyer debate; slug copied
  from Wikipedia's External links)
- https://api.parliament.uk/historic-hansard/commons/1940/mar/14/sir-michael-odwyer-assassination
  ('SIR MICHAEL O'DWYER (ASSASSINATION)', HC Deb 14 Mar 1940 vol 358 cc1372-3)

Rules:
- **Never guess a slug.** Every guess 404'd (`india`, `indian-administration`,
  `government-of-india`, `constitutional-reforms`, …). Take the exact slug
  from a debate link in a Wikipedia article's External links section, or use
  the search endpoint, which returns 200:
  `https://api.parliament.uk/historic-hansard/search?q=montagu&start=1917-08-20&end=1917-08-20`
- The sittings index page (`/historic-hansard/sittings/<date>`) returned ~14
  bytes (blocked) — don't build the pipeline on it.
- When a debate page's slug can't be resolved at all, cite the standard
  citation (HC Deb <date> vol <n> cc<n>) + the working search URL, and keep
  the verbatim text verification on the printed source (e.g. Keith's
  *Speeches and Documents* vol. 2, which carries the Montagu Declaration of
  20 Aug 1917 under the heading '5. Edwin S. Montagu, House of Commons,
  20 August, 1917' — grep the `_djvu.txt`).
