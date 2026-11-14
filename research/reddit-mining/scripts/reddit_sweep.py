#!/usr/bin/env python3
"""Resumable, budgeted Reddit sweeper over the Arctic Shift API.

Posts:
  reddit_sweep.py posts --subs paradoxplaza,eu4,victoria3 --start 2025-01-01 \\
      --end 2026-10-10 --out posts.jsonl [--budget 240]

Comments (needs a posts JSONL to pick threads from):
  reddit_sweep.py comments --posts posts.jsonl --out comments.jsonl [--budget 240]

State lives beside the output file (<out>.state.json); re-run to continue after the
budget is spent. Output is append-only JSONL, so a killed run loses nothing.
"""
import argparse, datetime, json, os, re, time
import urllib.error, urllib.parse, urllib.request

BASE = "https://arctic-shift.photon-reddit.com/api"
UA = "Mozilla/5.0 (compatible; reddit-research)"
MAX_PAGES = 3

DESIGN_RE = re.compile(
    r"(design|mechanic|system|rework|overhaul|balance|ai\b|late game|pacing|learning curve|"
    r"tutorial|depth|boring|tedious|fun\b|agency|railroad|sandbox|why (is|does|do|are)|"
    r"what makes|should|problem|opinion|unpopular|hot take|dlc|expansion|price|monetis|"
    r"monetiz|flaw|fail|worse|better)", re.I)


def api(path, tries=3, **params):
    qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    last = "unknown"
    for i in range(tries):
        req = urllib.request.Request(f"{BASE}{path}?{qs}", headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:120]
            last = f"{e.code}:{body}"
            time.sleep(1.0 * (i + 1))
        except Exception as e:  # noqa: BLE001
            last = repr(e)[:120]
            time.sleep(1.0 * (i + 1))
    return {"error": last}


def state_path(out):
    return out + ".state.json"


def load_state(out):
    if os.path.exists(state_path(out)):
        return set(tuple(x) for x in json.load(open(state_path(out))))
    return set()


def save_state(out, done):
    json.dump(sorted(list(done)), open(state_path(out), "w"))


def windows(start, end, months=3):
    """Yield (after, before) date strings covering [start, end)."""
    fmt = "%Y-%m-%d"
    cur = datetime.datetime.strptime(start, fmt)
    end_d = datetime.datetime.strptime(end, fmt)
    out = []
    while cur < end_d:
        nxt = min(cur + datetime.timedelta(days=30 * months), end_d)
        out.append((cur.strftime(fmt), nxt.strftime(fmt)))
        cur = nxt
    return out


def post_slim(p):
    return {"id": p.get("id"), "sub": p.get("subreddit"), "title": p.get("title"),
            "score": p.get("score"), "num_comments": p.get("num_comments"),
            "created": p.get("created_utc"), "permalink": p.get("permalink"),
            "flair": p.get("link_flair_text"), "ratio": p.get("upvote_ratio"),
            "selftext": (p.get("selftext") or "")[:1800]}


def comment_slim(c):
    return {"id": c.get("id"), "link": c.get("link_id"), "parent": c.get("parent_id"),
            "score": c.get("score"), "created": c.get("created_utc"),
            "author": c.get("author"), "body": (c.get("body") or "")[:2200],
            "depth": c.get("depth")}


def do_posts(a):
    subs = [s.strip() for s in a.subs.split(",") if s.strip()]
    wins = windows(a.start, a.end)
    jobs = [(s, x, y) for s in subs for (x, y) in wins]
    done = load_state(a.out)
    t0, added, completed = time.time(), 0, 0
    with open(a.out, "a") as f:
        for sub, after, before in jobs:
            if (sub, after, before) in done:
                continue
            if time.time() - t0 > a.budget:
                remaining = len([j for j in jobs if tuple(j) not in done])
                print(f"BUDGET REACHED completed={completed} posts={added} remaining={remaining}")
                return
            cursor, pages = before, 0
            while pages < MAX_PAGES:
                d = api("/posts/search", subreddit=sub, after=after, before=cursor,
                        limit=100, sort="desc", sort_type="created_utc")
                posts = d.get("data")
                if not posts:
                    break
                for p in posts:
                    f.write(json.dumps(post_slim(p)) + "\n")
                    added += 1
                oldest = min(p.get("created_utc", 0) for p in posts)
                cursor = datetime.datetime.utcfromtimestamp(oldest).strftime("%Y-%m-%d")
                pages += 1
                if len(posts) < 100:
                    break
                time.sleep(0.3)
            done.add((sub, after, before))
            save_state(a.out, done)
            completed += 1
            f.flush()
            print(f"  {sub:<18} {after}->{before} pages={pages} total={added}")
    print(f"DONE completed={completed} posts={added}")


def select_threads(posts_path, per_sub=12, kw_per_sub=10):
    posts = {}
    for line in open(posts_path):
        try:
            p = json.loads(line)
        except Exception:  # noqa: BLE001
            continue
        posts[p["id"]] = p
    by_sub = {}
    for p in posts.values():
        by_sub.setdefault(p["sub"], []).append(p)
    threads = {}
    for _sub, ps in by_sub.items():
        for p in sorted(ps, key=lambda x: x.get("num_comments") or 0, reverse=True)[:per_sub]:
            threads[p["id"]] = p
        for p in sorted([x for x in ps if DESIGN_RE.search(x.get("title") or "")],
                        key=lambda x: x.get("num_comments") or 0, reverse=True)[:kw_per_sub]:
            threads[p["id"]] = p
    return threads


def do_comments(a):
    threads = select_threads(a.posts)
    done = load_state(a.out)
    todo = [t for t in threads if t not in done]
    print(f"threads selected={len(threads)} done={len(done)} todo={len(todo)}")
    t0, added, completed = time.time(), 0, 0
    with open(a.out, "a") as f:
        for tid in todo:
            if time.time() - t0 > a.budget:
                print(f"BUDGET REACHED completed={completed} comments={added} remaining={len([t for t in todo if t not in done])}")
                return
            got, cursor = 0, None
            for _page in range(2):
                d = api("/comments/search", link_id=tid, limit=100, sort="desc", before=cursor)
                cs = d.get("data")
                if not cs:
                    break
                for c in cs:
                    f.write(json.dumps(comment_slim(c)) + "\n")
                    got += 1
                oldest = min(c.get("created_utc", 0) for c in cs)
                cursor = datetime.datetime.utcfromtimestamp(oldest).strftime("%Y-%m-%d")
                if len(cs) < 100:
                    break
                time.sleep(0.25)
            done.add(tid)
            save_state(a.out, done)
            added += got
            completed += 1
            if completed % 10 == 0:
                f.flush()
    print(f"DONE completed={completed} comments={added}")


def main():
    ap = argparse.ArgumentParser(description="Arctic Shift Reddit sweeper")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("posts", help="sweep submissions by time window")
    p.add_argument("--subs", required=True, help="comma-separated subreddit names")
    p.add_argument("--start", required=True, help="YYYY-MM-DD")
    p.add_argument("--end", required=True, help="YYYY-MM-DD")
    p.add_argument("--out", required=True, help="output JSONL path")
    p.add_argument("--budget", type=float, default=240.0, help="seconds")
    p.set_defaults(func=do_posts)

    c = sub.add_parser("comments", help="pull comments for selected threads")
    c.add_argument("--posts", required=True, help="posts JSONL from the posts step")
    c.add_argument("--out", required=True, help="output JSONL path")
    c.add_argument("--budget", type=float, default=240.0, help="seconds")
    c.set_defaults(func=do_comments)

    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
