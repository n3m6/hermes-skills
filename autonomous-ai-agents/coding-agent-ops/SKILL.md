---
name: coding-agent-ops
description: "Boot, supervise and inspect coding agents (dsh, codex)."
version: 1.0.0
author: Hermes Agent (curator)
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [coding-agents, harness, systemd, tmux, observability, opencode, dsh, benchmark]
    related_skills: [gated-repo-workflow]
---

# Coding agents on this box: launch, supervise, inspect, nudge

The owner points at an agent CLI on this machine and asks one of three things: get it installed and
staying up, tell me what it is doing, or nudge it. One discipline covers all three — **the process list
and the agent's own state store are the authority**; the TUI pane, the README and the agent's
self-report are not.

## When to Use

- **Launch & supervise (A)** — installing, upgrading, running or keeping alive an agent harness or a
  harness profile/plugin bundle (dsh and similar): "run it from my checkout", "make it survive a
  reboot".
- **Inspect (B)** — "there's an opencode session in a tmux — do you see it?", "what's the last
  message", "what is that agent doing right now", "is it still working", "check status now"; or
  learning what a benchmark subject (opencode, codex, cline, aider, pi, claude-code, cursor,
  antigravity-cli, copilot-cli) actually did in a real run rather than what its docs say.
- **Nudge (C)** — "ask whether it's stuck", "tell it X". The one case where typing into a pane is the
  job.

Not for: the owner's repos, gates and plan execution (`gated-repo-workflow`), or the design of the
agent product's own codebase.

## Rules that hold in all three modes

1. **Observe, do not drive.** No pane input, no signals to the agent's processes, no killing a run that
   merely looks slow — unless the owner asked for that specific action. Mode C is that ask.
2. **The store outranks the pane.** The pane truncates every line to the window width and renders only
   the one session the TUI is attached to; the on-disk transcript is untruncated, sequenced and
   timestamped. Answer from the store, and quote the pane only as "what is on screen".
3. **Read any store READ-ONLY.** For SQLite: `sqlite3.connect("file:" + path + "?mode=ro", uri=True)`.
   A live agent is mid-write in WAL mode; a writable open takes a lock and can force a checkpoint while
   it is committing. The `sqlite3` CLI being missing is not a blocker — Python's stdlib reads the DB and
   its WAL fine, including the read-only URI.
4. **Identify the binary from `/proc`, not from `ps`.** Agents launch through renamed aliases, so read
   `/proc/<pid>/exe`, `cmdline` and `cwd` and name the tool from those. An alias usually exists so a
   second instance can carry a distinct `argv[0]` (some CLIs key their state dir, socket or lock off
   it) — state that as the likely reason and confirm it from the processes and state paths.
5. **Prove liveness from CPU time, not `%CPU`.** Sample `utime+stime` (fields 14/15 of
   `/proc/<pid>/stat`) twice a few seconds apart and read the state field (`R` = running). A resident
   but stuck process shows a flat counter; `%CPU` is a lifetime average and still reads busy after it
   stopped.
6. **A plan and a set of setup questions are not approval.** Collecting repository, agent account,
   model provider and isolation answers is reconnaissance; create no profile, service or account wrapper
   until the owner explicitly says go. When he pushes back ("wait", "not yet"), stop cleanly, state
   what — if anything — was changed on the machine, and leave it until asked again.
7. **A proactive agent runs shell commands as the operator's OS user with no sandbox.** The blast radius
   is the credential set, not the watched repository: enumerate what the process can read (`~/.ssh`,
   agent configs, tokens, private repos), which account/CLI it acts as and what scope that token
   carries, and say so plainly before the first start — not after.
8. **Report verdict-first, and only what is written.** The exact last message verbatim in a code block,
   who wrote it, its timestamp, then what is running now. Answer the question asked before adding
   anything else; if the last message is a status line, call it a status line. State what you cannot
   see — "both sessions are alive and neither has produced user-facing output since X" is a complete
   answer, and speculation about intent is not.

## A — Launch and supervise

**A harness is a launcher, not an agent.** In dsh every agent behaviour lives in a *profile*: a
directory of plugins composed from ordered patch layers, so "install product X" means create a profile
and add X's bundle to it.

- **Composition order:** bundles in `dsh.profile.bundles` order → profile `cordis.patch.yml` → home
  `cordis.patch.yml` → `--patch` overlays. A bundle row can be `disabled: true`; that is how optional
  Sources ship.
- **Version gates fire at startup:** a plugin's `engines.dsh` (or its DSH peer ranges) must match the
  running CLI or boot/install fails and demands an explicit exemption. Check that before blaming the
  bundle.
- **Shipped profiles auto-initialize** (`web`, `headless`, `sdk`, `sdk-minimal`, `acp`); any other name
  (`superagent`, `work`, …) must be created once with `--from-default-profile <template>`. The launcher
  parses only its own flags — the first token it does not recognize starts the app's arguments.
