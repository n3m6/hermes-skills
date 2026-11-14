# Mining community corpora (Reddit and forum feedback at scale)

For a teardown that needs *voice-of-the-customer* depth beyond a bounded review
sample: what the community argues about, not just what it upvotes. Pairs with
`game-market-metrics.md` (which covers the store-page side).

## Access: Reddit blocks the host — use the mirror API

- `reddit.com` (and `*.json`, `api.reddit.com`) returns `403 Blocked` from a
datacenter IP, and the IP-level block can extend to the browser session
  ("You've been blocked by network security"). Don't retry in a loop, and never
  route a blocked site through a generic web proxy.
- Read-only redlib/teddit frontends are mostly bot-gated (Anubis challenge) or
  dead (`429`/`410`). One quick probe is enough; don't invest in them.
- **The route that works: Arctic Shift**, a Pushshift-style mirror at
  `https://arctic-shift.photon-reddit.com/api`. `api.pullpush.io` is the other
  mirror but rate-limits hard (`429`) — try it once, then fall through. Both are
  open JSON; a plain UA is fine.

| Need | Endpoint | Params |
|---|---|---|
| posts | `/posts/search` | `subreddit`, `query` (title/body full-text), `limit<=100`, `sort=desc`, `sort_type=created_utc`, `after`/`before` (`YYYY-MM-DD`) |
| comments | `/comments/search` | `subreddit`, `link_id` (thread id, no `t3_` prefix), **`body`**, `limit`, `sort`, `after`/`before` |

## Pitfalls that cost time

- **The comment full-text param is `body`.** `query`/`q`/`text` are rejected
  (`Unknown query parameter`).
- **No score sort.** `sort_type` accepts only `default|created_utc` — fetch by
  date window and sort by `score` locally.
- **Unbounded full-text queries time out** (`422 Timeout. Maybe slow down a bit`)
  on large subs. Bound every query with `after`/`before` (a quarter is safe) and
  back off between retries.
- **Window pulls without a query are cheap** (~1-3 s per 100 posts). Fetching a
  date window and filtering locally beats firing many keyword searches.

## The sweep: resumable collector, not one long call

A corpus harvest outlives a single tool call. Write a script that:

- takes a **seconds-budget** argv and appends to a JSONL file, with a state file
  of completed `(sub, window)` pairs — so each call resumes where the last stopped
  and a timeout loses nothing;
- pages *within* a window by setting `before` to the oldest `created_utc` seen;
- keeps only slim fields (`id, sub, title, score, num_comments, created_utc,
  permalink, flair`, first ~1800 chars of selftext).

Re-run in chunks of ~200-280 s until it prints `remaining=0`, then dedupe by id.
Use the same pattern for the comment pass.

## Thread selection

Per subreddit, take the top ~12 threads by `num_comments` **plus** the top ~10 by
comment count whose title matches design/discussion keywords. Comment counts find
the arguments; keywords find the topical ones. Then pull each thread's comments by
`link_id` (100/page, 2 pages), keeping the highest-scored.

## Where the signal actually is

- **Top-scored posts are memes.** Design reasoning lives in the comments — mine
  comments, and use posts only to *choose threads*.
- **Filter for substance before theming**: drop comments under ~200 characters;
  short high-score comments are jokes and one-liners.
- Bucket the survivors with theme regexes (agency, AI/opponents, economy,
  pacing/late-game, DLC/monetisation, depth-vs-accessibility, onboarding/UI,
  flavour, mods, bugs/perf), read the top substantive comment per theme, then read
  the top ~15 comments of the pivotal threads in full. Quote verbatim, with score
  and thread link.
- **Communities are split, not unanimous.** Report a real tension (e.g. micro vs
  abstraction) as a tension, say which side is louder, and don't flatten it to a
  verdict.

## Reporting discipline this user audits

State provenance in three explicit tiers: what you fetched directly, what you saw
only as a search snippet, and what is your own synthesis. Name any load-bearing
number that leans on a weaker source than the rest. He asks "what did we mine?"
and checks — a blurred tier discredits the whole report.
