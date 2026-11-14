---
name: reddit-mining
description: "Use when mining Reddit at scale from a blocked IP."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Research, Reddit, Arctic Shift, Pushshift, Corpora]
    category: research
    related_skills: [blocked-page-recovery, grounded-citations]
---

# Reddit Mining

**Reddit will not let a server in the front door.** From a datacenter IP, `reddit.com`,
`old.reddit.com`, `api.reddit.com` and every `.json` endpoint return `403 Blocked`, and
the real browser is blocked too ("You've been blocked by network security") — the block
is on the IP, not on the client or the User-Agent. Do not burn calls discovering this:
go straight to the **Arctic Shift** mirror API and pull a bulk corpus from there.

## When to Use

- "What do people say about X" where the answer lives in threads and comment sections
- Gathering user feedback / sentiment / design debate at scale across subreddits
- Any task needing Reddit posts or comments as a corpus for analysis

Skip it for a single known thread you can cite directly — but note the front door is
still blocked, so even one thread goes through the API (or `blocked-page-recovery`).

## The Access Ladder

Try in this order; stop at the first that works.

1. **Arctic Shift** — `arctic-shift.photon-reddit.com/api`. Pushshift-style, no auth, bulk
   posts + comments + full-text search. This is the workhorse. Use it first.
2. **Pullpush** — `api.pullpush.io`. Same shape, but frequently `429` from shared IPs.
   A second choice with backoff, not the first.
3. **Redlib / teddit mirrors** — mostly `429`, `410 Gone`, or an Anubis JS challenge
   ("Verifying your browser"/"Making sure you're not a bot"). Do not build a pipeline on
   them; they rotate and die.
4. **Jina Reader** — only with `JINA_API_KEY` set (anonymous access is `403`).
5. **reddit.com direct** — assumed blocked from a server. Only try it from a residential
   path; never loop on it.

## API Quick Reference (verified)

Base: `https://arctic-shift.photon-reddit.com/api` — all GET, return `{"data": [...]}`.

| Endpoint | Purpose |
|---|---|
| `/posts/search` | submissions |
| `/comments/search` | comments |
| `/subreddits/search` | sub metadata (`subreddit_prefix=`) |

Params that matter:

- `subreddit`, `author` — filters (single value).
- `query` — full-text on **posts** only.
- `body` — full-text on **comments**. There is no `query`/`q`/`text` on comments; using
  the wrong name returns `400 Unknown query parameter: 'x'` (the error tells you the truth).
- `link_id` — pull a thread's comments (pass the `t3_...` id or the bare post id).
- `limit` — **max 100** per request.
- `sort` = `asc`|`desc`; `sort_type` = `default`|`created_utc` only.
- `after` / `before` — `YYYY-MM-DD` or unix epoch. Half-open window.

**There is no score sort.** To approximate "top posts", page time windows and sort locally
by `score`. Post fields: `id, subreddit, title, selftext, score, num_comments, created_utc,
permalink, link_flair_text, upvote_ratio`. Comment fields: `id, link_id, parent_id, score,
body, created_utc, author, depth`.

Error meanings:

- `422 {"error":"Timeout. Maybe slow down a bit"}` — the query is too heavy (usually
  full-text across a big sub with no date window). Fix by narrowing `after`/`before`,
  not by retrying the same call.
- `429` — rate limited. Back off exponentially.
- `400` — bad param name or value; read the message, it names the offender.

## Procedure

1. **Probe once** with a tiny request (`subreddit=...&limit=2`) to confirm the mirror is up.
2. **Sweep posts by time window.** Page quarterly windows with `sort=desc&sort_type=created_utc`,
   using the oldest `created_utc` seen as the next `before` cursor, ~3 pages per window.
   Write each post to a JSONL immediately.
3. **Select threads, not posts.** Rank by `num_comments` and by design-keyword title match.
   Ranking by `score` returns memes, not arguments.
4. **Pull comments** per selected thread with `link_id=<id>&limit=100`, paging with `before`.
   Comments are where the reasoning is; the submissions are mostly jokes and questions.
5. **Analyse** (see `scripts/reddit_analyze.py`).

### Make every sweep resumable and budgeted

A single tool call will not finish a real corpus. Pass a wall-clock budget (e.g. 240s) and
keep a state file of completed `(subreddit, window)` / thread ids; on timeout the script
prints remaining work and exits clean. Re-invoke it to continue. Append-only JSONL means a
killed run never loses data. This is the difference between a corpus and a re-scrape.

## Selecting Signal

- **Top-by-score is a trap.** Front-page hits are memes, screenshots and jokes.
  Use `num_comments` (argument volume) plus keyword-matched titles.
- **Drop short comments.** Filter to `len(body) >= 180` to bias away from one-liners.
- **Join comments to their post** via `link_id` (strip `t3_`) to recover the thread title
  and subreddit for context — a quote without its thread is unusable.
- Sweep the **general** subs too (`r/gamedesign`, `r/truegaming`, `r/4Xgaming`), not just the
  product subs: the durable design theory usually comes from there, while the product subs
  give concrete complaints.

## Analysis

- **Build theme regexes as simple, escaped alternations — and compile-check before the run.**
  One unbalanced group or stray quantifier in a bucket pattern aborts the whole
  `execute_code` cell (`re._parser.parse` error) and burns the call. If the patterns come
  from a keyword list, `re.escape` each term and join with `|` inside one non-capturing
  group; `for rx in THEMES.values(): re.compile(rx)` up front makes it fail cheaply.
- Bucket comments by regex theme, then read the **highest-scored substantive** comment per
  theme — that is where the load-bearing argument is.
- Quote verbatim and keep the thread permalink; Reddit quotes are evidence and need provenance.
- Separate **what the community says** from **your synthesis**. Label the synthesis.

## Caveats to carry into any writeup

- **Selection bias.** Top-comment and keyword-thread sampling over-represents vocal critics.
- **Upvotes reward jokes and confident contrarians**, not correctness.
- **The mirror can lag** a few days at the edges, and some threads may be missing.
- **Factions are real.** A loud complaint ("the war system is bad") often has a substantial
  silent-but-upvoted opposing camp ("the micromanagement was worse"). Report the split as a
  tension, never as a verdict.

## Files

- `scripts/reddit_sweep.py` — resumable, budgeted posts + comments sweeper.
- `scripts/reddit_analyze.py` — dedupe, theme-bucket, extract top quotes with thread context.
- `references/arctic-shift-api.md` — full endpoint/param reference and worked URLs.