- **A local checkout or fork is the normal path** for a `private: true` bundle, since there is no npm
  package to install: `pnpm install && pnpm build`, then `dsh plugin --profile <p> add "link:$PWD"` with
  an absolute path — `link:`, not `file:`, so the profile resolves the live checkout instead of a
  snapshot. `main`/`exports` point at `lib/`, so **the compiled output is what runs**; editing `src/`
  alone changes nothing.
- **Never build while the service is running** — a partially written `lib/` can be loaded mid-boot. The
  development loop is edit → `pnpm build && <restart>` as one command. Files read at runtime rather than
  compiled (`prompts/*.md`, `skills/*/SKILL.md`, `locale/*.json`) take effect on restart without a
  rebuild; use that path for prompt and behaviour work.
- **Supervise with a systemd user unit, never `nohup`/tmux** — those die at reboot and hide failures.
  Linger must be on (`loginctl enable-linger $USER`) so the unit starts without a login session.
  `KillSignal=SIGINT` with a long `TimeoutStopSec`, because an agent bundle finishes in-flight work on
  SIGINT and an Executor turn can run for minutes. If the bundle ships a `start|stop|status` script that
  launches tmux, let systemd own the process and use the script only for `status` — its `stop` would
  kill what `Restart=always` immediately brings back.
- **Panels bind loopback.** Reach them with `ssh -L <port>:127.0.0.1:<port> <host>`; never widen the
  bind to publish an agent's UI.
- **Read the manifest before the README prose** — `name`, `private`, `engines`, `peerDependencies`, the
  `exports` map (each entry may be a separate plugin), the `dsh` block — and verify provenance from the
  API (`gh repo view <owner>/<repo> --json isFork,parent,visibility,pushedAt`), not from a README that
  may describe itself as an unofficial prototype while being published under the vendor's org.

Pitfalls: `--from-default-profile` **deletes** the profile's `cordis.patch.yml` — on an existing
installation edit the patch file, do not re-run the creation command. An `engines.dsh` pin is a tested
version, not a floor; pin the documented version for first boot. `private: true` means the upgrade path
is `git pull` + rebuild + restart. State is one-way: a schema bump writes a database an older build
cannot open, so back up `stateDir` before upgrading or changing schema code. `dsh plugin` forwards to
pnpm inside the profile dir, so let corepack resolve the profile's own `packageManager` pin.

Depth: `references/dsh-profiles-and-bundles.md` (command surface, layout, the unit file, the
local-checkout and systemd procedures) and `references/dsh-superagent.md` (one bundle's domain model,
authorization, execution and customization traps).

## B — Inspect a live session

**1. Locate it — tmux and ps, not assumptions.**

```bash
tmux ls
tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} #{pane_pid} #{pane_current_command} #{pane_current_path} #{pane_tty}'
tmux capture-pane -p -t <session>:<win> -S -60      # the visible screen; the TUI render
ps -eo pid,ppid,etime,pcpu,args --sort=-pcpu | grep -iE 'opencode|codex|aider|claude|cursor|cline' | grep -v grep
```

`#{pane_title}` usually carries the agent's own session/task name, so capture it too. Hermes runs in its
own terminal session: the tmux you are asked about is almost never the one you are executing in, and a
`cd` failure from a stale session cwd says nothing about the agent's session.

**2. Identify** the real binary, cwd and repo from `/proc` before describing it (rule 4).

**3. Read the pane for the live render, then the store for the truth.** `references/opencode.md` carries
opencode's state paths, schema and ready-made read-only queries; the same shape — a session database or
JSONL log under the tool's state dir — holds for other agent CLIs. Find it rather than guessing.

**4. Establish the live state**, attributing each process:

```bash
ps -eo pid,etime,pcpu,args --sort=-pcpu | head -15; cat /proc/loadavg
```

Elapsed (`etime`) proves which long-running commands are still alive. Agents commonly blame
"contention" for a slow run; the process list and load average are how you check that claim instead of
repeating it.

**5. Classify the state: working, parked, or wedged.**

- *Working* — a turn is open: a tool call in flight, new message rows appearing.
- *Parked* — the turn ended cleanly on a background command: the last message is a status line followed
  by `type='idle'`, and the agent resumes when that command finishes.
- *Wedged* — parked, but the resume can never arrive. Prove all of it before saying wedged: the
  command's process is gone from `ps`; its output file is gone or the store still lists the job as
  running; there is no `type='synthetic'` resume row and the session's max `time_created` still equals
  the parked turn; and it has been silent far longer than the command should take, with no other
  session on the box explaining the CPU.

