---
name: multi-llm-wiki
description: "Operate a fleet of Karpathy-style LLM wikis: identify the right wiki, orient per-repo, scaffold new wikis by mirroring existing conventions."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [wiki, knowledge-base, research, notes, markdown, multi-wiki]
    related_skills: [llm-wiki, obsidian, github-repo-management]
---

# Multiple LLM Wikis (fleet operations)

Companion to the bundled `llm-wiki` skill. `llm-wiki` documents the mechanics of
a single Karpathy-style wiki (ingest, query, lint, SCHEMA/index/log upkeep).
THIS skill covers what changes when the user runs SEVERAL wikis — one per
research domain, each its own git repo — and what to do when scaffolding a NEW
one. Read this before `llm-wiki` whenever more than one wiki exists.

## When This Skill Activates

- User references "the wiki" but multiple wikis exist (check memory for a
  registry of wiki locations; ask if ambiguous)
- User asks to create/start a NEW wiki and an existing wiki is already present
- User drops a repo URL or path that could be a wiki repo
- Multi-wiki orientation: which SCHEMA.md / index.md / log.md to read first

## Core Rules

1. **Identify the wiki explicitly.** Ask by name, path, or repo URL — never
   silently assume the `WIKI_PATH` env target. `WIKI_PATH` is a convenience
   default for single-wiki setups, NOT a registry. Users who run multiple wikis
   prefer naming the wiki over env-var indirection.
2. **Each wiki repo is self-describing.** Its `SCHEMA.md` carries a `**Repo:**`
   line with the canonical URL; its `AGENTS.md` holds the non-negotiables. To
   orient: read `AGENTS.md` (if present — the agent operating contract:
   capture pipeline, hash discipline, commit rules) + `SCHEMA.md` + `index.md`
   + recent `log.md` from THAT repo — same ritual as `llm-wiki`, pointed at
   the right directory. `git -C <dir> remote get-url origin` confirms
   identity.
3. **Keep a registry in memory.** Record each wiki's local path, repo name, and
   domain in memory so future sessions know the full set. Memory MAY hold local
   paths and repo names; it REJECTS SSH key paths, host aliases, and dotfile/env
   references (threat guard) — keep those in `~/.ssh/config`.

## Scaffolding a New Wiki (when wikis already exist)

