#!/usr/bin/env python3
"""
Fetch arXiv paper full text as markdown, with raw frontmatter for KB ingestion.

Usage:
    python3 fetch_arxiv.py 2302.10149                # prints markdown to stdout
    python3 fetch_arxiv.py 2302.10149 -o out.md      # saves with frontmatter
    python3 fetch_arxiv.py 2302.10149 --slug my-name # override output slug

Stdlib only. Tries arxiv.org/html first, then the ar5iv mirror
(ar5iv.labs.arxiv.org/html), then falls back to the abs page.
Rejects stub pages ("No HTML for", "Fatal error", "Untitled Document")
at each step. Verify the paper exists BEFORE calling this (arXiv API /
web search) — this script fetches, it does not verify.
PDFs (pypdf in a venv) are handled outside this script — see the
SKILL.md Step 1 for the full chain.
"""

import argparse
import hashlib
import html
import re
import sys
import urllib.request


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research ingest)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def html_to_markdown(html_bytes):
    text = html_bytes.decode("utf-8", errors="replace")
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", text, flags=re.S | re.I)
    text = re.sub(r"<h1[^>]*>", "\n# ", text)
    text = re.sub(r"<h2[^>]*>", "\n## ", text)
    text = re.sub(r"<h3[^>]*>", "\n### ", text)
    text = re.sub(r"</h[1-6]>", "\n", text)
    text = re.sub(r"</(p|div|section|li|tr)>", "\n", text)
    text = re.sub(r"<(p|div|section|li|tr)[^>]*>", "\n", text)
    text = re.sub(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', r"[\2](\1)", text, flags=re.S)
    text = re.sub(r"<(b|strong)[^>]*>", "**", text)
    text = re.sub(r"</(b|strong)>", "**", text)
    text = re.sub(r"<(i|em)[^>]*>", "*", text)
    text = re.sub(r"</(i|em)>", "*", text)
    text = re.sub(r"<code[^>]*>", "`", text)
    text = re.sub(r"</code>", "`", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def strip_toc(body):
    """Remove BOTH ToC link forms: [text](https://arxiv.org/html/...) AND
    [text](#S4.SS3) anchor links. Missing the anchor form is the classic
    bug — it leaves ToC lines that pollute section extraction."""
    lines = body.split("\n")
    kept = []
    for l in lines:
        if re.match(r"^\s*\[[^\]]+\]\([^)]*#?S?\d", l):
            continue
        if re.match(r"^\s*\[[^\]]+\]\(https://arxiv\.org/html/", l):
            continue
        kept.append(l)
    return "\n".join(kept)


def get_abstract(aid):
    """Clean abstract from the arXiv API — always more reliable than
    extracting it from converted HTML."""
    import xml.etree.ElementTree as ET
    ns = {"a": "http://www.w3.org/2005/Atom"}
    with urllib.request.urlopen(f"https://export.arxiv.org/api/query?id_list={aid}", timeout=30) as r:
        root = ET.parse(r).getroot()
    entry = root.find("a:entry", ns)
    if entry is None:
        return None
    title = entry.find("a:title", ns).text.strip().replace("\n", " ")
    summary = entry.find("a:summary", ns).text.strip()
    return title, summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arxiv_id")
    ap.add_argument("-o", "--output")
    ap.add_argument("--slug")
    args = ap.parse_args()
    aid = args.arxiv_id

    # Stub markers: arXiv/ar5iv return plausible-looking stub pages instead
    # of 404s ("No HTML for '<id>'", "Untitled Document", "Conversion to
    # HTML had a Fatal error..."). Markers can sit past byte 3000 of the raw
    # HTML, so check the CONVERTED body (full scan), not the raw head.
    BAD = ["no html for", "fatal error", "untitled document", "truncated or damaged"]

    def good(body):
        low = body.lower()
        return len(body) >= 500 and not any(m in low for m in BAD)

    html_url = f"https://arxiv.org/html/{aid}"
    try:
        body = html_to_markdown(fetch(html_url))
        if not good(body):
            raise ValueError("stub or too short")
        source = html_url
    except Exception:
        # ar5iv mirror before settling for abstract-only
        ar5iv_url = f"https://ar5iv.labs.arxiv.org/html/{aid}"
        try:
            body = html_to_markdown(fetch(ar5iv_url))
            if not good(body):
                raise ValueError("stub or too short")
            source = ar5iv_url
        except Exception:
            abs_url = f"https://arxiv.org/abs/{aid}"
            body = html_to_markdown(fetch(abs_url))
            source = abs_url
            print(f"NOTE: full text unavailable (native+ar5iv), fell back to abs page: {abs_url}", file=sys.stderr)

    body = strip_toc(body)
    sha = hashlib.sha256(body.encode()).hexdigest()
    today = __import__("datetime").date.today().isoformat()
    fm = f"---\nsource_url: {source}\ningested: {today}\nsha256: {sha}\n---\n"
    out = fm + body

    if args.output:
        with open(args.output, "w") as f:
            f.write(out)
        print(f"saved {len(body)} chars -> {args.output}")
    else:
        print(out)


if __name__ == "__main__":
    main()