Wedging is a real, repeating defect, not a slow model: the background job's output is reaped as the job
ends, the completion notification then fails to deliver, the persistent job record is never reconciled,
and the agent waits forever with no error shown anywhere. State what is unrecoverable (if the output was
reaped, that run's result is gone and must be re-run) and separate the version-control fallout — work
left uncommitted in the tree — from the agent's own report.

**6. Answer "how far did it get" from the transcript timeline, not the pane.** Progress against a
review/plan checklist ("which finding did it finish last?") is recoverable read-only: take every
`type='assistant'` row of the current turn, concatenate its `content[].reasoning` and `text`, and collect
the work-item ids the agent quotes (the list's own id shape — `F01`, `W-257`, `phase 5`); the tool
commands in the same row say what was edited. An item is verified when its edit is followed by a
`state.status='completed'` tool row whose output ends in a green gate. Give both answers and keep them
apart: **last item verified** (newest targeted gate that passed) and **last item edited** (its tests have
not reported yet) — they are usually different, and calling the edited one complete is the error.
`scripts/opencode_timeline.py` prints this view.

A long turn can carry zero assistant `text` rows for hours — reasoning and tool calls only. Then there is
no interim report to read: say so rather than inferring phase status from the model's plans.

Pitfalls:

- **The pane is not the session.** A child/subagent session keeps writing to the store while the pane
  shows the parent, so a pane frozen for ten minutes can have live work behind it. Check the newest
  messages across ALL sessions by time and follow `parent_id` to find the child tree.
- **Order by the store's own sequence and time columns**, never rowid or the order rows come back.
- **"Waiting" next to a running shell means the turn ended, not the work.** The agent resumes when the
  command finishes.
- **A `| tail -N` pipeline writes nothing until the command exits.** A zero-byte or absent output file
  is not evidence of failure; judge liveness from the process.
- **A shared agent log receives lines from every invocation on the box, including your own probes.** A
  `--version` or update check you run lands in the same file; attribute by run id and role before
  calling anything the session's activity.
- **A shell output directory whose mtime is newer than every file in it means a file was removed** —
  that is how you time a reaped output when the file itself is gone.
- **The store file's mtime moving is not session activity.** WAL checkpoints and internal bookkeeping
  touch it; only message rows and job records are activity.
- **A long build under load is not a hang.** Check the load average and the child process list before
  suggesting anything be killed, and never kill or interrupt the agent's processes on your own
  initiative.
- **Do not chase the agent's HTTP API for state.** The service URL and secret are in its state dir, but
  the auth scheme is not the obvious Bearer header and guessing costs calls; the on-disk store is
  authoritative and cheap.
- **An agent's shell commands run under the shared `serve --service` process, not the TUI.** `pgrep -P
  <tui-pid>` is empty while a gate test compiles; find the job by its command line under the service pid
  and read its `shell/<hash>/sh_*.out`. Trace from the service, and check `cwd` before assuming a repo.
- **`max(seq)` stays flat while a tool call runs.** The next row is written when the model produces its
  next assistant message, so `session_v2.time_updated` moving with no new `seq` means the same turn is
  still open — not that it advanced. Judge the turn by `max(seq)` plus the absence of a later `idle` row.
- **The pane interleaves tool blocks and collapses each with "(N earlier lines)".** A `test result: ok`
  or `job: ... ok (exit 0)` line can belong to a *previous* tool call, not the command above it; only the
  `.out` file or the store's `seq` orders them.
- **Between two reads a gate job can finish.** A pid that vanishes right after a green line in the `.out`
  ended cleanly; re-read the store and `.out` before reporting "still running".

## C — Nudge a parked or wedged session (only on request)

Type **one self-contained message** into the pane, then confirm from the store that a turn started.
Never nudge silently, and never report a nudge as delivered on the pane alone.

- **Check for a modal first.** Grep the capture for `allow|deny|permission|[y/n]|confirm|select`;
  keystrokes aimed at an agent prompt land in a dialog instead.
- **Send the text literally** — `tmux send-keys -t <t> -l '<line>'`, then `Enter` as its own call — and
  verify from the store: a new `user` row carrying your text, then `assistant` rows, then a fresh
  `idle`. A parked session resumes in seconds.
- **Put the diagnosis in the message.** The agent cannot see what you can: give it the observed facts
  (what exited, when, what was lost) and ask for its current state, not a bare "are you stuck?" it can
  only answer with a guess. Add nothing the owner did not approve — "report your state" is a nudge,
  "do the next phase" changes the task.

Recipe, timings and the wedge signature: `references/opencode.md`.

## Support files

- `references/opencode.md` — opencode's state paths, the `session_v2` / `session_message` / `kv` schema,
  read-only query recipes, the work-list progress timeline, the background-shell wedge signature, and the
  pane/log/nudge procedure.
- `scripts/opencode_timeline.py` — read-only dump of a session's current-turn timeline: work-item ids
  quoted in reasoning, edit/gate commands, tool status, and the newest shell-output tails.
- `references/dsh-profiles-and-bundles.md` — the dsh command surface, profile layout and composition
  order, running a bundle from a local checkout, the systemd unit, and pre-deploy manifest reading.
- `references/dsh-superagent.md` — the dsh-superagent bundle: domain model, authorization, execution,
  architecture and customization traps.
