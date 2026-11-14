---
name: product-teardown
description: "Teardown products; verify people and outreach are legit."
version: 1.2.0
author: Hermes Agent (curator)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [product, competitor, teardown, recon, market, osint, identity, diligence]
    related_skills: [game-production, sourced-country-files, reddit-mining, grounded-citations]
---

# Product Teardown (external recon from the public web)

Core value this serves: report shipped reality vs marketing claims, and never blur the two. The user checks; a teardown that parrots landing-page copy back is worthless.

## When to use
- "Explain this product to me" / "get familiar with <site>"
- Competitor analysis, diligence, partnership vetting
- Vetting a person, profile, recruiter or seller — "is this account legit"
- Grounding any writing about a product in evidence (before GTM work, reviews, comparisons)

## Legitimacy triage (inbound outreach: recruiter, VC, "we saw your GitHub")

The domain, not the profile, is the first check — a profile takes an hour to build, a
domain leaves a registration trail. Full playbook:
`references/person-and-account-vetting.md`.

1. **WHOIS the sender's domain before reading the message twice.** Creation date first: a
   firm claiming years of history on a domain registered weeks ago is a lure, and a
   one-year registration is a burner. `.fi` → Traficom; otherwise RDAP over curl (`curl -s https://rdap.org/domain/<d>`). **There is no `whois` binary on this box** — a bare `whois` call is a dead call, not a check.
2. **Registrant vs brand.** Free-Gmail tech contact, a fabricated street/ZIP (country
   mismatch, wrong digit count in the company number), a registrar parking page, or a
   domain that 301s to the real firm's `.com` — all disqualifying. That is impersonation.
3. **Mail auth is decorative**: SPF pass on a shared host, `_dmarc p=none`, no DKIM. A
   passing SPF on a Hostinger plan means nothing; say so instead of quoting it as evidence.
4. **Borrowed credibility**: recognizable names in CC, personal Gmails, no named sender,
   no signature, no requisition. That CC list harvests bounces, not endorsements.
5. **The payload comes after engagement** — fake "meeting app" installers, take-home repos
   with a postinstall script, "audit" repos with a wallet drainer. Advice: don't install
   their app, don't run their repo, don't connect a wallet, don't paste anything in Terminal.
6. **Report verdict-first**: the hard evidence, then what could NOT be verified. A real
   person whose message matches their public work IS a legitimate outcome — say "legit"
   when it is, and reserve "could not confirm" for the genuinely thin case.

### Drafting the reply

- The draft is the deliverable: **≤60 words, one question**, no preamble, no explaining the
  draft. He asked twice in one thread for shorter and for "without the 20 minutes".
- **Never commit his time or availability** ("happy to jump on a 20-min call"). He sets
  that; draft the ask without it.
- When vetting is inconclusive, ask the one question that discriminates (which company,
  which requisition, real capital or paper) rather than proposing a call.
- When he says "tell them we're not hiring", one line says exactly that; keep the rest.

## Method
1. **Shell check first**: `curl -sL -A "<browser UA>" <url> -o /tmp/site.html -w "HTTP %{http_code} | %{url_effective} | %{size_download} bytes\n"`
   - Tiny HTML + `<div id="root">` + `/assets/index-*.js` = SPA; the real copy lives in the JS bundle, not the HTML.
2. **Render anyway** (browser_navigate) — catches client-side redirects and gives the a11y tree. Pitfall: the compact a11y snapshot drops prose (paragraphs render as empty). Get full copy via browser_console: `document.body.innerText`.
3. **Link inventory** via browser_console JS: `Array.from(document.querySelectorAll('a')).map(a=>({text:a.innerText.trim(),href:a.href}))`. Dead links have `href="#"` (placeholder stage); real links reveal whitepaper PDFs, /docs, /manifesto, subdomains.
4. **Fetch and fully read every substantive linked asset** (whitepaper, manifesto, docs). PDFs: `curl` then `pdftotext -layout file.pdf file.txt` (poppler-utils if missing), then read_file in ~200-line chunks. A whitepaper IS the spec — read it end-to-end; extract architecture, numbers, and comparison tables.
   - Doc sites publish machine-readable forms: append `.md` to any page URL for markdown, and fetch `/llms.txt` for the whole tree. Faster and cleaner than scraping HTML — do both before rendering anything.
   - **Footnotes and limitations asides are primary evidence.** A one-line footnote in the spec ("does not currently operate as a privacy-focused rollup") is frequently the single most load-bearing fact about the product's trust model, and it is never in the landing copy. Read them; quote them.
5. **Bundle archaeology** — grep the minified JS for the real product surface behind the marketing:
   - API hosts: `grep -oE "https://api\.[^\"']+" bundle.js | sort -u`
   - Endpoints/websockets: `grep -oE "(/api/[^\"']+|wss?://[^\"']+)" bundle.js | sort -u`
   - RPC URLs reveal chain integration (e.g. Solana mainnet/devnet/testnet = wallet adapter present)
   - Context around hits: `grep -oE ".{80}<KEY>.{160}" bundle.js`
   - A live backend (`api.<domain>` with real endpoints) vs a marketing-only site is the single most important stage signal.
