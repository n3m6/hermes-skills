# Sourcing real design documents

Three artifact types, each teaching something different:

- **Design philosophy pages** -> the values / pillars section of a doc.
- **Published design-doc excerpts** -> real structure and real doc voice.
- **Dev diaries** -> the living version: vision, then goals, then named
  pillars, then a feature-by-feature breakdown. The closest thing the industry
  publishes to a running GDD.

## Known-good artifacts

- **gamedeveloper.com** (ex-Gamasutra) is server-rendered, fetchable under curl,
  and has no bot wall — the best free source of *developer-stated* design
  reasoning in this genre. Two artifact classes:
  - **Design-doc excerpts**: Jon Shafer's published section of the *At the Gates*
    design doc — a real doc section structured phase x activity (Turn 1,
    Turns 2-6, Turns 7-12; under each: Exploration, Economics, Military,
    Diplomacy, New Challenges, Strategic Opportunities).
  - **First-party dev deep dives and postmortems** — the highest-value material,
    because the byline is the signal (a lead designer outranks an SEO listicle):
    the Victoria 3 economy deep dive (Mikael Andersson, Vic3 lead designer), the
    Stellaris postmortem (Henrik Fåhraeus + Rikard Åslund), Chris King's GDC talk
    on plundering history, the CK2 "surprising design" interview, the CK3
    tutorial-UX deep dive, the CK3 feedback-backlog interview, and Jon Shafer's
    "Strategy Games Are Broken".
  Mining the site at scale: see the fetch recipe below.
- **FreeOrion design philosophy** — a real open-source 4X doc's values section:
  Realism ("we're not making a simulation"), K.I.S.S., Avoiding Micromanagement
  ("sliders suck"), Relation to Master of Orion. The live wiki is
  Cloudflare-walled; Wayback holds the pages.
- **Paradox dev diaries** (CK3, Stellaris, EU4, HOI4) — the forum is
  CAPTCHA-walled, but the storefront API returns full text. See the recipe.

## Fetch recipe

```bash
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

# 1. Steam news API -> full announcement bodies as JSON, curl-friendly
curl -sL "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid={APPID}&count=300&maxlength=0&format=json"
#    maxlength=0 returns the UNTRUNCATED body in newsitems[].contents
#    appids: CK3=1158310 Stellaris=281990 EU4=236850 HOI4=394360 CivVI=289070

# 2. Wayback for Cloudflare-walled wikis and forums
curl -sL "https://web.archive.org/web/2023/http://freeorion.org/index.php/Philosophy"

# 3. Always strip tags before reading — chrome is ~90% of the bytes
```

### Mining gamedeveloper.com at scale

```bash
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

# 1. The search page is SERVER-RENDERED — the result list is in the HTML, no JS
#    needed, no bot wall. robots.txt disallows /search, so seed from it sparingly
#    (or use the sitemap: https://www.gamedeveloper.com/articles-archive-index.xml)
#    and keep display going to the article URLs.
curl -sS -A "$UA" -o p1.html "https://www.gamedeveloper.com/search?q=<topic>&terms=%2Fdesign"
#    Paginate with &page=N; a page shows 30 of N ("Showing results 1 - 30 of 258").

# 2. Parse the results out of the server-rendered blocks (not the a11y/JS tree).
#    Each result is div.ContentPreview.SearchResult-ContentPreview, holding:
#      title + href -> a.ListPreview-Title
#      date         -> span.ListPreview-Date
#      read time    -> span article-read-time-text
#      author       -> a.Contributors-AvatarLink[aria-label]

# 3. Fetch article pages; extract the body from the CMS container:
#      start at  data-testid="article-base-body-content"   (the INNER body, not
#                the outer data-testid="article-base-body" wrapper, which also
#                carries contributors, featured image and share chrome)
#      end   at  the next data-testid="article-base-more"  (or the first of
#                </article> / ArticleBase-Footer / TwoColumnLayout-Aside)
#      then take <p> <h2> <h3> <blockquote> in document order
#    A stdlib html.parser.HTMLParser that emits newlines on block tags is enough;
#    no third-party HTML parser is required.
#    JSON-LD is present but carries NO articleBody field — do not rely on it.
```

**Two-tier reading (do not skip).** Index *all* results and filter by keyword
first, then read in full only the first-party/designer pieces and excerpt the
rest. A dozen long articles is ~200k characters — more than fits in context, and
the tail is lower-authority than the head. Deduplicate by href before reading.

**Cite the byline, not the publisher.** The load-bearing distinction in this
corpus is author-as-practitioner (a Paradox lead designer describing their own
system) vs journalist summary vs SEO listicle. Say which tier each claim sits in.

## Pitfalls

- **Check the tail of every extracted article.** If it ends in newsletter copy,
  "Latest News", podcast promos or footer links, the end boundary failed and
  sidebar/footer chrome bled in — re-cut at `article-base-more` before reading.
  The tail is the cheapest signal that the extractor is wrong.
- **`web_extract` is search-only and cannot fetch a URL's content.** Go
  straight to curl; do not burn a call discovering this again.
- **Do not treat the automation browser as the way past a bot wall.** Paradox's
  forum returns an image CAPTCHA and Cloudflare-protected wikis return the same
  managed-challenge interstitial to curl and to the browser alike. Route to the
  archive or the platform API instead of escalating.
- **A Wayback `404` means "not archived at that exact URL", not "gone".**
  Enumerate alternate page titles with the CDX prefix wildcard before giving
  up. A `429` from the availability API means "unknown", not "no snapshot".
- **Dev diaries are marketing.** They state pillars and direction, never
  numbers or failure modes. Never cite one as evidence for how a system is
  actually implemented.
- **Games journalism and SEO template farms are noise** for this question. A
  search for "grand strategy design document TOC" returns storefronts and
  listicles; go straight to the artifacts above.

## Bulk-fetching a corpus (22 articles, one round of calls)

- One `for url in ...; do curl -sL -A "<browser UA>" ...; done` loop, one
  `<sha1>.html` per article — gamedeveloper.com answers 200 with no bot wall, so
  the whole list costs a handful of calls, not one per article.
- **`lxml` is not installed in the tool python** (`ModuleNotFoundError: lxml`, one
  wasted call 2026-10-18). Strip the body with the stdlib — `html.parser` or a
  targeted `re` between the article container and `article-base-more` — and write
  `.txt` next to the `.html`.
- Read the `.txt` back; never re-fetch a page already on disk. Scratch lives under
  `~/.hermes/cache/scratch`, not `/tmp`.
- Close the loop with a count: `N distinct sources cited` must equal `N in the
  ledger`. On 2026-10-18 it was 22/22, and that number is what made the 37-item
  list auditable.
