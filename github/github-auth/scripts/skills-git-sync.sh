#!/usr/bin/env bash
# skills-git-sync.sh - weekly reconcile of the live Hermes skills dir with GitHub,
# with automatic agent resolution when a rebase conflicts.
#
# Runs as a Hermes cron no_agent script job ('skills-git-sync', Mondays):
# stdout is delivered verbatim, non-zero exit = failure alert.
#
# Each run, inside $SKILLS_REPO (default ~/.hermes/skills):
#   1. single-flight lock; abort any leftover rebase/merge/cherry-pick from a
#      previously interrupted run (half-resolved state must never be committed)
#   2. commit everything the .gitignore does not exclude
#   3. fetch origin, rebase local work onto origin/<branch>
#      clean  -> push, report, exit 0
#      clash  -> safety refs for both sides, abort the rebase (clean tree), hand the
#                resolution to a real agent (`hermes chat --oneshot`, bounded budget),
#                then VERIFY its work independently before reporting success
#   4. one status line; exit 3 whenever a conflict could not be verifiably resolved
#
# Auth: global credential helper from `gh auth setup-git` (!gh auth git-credential),
# hence ~/.local/bin on PATH. Never force-pushes, never rewrites published history.
#
# Env knobs:
#   SKILLS_REPO / SKILLS_BRANCH    target repo / branch (default ~/.hermes/skills, main)
#   SKILLS_SYNC_RESOLVER=0        disable the agent resolver (report-only mode)
#   SKILLS_SYNC_HERMES=<path>     hermes binary used for the resolver
#   SKILLS_SYNC_BUDGET=<seconds>  resolver run budget (default 420)
#
# Exit codes: 0 ok/no-op/resolved, 2 fetch or push trouble, 3 unresolved conflict, 1 setup error.
set -uo pipefail

REPO="${SKILLS_REPO:-$HOME/.hermes/skills}"
BRANCH="${SKILLS_BRANCH:-main}"
COMMIT_NAME="${SKILLS_SYNC_NAME:-Abdulla Faraz}"
COMMIT_EMAIL="${SKILLS_SYNC_EMAIL:-n3m6@users.noreply.github.com}"
RESOLVER="${SKILLS_SYNC_RESOLVER:-1}"
RESOLVE_BUDGET="${SKILLS_SYNC_BUDGET:-420}"

export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"

say() { printf '%s\n' "$*"; }
fail() { say "skills-sync: FAILED - $1"; exit "${2:-1}"; }

[ -d "$REPO/.git" ] || fail "no git repository at $REPO"
cd "$REPO" || fail "cannot cd into $REPO"

# --- 1. single-flight ------------------------------------------------------
exec 9>".git/skills-sync.lock" || fail "cannot open lock file in $REPO/.git"
if ! flock -n 9; then
  say "skills-sync: SKIPPED - a previous sync still holds the lock"
  exit 0
fi

# leftover operation from an interrupted run: restore a clean tree BEFORE anything else.
# (a rebase leaves HEAD detached, so this must run before the branch check below)
leftover=""
if [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ]; then
  if git rebase --abort >/dev/null 2>&1 || git am --abort >/dev/null 2>&1; then
    leftover="rebase"
  fi
elif [ -f .git/MERGE_HEAD ]; then
  if git merge --abort >/dev/null 2>&1; then leftover="merge"; fi
elif [ -f .git/CHERRY_PICK_HEAD ]; then
  if git cherry-pick --abort >/dev/null 2>&1; then leftover="cherry-pick"; fi
fi

cur_branch=$(git symbolic-ref --short -q HEAD) || fail "detached HEAD in $REPO (and not inside a rebase/merge to abort)"
[ "$cur_branch" = "$BRANCH" ] || fail "on branch '$cur_branch', expected '$BRANCH'"
git rev-parse --verify -q HEAD >/dev/null || fail "repository has no commits"

STATE_DIR=".git/skills-sync"
mkdir -p "$STATE_DIR" || fail "cannot create $STATE_DIR"

try() {  # retries cover a transient .git/index.lock held by another process
  local n=0
  until "$@" >/dev/null 2>&1; do
    n=$((n + 1))
    [ "$n" -ge 4 ] && return 1
    sleep 5
  done
  return 0
}

start_sha=$(git rev-parse --short HEAD)

# --- 2. commit local changes ----------------------------------------------
changed=0
if [ -n "$(git status --porcelain)" ]; then
  changed=$(git status --porcelain | wc -l)
  try git add -A || fail "git add -A failed (index locked?)"
  git diff --cached --quiet && changed=0
  if [ "$changed" -gt 0 ]; then
    try git -c user.name="$COMMIT_NAME" -c user.email="$COMMIT_EMAIL" \
        commit -q -m "skills sync $(date -u +%Y-%m-%d) ($changed path(s))" \
      || fail "git commit failed"
  fi