6. **Mock-vs-live check**: grep a formatted display value (e.g. a price string like "91,614"). A single hardcoded occurrence cloned into a marquee = cosmetic demo data. Say so explicitly.
7. **Cross-asset claim drift**: compare landing copy vs whitepaper vs bundle (e.g. landing "200k TPS / <300ms finality" vs whitepaper "150k ops/s / sub-200ms"). Flag inconsistencies as observations.
8. **Report**: verdict-first explanation — (a) what the product is in one line, (b) the problem it solves in plain language, (c) architecture/mechanics, (d) what is ACTUALLY shipped right now, (e) honest observations (claim drift, dead links, cosmetic data, trust-model limits).

## When the target ships source: recon the implementation

For technical products (crypto, infra, dev tools) the web presence is the weakest evidence available. If there is a public repo, the pipeline is readable — go read it; the recipe lives in [references/source-and-docs-recon.md](references/source-and-docs-recon.md) (org/repo discovery, reading a repo without cloning, the doc-site `.md`/`llms.txt` trick, whitepaper grep, cross-checking against our own stack).

Rules that decide this half of a teardown:

- **Marketing docs state intent; manifests and build scripts state the pipeline.** Reconstruct the stack from dependency lists, build scripts, and the source directory inventory *before* repeating any architecture sentence from the paper. The paper is what they meant to build.
- **Check for convergent stacks by name.** Grep their manifests for components you also depend on. A shared vendored component is the highest-value comparison in the whole exercise: either independent validation of your own choice, or a divergence that is a defect on one side. Report which fork/version each side pinned.
- **Their performance, gas, and cost figures are claims until reproduced.** Say so explicitly, with the same discipline we apply to our own measurements.
- **Footnotes are where the trade-off is admitted** (see step 4). Lead with them when they contradict the abstract.

## Comparing the target against the user's own system

When the user owns the thing being compared against ("compare theirs to ours, what are we doing wrong, what can we learn"), the deliverable is not a summary — it is an honest diff, and the user wants the self-criticism first-class, not softened:

1. **Verdict first**, in one short paragraph: are these the same product? Name the single structural decision that explains every downstream difference, because that is what makes the rest of the list readable rather than a pile of features.
2. **Where the two converge** — and what that validates about our work. Convergence found independently is evidence; say so.
3. **Pros and cons both directions**, including a section for what *we* lack. Flattering asymmetries destroy the report's credibility with this user.
4. **"What we are doing incorrectly"** — ordered by size, each item quantified against our own measured numbers rather than adjectives. Pull those numbers from our registers (measurements, obligations, ADRs), not from recollection: the credibility of the whole comparison rests on our side being cited as carefully as theirs.
5. **"What to learn and adopt"** — ordered by value, each item carrying its precondition or caveat. An adoption recommendation with no stated cost is a marketing bullet.
6. **Close with what could not be verified** — what you read vs what you inferred, and which of their claims remain their claims.

## Games and pre-release products: the numbers you can actually get

For games the public presence *is* the store page, and the numbers come from the
platform's own endpoints rather than third-party trackers. Endpoint list, BBCode
cleaning, wall fallbacks and how to read a pre-release title honestly:
[references/game-market-metrics.md](references/game-market-metrics.md).

When the ask is *what the community says* — what works and what does not, not
just the score — mine the whole forum corpus, not a bounded review sample.
Reddit's mirror API, the resumable sweep, and the comment-first reading method:
[references/forum-corpus-mining.md](references/forum-corpus-mining.md). The
operational home, with the runnable sweeper scripts, is the `reddit-mining` skill.

- Review counts are a sales *proxy* — label them as such, never convert them to
  units.
- Wishlist/follower counts are not public: write "could not verify" instead of an
  estimate. A store page's feature list is a claim until the title ships; the
  dev-diary corpus is where admitted weaknesses live.

## The competitor-study deliverable (analysis + lessons, never in their repo)

When the target competes with a product the user owns, the deliverable is TWO
native Google Docs, not one report — the second is the part the user keeps:

1. **Competitive analysis** — verdict first; product facts; commercial shape
   (prices, DLC/monetisation ladder); review and player trajectory; where it is
   strong and where it leaks; relevance to the user's own design (every
   positioning wedge must cite the user's own document, pillar or register item);
   where NOT to compete; closing data-gaps section.
2. **Lessons** — numbered, each anchored to a dated verbatim quote from the
   target's own published posts, plus a "what is NOT a lesson" section (their
   choices are consequences of a different product decision, not mistakes to
   copy) and a closing "the three things I would do with this".

Rules that hold for every one of these:
- **Never write competitor material into the product's own repo.** The repo is its
  source of truth and its design history; competitor notes are not design. Keep
  fetched raw material in the scratch cache (`~/.hermes/cache/scratch/<target>/`)
  and deliver to Drive.
