#!/usr/bin/env python3
"""
Wiki lint: structural health check for a Karpathy-style LLM wiki.

Checks:
  1. Broken [[wikilinks]] (links to pages that don't exist)
  2. Orphan pages (no inbound wikilinks from other wiki pages)
  3. Index completeness (every page in index.md; no phantom index entries)
  4. Frontmatter validation (required fields on every wiki page)
  5. Tag audit (every tag used must be in the SCHEMA.md taxonomy)
  6. Page size (flag pages over 200 lines - split candidates)
  7. Source drift (raw/ sha256 frontmatter vs actual content hash)
  8. Log rotation (flag when log.md exceeds 500 entries)
  9. Quality signals (contested/low-confidence pages needing review)
     -- advisory only, does NOT fail the lint

Usage:
    python3 lint.py                # lint WIKI_PATH or ~/wiki
    python3 lint.py /path/to/wiki  # lint a specific wiki

Exit code: 0 = clean, 1 = issues found, 2 = wiki path missing.
Stdlib only, no dependencies.
"""

import hashlib
import os
import re
import sys
from collections import defaultdict

WIKI = os.environ.get("WIKI_PATH", os.path.expanduser("~/wiki"))
LAYERS = ["entities", "concepts", "comparisons", "queries", "tactics"]
REQUIRED_FM = ["title", "created", "updated", "type", "tags", "sources"]
MAX_PAGE_LINES = 200
MAX_LOG_ENTRIES = 500
WIKI_PAGE_TYPES = {"entity", "concept", "comparison", "query", "summary", "tactics"}


def find_pages(wiki):
    pages = {}
    for layer in LAYERS:
        d = os.path.join(wiki, layer)
        if os.path.isdir(d):
            for fn in sorted(os.listdir(d)):
                if fn.endswith(".md"):
                    pages[f"{layer}/{fn}"] = os.path.join(d, fn)
    return pages


def parse_frontmatter(content):
    m = re.match(r"^---\n(.*?)\n---", content, re.S)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


def extract_tags(tag_field):
    return re.findall(r"[a-z][a-z0-9-]*", tag_field.replace("[", "").replace("]", ""))


