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

## Step 0: the domain, not the profile

A LinkedIn profile is free and takes an hour to fake convincingly; a domain registration is
dated, permanent, and cheap to query. **Do this before any profile recon.**

- RDAP first: `curl -s https://rdap.org/domain/<domain>`. **No `whois` binary on this box**
  (2026-11-02: `whois` → `command not found`, one wasted call); use it only where installed.
  Read in this order: **created / expiry**, registrant org,
  tech/admin contact email, registrar + reseller, nameservers, MX.
- **Age is the whole game.** A fund, agency or "established platform" whose domain was
  registered weeks before it emailed you is a lure. A one-year registration on a firm
  claiming institutional history is a burner.
- **.fi registry = Traficom** (whois.traficom.fi); other ccTLDs have their own registry
  whose output is richer than the thin ICANN `whois` port-43 answer.
- Registrant signals that disqualify on their own:
  - tech contact on a **free Gmail** rather than the corporate domain;
  - a registrant address that does not exist (street/ZIP country mismatch, US ZIP on a
    "French" company, company-number digit count wrong for the country);
  - nameservers/MX on a **registrar parking plan** (`*.dns-parking.com`, parked `noindex`
    page) — a firm with real capital does not run HR mail off that;
  - the domain merely **301s to the real company's `.com`** — impersonation by redirect.
- **Mail auth**: `_dmarc p=none`, no DKIM selector, SPF that includes the shared host. All
  of it is decorative. Do not present "SPF passed" as corroboration.

## Crypto/Web3 recruitment lure — the recurring shape

Four unsolicited crypto/Web3 approaches arrived in one week (2026-10-18 → 10-24): two
clear lures, one cold sales/lead-gen pitch, one genuinely legit practitioner. The tells,
cheapest first:

1. **Unsolicited + generic role + crypto** ("Blockchain Tech Lead", "Web3 staking") with no
   company in the first line, no named sender, no requisition.
2. **Borrowed credibility in CC or in the text**: recognizable names on personal Gmails
   (e.g. a known protocol founder) added to "vouch" for a cold blast. It is a bounce
   harvest — it tells the sender which inboxes are live.
3. **A shell "partner" company**: LinkedIn page with few followers, image assets dated
   months not years, contradictory company facts ("founded 2022" + "Public Company" +
   11-50 employees), and its own domain parked on the same IP as the sender's.
4. **The ask arrives late.** Stage one is conversation; the payload is a "meeting app"
   installer, a take-home repo with a postinstall script, or an "audit" repo that drains a
   wallet. Never install, never run, never connect a wallet.
5. **What to tell the owner**: verdict first, hard evidence second, unverified third, and
   the specific next action ("don't reply", "ask which company this requisition is for").

Worked example (10-19, `lasalle.fi`): created 17 Aug 2026, one-year term, registrant
"Cointree Investing" with a Gmail tech contact, fabricated "North Creek, France, 12853"
address, Hostinger parking nameservers, `_dmarc p=none`, 301 to the real JLL-subsidiary
`lasalle.com`. Verdict: phishing lure. Copy that evidence ladder — it took ten calls and no
login.

## Reply drafting (what he actually wants)

- **≤60 words, one question, the message only.** He asked twice in one thread: "Shorter
  more inquisitive", then "a reply without the 20 minutes". Long drafts get sent back.
- Keep any 20-minute call, availability or scheduling line **out** — he sets that, not you.
- Inconclusive vetting → one discriminating question (real capital or paper; which company;
  which requisition) beats any proposed call.
- "Tell them we're not hiring" → one clause says exactly that, and the rest of the reply
  stays as drafted.
