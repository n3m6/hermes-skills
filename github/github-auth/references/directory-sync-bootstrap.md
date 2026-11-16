# Attaching a live directory to a remote repo (bootstrap + weekly sync)

## When to Use

A directory already full of local work has to become a checkout of a remote
repo — and the local files must survive: a skills tree, a dotfiles dir, a config
store. The failure mode to avoid is a mirror sync that deletes files the remote
never tracked. The recurring job lives in `scripts/skills-git-sync.sh`;
this file is the one-time attach plus the verification that decides whether the
job can be trusted.

## 1. Back up before touching anything

```bash
tar czf ~/.hermes/backups/$(basename "$DIR")-pre-sync-$(date +%Y%m%d-%H%M%S).tar.gz \
  -C "$(dirname "$DIR")" "$(basename "$DIR")"
```

Record the path in your reply. A backup is cheap; a mistaken `rsync --delete`
against a live tree is not recoverable.

## 2. Diff the trees before choosing a direction

Walk both trees, hash every file, and classify: identical, differing,
remote-only, local-only. Then, for differing *skill* files, read frontmatter
`version:` on both sides — **do not assume the remote is newer**. A machine
installed from a newer release is routinely ahead of a repo snapshot, and
taking the remote there silently downgrades the tool it belongs to.

Local-only files are the real risk: a mirror sync would delete them. Decide per
class — keep them untracked (they stay on disk and show as `??`), or add them
to `.gitignore` if they are regenerated artifacts.

## 3. Attach without clobbering

```bash
cd "$DIR"
git init -q -b main
git remote add origin <url>
git fetch -q origin main
git reset -q --mixed origin/main        # HEAD+index = remote tree, WORKTREE UNTOUCHED
git branch -q --set-upstream-to=origin/main main
git checkout -- .                       # materialize tracked files; untracked stay
git status --short
```

`git reset --mixed` followed by `git checkout -- .` is the whole trick: the
checkout writes every tracked path (overwriting differing ones and creating
remote-only directories) but never removes untracked local files, which is what
`git clone` into a non-empty dir cannot do.

Then restore the paths where local is ahead from the backup:

```bash
tar xzf <backup>.tar.gz -C "$(dirname "$DIR")" "$(basename "$DIR")/<path>"
```

Those show as ` M` in `git status` — that is the correct, honest state until
they are committed.

## 4. Verify with the host's own discovery, not file counts

Run the program's scanner (for Hermes: `hermes skills list`) and reconcile every
disk entry against it. Absences are legitimate when gated — e.g. `platforms:
[macos]` skills never list on Linux, and `environments: [kanban]` skills only
load in that environment. A scanner also skips dot-directories such as
`.archive/` by design, so materializing an archive from the repo adds no live
skills.

## 5. Scan before the first push

The first sync publishes everything the `.gitignore` does not exclude. Before
running it: grep the staged set for token/key patterns and for sensitive
filenames (`.env`, `id_*`, `*.pem`, `credentials*`), and abort on a real hit.
Documentation placeholders (`ghp_xxxx…`, `sk-xxxx`) are fine — say so rather
than reporting them as leaks.

## 6. Wire the recurring job

Shim in `~/.hermes/scripts/` that `exec`s the script inside the skills tree, so
the tree copy stays the single source of truth:

```bash
#!/usr/bin/env bash
exec "$HOME/.hermes/skills/github/github-auth/scripts/skills-git-sync.sh" "$@"
```

Then a `no_agent` cron job whose `script` is the shim's filename (resolved under
`~/.hermes/scripts/`), scheduled weekly. `no_agent` matters: stdout is delivered
verbatim, an empty stdout sends nothing, and a non-zero exit becomes the failure
alert — no tokens spent on the happy path.

Set the PATH inside the script, not in the job: a credential helper that lives on
an interactive PATH fails at 06:00.

## 7. Test the matrix before trusting the schedule, then run it once

Against a throwaway clone with a **local bare repo** as origin (no network, no
risk to the real remote):

1. happy path — local change committed and pushed, local head == bare head
2. no-op — reports already in sync, exit 0
3. conflict with `SKILLS_SYNC_RESOLVER=0` — exit 3, clean tree, both safety
   refs kept, no rebase left open
4. lying resolver (`SKILLS_SYNC_HERMES=<fake>` printing `RESULT: RESOLVED` and
   doing nothing) — must be caught as `push did not land`, exit 3

Then run the real script once in the foreground, and verify from three sources:
local `HEAD`, `git -C "$DIR" ls-remote origin refs/heads/main`, and
`gh api repos/<owner>/<repo>/commits/main --jq .sha`. Waiting for the first
scheduled tick to discover a broken job is the expensive way.

## Pitfalls

- Run every git command with `git -C <repo>` (or `cd` first). The shell's cwd
  persists between tool calls; a leftover cwd in a sandbox clone made a
  `ls-remote` read the sandbox remote and report a false MISMATCH.
- Never `rm -rf` the directory the persistent shell is sitting in. Every later
  command then fails at `getcwd`; `cd` to a stable path first, or pass the
  tool's own workdir override.
- `gh repo list` covers repos you own; for everything reachable use
  `gh api 'user/repos?per_page=100&affiliation=owner,collaborator,organization_member' --paginate`.
- `gh repo list --json visibility` returns `PRIVATE` / `PUBLIC` (uppercase);
  filter the `isPrivate` boolean instead of matching lowercase strings.
- A sync job that mirrors a whole directory will adopt files the remote never
  had (bundled dependencies, generated docs). Decide that explicitly with the
  user before the first run rather than discovering it in the commit.
- The conflict resolver is an unattended `hermes chat` run, so it needs a
  non-interactive approvals mode. Under an interactive mode a blocked command
  ends as `UNRESOLVED` (exit 3) rather than a hang — the script verifies state
  either way, so never re-label that alert as success.
