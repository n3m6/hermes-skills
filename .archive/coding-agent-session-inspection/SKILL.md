---
name: coding-agent-session-inspection
description: "Use when reading or nudging a live coding agent session."
version: 1.1.0
author: Hermes Agent (curator)
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [coding-agents, opencode, tmux, observability, benchmark]
    related_skills: [gated-repo-workflow, deepseek-harness]
---

# Inspecting a live coding-agent session

## When to Use

- The owner points at an agent CLI running on this box and asks about it: "there's an opencode session in a
  tmux — do you see it?", "what's the last message in that session?", "what is that agent doing right now?",
  "is it still working?", "check status now".
- The owner asks whether it is **stuck**, or asks you to **nudge** it ("ask whether it's stuck", "tell it
  X") — steps 6 and 7; that is the one case where typing into the pane is the job.
- You need to know what one of the benchmark subjects (opencode, codex, cline, aider, pi, claude-code,
  cursor, antigravity-cli, copilot-cli) actually did in a real run, not what its docs say.
- Default posture is **observe, do not drive**: no pane input, no signals to the agent's processes, no
  killing a run that merely looks slow — unless the owner asks for that specific action.

Not for an agent that never started: a profile, bundle or service that fails to boot is a launcher and
supervision problem (`deepseek-harness`), not a live session to read.

## Procedure

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

**2. Identify the real binary, cwd, and repo before describing it.**

```bash
ls -l /proc/<pid>/exe; tr '\0' ' ' < /proc/<pid>/cmdline; ls -l /proc/<pid>/cwd
```

Agents are frequently launched through a renamed alias or a second instance name, so `ps` shows a name that
is not the product. Read `exe` and `cwd` and name the tool from those. An alias that resolves to the same
`exe` is normally there so a second instance can carry a distinct `argv[0]` (some CLIs key their state
directory, socket, or lock off it) — state that as the likely reason, and confirm it from the processes and
state paths rather than presenting the guess as fact.

**3. Read the pane for the live render, then read the agent's own store for the truth.**

The pane truncates every line to the window width and renders only the one session the TUI is attached to.
The agent's on-disk transcript is untruncated, sequenced, and timestamped — answer from it, and quote the
pane only as "what is on screen". See `references/opencode.md` for opencode's store, schema, and queries;
the same shape (a session database or JSONL log under the tool's state dir) holds for other agent CLIs — find
it rather than guessing the path.

**4. Establish the live state, attributing each process.**

```bash
ps -eo pid,etime,pcpu,args --sort=-pcpu | head -15; cat /proc/loadavg
```

Elapsed (`etime`) proves which long-running commands are still alive. Agents commonly blame "contention"
for a slow run; the process list and load average are how you check that claim instead of repeating it.

**5. Report verdict-first.** The exact last message verbatim in a code block, who wrote it, its timestamp,
then what is running now. Answer the question asked before adding anything else — "do you see it" gets the
session, its repo, its model, and its current task; "the last message" gets that message.

**6. Classify the state: working, parked, or wedged.**

- *Working* — a turn is open: a tool call in flight, new message rows appearing.
- *Parked* — the turn ended cleanly on a background command; the last message is a status line followed by
  `type='idle'`, and the agent resumes when that command finishes.
- *Wedged* — parked, but the command is over and the resume can never arrive. Prove all of it before saying
  wedged: the command's process is gone from `ps`; its output file is gone or the store still lists the job
  as running; there is no `type='synthetic'` resume row and the session's max `time_created` still equals
  the parked turn; and it has been silent far longer than the command should take with no other session on
  the box explaining the CPU.

Wedging is a real, repeating defect, not a slow model: the background job's output is reaped as the job
ends, the completion notification then fails to deliver, the persistent job record is never reconciled, and
the agent waits forever with no error shown anywhere. State what is unrecoverable — if the output file was
reaped, that run's result is gone and must be re-run — and separate the version-control fallout (work left
uncommitted in the tree) from the agent's own report.

**7. Nudge a parked or wedged session — only when the owner asks, and verify it landed.**

Type one self-contained message into the pane and then confirm from the store that a turn started. Never
nudge silently, and never report a nudge as delivered on the pane alone. The recipe, modal pre-check, and
what a good nudge says are in `references/opencode.md`. Give the agent the diagnosis it cannot see, ask for
its current state, and add nothing the owner did not approve — "report your state" is a nudge, "do the next
phase" changes the task.

## Pitfalls

- **Read any store READ-ONLY.** For SQLite: `sqlite3.connect("file:" + path + "?mode=ro", uri=True)`. A live
  agent is mid-write in WAL mode; opening it writable takes a lock and can force a checkpoint while it is
  committing.
- **The `sqlite3` CLI may not be installed — that is not a blocker.** Python's stdlib `sqlite3` reads the
  database and its WAL fine, including the read-only URI. Do not stop at `command not found`.
- **The pane is not the session.** A child/subagent session keeps writing to the store while the pane shows
  the parent, so a pane that has looked frozen for ten minutes can have live work behind it. Before saying
  "nothing new", check the newest messages across ALL sessions by time, and follow `parent_id` to find the
  child tree.
- **Order by the store's own sequence and time columns**, never by rowid or the order rows come back.
- **"Waiting" next to a running shell means the turn ended, not the work.** The last assistant message is
  the last thing written before a background command; the agent resumes when the command finishes.
- **Report what is written, not what you infer.** If the last message is a status line, call it a status
  line. Do not manufacture a question or a request the agent never asked — the owner may be asking precisely
  because he missed something and cannot tell the difference from your summary.
- **A shared agent log receives lines from every invocation on the box, including your own probes.** A
  `--version` or update check you run lands in the same file. Attribute lines by run id and role before
  calling anything the session's activity.
- **A long build under load is not a hang.** Check the load average and the child process list before
  suggesting anything be killed, and never kill or interrupt the agent's processes on your own initiative.
- **State what you cannot see.** "Both sessions are alive and neither has produced user-facing output since
  X" is a complete answer; padding it with speculation about what the agent intends is not.
- **A `| tail -N` pipeline writes nothing until the command exits.** A zero-byte or absent output file is not
  evidence of failure; judge liveness from the process, not from the log.
- **Prove a process is alive and progressing from CPU time, not `%CPU`.** Sample `utime+stime` (fields 14/15
  of `/proc/<pid>/stat`) twice a few seconds apart and read the state field (`R` = running). A resident but
  stuck process shows a flat counter; `%CPU` is a lifetime average and still looks busy after it stopped.
- **A shell output directory whose mtime is newer than every file in it means a file was removed.** That is
  how you time a reaped output when the file itself is gone.
- **The store file's mtime moving is not session activity.** WAL checkpoints and internal bookkeeping touch
  it; only message rows and job records are activity.
- **On a nudge, put the diagnosis in the message.** The agent cannot see what you can — give it the observed
  facts (what exited, when, what was lost) and ask for its state, not a bare "are you stuck?" it can only
  answer with a guess.
- **Check for a modal before typing into a pane.** Grep the capture for permission/confirm/select markers
  first; keystrokes aimed at an agent prompt land in a dialog instead.
- **Do not chase the agent's HTTP API for state.** The service URL and secret are in its state dir, but the
  auth scheme is not the obvious Bearer header and guessing costs calls. The on-disk store is authoritative
  and cheap; reserve API calls for when the store genuinely cannot answer.

## References

- `references/opencode.md` — opencode's state paths, database schema (`session_v2`, `session_message`, the
  `kv` background-job records), the wedge signature, the nudge recipe, and ready-made read-only queries.
