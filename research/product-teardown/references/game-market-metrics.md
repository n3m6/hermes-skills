# Game market metrics from public sources

Steam's own endpoints give most of what a game teardown needs. Third-party
trackers (SteamDB, games-stats, Steambase) sit behind IP bans and Cloudflare
challenges and are not worth routing around when the source data is public.
Always send a desktop browser UA — bare curl gets stripped responses. The
endpoints below are JSON APIs, so fetch them from a python loop (`urllib`), not a
bash `for url:path` loop (splitting on `:` shreds `https://`).

## The endpoints that work

- **Name → appid**: `https://store.steampowered.com/api/storesearch/?term=<query>&cc=us&l=en`
  gives `items[].id`/`name`. Match the title exactly; `items[0]` is frequently a
  demo, a DLC or an unrelated same-named game.
- **Facts**: `https://store.steampowered.com/api/appdetails?appids=<id>&cc=us`
  → release date, price, developer, publisher, `recommendations.total`, languages,
  categories, and the `dlc` array of every DLC appid.
  - **Do not index the response by the appid you asked for.** Steam sometimes keys
    the payload by a different id and carries the real one inside
    (`data.steam_appid`); reading `j[str(appid)]` then raises `KeyError`. Take
    `list(j.values())[0]["data"]` and sanity-check `data.name`.
  - Per-DLC names, prices and release dates come from one appdetails call per
    id in `data.dlc` (skip any that 404 or return an unreleased stub). Iterate the
    array — it is the monetisation ladder, and expansions vs "mechanics packs" vs
    immersion/region/music tiers is a positioning fact, not trivia.
- **Size**: `https://store.steampowered.com/appreviews/<id>?json=1&num_per_page=0&language=all`
  → `query_summary.total_reviews` / `total_positive`. This is the only public
  proxy for units sold: report it as a proxy, never convert it into a sales figure.
  - `purchase_type` changes the population: `all` counts key/free activations,
    `steam` counts store purchases only. The store page and the API therefore
    disagree by design — cite both and say which is which.
  - **A date window needs `num_per_page>0`.** With `num_per_page=0` the
    `filter=recent&day_range=30` query silently returns the ALL-TIME summary; with
    `num_per_page=100` it returns the window. If recent and all-time numbers look
    identical, that is the bug, not a stable game.
  - **Prefer the store page for the last-30-days figure.** The API window is fussy:
    even with `num_per_page>0`, a large `day_range` can return a window that is not
    the 30 days you asked for. The store page HTML is unambiguous —
    `<div class="subtitle column">Recent Reviews:</div>` followed by the
    `game_review_summary` span (the descriptor) and, in `responsive_reviewdesc`,
    `- N% of the M user reviews in the last 30 days are positive`.
  - **`query_summary` is not a fixed shape.** Once `review_type` or a `day_range` is
    set it can collapse to just `{'num_reviews': N}`, so indexing `total_reviews`
    raises `KeyError`. Read `total_reviews` only from the plain all-time call.
  - **The `reviews[]` array does honour `review_type`/`day_range`** even when the
    summary misreports — filter the list to pull, e.g., the window's negative
    reviews. A recent-window count on an older title is tiny (tens to low
    hundreds): say N and treat the percentage as noisy.
- **What the developer has actually said**: `https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=<id>&count=2000&maxlength=200000`
  → full post bodies.
  - **A small `maxlength` truncates every body to a stub** — a dev diary comes back
    as `"H..."` and can be mistaken for a client-rendered page. Pass a large value
    (200000); if bodies look like stubs, check `maxlength` first.
  - `count=2000` returns the whole archive of a multi-year title (hundreds of
    items), and `enddate=<unix>` pages further back than the newest window.
  - **The feed mixes studio posts with syndicated third-party press.** Count the
    numbered dev diaries and update/hotfix posts by title regex; never report the
    raw item count as the developer's output. Titles alone give the patch, DLC and
    release timeline.
- **Player history**: `https://steamcharts.com/app/<id>` — the monthly table parses
  with a `<tr>`/`<td>` regex (cells carry `month-cell`; `num-f` is average, `num` is
  peak). How far back it reaches varies: page 1 can carry several years for a
  long-lived title, so check the earliest row before writing a launch peak off as
  unverifiable rather than assuming a thirteen-month window. The shape to look for
  is the launch/DLC spike followed by decay, which is how a live DLC-funded title
  behaves.
- **Live concurrent, right now**:
  `https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=<id>`
  → `response.player_count`. The instant reading sits above the monthly average on
  weekends and update days — pair it with the monthly table, never report it alone
  as the trend.
