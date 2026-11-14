#!/usr/bin/env python3
"""Strip curl-fetched HTML to plain text for research extraction.

For non-Wikipedia pages (grokipedia, JVL, USHMM, wikisource Page: namespace,
archive.org snapshots) there is no wikitext endpoint — fetch the HTML and strip.

Usage:
  python3 html2text.py page.html                     # whole page (first 40k chars)
  python3 html2text.py page.html -k "5,000"          # context windows around keyword
  python3 html2text.py page.html -k "Article 1" -k "subsidy" -w 400 -n 2
  cat page.html | python3 html2text.py - -k "1928"   # stdin

If a plausible page reports NO MATCH, it is likely JS-rendered (e.g. palquest.org):
record "JS-rendered, not curl-extractable" and find the document on another host.
"""
import argparse
import html
import re
import sys


def strip(raw: str) -> str:
    t = re.sub(r"<script.*?</script>", " ", raw, flags=re.S | re.I)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    return re.sub(r"\s+", " ", t).strip()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("file", nargs="?", default="-")
    ap.add_argument("-k", "--keyword", action="append", default=[])
    ap.add_argument("-w", "--window", type=int, default=350)
    ap.add_argument("-n", "--max-matches", type=int, default=3)
    args = ap.parse_args()

    raw = sys.stdin.read() if args.file == "-" else open(
        args.file, encoding="utf-8", errors="replace").read()
    text = strip(raw)

    if not args.keyword:
        print(text[:40000])
        return

    for kw in args.keyword:
        hits = 0
        for m in re.finditer(re.escape(kw), text, re.I):
            i = m.start()
            print(f"--- {kw} ---")
            print(text[max(0, i - args.window): i + args.window])
            print()
            hits += 1
            if hits >= args.max_matches:
                break
        if hits == 0:
            print(f"--- {kw}: NO MATCH (JS-rendered or redirect?) ---")
            print()


if __name__ == "__main__":
    main()
