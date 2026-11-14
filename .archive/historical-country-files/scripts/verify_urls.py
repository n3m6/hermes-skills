#!/usr/bin/env python3
"""Verify every http(s) URL cited in a markdown deliverable.

Usage:
    python3 verify_urls.py <file.md> [--sleep 0.7] [--quiet]

Extracts all http(s):// URLs from the file, dedupes, curl-checks each with
-L (follow redirects), and retries once after a pause on transient
429/5xx responses (Wikipedia rate-limits rapid sequential curls; a single
delayed retry normally returns 200).

Exit code 0  = every URL returned HTTP 200.
Exit code 1  = one or more URLs failed (listed on stdout).
Exit code 2  = usage error or no URLs found.

Standard use at the end of a research file task: run it, fix/flag any
non-200, then report 'all N URLs verified HTTP 200' in the final summary.
"""
import argparse
import re
import subprocess
import sys
import time

# Strip closing punctuation that markdown prose leaves on a bare URL.
# Deliberately NOT stripping '/' (it can be significant).
_TRAILING = set('.,;:!?)]}\u201d\u2019\u201c\u2018')


def fetch(url: str, max_time: int = 25) -> str:
    try:
        r = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
             "-L", "--max-time", str(max_time), url],
            capture_output=True, text=True, timeout=max_time + 10,
        )
        return r.stdout.strip()
    except Exception:
        return "ERR"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--sleep", type=float, default=0.7,
                    help="seconds between requests (default 0.7)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    try:
        text = open(args.file, encoding="utf-8").read()
    except OSError as e:
        print(f"cannot read {args.file}: {e}")
        return 2

    urls = sorted({u.rstrip(''.join(_TRAILING))
                   for u in re.findall(r"https?://[^\s]+", text)})
    if not urls:
        print("no URLs found in", args.file)
        return 2

    bad = []
    for u in urls:
        code = fetch(u)
        # Transient rate-limit / server blip: one retry after a pause.
        if code.startswith(("429", "5")):
            time.sleep(10)
            code = fetch(u)
        if code != "200":
            bad.append((code, u))
        if not args.quiet:
            print(f"{code:>3}  {u}")
        time.sleep(args.sleep)

    print(f"\n{len(urls) - len(bad)}/{len(urls)} URLs OK")
    if bad:
        print("NON-200:")
        for code, u in bad:
            print(f"  {code}  {u}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