1. Check for existing wikis FIRST (memory, or search for dirs containing
   `SCHEMA.md`). Mirror their conventions in the new wiki:
   - Same directory layout — including extras like a `tactics/` layer if the
     existing wiki has one (raw/, entities/, concepts/, comparisons/, queries/,
     _archive/ come from `llm-wiki`'s template). If you mirror a `tactics/`
     layer, mirror its page spec too: `type: tactics` + `confidence:
     high|medium|low` frontmatter, numbered principles (T1/V1/E1/R1/H1) each
     tagged **demonstrated** vs **inferred**, provenance markers per
     principle, and a `## Tactics` section in index.md (the lint's LAYERS
     list must include tactics/ or its pages skip checks)
   - Carry over domain-critical rules into the new `SCHEMA.md` — e.g. the
     source-verification rule ("verify before ingest, never fabricate a
     citation") that the existing wiki enforces
   - Adapt the existing `AGENTS.md` skeleton (non-negotiables + structure) to
     the new domain
   - Add the `**Repo:**` line to SCHEMA.md so the wiki is self-describing
   - **Copy the existing wiki's `scripts/` tooling.** The generic `lint.py`
     (9 checks; derives the tag taxonomy from each wiki's own SCHEMA.md, so
     it ports verbatim — ships with `research-paper-ingestion`) belongs in
     the new wiki. Copy it, run it against the empty wiki (expect
     "WIKI HEALTHY", 0 pages), and commit it with the skeleton. Users
     explicitly ask for this when scaffolding ("copy the linting etc").
2. Confirm the repo is private/public and create it EMPTY (no auto-init
   README/.gitignore) — see `private-repo-access` for the deploy-key flow.
3. Initialize git locally, push the skeleton, then ingest per `llm-wiki`.

## First ingest: curate the canon (don't make the user pick)

When the user says "prepare / gather the most important <domain> material"
for a new wiki, they want initiative, not a menu of options:

1. **Draft the tiered canon yourself**: Tier 0 frameworks/harnesses, Tier 1
   canonical entities (benchmarks, datasets), Tier 2 methodology/edge topics.
2. **VERIFY every source before presenting** (arXiv API id_list / title
   search, GitHub API for repos — see `research-paper-ingestion` Step 0).
   Title-match each response; misremembered IDs resolve to real-but-wrong
   papers.
3. **Present the verified canon briefly, then START ingesting tier by tier
   in the same session** — do not end the turn on "which paper first?".
   (Session evidence: the user was asked that question and answered with
   "let's prepare, gather" — i.e. *you decide, go*.)
4. **Capture each source as raw** (full text; ar5iv fallback per
   `research-paper-ingestion`), create entity/concept pages interlinked only
   to pages that exist NOW (the lint flags links to not-yet-created pages —
   mention future entities as plain text), update index + log per batch,
   lint, commit, push.

## When the goal refocuses the wiki mid-flight

The Domain paragraph in SCHEMA.md is a working hypothesis, not a contract.
When the user reveals the concrete goal behind a wiki ("I'm building a
coding-assistant benchmark — what am I missing for this?"), treat it as a
RE-TIERING signal, not a new task:

1. **Re-center the canon around the goal.** The original canon becomes
   infrastructure/context; verify a new tier for the goal's core (here:
   agentic coding benchmarks, validity critiques, task material) using
   `research-paper-ingestion` Step 0. Expect several memorized IDs to be
   wrong; correct them without drama.
2. **Update SCHEMA.md before writing pages:** rewrite the Domain paragraph
   and ADD new tags to the Tag Taxonomy first, then use them (session:
   added `agent`, `coding`, `validity` for coding-agent evaluation).
3. **Present the gap analysis** (what's missing, tiered, all verified),
   then start the first wave in the same turn.

## Contested findings in research wikis

When the domain's own literature is in open dispute (session: SWE-bench
validity — "underestimates capability" 2024 vs "memorization, not
reasoning" 2025–26), encode the debate instead of picking a side:

- On the contested ENTITY page, write a dated "both positions" section
  (position → year → sources) and set `contested: true` in frontmatter.
- Create ONE synthesizing concept page that lays out the debate, the open
  questions, and what a builder should do, with `^[raw/...]` provenance
  markers per position (session: `agentic-coding-evaluation.md`).
- Lint `contested` advisories are BY DESIGN (review signals), not failures
  — the wiki stays healthy with them; resolution happens at user review.

## Pitfalls

- **Don't treat WIKI_PATH as a registry** — a single env var can't represent a
  fleet. If it's set, it points at ONE wiki (often an older one); the others
  are found via memory or explicit user naming.
- **WIKI_PATH may already be set** — grep the `.env` file before appending
  anything, and never silently repoint it; ask the user which wiki should be
  default (or none).
- **Verify env edits after writing.** Compound `&&`/`||` append one-liners lie:
  `grep -q X f && echo already || echo X >> f && echo appended` prints BOTH
  messages when the grep succeeds — a skipped append can still echo "appended".
  Always re-grep to confirm actual state.
- **Don't duplicate `llm-wiki` content** — this skill is only the multi-wiki
  delta. Mechanics, templates, lint rules, and Obsidian integration live in the
  bundled skill; cite it rather than re-implementing it.
- **Wiki count grows** — each new domain wiki gets its own repo + deploy key
  (one key per repo; GitHub rejects reuse — see `private-repo-access`).
- **Index page-count header silently drifts** — "Total pages: N" in index.md
  goes stale (a sed one-liner can fail without error; header arithmetic
  compounds). Recompute from the filesystem
  (`ls entities/*.md concepts/*.md tactics/*.md comparisons/*.md | wc -l`)
  rather than trusting the previous header number.
- **Codify proven workflow back into AGENTS.md/SCHEMA.md on request** — after
  several ingest waves prove a pipeline (capture fallback chain, hash
  discipline, orphan prevention), the user may ask to "fix AGENTS.md and
  SCHEMA.md so these are captured when ingesting". Do it: non-negotiables +
  pipeline summary in AGENTS.md, the authoritative spec (verification
  endpoints, fallback chain, hash rule, page-type specs) in SCHEMA.md, and a
  log entry. Future sessions then get the workflow from the repo itself via
  the orient-first ritual — this is the user's standing preference for
  durable knowledge living in-repo, not in session memory.