- **Mine the post-mortems, not the marketing.** For a shipped title, filter the
  news archive's titles for `post-release`, `post release`, `retrospect`,
  `anniversary`, `roadmap` and the launch-day plans post. Studios admit what went
  wrong there and nowhere else — that is where the lessons actually are, and a
  cheerful anniversary post is the counter-example that proves the filter works.
- **Ownership and sharing are the user's call.** Docs land under the authenticated
  Workspace account, not the user's personal mailbox; never change sharing or
  permissions without asking.
- **Label sampling.** Review themes read off N sampled reviews are indicative, not
  a corpus analysis — state N. Review counts from the store page and from the
  review API differ by purchase-type filter: cite both, say which is which, and
  never quietly pick the flattering one.
- **Report provenance in three tiers** — what you fetched directly, what you saw
  only as a search snippet, and what is your own synthesis — and name any
  load-bearing number that leans on a weaker source than the rest. This user
  audits it ("what did we mine?"); a blurred tier discredits the whole report.
- **Delivery mechanics are scripted**: [scripts/gdocs_report.py](scripts/gdocs_report.py)
  turns a markdown-ish file into a styled native Doc (skipping the manual heading
  styling and folder-move dance each time).

## Vetting a person or account (identity diligence)

Same discipline applied to a person: "is this recruiter/account legit", "can I trust
this profile", a forwarded suspicious DM, or an account presented as evidence of a
business relationship. The deliverable is a decision, not a dossier.

- **Line 1 is the verdict**: `Legit` / `Likely legit` / `Cannot verify` / `Likely
  fake`. "Cannot verify" is a real and common verdict — an unverifiable account is
  not a fake one, and calling it fake without evidence is as dishonest as vouching.
- Then a **verified / could-not-verify split**, **ranked flags** (green/yellow/red)
  each with the mechanism, not just the label — green: mutuals they actually know,
  a dated history that tracks independently verifiable events, one consistent photo;
  yellow: thin network for the claimed seniority, no footprint off the platform,
  employer unconfirmable anywhere, a headline that reads like a job description;
  red: a photo reused from stock or another person, impossible dates or companies
  that do not exist, several near-identical accounts, a new account claiming a long
  career. Then 3–5 checks the user can run from inside their logged-in session, and
  a request for the message text or a screenshot (wording is the fastest intent
  signal, and a screenshot hands over fields guest access cannot fetch).
- **Separate three questions that fail independently**: identity (a real person),
  affiliation (works where claimed), intent (is the approach a scam). A real
  person's identity can be cloned into a fake account; a real employee can be a
  fraudster; a fake account can be doing no harm. Say which one you are answering.
- Harvest the search-index card first (exact profile URL; `"Full Name" <platform>`),
  date the account from its own activity ids, corroborate the employer against team
  pages, newsroom releases, award and speaker lists and B2B contact databases, and
  test the **name** separately from the **profile** — a real name does not prove
  this profile belongs to it.
- Score network size against the claimed role, not a universal number; report
  sibling accounts under the same name as context, not conviction.
- **Never upgrade a verdict because the posts look real** — fake personas repost
  genuine industry news precisely because it looks checkable. Don't read a
  locked-down profile as concealment (it is a blocker, not a tell); don't burn calls
  on a proxy ladder for a walled profile (one archive attempt, then ask the
  logged-in user for a screenshot); do the searching yourself; state the timestamp
  of the evidence.
- Red in the message regardless of profile quality: investment or crypto
  "signals", a job offer requiring the user to buy equipment or forward funds,
  pressure to move to WhatsApp/Telegram, ID/passport/selfie requests, romance
  framing, urgency plus secrecy, any "verification" link that needs a login.
- Walled-profile procedure and the activity-id decoder:
  `references/person-and-account-vetting.md`.

## Pitfalls
- Never conclude from the compact a11y snapshot alone — prose gets dropped; always innerText for copy.
- Never assume social/legal links work; `#` hrefs mean not-yet-shipped.
- Minified bundles run 1MB+; grep is right for strings/endpoints, wrong for logic.
- Separate marketing stage (waitlist/landing) from shipped functionality (real endpoints in the bundle).
- Landing tickers/stats are frequently hardcoded — verify before quoting them as live.

## Worked example
A DEX/wallet-shaped target follows one spine: shell check finds a `<div id="root">` SPA → bundle grep
surfaces a live backend (`api.<domain>`, `/api/*`, ws mirrors) → the whitepaper PDF is read end to end,
trust model first (TEE/attestation, proof construction, settlement chain, disclosure model) → the ticker's
formatted numbers appear exactly once in the bundle, i.e. hardcoded → landing-vs-paper claim drift is
logged as an observation, not smoothed. Report the findings off that spine, not the sequence of fetches.

Launch planning is a separate, forward-looking job: use `game-production`. Market *measurement* stays here.
