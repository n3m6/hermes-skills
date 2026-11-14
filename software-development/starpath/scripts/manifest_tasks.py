#!/usr/bin/env python3
"""Summarize a server-validation manifest without paging the raw JSON file.

Usage:
  python3 manifest_tasks.py <manifest.json> [id-prefix ...]

With prefixes, prints one block per matching task containing the fields that
decide scheduling, credentials, and evidence acceptance. With no prefix, prints
an id/kind/suite listing for every task so you can pick a prefix to drill into.

Exit status 0 when at least one task matched, 1 when none did.
"""

from __future__ import annotations

import json
import sys

FIELDS = (
    "kind",
    "suite",
    "working_directory",
    "command",
    "depends_on",
    "exclusive",
    "resource_locks",
    "required_credentials",
    "required_outputs",
    "acceptance_parser",
    "artifact_roles",
    "artifact_inputs",
    "external_readiness",
    "runtime_dependencies",
    "timeout_seconds",
    "memory_policy",
    "memory_max_fraction",
    "memory_high_fraction",
    "swap_max_bytes",
)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    path, prefixes = argv[1], argv[2:]
    with open(path, encoding="utf-8") as handle:
        document = json.load(handle)
    tasks = document.get("tasks", [])
    print(
        f"# {path}: schema_version={document.get('schema_version')} tasks={len(tasks)}"
    )
    if not prefixes:
        for task in tasks:
            print(f"{task.get('id', '?')}\tkind={task.get('kind')}\tsuite={task.get('suite')}")
        return 0 if tasks else 1

    matched = 0
    for task in tasks:
        identifier = task.get("id", "")
        if not any(identifier.startswith(prefix) for prefix in prefixes):
            continue
        matched += 1
        print(f"\n== {identifier}")
        for field in FIELDS:
            value = task.get(field)
            if value in (None, "", [], {}):
                continue
            print(f"  {field}: {json.dumps(value)}")
    print(f"\nmatched {matched} task(s)")
    return 0 if matched else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
