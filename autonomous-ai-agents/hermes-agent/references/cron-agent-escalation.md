# Escalating a cron script to an agent (rare-path pattern)

Use when a recurring job is deterministic almost every time but occasionally needs
judgment: a git conflict, a malformed input, a fetch that needs a workaround, a merge
that needs reading. Shape: **one `no_agent` script job**; the happy path costs zero
tokens, and the script itself spawns an agent only on the branch that needs reasoning.

Why not `monitor`: monitor gates an agent on changed script output. If the happy-path
output varies (shas, timestamps, counts) it wakes the agent on every tick, and when it
does gate, the agent's prose replaces the script's own precise status line. Reach for
monitor only when the happy-path output is genuinely stable; otherwise escalate from
inside the script.

## Script skeleton

```bash
# 1. single-flight, so two ticks (or a manual run) can never overlap
exec 9>".git/myjob.lock" || exit 1
flock -n 9 || { echo "job: SKIPPED - already running"; exit 0; }

# 2. repair leftover state BEFORE any precondition check.
#    A rebase leaves HEAD detached, so a "detached HEAD" branch guard that runs first
#    makes the job fail forever on a repo whose only problem is a half-finished rebase.
#    Abort it, remember that you did, and carry on.

# 3. happy path: small, deterministic, idempotent

# 4. exceptional path: write a self-contained brief to a file INSIDE .git
#    (keeps `git status` clean) and hand it over
BRIEF=".git/myjob-brief-$(date -u +%Y%m%dT%H%M%SZ).md"
hermes chat --oneshot -Q -t terminal,file --max-turns 40 \
  --run-budget "$BUDGET" --in "$TARGET_DIR" --query-file "$BRIEF" >"$LOG" 2>&1

# 5. verify the OUTCOME from state, then report one status line and exit 0/2/3
```

Budget: a `no_agent` **script** job may run up to 3600 s (`_DEFAULT_SCRIPT_TIMEOUT` in
`cron/scheduler.py`), while an agent-driven cron run is bounded by an inactivity window
(`HERMES_CRON_TIMEOUT`, default 600 s, `0` = unlimited). That is why the escalation runs
as a child process of the script: the long work happens inside the script's budget, not
inside an agent run's inactivity window. Wrap it in `timeout -k 30 $((BUDGET+240))` anyway.

## The brief is an interface, not a suggestion

Use `--query-file`, never `-q` with interpolated text: the brief contains paths, shas and
file contents that would otherwise be shell-interpreted or quote-broken. Require an
exact machine-checkable footer, because the script parses it and the user reads it:

```
RESULT: RESOLVED | UNRESOLVED
FILES: <path> - <what was kept for that file and why>   (one line per changed file)
PUSHED: yes | no
NOTES: <what the owner must re-check, or ->
```

Also state in the brief: the one rule the owner chose for ambiguous cases (this user
prefers per-hunk judgment with a per-file explanation over a blanket "local wins"),
that the agent must leave a clean state before stopping if it runs out of budget, and
that it must not touch anything outside the target directory.

## Never trust the agent's self-report

A resolver agent that prints `RESULT: RESOLVED` / `PUSHED: yes` is the single most
common false success: it can do nothing, resolve locally and skip the push, or leave a
rebase open and still print success. Verify from state, and only then print your own OK:

- no rebase/merge/cherry-pick still in progress (`[ -d .git/rebase-merge ]`)
- no unmerged paths (`git diff --name-only --diff-filter=U`)
- clean worktree (`git status --porcelain`)
- no conflict markers left **in the paths that were actually conflicted** — scanning the
  whole tree false-positives on docs that quote marker examples
- the push landed: `git ls-remote origin refs/heads/<branch>` equals `git rev-parse HEAD`

On failure: restore a clean, known state, print the reason plus the agent log path, keep
rollback refs, and exit non-zero — that non-zero exit is what turns into a failure alert
for a `no_agent` job.

## Containing what the agent may break

