# opencode: on-disk state and read-only queries

Verified against opencode v2.x (`@opencode/cli`). Paths are per-user, under `$HOME`; adjust if the agent
runs as another user.

## Launcher and processes

- `~/.local/node-v24.10.0/bin/opencode` — a symlink to `../lib/node_modules/@opencode/cli/bin/opencode.exe`.
  A second alias pointing at the same target (e.g. `opencode2`) is how a second concurrent instance is
  started; both report the same `opencode --version`, so the alias name is not a version difference.
- The TUI spawns a long-lived child: `opencode.exe serve --service`. One per box, shared by instances — its
  presence does not mean anyone is attached to a session. **Every shell tool command is a child of this
  service**, not of the TUI and not of the session's `opencode -s ses_...` process: while a gate test
  compiles, `pgrep -P <tui-pid>` shows nothing and the job lives under the service pid.

## State directories

- `~/.local/share/opencode/`
  - `opencode.db` (plus `-wal`, `-shm` — the DB is live and in WAL mode)
  - `log/opencode.log` — every process's log, all invocations on the box, in one file
  - `snapshot/` (git-based file snapshots), `repos/`, `shell/`
- `~/.local/state/opencode/`
  - `prompt-history.jsonl` — the **user's** submitted prompts, one JSON object per line, oldest first
  - `service.json`, `model.json`, `frecency.jsonl`, `locks/`, `latest/`

`prompt-history.jsonl` holds prompts only. The agent's own replies are never in it — do not look there for
"the last message".

## Schema (the two tables that answer the question)

`session_v2` — one row per session, including subagent sessions:

| column | meaning |
| --- | --- |
| `id` | session id (`ses_...`), the key `session_message.session_id` joins on |
| `parent_id` | the parent session for a subagent; `NULL` for a top-level session. This is the subagent tree |
| `slug` / `title` | human name (`eager-wizard`) and the task text shown in the TUI title |
| `directory` | the repo/worktree the session runs in |
| `agent`, `model` | e.g. agent `build`, model `deepseek-v4.1-flash` |
| `cost`, `tokens_input/output/reasoning/cache_read/cache_write` | usage totals |
| `time_created`, `time_updated`, `time_idle` | ms epoch |
| `idle_outcome` | `succeeded` etc. — set when the session goes idle |

`session_message` — the transcript, one row per message:

| column | meaning |
| --- | --- |
| `session_id`, `seq` | the session, and the ordering key (order by `seq`, not rowid) |
| `type` | `user` \| `assistant` \| `idle` \| `synthetic` \| `tool` |
| `time_created` / `time_updated` | ms epoch |
| `data` | JSON payload (see below) |

`data` shapes:

- `type='user'` → `{text, files[], agents[], skills[]}`; `files[].mention` gives the `@path` spans.
- `type='assistant'` → `{agent, model, content[], finish, cost, tokens{...}, time{}}`. `content[]` entries are
  `{type:'reasoning'|'text'|'tool', ...}`; tool entries carry `name` and `state.input.command`.
- `type='idle'` → `{outcome}` — the turn boundary. A turn's last assistant text is the message immediately
  before it.
- `type='synthetic'` → injected context (e.g. a resume notice); not something the user typed.

Also present but normally empty: `session_inbox`, `session_pending`, `event`.

`kv` — small key/value table; the useful keys are in-flight background jobs:

| key | value |
| --- | --- |
| `job.background/<notificationMsgID>` | `{id: <shellID>, notificationID, recovery: {kind: 'shell', sessionID, shellID, command}, status}` |

One row per background shell the app is still tracking. `status: "running"` is written at launch and only
reconciled when the completion notification is delivered, so a row whose shell's process has exited is a
wedge, and more rows than jobs actually running means orphans have accumulated. `notificationID` is a
`msg_...` id: if no `session_message` row carries that id, the notification that would have resumed the
agent was never written. `recovery.command` is the exact command line — the fastest way to name an orphan.

## Read-only query recipes

Always the read-only URI; never open the live DB writable.

```python
import sqlite3, json, datetime
con = sqlite3.connect("file:/home/<user>/.local/share/opencode/opencode.db?mode=ro", uri=True)
con.row_factory = sqlite3.Row
cur = con.cursor()
def ts(ms): return datetime.datetime.utcfromtimestamp(ms/1000).strftime("%Y-%m-%dT%H:%M:%SZ")
```

Which session is live, and the subagent tree:

```sql
select id, slug, title, parent_id, directory, time_updated, time_idle, idle_outcome
from session_v2 order by time_updated desc limit 6;
```

Newest messages anywhere on the box — the step that catches an active child session the pane is not
showing:

```sql
select session_id, type, seq, time_created from session_message order by time_created desc limit 10;
```

Last user message of a session:

```sql
select seq, time_created, data from session_message
where session_id = ? and type = 'user' order by seq desc limit 1;
```

Last assistant text of a session (parse the JSON; keep only `content[].type == 'text'`):

```python
for m in cur.execute("select seq, time_created, data from session_message "
                     "where session_id = ? and type = 'assistant' order by seq desc limit 1", (sid,)):
    j = json.loads(m["data"])
    for part in j.get("content", []):
        if part.get("type") == "text":
            print(m["seq"], ts(m["time_created"]), part["text"])
```

