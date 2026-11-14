#!/usr/bin/env python3
"""Analyse a swept Reddit corpus: dedupe, theme-bucket, print top substantive quotes
with their thread context.

  reddit_analyze.py --posts posts.jsonl --comments comments.jsonl [--theme war] [--n 6]

Themes are regex buckets; add your own to THEMES. Quotes print with the parent thread
title and permalink so they can be cited and checked.
"""
import argparse, collections, json, re

THEMES = {
    "AGENCY": r"(player agency|no agency|railroad|on rails|i can'?t control|auto[- ]?resolv|dice roll|rng)",
    "AI": r"(\bthe ai\b|ai (is|does|can'?t|doesn'?t|never|always|cheat)|ai cheats|braindead|competent ai)",
    "WAR": r"(war system|warfare|front ?line|combat system|army micro|doom ?stack)",
    "ECONOMY": r"(economy|economic sim|market|spreadsheet|production (chain|method)|building queue)",
    "PACING": r"(late game|late-game|pacing|snowball|becomes boring|gets boring|tedious|nothing to do)",
    "DEPTH": r"(learning curve|too complex|overwhelm|steep|dumb(ed)? down|water(ed)? down|simplif)",
    "DLC": r"(dlc|expansion|monetis|monetiz|paywall|overpriced|cut content|subscription)",
    "FLAVOUR": r"(flavou?r|immersion|immersive|roleplay|atmosphere|historically accurate)",
    "BUGS": r"(performance|lag|optimis|optimiz|desync|unplayable|hotfix|patch broke|crash)",
    "ONBOARDING": r"(tutorial|new player|beginner|onboard|tooltip|confus|don'?t understand)",
}

MIN_LEN = 180  # drop one-line jokes


def load_jsonl(path):
    out = []
    for line in open(path):
        try:
            out.append(json.loads(line))
        except Exception:  # noqa: BLE001
            continue
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--posts", required=True)
    ap.add_argument("--comments", required=True)
    ap.add_argument("--theme", help="print only this theme")
    ap.add_argument("--n", type=int, default=6, help="quotes per theme")
    ap.add_argument("--maxlen", type=int, default=520)
    a = ap.parse_args()

    posts = {p["id"]: p for p in load_jsonl(a.posts)}
    comments = {c["id"]: c for c in load_jsonl(a.comments)}
    print(f"posts={len(posts)} comments={len(comments)}")

    def ctx(c):
        p = posts.get((c.get("link") or "").replace("t3_", ""), {})
        return p.get("sub", "?"), p.get("title", "?"), p.get("permalink", "")

    substantive = [c for c in comments.values()
                   if len(c.get("body") or "") >= MIN_LEN
                   and (c.get("body") or "").strip().lower() not in ("[deleted]", "[removed]")]
    print(f"substantive (>= {MIN_LEN} chars) = {len(substantive)}")

    themes = {a.theme.upper(): THEMES[a.theme.upper()]} if a.theme else THEMES
    for name, rx in themes.items():
        rows = [c for c in substantive if re.search(rx, c["body"], re.I)]
        print(f"\n{'#' * 84}\n## {name}  (matches={len(rows)})\n{'#' * 84}")
        seen, k = set(), 0
        for c in sorted(rows, key=lambda x: x.get("score", 0), reverse=True):
            b = re.sub(r"\s+", " ", c["body"]).strip()
            if b[:45] in seen:
                continue
            seen.add(b[:45])
            sub, title, perm = ctx(c)
            print(f"[{c.get('score')}up] r/{sub} - \"{title[:72]}\"\n   {b[:a.maxlen]}")
            if perm:
                print(f"   https://reddit.com{perm}")
            print()
            k += 1
            if k >= a.n:
                break

    dist = collections.Counter((c.get("link") or "").replace("t3_", "") for c in comments.values())
    print(f"\ncomments span {len(dist)} threads; largest = {dist.most_common(3)}")


if __name__ == "__main__":
    main()
