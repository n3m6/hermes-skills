# LinkedIn profile recon without an account

## What guest access gives you

- `/in/<slug>` redirects to `/authwall?sessionRedirect=...`. `curl` with a normal or
  Googlebot UA gets HTTP 999; anonymous reader proxies get 403. There is no guest view
  of the full profile.
- What still leaks publicly: the search-index card — name, location, connection count,
  sometimes follower count — and `/posts/<slug>_<words>-activity-<id>` URLs for public
  posts, whose snippets include the post text and date.
- A profile whose public card is only "Location: X · N connections" has its public
  visibility turned down. That is a blocker, not evidence of anything.

## Queries that work (search backend, not direct fetch)

| Goal | Query |
|---|---|
| Metadata card | the exact profile URL |
| Card via phrase | `"Full Name" "N connections"` |
| Employer claim | `"Full Name" "Company Name"` |
| Employer's own site | `site:company.com "Surname"` |
| Role/title | `"Full Name" <city> <function>` |
| Name's real-world footprint | `"Full Name" -linkedin` |
| Sibling accounts | `"Full Name"` (the platform's `/pub/dir/` listing often surfaces in results) |
| Post text trace | the post's opening sentence in quotes — shows whether other employees posted the same text |

Search-engine caveat: a datacenter IP gets captcha-walled by Google, Startpage and
Brave, and Bing may answer "no results" for a phrase that the search backend indexes
fine. Treat one engine's emptiness as no evidence; cross-check with the search backend
that is actually returning content.

## Decoding a LinkedIn activity ID

The numeric tail of `urn:li:activity:<id>` packs the creation time in its top 41 bits:

```python
from datetime import datetime, timezone

def activity_time(activity_id: int) -> str:
    return datetime.fromtimestamp((activity_id >> 22) / 1000, tz=timezone.utc).isoformat()

# 7510510305412714496 -> 2026-09-29T01:26:35+00:00
```

Use it to build a timeline of the account: the span from earliest to latest post is a
proxy for how long the account has actually been operating.

## Employer corroboration checklist

1. Company site `/about-us/meet-the-team/` or leadership page (usually execs only —
   absence proves little).
2. Company newsroom / PR Newswire releases: employees are quoted by name in deals and
   awards.
3. Award shortlists and conference speaker lists for the claimed specialism.
4. B2B contact databases: ZoomInfo, RocketReach, SignalHire, The Org, Lusha.
5. The company's own LinkedIn company page "People" tab — only visible to a logged-in
   user; ask them to check it.

## What to ask the logged-in user for

- Screenshot of the top card: photo, headline, location, connections vs followers, any
  **Verify** badge.
- The experience section with **dates** — not just titles.
- Mutual connections, and whether any are people they actually know.
- The opening message itself, pasted as text.

## Photo check

Ask the user to right-click → search image (or upload it) — reverse image search needs
the logged-in session or an upload you cannot perform from a walled page. A photo that
matches a stock library, a different professional, or several unrelated profiles is a
strong red flag; a photo that matches the same person's conference bio is a green one.
