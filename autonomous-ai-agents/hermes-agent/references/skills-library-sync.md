# Skills Library ↔ Git Repo Sync

Use when the user wants `$HERMES_HOME/skills` connected to their own skills
repo ("sync this repo to ~/.hermes/skills", "back up my skills to git", "pull
my skills onto this machine").

## Core rule: attach, never mirror-delete

A fresh Hermes install carries bundled skills the user's repo may not track.
`rsync --delete`, `git clean`, or a `checkout -f` against an empty tree wipes
them. The goal is: repo is the baseline for tracked paths, local-only skills
survive untouched, and every real difference stays visible in `git status`
for the user to decide on.

## Procedure

1. **Inventory both sides before writing.** Clone or fetch the repo into
   scratch, then compare SKILL.md sets and per-file hashes:
   `git -C ~/.hermes/skills rev-parse --is-inside-work-tree` first — it is not
   a repo on most machines. Report counts of identical / differing /
   repo-only / local-only before touching anything. If local-only skills
   exist (apple/*, pdf, maps, xurl, dogfood on a stock install), a deletion-
   style sync is wrong and the user should hear why before it happens.
2. **Back up unconditionally.** ~1 MB, takes a second:
   ```bash
   mkdir -p ~/.hermes/backups
   tar czf ~/.hermes/backups/skills-pre-sync-$(date +%Y%m%d-%H%M%S).tar.gz \
     -C ~/.hermes skills
   ```
3. **Attach the worktree without moving files.** `git clone` refuses a
   non-empty dir and `checkout -f` clobbers everything; this sequence makes
   the repo the baseline while leaving untracked skills alone:
   ```bash
   cd "$HERMES_HOME/skills"
   git init -b main
   git remote add origin <repo-url>
   git fetch origin main
   git reset --mixed origin/main      # HEAD+index = repo tree, worktree untouched
   git branch --set-upstream-to=origin/main main
   git checkout -- .                  # writes tracked files only; untracked survive
   ```
   Afterwards local-only skills show as `??`, kept-local edits as `M`, and
   repo-only skills are on disk. Future syncs are `git pull`.
4. **Choose direction per file, not per repo.** Diff the frontmatter
   `version:` on each conflicting SKILL.md — a machine installed from a newer
   Hermes can be AHEAD of a repo snapshot that is only days old. Keep the
   newer side, restore the kept-local trees from the backup tarball, and say
   plainly that those paths are now deliberately modified relative to HEAD.
5. **Let `.archive/` materialize.** `EXCLUDED_SKILL_DIRS` in
   `agent/skill_utils.py` lists `.git`, `.github`, `.hub`, `.archive`,
   `.curator_backups`, `.locks`, venv/node_modules/cache dirs; the scanner
   prunes them. Archived skills therefore cannot load. Do not assume that for
   arbitrary hidden dirs — only the named set is excluded.
6. **Verify with `hermes skills list`, not by counting SKILL.md.** A count
   mismatch is expected and correct: `platforms: [macos]` skills are hidden
   on Linux, and `environments:` / `requires_toolsets:` gating (e.g.
   `kanban`) hides others. Reconcile the difference before calling anything
   broken.
7. **Report the end state**: baseline commit, skills added, skills kept at a
   newer local version, bundled skills left untracked, backup path, and that
   the current session's skill index predates the sync (new skills register
   at the next session start; `skill_view` resolves them immediately).

## Pitfalls

- Do not "tidy" the resulting `git status`. Untracked bundled skills and the
  handful of `M` files are the user's local deltas and the point of the
  exercise.
- Do not push to the repo as part of a sync the user framed as pulling. Ask
  first; kept-local newer versions are the natural thing to commit later.
- Overlap is a review item, not an error: a library can ship a consolidated
  skill and older split ones for the same domain. Flag the duplication and
  let the user pick a set instead of silently deleting skills.