def load_taxonomy(wiki):
    schema_path = os.path.join(wiki, "SCHEMA.md")
    if not os.path.exists(schema_path):
        return set()
    with open(schema_path) as f:
        schema = f.read()
    tax = set()
    m = re.search(r"## Tag Taxonomy(.*?)(?=\n## |\Z)", schema, re.S)
    if m:
        tax.update(re.findall(r"`([a-z][a-z0-9-]*)`", m.group(1)))
    return tax


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    wiki = os.path.abspath(args[0] if args else WIKI)
    if not os.path.isdir(wiki):
        print(f"ERROR: wiki path not found: {wiki}")
        sys.exit(2)

    issues = []
    pages = find_pages(wiki)
    print(f"Linting wiki: {wiki}")
    print(f"Wiki pages found: {len(pages)}")

    outbound, fm_map, sizes = {}, {}, {}
    for rel, path in pages.items():
        with open(path) as f:
            content = f.read()
        sizes[rel] = content.count("\n")
        outbound[rel] = re.findall(r"\[\[([^\]]+)\]\]", content)
        fm_map[rel] = parse_frontmatter(content)

    inbound = defaultdict(int)
    broken = []
    for rel, links in outbound.items():
        for l in links:
            target = l.split("#")[0].split("|")[0].strip()
            found = False
            for layer in LAYERS:
                if os.path.exists(os.path.join(wiki, layer, target + ".md")):
                    inbound[f"{layer}/{target}.md"] += 1
                    found = True
                    break
            if not found:
                broken.append((rel, l))

    if broken:
        issues.append(f"[1] BROKEN WIKILINKS ({len(broken)}):")
        for src, l in broken[:20]:
            issues.append(f"    {src} -> [[{l}]]")
        if len(broken) > 20:
            issues.append(f"    ... and {len(broken) - 20} more")

    orphans = [rel for rel in pages if inbound[rel] == 0]
    if orphans:
        issues.append(f"[2] ORPHAN PAGES - no inbound links ({len(orphans)}):")
        for o in orphans:
            issues.append(f"    {o}")

    index_path = os.path.join(wiki, "index.md")
    if os.path.exists(index_path):
        with open(index_path) as f:
            idx = f.read()
        index_slugs = {i.split("|")[0].split("#")[0].strip()
                       for i in re.findall(r"\[\[([^\]]+)\]\]", idx)}
        page_slugs = {rel.split("/")[-1][:-3] for rel in pages}
        not_indexed = sorted(page_slugs - index_slugs)
        phantom = sorted(index_slugs - page_slugs)
        if not_indexed:
            issues.append(f"[3] PAGES MISSING FROM INDEX ({len(not_indexed)}): {', '.join(not_indexed)}")
        if phantom:
            issues.append(f"[3] INDEX ENTRIES WITH NO PAGE ({len(phantom)}): {', '.join(phantom)}")
    else:
        issues.append("[3] index.md not found")

    for rel, fm in sorted(fm_map.items()):
        missing = [f for f in REQUIRED_FM if f not in fm]
        if missing:
            issues.append(f"[4] FRONTMATTER: {rel} missing {missing}")
        ptype = fm.get("type", "").strip("\"'")
        if ptype and ptype not in WIKI_PAGE_TYPES:
            issues.append(f"[4] FRONTMATTER: {rel} unknown type '{ptype}'")

    taxonomy = load_taxonomy(wiki)
    if taxonomy:
        for rel, fm in sorted(fm_map.items()):
            for tag in extract_tags(fm.get("tags", "")):
                if tag not in taxonomy:
                    issues.append(f"[5] TAG: {rel} uses '{tag}' not in SCHEMA.md taxonomy")

    for rel, size in sorted(sizes.items(), key=lambda x: -x[1]):
        if size > MAX_PAGE_LINES:
            issues.append(f"[6] PAGE SIZE: {rel} is {size} lines (split at >{MAX_PAGE_LINES})")

    raw_dir = os.path.join(wiki, "raw")
    if os.path.isdir(raw_dir):
        for root, _, files in os.walk(raw_dir):
            for fn in sorted(files):
                if not fn.endswith(".md"):
                    continue
                path = os.path.join(root, fn)
                with open(path) as f:
                    content = f.read()
                m = re.match(r"^---\n(.*?)\n---\n", content, re.S)
                if not m:
                    continue
                stored = re.search(r"sha256: (\w+)", m.group(1))
                if not stored:
                    continue
                actual = hashlib.sha256(content[m.end():].encode()).hexdigest()
                if actual != stored.group(1):
                    issues.append(f"[7] SOURCE DRIFT: {os.path.relpath(path, wiki)} "
                                  f"(stored {stored.group(1)[:8]}... actual {actual[:8]}...)")

    log_path = os.path.join(wiki, "log.md")
    if os.path.exists(log_path):
        with open(log_path) as f:
            entries = len(re.findall(r"^## \[", f.read(), re.M))
        if entries > MAX_LOG_ENTRIES:
            issues.append(f"[8] LOG: {entries} entries (rotate at >{MAX_LOG_ENTRIES})")

    # Quality signals are ADVISORY — they must NOT fail the lint (a contested
    # page is intentional; it means the wiki is honestly flagging a debate).
    signals = []
    for rel, fm in sorted(fm_map.items()):
        if fm.get("contested", "").lower() == "true":
            signals.append(f"[9] CONTESTED: {rel} has unresolved contradictions - review")
        if fm.get("confidence") == "low":
            signals.append(f"[9] LOW CONFIDENCE: {rel} - weak claims, seek corroboration")
    if signals:
        print("\n=== REVIEW SIGNALS (advisory, not failures) ===")
        for s in signals:
            print(s)

    if issues:
        print("\n=== ISSUES FOUND ===")
        for line in issues:
            print(line)
        print(f"\n{len(issues)} issue line(s). Fix before treating the wiki as healthy.")
        sys.exit(1)
    else:
        print("\n=== WIKI HEALTHY === no issues found.")


if __name__ == "__main__":
    main()
