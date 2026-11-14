# dsh-superagent: what the bundle does and where to change it

A proactive coding agent scoped to **one GitHub repository**, packaged as a DSH bundle. Optional
Feishu Source. Published as a research prototype (README disclaims product status); usually
encountered as a fork of the vendor's single-commit repo. Workers act through a dedicated GitHub
account's `gh` wrapper, so comments and PRs appear under that identity.

## Flow

`Source → Trigger → Thread → Eval → Decision → Ticket → Assignment → Executor → Channel`

- **Source** — event stream (GitHub notifications/issue/PR/CI; Feishu live+h history+topic polling).
  Holds its own read cursor; drops the bot's own messages before they enter the domain.
- **Trigger** — one immutable event. Idempotence unit: accepting it twice creates one Ticket.
- **Thread** — triggers in time order. One Eval at a time; concurrent triggers batch into the next.
- **Eval** — deterministic **gate** (who may originate work) + model **assessment** (is this work, which
  written rules match). Stateless; has a deadline that starts only when the candidate reaches the main
  session; two requeues then a third expiry records `unavailable`.
- **Mandate** — what an accept grants: scope, strength, matched rules, requester identity, Policy
  version. Immutable; only a human stop withdraws it; revalidation can revoke it before a resume.
- **Ticket** — unit of authorized work, owns execution state `open → ended`, back to open when a
  human writes on one of its Threads (unless stopped). A later PR comment resumes the *same* Ticket
  under the *same* Mandate; no new Eval.
- **Subscription** — Ticket↔Thread fan-out. Delivers later discussion to the worker as context,
  **bypasses the gate, grants no authority**; bot/CI messages reach it but never wake an ended Ticket.
- **Assignment** — Ticket bound to one Executor instance; several over time, independent lifecycle.

## Authorization (the part that decides whether it is safe)

- **explicit**: an allowed person addresses the agent, or follows up on a Thread that already has a
  Ticket. **inferred**: unlisted sender, unaddressed message, or a listed bot — needs assessment and
  at least one enabled rule.
- **Accept modes**: `off` (inferred never becomes a candidate), `observe` (default; positive
  assessments are recorded as "would accept" and nothing happens), `auto` (positive assessment
  accepts). Use `observe` to dry-run judgement against real traffic.
- **Admission table** per Source: three cells per receiving scope (on-list/unaddressed,
  off-list/addressed, off-list/unaddressed) → explicit / inferred / ignore.
- **Policy version** hashes rules + accept mode + per-Source policy. A change requeues running Evals
  and notifies only affected live Tickets; it does not cancel running work.

## Execution

- One DSH Session per Ticket (`worker-<ticketId>`) and one directory under the execution root,
  created by an optional prepare command (typically `git worktree`) with a 10-minute budget.
- Presets: `dsh-superagent-router` (main session) and `dsh-superagent-worker`. The worker preset
  moves any foreground shell command to a background job after 5 s so an incoming human message is
  not blocked by a long build. Both run with `danger-full-access` as the OS user.
- **Worker slots** cap concurrency; a human message or status request gets one extra slot and wakes
  ahead of new launches, so inbound work cannot starve a person.
- Background shell jobs/subagents keep the slot; after 30 min shell jobs are killed and the Ticket
  reports `waiting`. On host restart, running Assignments restart with a recovery note telling the
  worker to check directory/git/GitHub before repeating any outside action.

## Architecture (where to look when customizing)

- `src/core/` — pure synchronous domain, no I/O. `Engine` is the **single writer** of triggers,
  threads, decisions, tickets, assignments; five parts: `Intake`, `Evals`, `Tickets`,
  `Assignments`, `Replies`. Callers get role-scoped `Pick`s (`EngineForSources`,
  `EngineForMainSession`, `EngineForPeople`, `EngineForSettings`, `EngineForExecutor`).
- `src/app/` — composition root (`runtime.ts`), `Effects` (durable queue: `assessment`,
  `launch`, `delivery`, `relay`, `notice`, `reply`; enqueued inside the transaction, run after
  commit), `Outbox` (only writer of message receipts; per-Ticket ordering), `Sessions`, `Prompts`,
  `Settings`, HTTP API + React panel.
- `src/sources/` — `SourceKind` protocol + registry; `github*.ts`, `feishu*.ts`; each is also a
  separate package export (`./github-watch`, `./feishu-watch`).
- SQLite `orchestrator.sqlite` in `stateDir`, generated columns `open`/`active`/`subscribed` so the
  2-second pass reads only live work.

## Customization traps

- `SCHEMA_VERSION` is strict and only increases. Changing stored shapes means bumping it **and**
  adding a migration step; a DB written by a fork is unreadable by upstream and vice versa. Decide
  this before first boot, because `stateDir` creates the database immediately.
- `pnpm check` = typecheck + ~59 spec files + build, and two tests are documentation gates:
  `tests/class-docs.spec.ts` (JSDoc on every class) and `tests/docs.spec.ts` (numbered docs link only
  backwards; `docs/007-architecture.md` tables must list every module and test). Deep customization
  means maintaining those tables, or removing the gates deliberately.
- Adding a Source kind: implement `SourceKind`, register it in a plugin entry, add the `exports`
  entry + tsdown entry, and insert a row in `cordis.patch.yml`. A kind that is only configured, not
  registered, is invisible.
- Team-adjustable behaviour lives in `prompts/*.md` (read at runtime, no rebuild); structural
  behaviour lives in code. The docs' philosophy discourages adding settings — a business need
  becomes an attribute of an existing concept or prompt text.
- Watch limits/defaults (`eval.timeoutSeconds`, `executor.maxWorkers`, `blockedCommands`) are
  settings; anything about *who may authorize* is Policy and versioned.

## Deployment specifics

- `stateDir` holds DB, lock, `worker-bin` shims, `worker-gitconfig`, and `work/` ticket directories.
- Default panel/management API: `http://127.0.0.1:3082/orchestrator/api/`; requests need header
  `x-orchestrator-request: 1` and a loopback Host. API saves have panel permissions and can change
  environment/account fields.
- Agent account: a dedicated GitHub user with its own `GH_CONFIG_DIR` wrapper (`gh-agent`); never
  reuse the operator's token — the token's scope is its blast radius. Equivalent pattern for a
  Feishu bot (`LARKSUITE_CLI_CONFIG_DIR` + `lark-bot`, bot-only identity).
- The bundled `scripts/dsh-superagent` runs `dsh --profile <p> --no-open` inside tmux, signals SIGINT
  for graceful stop (up to 300 s), and exits 0 healthy / 1 not running / 2 component error / 3 setup
  needed. If systemd owns the process, use the script only for status.
- First real request: from an allowed account comment `@<agent login> <request>` on an Issue. A
  mention added by editing an Issue body is not received; post a new comment.
