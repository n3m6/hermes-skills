# Personality & SOUL.md

Two separate levers. Pick the right one before writing anything.

| Lever | Where | Scope | Selected by |
|---|---|---|---|
| **SOUL.md** | `$HERMES_HOME/SOUL.md` | Permanent identity — slot #1 of the system prompt, every surface (CLI, gateway, desktop, cron) | Automatic; nothing to enable |
| **/personality presets** | built-ins in `hermes_cli/personality.py`, extras under `personalities:` in config.yaml | Session-level system-prompt overlay; the base identity still applies underneath | `/personality <name>` in a session; default in `display.personality` |

Rule of thumb: **"who I am everywhere" → SOUL.md. "this conversation's voice" → preset.** If the user is vague ("set up your personality"), ask both questions in one `clarify` call — permanent vs switchable, and what vibe — rather than guessing at an identity change that is hard to notice is wrong.

## Procedure (permanent identity)

1. **Back up first.** `cp $HERMES_HOME/SOUL.md $HERMES_HOME/backups/SOUL.md.bak-$(date +%Y%m%d-%H%M%S)` (mkdir the backups dir if needed). There is no undo and the file is the agent's whole voice.
2. **Read the current file** so you know what you are preserving. A fresh install seeds it from `hermes_cli/default_soul.py` (`DEFAULT_SOUL_MD`), so most edits are "keep this spine, change this tone" — not a rewrite from zero.
3. **Write durable voice guidance only** — tone, directness, warmth, how to handle uncertainty, disagreement, and ambiguity. Keep it stable across contexts. File paths, repo conventions, and workflow steps belong in `AGENTS.md`, not here.
4. **Verify it actually loads** (see below). Do not assume a successful write means a loaded identity.
5. **Report** what changed in two or three bullets plus the backup path. Do not paste the whole file back — the user can read it, and pasting it reads as a replay.

## Verify the identity loads

```bash
cd $HERMES_HOME/hermes-agent && \
  python -c "from agent.prompt_builder import load_soul_md; s=load_soul_md(); print(len(s)); print(s[:120])"
```

- Returns `None` for a missing **or empty** file — that is the documented fallback to the built-in identity, so an empty SOUL.md is not "no personality", it is the default one.
- `load_soul_md()` runs the threat scanner. A user-authored SOUL.md that trips it is **warned, not blocked** (unlike AGENTS.md, where a hit blocks the content) — but a distribution-owned SOUL.md, planted by `hermes profile install <git-url>`, is scanned as untrusted.
- SOUL.md is read fresh each message: no restart, no `hermes config set`, nothing to reload. An already-running session keeps the prompt it started with, so say "applies from the next session" rather than claiming the live conversation changed.

## Built-in presets

14 ship in `hermes_cli/personality.py`: `helpful, concise, technical, creative, teacher, kawaii, catgirl, pirate, shakespeare, surfer, noir, uwu, philosopher, hype`. Custom entries in `personalities:` ADD to these or OVERRIDE one by name.

**There is no `hermes personality` CLI command.** Do not try to list or apply presets from the shell — they are applied with the `/personality` slash command (or `display.personality` for the default). To enumerate the current list, grep the source keys rather than inventing names:

```bash
grep -oE '^\s{4}"[a-z0-9_-]+"' \
  $HERMES_HOME/hermes-agent/hermes_cli/personality.py | tr -d ' "' | sort -u
```

Adding a custom preset (never hand-edit config.yaml — a stray indent corrupts it and breaks the live gateway):

```bash
hermes config set display.personalities.reviewer "You are a meticulous code reviewer."   # string form
```

The active selection lives in `display.personality`, never in `personalities:` and never in `agent.system_prompt` (that last one is the user's own manual prompt and is left alone).

## What a good SOUL.md looks like

Sections that carry weight: **Voice** (length matching, no filler, plain claims), **Warmth** (how care shows up), **Honesty** (uncertainty, disagreement, never inventing output). Keep it focused enough to actually shape behavior — a sprawling file dilutes into generic instructions the model skims.

A warmth rewrite is the common request. The shape that works: keep every directness rule intact as the spine, then redefine warmth as **attention, not enthusiasm** — remember what the user said, notice frustration, lead with the fix before the verdict, allow one line of "nice, that worked" and explicitly ban praise paragraphs and performed feelings. Warmth that reads as scripted is worse than none.