## Progress against a work list ("which finding did it finish?")

The agent quotes its own work-item ids in its reasoning, so the transcript dates each one. Read the current
turn's assistant rows and match the list's id shape (`F01`, `W-257`, `phase 5`) in
`content[].reasoning` + `text`; the tool commands in the same row show the edit or the gate.

```python
since = cur.execute("select max(seq) from session_message where session_id=? and type='user'",
                    (sid,)).fetchone()[0]
for r in cur.execute("select seq,time_created,data from session_message "
                     "where session_id=? and type='assistant' and seq>? order by seq", (sid, since - 1)):
    j = json.loads(r["data"]); txt, cmds, sts = "", [], []
    for p in j.get("content", []):
        if p.get("type") == "reasoning": txt += p.get("text", "")
        elif p.get("type") == "text": txt += "\n" + p.get("text", "")
        elif p.get("type") == "tool":
            st = p.get("state") or {}
            cmds.append(str((st.get("input") or {}).get("command") or p.get("name")))
            sts.append(st.get("status"))
    ids = sorted(set(re.findall(r"\b(?:F|W)\d{2,3}\b", txt)))
    print(r["seq"], ts(r["time_created"]), ids, sts, txt.strip().split("\n")[0][:120], cmds[:1])
```

- **Verified** = an edit row followed by a `state.status='completed'` tool row whose `.out` ends in a green
  gate (`test result: ok`, `job: ... ok (exit 0)`). The newest such row answers "which one did it finish
  last".
- **The last row is usually an edit whose tests have not reported.** Report it separately as the last item
  *edited*; it is not complete and the next gate can still fail it.
- Hours with no assistant `text` rows are normal on a long fix loop (reasoning + tool calls only). There is
  no interim report — say that instead of synthesizing one.
- Map an edit to its item from the `command` text: `python3 - <<'PY'` heredocs name the file in
  `p='...'`, and `tools/job test ... <filter>` names the suite that proves the item.

## Pane and log

- `tmux display-message -p -t <target> '#{pane_title}'` gives `OC | <session title>` — which session the TUI
  is attached to. Match that title against `session_v2.title` to know whose transcript answers the question.
- `log/opencode.log` lines carry `role=server` (the attached session — its `spawning process` lines give the
  exact command it is running right now) or `role=cli` (any CLI invocation on the box, including your own
  `--version` and update checks). `run=<id>` groups one process; use it to attribute lines rather than
  assuming everything recent belongs to the session.

## Background shells: output, exit, and the wedge

`shell/<worktree-hash>/sh_<id>.out` holds one background command's output, keyed by the worktree it ran in
(the same hash appears under `snapshot/`). The launching tool message records the id and that path in
`state.metadata.shellID`, plus a text part reading "Command moved to the background (shell ID: ...)".

Foreground shell tool calls still write to a `.out` under the same directory, and their processes are
children of the shared `serve --service` pid — not of the TUI. Read the newest `.out` for the verdict line
(`job: <id>: ok (exit 0) in <n> s`, or the failing test name); a pid that disappears between two reads is a
job that ended, so re-read the file before calling anything wedged.

The failure signatures, in the order they fire:

1. The shell exits and its `.out` is removed — the directory's mtime ends up newer than every file in it.
2. About a second later the service asks for that output and misses:
   `GET /api/shell/<shellID>/output` → `404` in `log/opencode.log`. That is the failed notification read.
3. No `type='synthetic'` row and no new message: the resume never happens, `session_v2.resume_attempts`
   stays 0, and the session's max `time_created` still equals the parked turn.
4. `kv` keeps `status: "running"` for that shell indefinitely; the next run adds a *second* row, so stale
   rows accumulate across wedges.

Everything under the shell directory is reaped, so a long run whose only result lives there can be lost.
When a run must be recoverable, have it write outside that directory instead of trusting the capture:

```bash
<cmd> > /tmp/<name>.log 2>&1; echo "exit $?" >> /tmp/<name>.log
```

## Nudging a parked session (only on the owner's request)

```bash
T=<session>:<win>
tmux capture-pane -p -t $T -S -40 | grep -inE 'allow|deny|permission|\[y/n\]|confirm|select'   # modal check
tmux capture-pane -p -t $T -S -8                    # know the exact frame before you type
tmux send-keys -t $T -l '<one self-contained line>'
sleep 1
tmux send-keys -t $T Enter
sleep 25; tmux capture-pane -p -t $T -S -24         # did it move?
```

`-l` sends the text literally (no key-name interpretation); send `Enter` as its own call. A parked session
resumes in seconds: the reply shows in the pane and lands in the store as a new `user` row (your text), then
`assistant` rows, then a fresh `idle`. Verify from the store, not the pane alone.

Write the nudge as an information transfer, not a question: state the observed facts (what exited, when,
what was lost) and ask the agent to report its current state. A pointed message like that earns a full
self-report — implemented, verified, outstanding, uncommitted — which is usually worth more than the
question the owner asked. Do not smuggle in new instructions.
