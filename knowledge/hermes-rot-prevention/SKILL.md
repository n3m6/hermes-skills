---
name: hermes-rot-prevention
description: "Use when setting up memory/skill rot prevention."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [hermes, memory, curator, cron, backup, rot-prevention]
---

# Hermes memory / skill rot prevention

## When to Use

When the user wants their Hermes install to stay healthy over months: small
memory, self-pruning skills, a weekly "dream loop", and tiered backups.
Most of this is NATIVE Hermes — configure it, do not rebuild it.

## What is already native (verify before building anything)

| Want | Native mechanism |
|---|---|
| Small memory | `memory.memory_char_limit` / `user_char_limit`; MEMORY.md + USER.md |
| Scheduled skill pruning | Curator (`hermes curator status/run/pin/adopt`) — ENABLED by default |
| Consolidation provenance | `absorbed_into` on a consolidation delete + `hermes curator ledger` |
| Pinned-but-patchable skills | `hermes curator pin` exempts a skill from auto-transition AND the LLM pass; patching is a separate path |
| Restricted-toolset cron job | cron job field `enabled_toolsets` (agent-side `cronjob` tool or job JSON) |
| Script-only cron (no LLM) | `hermes cron create --no-agent --script <name>`; stdout delivered verbatim |
| WAL-safe DB backup | `hermes backup` (sqlite3 online-backup API, `hermes_cli/backup_sqlite.py`) |
| Self-restoring image | `hermes backup` prints the restore line; `hermes import <zip>` restores |
| Tiered retention | NOT native — `-k N` is one linear policy; write grandfather-father-son yourself |

Non-native, user-built: the Obsidian-style reference vault (a directory + a skill
+ a memory pointer) and the dream-loop prompt.

## Setup