fi

# --- 3. fetch + rebase onto remote ----------------------------------------
try git fetch --prune --quiet origin "$BRANCH" \
  || fail "git fetch origin $BRANCH failed (network or auth)" 2

remote_sha=$(git rev-parse --verify -q "origin/$BRANCH" || true)
pulled=0

if [ -n "$remote_sha" ]; then
  pulled=$(git rev-list --count "HEAD..origin/$BRANCH" 2>/dev/null || echo 0)
  if [ "${pulled:-0}" -gt 0 ]; then
    pre_rebase=$(git rev-parse HEAD)
    if ! git rebase --quiet "origin/$BRANCH" >"$STATE_DIR/rebase.log" 2>&1; then
      # ---------------- conflict path -----------------------------------
      git diff --name-only --diff-filter=U >"$STATE_DIR/conflicted.txt" 2>/dev/null || true
      npaths=$(wc -l <"$STATE_DIR/conflicted.txt" 2>/dev/null || echo 0)
      stamp=$(date -u +%Y%m%dT%H%M%SZ)
      local_ref="skills-sync/local-$stamp"
      remote_ref="skills-sync/remote-$stamp"
      git branch -f "$local_ref" "$pre_rebase" >/dev/null 2>&1 || true
      git branch -f "$remote_ref" "origin/$BRANCH" >/dev/null 2>&1 || true
      # keep the 5 newest pairs of safety refs (local-only branch names; never pushed)
      for pat in 'refs/heads/skills-sync/local-*' 'refs/heads/skills-sync/remote-*'; do
        git for-each-ref --sort=-creatordate --format='%(refname:short)' "$pat" 2>/dev/null \
          | tail -n +6 | while IFS= read -r old; do git branch -D "$old" >/dev/null 2>&1; done
      done
      git rebase --abort >/dev/null 2>&1
      say "skills-sync: CONFLICT - $npaths path(s) clash between local work and origin/$BRANCH"
      say "  safety refs: $local_ref (local side), $remote_ref (remote side); rebase aborted, tree clean"

      hermes_bin="${SKILLS_SYNC_HERMES:-$(command -v hermes 2>/dev/null || echo "$HOME/.local/bin/hermes")}"
      if [ "$RESOLVER" = "0" ]; then
        say "  resolver disabled (SKILLS_SYNC_RESOLVER=0) - resolve by hand: cd $REPO && git rebase origin/$BRANCH"
        exit 3
      fi
      if [ ! -x "$hermes_bin" ]; then
        say "  resolver unavailable ($hermes_bin not executable) - resolve by hand: cd $REPO && git rebase origin/$BRANCH"
        exit 3
      fi

      prompt_file="$STATE_DIR/resolve-prompt-$stamp.md"
      log_file="$STATE_DIR/resolve-log-$stamp.txt"
      {
        echo "You are resolving a git rebase conflict in a Hermes skills repository. No human is"
        echo "watching; a cron job is waiting on your result. Work fast and leave the repo clean."
        echo
        echo "Repo: $REPO   branch: $BRANCH   remote: origin = $(git remote get-url origin 2>/dev/null || echo origin)"
        echo "State: the automatic sync committed local changes as commit $pre_rebase on top of"
        echo "  $(git rev-parse --short "$remote_ref"), which origin/$BRANCH has now moved past (${pulled} commit(s))."
        echo "  The rebase was aborted for you: the tree is clean and $BRANCH is at $pre_rebase."
        echo "  Safety refs: $local_ref = local side, $remote_ref = remote side. Do not touch either ref."
        echo
        echo "Conflicted paths from the attempt:"
        sed 's/^/  - /' "$STATE_DIR/conflicted.txt"
        echo
        cat <<'RULES'
Your job:
1. `git rebase origin/main` and resolve every conflict it raises.
2. Judge each hunk on its merits - there is NO blanket rule. These are agent skills:
   markdown SKILL.md files with YAML frontmatter, plus scripts and reference docs.
   Keep both sides when both added real content; take the remote text when it is a
   newer correction of the same passage; take the local text when it adds content the
   remote lacks. Never drop content just to make a conflict disappear, and never
   invent content neither side had.
3. Delete every conflict marker (<<<<<<<, =======, >>>>>>>). Leave no duplicated sections.
4. `git add` each resolved file, then `git rebase --continue` until the rebase ends.
   Do not amend existing commits and do not create empty commits.
5. Verify before pushing: `git status --porcelain` empty, `git diff --diff-filter=U` empty,
   and `grep -rn '^<<<<<<<' . --exclude-dir=.git` finds nothing.
6. `git push origin HEAD:main`. Never force-push, never rewrite history, never delete refs.
7. Final answer, exactly this shape and nothing else:
RESULT: RESOLVED | UNRESOLVED
FILES: <path> - <what you kept for that file and why>   (one line per conflicted file)
PUSHED: yes | no
NOTES: <what the owner must re-check, or ->

If you cannot finish inside your budget: run `git rebase --abort` before you stop, leave the
tree clean, and answer RESULT: UNRESOLVED with what blocked you. A clean abort beats a
half-finished rebase. Do not touch anything outside this repository.
RULES
      } >"$prompt_file"
      # make the instructions follow $BRANCH instead of the literal 'main' in the RULES block
      sed -i "s|origin/main|origin/$BRANCH|g; s|HEAD:main|HEAD:$BRANCH|g" "$prompt_file"

      say "  handing it to a resolver agent (budget ${RESOLVE_BUDGET}s, log: $log_file)"
      timeout -k 30 $((RESOLVE_BUDGET + 240)) "$hermes_bin" chat --oneshot -Q \
        -t terminal,file --max-turns 40 --run-budget "$RESOLVE_BUDGET" \
        --in "$REPO" --query-file "$prompt_file" >"$log_file" 2>&1
      resolver_rc=$?

      # never leave an operation hanging, whatever the agent did or failed to do
      mid_op=""
      if [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ]; then
        git rebase --abort >/dev/null 2>&1
        mid_op="rebase still in progress"
      elif [ -f .git/MERGE_HEAD ]; then
        git merge --abort >/dev/null 2>&1
        mid_op="merge still in progress"
      fi

      # --- independent verification: never trust the agent's self-report --
      why=""
      [ -n "$mid_op" ] && why="$mid_op"
      if [ -z "$why" ] && [ -n "$(git diff --name-only --diff-filter=U 2>/dev/null)" ]; then
        why="unmerged paths remain"
      fi
      if [ -z "$why" ] && [ -n "$(git status --porcelain 2>/dev/null)" ]; then
        why="worktree not clean"
      fi
      if [ -z "$why" ]; then
        while IFS= read -r f; do
          [ -n "$f" ] && [ -f "$f" ] || continue
          if grep -qE '^(<<<<<<< |>>>>>>> )' "$f" 2>/dev/null; then
            why="conflict markers left in $f"
            break
          fi
        done <"$STATE_DIR/conflicted.txt"
      fi
      local_head=$(git rev-parse HEAD 2>/dev/null)
      remote_head=$(git ls-remote origin "refs/heads/$BRANCH" 2>/dev/null | awk 'NR==1{print $1}')
      if [ -z "$why" ] && [ "$local_head" != "$remote_head" ]; then
        why="push did not land (local $(git rev-parse --short HEAD) vs remote ${remote_head:0:7})"
      fi

      if [ -n "$why" ]; then
        say "skills-sync: UNRESOLVED - $why (resolver exit $resolver_rc)"
        say "  repo left clean at $(git rev-parse --short HEAD); both sides preserved as $local_ref / $remote_ref"
        say "  agent log: $log_file"
        grep -E '^(RESULT|FILES|NOTES):' "$log_file" 2>/dev/null | head -8 | sed 's/^/  agent: /'
        say "  resolve by hand: cd $REPO && git rebase origin/$BRANCH"
        exit 3
      fi

      conflict_note=$(grep -E '^(FILES|NOTES):' "$log_file" 2>/dev/null | head -6 | tr '\n' ' ' | cut -c1-400)
      say "skills-sync: OK - conflict resolved by agent and verified: rebased onto origin/$BRANCH, pushed $(git rev-parse --short HEAD)"
      [ -n "$conflict_note" ] && say "  agent: $conflict_note"
      say "  safety refs kept: $local_ref / $remote_ref"
      exit 0
    fi
  fi
fi

# --- 4. clean path: push if ahead -----------------------------------------
pushed=0
if [ -n "$remote_sha" ]; then
  ahead=$(git rev-list --count "origin/$BRANCH..HEAD" 2>/dev/null || echo 0)
else
  ahead=$(git rev-list --count HEAD)
fi
if [ "${ahead:-0}" -gt 0 ]; then
  try git push --quiet origin "HEAD:$BRANCH" \
    || fail "git push failed - $ahead commit(s) still local" 2
  pushed=$ahead
fi

# --- 5. status line --------------------------------------------------------
end_sha=$(git rev-parse --short HEAD)
note=""
[ -n "$leftover" ] && note=" (cleaned up interrupted $leftover)"
if [ "$changed" -eq 0 ] && [ "${pulled:-0}" -eq 0 ] && [ "$pushed" -eq 0 ] && [ -z "$leftover" ]; then
  say "skills-sync: OK - already in sync with origin/$BRANCH ($end_sha)"
  exit 0
fi
say "skills-sync: OK - committed $changed path(s), pulled ${pulled:-0} remote commit(s), pushed $pushed commit(s); $start_sha -> $end_sha$note"
exit 0