- Create rollback refs before handing over (e.g. one ref for each side of a conflict) and
  prune them to the newest N pairs so forensics survive without unbounded growth.
- Re-check and abort any operation the agent left open after it exits, whatever it claims.
- Approvals do **not** have to be `off` for the child to act: editing files and running
  `git add/commit/rebase/push` are unflagged, so they never reach the approval gate even
  under `manual`. The per-context knobs (`approvals.single_query_mode`, `cron_mode`) only
  bite on *flagged* actions — `rm -rf`, `curl | bash`, guarded writes. Get a verdict with
  `hermes approvals test -- <cmd>` instead of asserting that a mode gates your job: a
  resolver kept working with global `manual` and `single_query_mode: deny`, which is
  exactly the kind of inherited assumption that gets written into a runbook unchecked.
  The directory restriction is an instruction, not a sandbox — say that to the user rather
  than implying isolation; a real boundary is a container or a separate unprivileged user.

## Test matrix before trusting it

Run against a throwaway copy (a local bare repo can stand in for the real remote) and
inject fake binaries through an env override such as `MYJOB_HERMES=/tmp/fake-hermes`:

1. happy path / no-op path — exit 0, status line, nothing changed
2. resolver does nothing — must report UNRESOLVED, must not claim success
3. resolver lies (`RESULT: RESOLVED`, real state untouched) — must be caught
4. resolver does the work but never pushes, while printing `PUSHED: yes` — must be caught
5. leftover operation from an interrupted run — must be aborted before any commit, and no
   conflict markers may reach a commit
6. then one real-agent end-to-end on the sandbox copy, asserting the resulting bytes and
   that local HEAD == remote HEAD

Assert with `grep -E '^(PASS|FAIL)'` in the harness itself; a harness that only prints
output proves nothing.

### Fixture mechanics that make these tests lie

Each of these yields a **false PASS**: the case runs, nothing looks wrong, and the behaviour
you meant to exercise never happened. Assert the precondition as its own check ("sandbox
really is mid-rebase") so a vacuous case fails loudly instead of passing.

- **Fetch before simulating.** A fresh clone's `origin/<branch>` is stale, so a fixture that
  pushes to the bare "remote" and then starts a rebase inside the working clone without
  `git fetch` finds nothing to replay and never conflicts. Only hand-driven fixtures need
  this — the job under test fetches itself.
- **Re-seed per case, or build fixtures from unique content.** A fixture that edits fixed
  text (`sed -i 's/^alpha v1/alpha REMOTE/'`) silently no-ops once an earlier case has
  already rewritten that line: nothing commits, no conflict appears, and the assertion
  passes for the wrong reason. Either `rm -rf` the whole sandbox for each case, or write a
  nonce (`echo "local-$(date +%s%N)" > conflict.txt`) so the same path always clashes.
- **`git commit -a` never stages a newly created fixture file.** When the conflict fixture
  is a file that did not exist before, use `git add -A`.
- **An add/add conflict is `AA` in `git status --porcelain`, not `UU`.** Detect unmerged
  paths with `git diff --name-only --diff-filter=U`; grepping status for `^UU` misses
  both-added and both-deleted conflicts entirely.

## Working implementation

`github/github-auth/scripts/skills-git-sync.sh` in this skills tree is the filled-in
version of this pattern: weekly reconcile of a skills directory with GitHub, agent-resolved
conflicts, independent verification, safety refs pruned to the newest five pairs. The cron
job reaches it through a **symlink** at `~/.hermes/scripts/skills-git-sync.sh`, so the file
in the skills tree is the single source of truth: edit it there, and never let the entry
point become a copy — a shim or duplicate drifts, a symlink cannot. Keep it executable
(`git ls-tree` shows `100755`) so a direct invocation works, not just `bash <path>`.

Put that file under a **non-bundled** skill — grep `.bundled_manifest` in the skills root for
the name; a bundled skill can be refreshed by a Hermes update and take your additions with
it, while a hub- or agent-owned skill keeps them.
