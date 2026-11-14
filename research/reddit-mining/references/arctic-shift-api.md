# Arctic Shift API — reference

Base URL: `https://arctic-shift.photon-reddit.com/api`
All endpoints are GET and return `{"data": [...]}` (or `{"data": null, "error": "..."}`).
No auth. Send a browser-ish `User-Agent`.

## Endpoints

### `/posts/search`

| param | notes |
|---|---|
| `subreddit` | single subreddit name, no `r/` |
| `author` | single username |
| `query` | full-text over title+body (posts only) |
| `limit` | 1-100 |
| `sort` | `asc` \| `desc` |
| `sort_type` | `default` \| `created_utc` |
| `after`, `before` | `YYYY-MM-DD` or unix epoch |

Post object fields used in analysis:
`id, subreddit, title, selftext, score, num_comments, created_utc, permalink,
link_flair_text, upvote_ratio`.

### `/comments/search`

| param | notes |
|---|---|
| `subreddit` | single subreddit name |
| `author` | single username |
| `body` | **full-text over comment bodies** — this is the comments search param |
| `link_id` | restrict to one thread; pass `t3_<id>` or bare id |
| `limit`, `sort`, `sort_type`, `after`, `before` | as above |

Comment object fields:
`id, link_id, parent_id, score, body, created_utc, author, depth`.

### `/subreddits/search`

`subreddit_prefix=` returns matching subreddits with `_meta` counts
(`num_posts`, `num_comments`, earliest timestamps).

## Worked URLs

```
# newest 100 posts in r/victoria3 within a quarter
/posts/search?subreddit=victoria3&after=2026-07-01&before=2026-10-01&limit=100&sort=desc&sort_type=created_utc

# next page: reuse oldest created_utc as the new before cursor
/posts/search?subreddit=victoria3&after=2026-07-01&before=2026-09-14&limit=100&sort=desc&sort_type=created_utc

# all comments of one thread, 100 at a time
/comments/search?link_id=1hnnadw&limit=100&sort=desc
/comments/search?link_id=1hnnadw&limit=100&sort=desc&before=2026-01-10

# full-text comment search, kept cheap with a tight window
/comments/search?subreddit=eu4&body=player+agency&after=2025-06-01&before=2025-09-01&limit=50
```

## Errors

| Status | Body | Cause / fix |
|---|---|---|
| 422 | `Timeout. Maybe slow down a bit` | query too heavy — add/narrow `after`/`before`; do not retry identically |
| 429 | — | rate limited; exponential backoff |
| 400 | `Unknown query parameter: 'x'` | wrong param name (e.g. `query` on comments -> use `body`) |
| 400 | `'sort_type' must be one of default, created_utc` | you tried to sort by score; there is none |

## Notes

- No score sorting anywhere. Approximate "top" by sweeping windows then sorting locally.
- `limit` caps at 100; paginate with `before` = oldest timestamp already seen.
- It is a community-run mirror: keep ~0.3-1.5s between requests and back off on 429.
- Data can lag a few days at the far edge; treat the newest day as provisional.
