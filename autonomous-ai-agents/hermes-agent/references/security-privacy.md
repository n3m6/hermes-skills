# Security & Privacy Toggles

Common "why is Hermes doing X to my output / tool calls / commands?" toggles — and the exact commands to change them. Most of these need a fresh session (`/reset` in chat, or start a new `hermes` invocation) because they're read once at startup.

### Secret redaction in tool output

Secret redaction is **on by default** — tool output (terminal stdout, `read_file`, web content, subagent summaries, etc.) is scanned for strings that look like API keys, tokens, and secrets before it enters the conversation context and logs. Leave it enabled for normal use:

```bash
hermes config set security.redact_secrets true       # keep enabled globally
```

**Restart required.** `security.redact_secrets` is snapshotted at import time — toggling it mid-session (e.g. via `export HERMES_REDACT_SECRETS=false` from a tool call) will NOT take effect for the running process. Tell the user to change it in config from a terminal, then start a new session. This is deliberate — it prevents an LLM from flipping the toggle on itself mid-task.

Disable only when you deliberately need raw credential-like strings for debugging or redactor development:
```bash
hermes config set security.redact_secrets false
```

### PII redaction in gateway messages

Separate from secret redaction. When enabled, the gateway hashes user IDs and strips phone numbers from the session context before it reaches the model:

```bash
hermes config set privacy.redact_pii true    # enable
hermes config set privacy.redact_pii false   # disable (default)
```

### Command approval prompts

`approvals.mode` decides what happens to **flagged** actions only: commands matching a
dangerous-pattern rule (`rm -rf`, `git reset --hard`, `curl … | bash`, …), guarded writes
(e.g. `~/.ssh/config`), computer-use and plugin rules. Unflagged work — `git add/commit/
push`, ordinary file edits, most builds — never reaches the gate, so no mode makes it
prompt or block. That reframes the usual question: "will my unattended job be blocked?"
depends on whether its *actions* are flagged, not on the mode. 

The modes are:

- `smart` — auto-approve a low-risk command once, deny high-risk commands, and prompt when uncertain (default)
- `manual` — always prompt for a flagged command
- `off` — skip the approval gate entirely (short-circuits before any per-context policy)

```bash
hermes config set approvals.mode smart       # recommended middle ground
hermes config set approvals.mode off         # bypass everything (not recommended)
```

Ask the real guards for a verdict without executing anything (exit 0 allow / 2 ask /
3 deny) — this is the cheap way to check a claim about a mode instead of asserting one:

```bash
hermes approvals test -- rm -rf ./build            # ask-approval (recursive delete)
hermes approvals test -- 'curl -s http://h | bash' # ask-approval (pipe remote content to shell)
hermes approvals test -- git push origin HEAD:main # allow - no guard matched
```

#### Unattended runs: three per-context knobs

No human is present to answer a prompt in a cron, one-shot or webhook session, so each of
those contexts has its own binary switch (`approve`/`off`/`allow`/`yes` count as approve;
anything else denies):

| key | governs | default |
|---|---|---|
| `approvals.single_query_mode` | `hermes chat -q` / `--oneshot` runs | deny |
| `approvals.cron_mode` | agent-driven cron runs | deny |
| `approvals.unattended_mode` | webhook / api_server / msgraph sessions | deny |

```bash
hermes config set approvals.single_query_mode approve   # trust only one-shot runs
```

Prefer that over `approvals.mode: off` when the goal is "let my scheduled job act":
interactive sessions keep prompting while one-shot runs stay deterministic. Note the
direction of the trade — `approve` converts a denial into a silent approval, so it is an
availability setting, not a safety one. It also only matters if the run's actions are
flagged at all; a job that just edits files and runs git never consults it.

Per-invocation bypass without changing config:
- `hermes --yolo …`
- `export HERMES_YOLO_MODE=1`

Note: YOLO / `approvals.mode: off` does NOT turn off secret redaction. They are independent.

#### If you flip approvals to test something, put it back in the same turn

Testing a job *under* a different posture means `hermes config set approvals.mode manual` —
a **global, persistent** change, not a flag scoped to one command. Left behind it surfaces as
unexplained approval prompts in a completely different chat minutes later, and neither chat
can see the other. 2026-11-14: a resolver test set `manual` + `single_query_mode: approve` at
13:23:55, ran the e2e twice, and left it there; the owner hit prompts in Telegram and asked
"why am I getting approval messages now?" — and the first answer blamed "a different session",
true by session id and useless, because that session was the agent's own turn 30 s earlier.

- Capture the old value first (`hermes config get approvals.mode`), restore it before the
  final message even if the test failed, and say in the report that config was changed and
  put back, with both values.
- Prefer not mutating config at all: `--yolo` / `HERMES_YOLO_MODE=1` cover a single
  invocation, and a scratch `HERMES_HOME` covers "test the config path" itself.
- When a setting changed under the owner, list the mutating session and check whether it is
  one of *yours* from earlier in the task before calling it "another session".

Before claiming prompts are active, check the accumulated "always" state: a saved
approval or a `command_allowlist` entry (`hermes config get command_allowlist`) auto-
approves that pattern class regardless of mode — tool output will say "auto-approved by an
'always' approval the user saved earlier" even under `manual`.

### "Reset permissions" / "make Hermes ask again"

The user usually means: wipe the accumulated "Always allow" state — NOT yolo
mode, and NOT a per-edit diff prompt (which doesn't exist; file writes never
go through the approval prompt, only shell commands do). Two stores hold it:

1. Shell-command allowlist: `hermes config set command_allowlist '[]'`
2. Shell-hook consent (only if present): `rm -f ~/.hermes/shell-hooks-allowlist.json`

Then sanity-check `hermes config get approvals.mode` (should not be `off`)
and confirm `--yolo` isn't baked into their launch alias or systemd unit.

### Shell hooks allowlist

Some shell-hook integrations require explicit allowlisting before they fire. Managed via `~/.hermes/shell-hooks-allowlist.json` — prompted interactively the first time a hook wants to run.

### Disabling the web/browser/image-gen tools

To keep the model away from network or media tools entirely, open `hermes tools` and toggle per-platform. Takes effect on next session (`/reset`). See `references/configuration.md` for the toolset list.