1. Memory: put a first-line rule in MEMORY.md ("Memory = only facts relevant to
   ALL conversations; everything else -> vault/skills") and keep it under ~75%.
2. Reference vault: `~/reference-vault/reference/` one doc per system; a skill
   telling the agent to read it on demand; one memory line pointing at it.
3. Curator: already on. Tune `curator.interval_hours`, `curator.consolidate`
   (LLM merge pass, costs aux-model tokens, off by default). `hermes curator
   adopt <name>` hands an unmanaged skill to the curator — until then it is
   never auto-staled/archived.
4. Dream loop: one cron job, `enabled_toolsets` restricted, `continuity`
   on, prompt = review the window's sessions from state.db -> self-critique ->
   dream log + insights to the vault -> skill audit -> memory triage. Weekly
   (`0 3 * * 0`, Sundays 03:00) as of the last change; it was nightly before.
   **When you change the cadence, change the lookback in the prompt too** — a
   weekly schedule still running a "review today" step silently skips six days.
5. Backups: one `--no-agent` cron job running a Python script: `hermes backup`
   into daily/, promote to weekly/ (Sundays) and monthly/ (1st), zipfile.testzip
   verify, drop RESTORE.txt, prune each tier, print a status line.

## Pitfalls (each cost real time)

- **Check the ledger before writing the day's fix list.** Hermes runs a built-in
  background review after each turn (`agent.background_review`) that already patches
  or creates skills from what the turn learned; its mutations are in
  `~/.hermes/skills/.curator_ledger.jsonl`. **Filter on `evidence.session_id`, not
  `actor`**: a real curator pass carries a `YYYYMMDD_HHMMSS_xxxxxx` gateway id, while the
  per-turn background review writes `actor=curator` with a **live session id** — 16 of 29
  rows in the 10-25→11-01 window were the review mislabelled as curator, which makes the
  curator look far more active than it is. Read the tail for the
  day first — otherwise the dream loop "fixes" a lesson that landed hours earlier
  and its log misrepresents the day as unfixed.
- **An umbrella merge can rename the trigger away from the user's own words, and then the
  skill never loads.** `account-legitimacy-vetting` (created 2026-10-18 by the background
  review) was absorbed into `product-teardown` on 10-19 with its "is this account legit"
  section intact — but the umbrella DESCRIPTION ("Product, person, competitor teardown from
  public evidence") does not contain the word the user types. The next two sessions that did
  exactly that task (10-20 16:40, 10-24 17:55) loaded **zero** skills and re-derived the
  method from scratch, losing the WHOIS domain-age check entirely. Test routing with data:
  `SELECT tool_name FROM messages WHERE session_id=? AND role='tool' AND tool_name='skill_view'`
  for the sessions that performed the task — an empty list is a routing failure, not a clean
  session. Fix the description (≤60 chars, use the user's noun: legit / scam / recruiter);
  the body was already correct. A merge that loses the trigger has made the pool *worse*.
- **A pitfall is inert unless it sits in the skill that LOADS for the triggering task.**
  When writing a lesson, name the task that trips it and the skill that loads for
  that task; if they differ, move the rule. Real case: the "skill description must
  fit 60 chars" rule lived only here (a rot task), so authoring a new skill still
  spent a failed `skill_manage(create)` discovering it. Route rules by load-path,
  not by topic.
- The cron lifecycle guard scans the JOB AND THE SCRIPT CONTENTS for
  `hermes gateway restart|stop` and `launchctl submit` (cron/lifecycle_guard.py).
  A restore note containing "hermes gateway stop" blocks the whole job. Never
  put that verb+noun pair in a script or prompt.
- Cron script timeout default is 3600 s (`cron.script_timeout_seconds` or
  `HERMES_CRON_SCRIPT_TIMEOUT`), not the 3-minute agent interrupt. Long backups
  are fine.
- `updates.pre_update_backup` is a MODE string (`off`/`quick`/`full`), not a
  bool. `hermes config set` writes the value as a quoted string; `"true"` maps
  to `full` via aliases but set `full` explicitly.
- `hermes cron create` (CLI) has NO --toolsets flag; set `enabled_toolsets`
  through the agent-side cronjob tool.
- A skill description must fit 60 chars or `skill_manage(create)` fails. The rule binds the
  CURATOR too — and **documenting it here does NOT stop the curator re-hitting it**: the
  curator pass is its own LLM context that never loads skills. Observed twice — 2026-10-12
  17:27 (200 chars) and 2026-10-13 17:44 (77 chars), the second 14 h after this rule was
  written — then twice more on 2026-10-14: a curator pass (`create gated-repo-workflow`, 64
  chars, 17:57:04) and the background review inside a live user session (183 chars, 20:10:54).
  Four passes, four refusals. Record it as a curator-prompt defect; do not re-patch skills for it.
- The background review has a SECOND chronic refusal class worth recognizing on sight: a `patch`
  is refused unless that SKILL.md body was loaded with `skill_view` in the same review turn
  ("the current SKILL.md content has not been loaded in this review turn"). Present since
  2026-08-08 across `arxiv`, `llm-wiki`, `research-paper-ingestion`, `sourced-country-files`,
  `private-repo-access`, and on 2026-10-14 20:11:35 `game-go-to-market`. It costs one call, not
  the lesson — the pass retries and lands.
- `skill_manage(delete)` must be the SOLE op in its call — it refuses to compose with other
  ops ("doesn't compose with other ops' rollback"). Same shape as the description rule: the
  curator re-hit it on 2026-10-13 17:47, a day after being told. Prompt defect, not a lesson.
- Dream-loop/session queries: `messages.timestamp`, `sessions.started_at` and
  `sessions.last_activity_at` are **epoch floats**, not ISO strings. `WHERE timestamp >= '2026-10-12'`
  matches nothing and returns an empty set *silently*; filter on
  `timestamp >= 1791774069.0` (compute it from the window). **Name the columns exactly: it is
  `last_activity_at`, not `last_active`** (`no such column`, one wasted call 2026-10-14). Three
  runs in a row guessed at this schema (10-11 mangled `python3 -c`, 10-12 ISO filter, 10-13 bad
  column) — run `PRAGMA table_info(<table>)` first instead of guessing. **A fourth run (10-16)
  ran the PRAGMA and still guessed the SELECT: it wrote `session_id`/`message_count`/
  `tool_calls`/`estimated_cost` and got `no such column: session_id`.** Build the query from the
  column list the PRAGMA just printed. Exact names: `sessions(id, title, source, started_at,
  ended_at, last_activity_at, message_count, tool_call_count, api_call_count, end_reason,
  estimated_cost_usd, cost_status)`; the first two of those are `id` and `tool_call_count`.
  Known-good one-liner:
  `SELECT id, started_at, last_activity_at, message_count, tool_call_count, estimated_cost_usd, end_reason, title FROM sessions ORDER BY started_at DESC LIMIT 30`.
  Validated 2026-10-17: assembling the SELECT from the PRAGMA output worked first try, no retry.
- **A `memory` op can be refused twice in a row, for two unrelated reasons — read the text.**
  First the content matched the `ssh_access` threat pattern: memory is injected into every
  system prompt, so any credential-path wording (`~/.ssh/…`, `IdentityFile`, a
  `credential.helper` line) is treated as an injection payload. Reword to the fact without
  the literal path and put the exact strings in a vault doc. Then the char limit refuses the
  reworded op — and that one is only checked on the **batch result**, so send ONE `operations`
  array that removes/patches stale entries *and* adds, never an add followed by a retry.
- **The char count shown in a session prompt is not `wc -m` on the file.** 2026-11-15 the
  injected header said 2,185/2,200 while `MEMORY.md` was **2,210** bytes — over budget for an
  unknown number of days, and invisible because every prompt looked compliant. Measure the
  file (`wc -m ~/.hermes/memories/MEMORY.md`) as the first step of triage, not the header.
- The dream log is named for the last day it reviews, not the run date: on weekly cadence the
  Sunday 03:00 run writes `dream/<Saturday>.md` covering the prior 7 days, so that file does not
  exist when the run starts (checking it blind cost a call). The run treats the newest existing
  `dream/*.md` as the start of its window.
- **A run that dies leaves NO log, and the window does not rewind for you.** On 2026-10-15 the
  03:00 run stalled on a `deepseek-flash` 503 storm: 600 s stale-stream threshold, retried, then
  `Provider has been unresponsive (no response received) for 7 consecutive stale attempts` —
  ~60 min of wall clock, one message row, no `dream/2026-10-14.md`. Nothing backfills it. The
  next run must (a) notice the missing log, (b) review the WHOLE gap from the last written log,
  and (c) write ONE log that says so at the top. Signal to look for: the job's row in
  `state.db.sessions` (`source='cron'`, `end_reason IS NULL`, `message_count` ~2) plus
  `errors.log` lines tagged with that cron session id — the file is `~/.hermes/logs/errors.log`,
  NOT `~/.hermes/errors.log`; the wrong path greps empty and reads as "no errors" (cost a call
  2026-10-17).
- **`terminal` without `workdir` can exit 126** — `cd: ~/.hermes/cache/scratch/<old dir>: No
  such file or directory` — when the persisted shell cwd is a scratch dir deleted by the 24 h
  idle prune. Every command in that session then fails at line 4 until a `workdir` is passed
  (2026-10-17: 6 calls across 4 sessions). Pass `workdir` on every terminal call; the same
  applies to `execute_code` that shells out.
- Write multi-line analysis as `python3 - <<'PY'` heredocs, never `python3 -c "…"`: nested
  quotes inside a `-c` string mangle easily and kill the whole cell (one lost 2026-10-12).
- Curator cadence is `curator.interval_hours` (24 here), so it runs DAILY, not weekly; a pass
  is ~3 min of the main provider. **Verify a curator verdict's numbers before acting on them:**
  pass #6 (2026-10-16) rejected distilling `gated-rust-workspace` because its body was "~30k
  chars, past the ~24k ceiling" — `wc -m` says 23,456, i.e. under the line it was judged against.
  Pass #7 (10-17) then claimed a cut to "roughly half its former size (~15k)" (actual **17,046**)
  and a description "tightened to the 57-char routing window" (**212 chars, untouched**) and its
  host-specific bullets "gone from SKILL.md" (**still in step 3**, duplicating the new reference
  word for word). Two passes, two reports that overstate — always `wc -m`/count yourself before
  believing a pass, and after a distillation grep the body for a host the reference covers:
  if the string appears in both files, the cut was not made.
  **And a no-op streak is not convergence:** three no-op passes (10-14/15/16) were followed by
  the most mutating pass of the week, so never advise raising `curator.interval_hours` on the
  strength of a streak — the next pass may be the one that does the work.
  A pass that changes nothing also calls `skill_manage` zero times (pass #6: 11 calls = 10
  `skill_view` + 1 `skills_list`), so "no refusals this pass" is not evidence the refusal classes
  went away — they only fire on attempted mutations. It takes its own pre-mutation snapshot (`gateway.log`:
  `curator: snapshot created (<ts>Z)`) and `logs/curator/` keeps ~10 report dirs.
- Curator mutations never appear in `state.db.sessions` — its gateway session id
  (`YYYYMMDD_HHMMSS_xxxxxx`) lives only in the ledger `evidence.session_id` and `gateway.log`.
- `hermes backup` full image is ~209 MiB / ~60 s on a small box — cheap enough
  to keep 7 daily + 4 weekly + 6 monthly images.
- `~/.hermes/vault` is the CREDENTIAL vault, not a knowledge vault. Do not
  confuse the two.
- Cron jobs created from a CLI session deliver locally by default; set
  `deliver` to a gateway platform (e.g. `telegram:<chat_id>`) for a real ping.
- Curator never deletes (max = archive); only explicit `hermes curator purge`
  removes archived skills, and it is recorded in the ledger. **But a consolidation archive is
  BODY-ONLY**: support files of a merged skill are re-homed into the umbrella, never copied
  into `.archive/<name>/` (2026-10-13: `.archive/starpath-validation/` = SKILL.md alone while
  its 8 references live under `software-development/starpath/`). `hermes curator restore <name>`
  therefore returns a body whose relative links point at nothing — take the files from the
  umbrella.