- **Owner band (coarse proxy only)**:
  `https://steamspy.com/api.php?request=appdetails&appid=<id>` answers without a
  wall and gives an `owners` band (e.g. `1,000,000 .. 2,000,000`). Use it as an
  order-of-magnitude claim at most. **Ignore its `ccu` field** — it is stale, not
  live; get a live count from `GetNumberOfCurrentPlayers`.
- **The store page HTML itself** is fetchable with curl + UA and carries the
  description, feature list (single/multiplayer, Workshop, achievements),
  supported languages, user tags, system requirements and any Steam annotation such
  as a notice that periods of *off-topic review activity* have been excluded from
  the score. Quote such a notice as an observed fact; do not attribute a cause you
  could not verify.
- **A shipped title's reception**: `https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1&format=json&titles=<Title>`
  returns a clean extract whose Reception section usually quotes the original
  reviews (who praised which system, and the one sentence each critic used to name
  the flaw). Cheap, citable, and it is the launch-window story that the store page
  will never tell you.

## Cleaning Steam news bodies

Bodies are Steam BBCode with embedded markup. Strip in this order, then flatten
and drop duplicate consecutive lines (Steam repeats nav and boilerplate):
`<script|style>` blocks → tags → `\[/?[a-z0-9*=][^\]]*\]` (BBCode) →
`\{STEAM_CLAN_IMAGE\}\S*` (image handles) → collapse whitespace. Drop the
recurring "What's happening / TLDR: developer diaries introduce details of…"
boilerplate paragraph before reading a diary.

## Reading sentiment from the review API

- Pull a bounded sample (`?json=1&language=english&purchase_type=steam&num_per_page=100`,
  optionally `review_type=negative` and a `day_range` to scope it), then split
  `reviews` on `voted_up`. Count word frequencies over the negative set and read a
  handful of the longest in each direction. Report it as a sample of N.
- `reviews[].author.playtime_forever` (minutes) is the most useful field nobody
  quotes: the average playtime of *positive* reviewers measures how deep the
  audience is, and the gap between that and the negative set is usually the
  onboarding story told in one number.
- **Turn an "off-topic review activity" notice into a verdict.** When a beloved
  title's store page shows a collapsed 30-day score plus that notice, pull the
  window's negative reviews and read them: a single-language cluster of off-topic
  content (nationalist spam, a pricing protest, a coordinated campaign) is a review
  bomb, not a design signal. Report it as a bomb and fall back to the all-time
  score and the player-count trend for the real read — never quote the bombed
  percentage as a design verdict.

## Walls and fallbacks

- Cloudflare-fronted studio/publisher sites answer a challenge page to curl and to
  reader proxies; content and preview sites may `429` under a burst. A `429` is a
  pacing problem: sleep 15-30s and retry rather than changing the UA.
- When an aggregator is walled, substitute a *different primary source* rather than
  fighting the wall — the platform's own API for facts, a player-count table for
  concurrency, Wikipedia's sourced reception for launch coverage. Aggregators are
  also frequently stale for unreleased titles.
- `https://r.jina.ai/<url>` (prepend to the full URL) returns readable text for
  rate-limited article pages. It does not solve a Cloudflare challenge.

## Reading a pre-release title honestly

- Everything on a store page is a claim. The dev-diary corpus is where intent and
  admitted weakness live — release-date slips, the developer's own list of what
  still blocks release, systems he calls deliberately thin. Quote it with dates.
- The store tag list is a positioning fact: tags a competitor already owns are tags
  the user's own product must not claim identically.
- Follower/wishlist counts are not public. If a number cannot be fetched, say so in
  the report — never estimate one. Press roundup rankings are citable only as
  "per <site>".
- Size the niche and the benchmark audience separately: compare like-for-like
  review counts for genre neighbours, and name the audience-defining titles (far
  larger) as a separate number rather than mixing them into one figure.
- When the user owns the thing being compared against, pair each competitor
  strength with the user's own decided design line that answers it, and cite the
  design document or register item — positioning claimed without a citation is
  just a wish.
- Unverified name-alike repos and fan "prototype" projects show up for announced
  titles. Do not open or cite them without a link from an official source; list
  them as unverified.

## Reading a shipped title: the trajectory, not the snapshot

- Build the timeline from news titles first (updates, hotfixes, DLC drops, open
  betas, changelog posts), then read the post-mortem diaries in full. The studios
  that say "this release was not okay" also name the mechanism that caused it.
- The headline review score is set in the launch window and barely moves afterward.
  Recovery shows up in recent-review percentages, player-count spikes and press
  headlines — say which of those you are reading.
- A long-lived title's open-beta branch and published-changelog habit are the
  release machinery worth reporting: they tell the user what shipping looks like at
  the top of this genre, and what it costs.
