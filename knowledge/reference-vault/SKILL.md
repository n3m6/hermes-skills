---
name: reference-vault
description: "Use when a task needs durable non-memory facts."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [memory, vault, reference, infra, rot-prevention]
---

# Reference vault

Durable, on-demand reference store that keeps MEMORY.md tiny. This is how memory
rot is avoided: memory holds only facts relevant to EVERY conversation and points
here; everything else lives in the vault and is read only when needed.

## Location

`~/reference-vault/`
- `reference/` — one doc per system (lab-host, network, hermes-install,
  models-and-secrets, repos, projects, backups).
- `dream/` — nightly dream-loop logs + consolidated insights.
- `README.md` — index and rules.

## When to read it

Load the matching doc BEFORE planning or executing a task that depends on:
host hardware/disk, network/addressing, Hermes layout or version, where a
credential lives, a repo path or its SSH alias, or active-project paths.
Cheapest path: `read_file` the specific doc; grep the folder for a keyword.

## When to write it

- Memory reaches ~75% of its char budget (see `memory.memory_char_limit` in
  `~/.hermes/config.yaml`): offload task-specific detail here, then trim memory.
- You learn a durable infra fact or the live system changed.
- Never write a secret value here — record only WHERE the secret lives.

## Rules

1. Order of truth: live system > vault > memory. If they disagree, fix the vault.
2. Extend an existing doc before creating a new one; one doc per system.
3. Never store secrets, tokens, passwords, or keys here.
4. Trim memory only AFTER the detail is safely written to the vault.
