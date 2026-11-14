---
name: github-auth
description: "GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Authentication, Git, gh-cli, SSH, Setup]
    related_skills: [github-pr-workflow, github-code-review, github-issues, github-repo-management]
---

# GitHub Authentication Setup

This skill sets up authentication so the agent can work with GitHub repositories, PRs, issues, and CI. It covers two paths:

- **`git` (always available)** — uses HTTPS personal access tokens or SSH keys
- **`gh` CLI (if installed)** — richer GitHub API access with a simpler auth flow

## Detection Flow

When a user asks you to work with GitHub, run this check first:

```bash
# Check what's available
git --version
gh --version 2>/dev/null || echo "gh not installed"

# Check if already authenticated
gh auth status 2>/dev/null || echo "gh not authenticated"
git config --global credential.helper 2>/dev/null || echo "no git credential helper"
```

**Decision tree:**
1. If `gh auth status` shows authenticated → use `gh` for API work, then wire git to that token (§ "gh is already logged in" below) instead of minting a PAT
2. If `gh` is installed but not authenticated → use "gh auth" method below
3. If `gh` is not installed → use "git-only" method below (no sudo needed)

**Authenticated `gh` does not mean `git` can push.** `gh auth status` also reports a
"Git operations protocol" line (often `ssh`); that is gh's own preference, not git's
configuration. Always check the two things git itself will use before you promise a
push will work:

```bash
git config --get-all credential.helper
git config --get-all 'credential.https://github.com.helper'
git ls-remote <remote-url>   # empty output + exit 0 = reachable and unauthenticated-OK
```

---

## Method 1: Git-Only Authentication (No gh, No sudo)

This works on any machine with `git` installed. No root access needed.

### Option A: HTTPS with Personal Access Token (Recommended)

This is the most portable method — works everywhere, no SSH config needed.

**Step 1: Create a personal access token**

Tell the user to go to: **https://github.com/settings/tokens**

- Click "Generate new token (classic)"
- Give it a name like "hermes-agent"
- Select scopes:
  - `repo` (full repository access — read, write, push, PRs)
  - `workflow` (trigger and manage GitHub Actions)
  - `read:org` (if working with organization repos)
- Set expiration (90 days is a good default)
- Copy the token — it won't be shown again

**Step 2: Configure git to store the token**

```bash
# Set up the credential helper to cache credentials
# "store" saves to ~/.git-credentials in plaintext (simple, persistent)
git config --global credential.helper store

# Now do a test operation that triggers auth — git will prompt for credentials
# Username: <their-github-username>
# Password: <paste the personal access token, NOT their GitHub password>
git ls-remote https://github.com/<their-username>/<any-repo>.git
```

After entering credentials once, they're saved and reused for all future operations.

**Alternative: cache helper (credentials expire from memory)**

```bash
# Cache in memory for 8 hours (28800 seconds) instead of saving to disk
git config --global credential.helper 'cache --timeout=28800'
```

**Alternative: set the token directly in the remote URL (per-repo)**

```bash
# Embed token in the remote URL (avoids credential prompts entirely)
git remote set-url origin https://<username>:<token>@github.com/<owner>/<repo>.git
```

**Step 3: Configure git identity**

```bash
# Required for commits — set name and email
git config --global user.name "Their Name"
git config --global user.email "their-email@example.com"
```

**Step 4: Verify**

```bash
# Test push access (this should work without any prompts now)
git ls-remote https://github.com/<their-username>/<any-repo>.git

# Verify identity
git config --global user.name
git config --global user.email
```

### Option B: SSH Key Authentication

Good for users who prefer SSH or already have keys set up.

**Step 1: Check for existing SSH keys**

```bash
ls -la ~/.ssh/id_*.pub 2>/dev/null || echo "No SSH keys found"
```

**Step 2: Generate a key if needed**

```bash
# Generate an ed25519 key (modern, secure, fast)
ssh-keygen -t ed25519 -C "their-email@example.com" -f ~/.ssh/id_ed25519 -N ""

# Display the public key for them to add to GitHub
cat ~/.ssh/id_ed25519.pub
```

Tell the user to add the public key at: **https://github.com/settings/keys**
- Click "New SSH key"
- Paste the public key content
- Give it a title like "hermes-agent-<machine-name>"

**Step 3: Test the connection**

```bash
ssh -T git@github.com
# Expected: "Hi <username>! You've successfully authenticated..."
```

**Step 4: Configure git to use SSH for GitHub**

```bash
# Rewrite HTTPS GitHub URLs to SSH automatically
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

**Step 5: Configure git identity**

```bash
git config --global user.name "Their Name"
git config --global user.email "their-email@example.com"
```

---

## Method 2: gh CLI Authentication

If `gh` is installed, it handles both API access and git credentials in one step.

### Interactive Browser Login (Desktop)

```bash
gh auth login
# Select: GitHub.com
# Select: HTTPS
# Authenticate via browser
```

### Token-Based Login (Headless / SSH Servers)

```bash
echo "<THEIR_TOKEN>" | gh auth login --with-token

# Set up git credentials through gh
gh auth setup-git
```

### Verify

```bash
gh auth status
```

#### gh is already logged in? Wire git to it instead of minting a PAT

When `gh auth status` is already green with a `repo`-scoped token, the user needs **no
new token**. One command points git's HTTPS credential lookup at gh's token:

```bash
gh auth setup-git
# writes, globally:  credential.https://github.com.helper = !/abs/path/to/gh auth git-credential
git config --get-all 'credential.https://github.com.helper'   # confirm
```

Then `git push` over an `https://github.com/...` remote authenticates silently.
Verify it in the same stripped environment a cron job or service would have — a
helper that only works on an interactive `PATH` fails at 03:00:

```bash
printf 'protocol=https\nhost=github.com\n\n' | \
  env -i HOME="$HOME" PATH="$HOME/.local/bin:/usr/bin:/bin" git credential fill \
  | sed -E 's/^(password=).*/\1<len-check>/'
# expect: username=<account>, password=<40 chars for gho_ tokens>
```

Note the scope: `setup-git` writes to **global** git config, so every `https://github.com`
push from this account uses that token from then on. If the user wants it scoped to one
repo, unset the global key and set the same value with `git config --local`.

---

## Using the GitHub API Without gh

When `gh` is not available, you can still access the full GitHub API using `curl` with a personal access token. This is how the other GitHub skills implement their fallbacks.

### Setting the Token for API Calls

```bash
# Option 1: Export as env var (preferred — keeps it out of commands)
export GITHUB_TOKEN="<token>"

# Then use in curl calls:
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user
```

### Extracting the Token from Git Credentials

If git credentials are already configured (via credential.helper store), the token can be extracted:

```bash
# Read from git credential store
uv run python3 "${HERMES_HOME:-$HOME/.hermes}/skills/github/github-auth/scripts/git-credential-token.py"
```

### Helper: Detect Auth Method

Use this pattern at the start of any GitHub workflow:

```bash
# Try gh first, fall back to git + curl
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  echo "AUTH_METHOD=gh"
elif [ -n "$GITHUB_TOKEN" ]; then
  echo "AUTH_METHOD=curl"
elif _hermes_env="${HERMES_HOME:-$HOME/.hermes}/.env"; [ -f "$_hermes_env" ] && grep -q "^GITHUB_TOKEN=" "$_hermes_env"; then
  export GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "$_hermes_env" | head -1 | cut -d= -f2 | tr -d '\n\r')
  echo "AUTH_METHOD=curl"
elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
  export GITHUB_TOKEN=$(uv run python3 "${HERMES_HOME:-$HOME/.hermes}/skills/github/github-auth/scripts/git-credential-token.py")
  echo "AUTH_METHOD=curl"
else
  echo "AUTH_METHOD=none"
  echo "Need to set up authentication first"
fi
```

---

## Before the first push to a brand-new repo

A `.gitignore` only governs *future* commits. Anything already in the initial commit
stays in history and is published with the first push — adding `git rm --cached` plus a
`.gitignore` afterwards leaves the bytes in the repo and in every clone. Check before
pushing, not after:

```bash
# what will the world actually see, across all history (not just the worktree)?
git log --all --name-only --pretty=format: | sort -u | grep -E '^(\.usage|\.cache|node_modules|\.env)' 
git count-objects -vH | grep size-pack
```

If nothing has been pushed yet (`git ls-remote origin` returns empty / `gh repo view
--json isEmpty` says `true`), rewrite instead of stacking a delete commit on top:

```bash
git checkout --orphan __clean
git add -A
git commit -m "Initial import"
git branch -M __clean main       # force-rename over the old branch
```

Then confirm the ignored paths are gone from history (`git log --all --name-only`
again) and, after the push, from the remote: `gh api repos/<owner>/<repo>/contents/<path>`
should return 404. Say plainly that history was rewritten — a single squashed import
commit is normal for a never-pushed repo, and silently collapsing commits on a repo
someone else already has is not.

### Verify a push landed

```bash
git rev-parse HEAD
git ls-remote origin refs/heads/<branch>        # same sha or it did not land
gh repo view <owner>/<repo> --json isEmpty,defaultBranchRef,pushedAt
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `git push` asks for password | GitHub disabled password auth. Use a personal access token as the password, or switch to SSH |
| `git push` prompts for a password even though `gh auth status` is green | gh's login covers gh only — run `gh auth setup-git` (or set `credential.https://github.com.helper` yourself) |
| `ssh -T git@github.com` → `Permission denied (publickey)` while keys exist | The keys in `~/.ssh` belong to per-repo deploy-key host aliases, not the account. Switch the remote to HTTPS and use the gh helper, or add a key to the account |
| `remote: Permission to X denied` | Token may lack `repo` scope — regenerate with correct scopes |
| `fatal: Authentication failed` | Cached credentials may be stale — run `git credential reject` then re-authenticate |
| `ssh: connect to host github.com port 22: Connection refused` | Try SSH over HTTPS port: add `Host github.com` with `Port 443` and `Hostname ssh.github.com` to `~/.ssh/config` |
| Credentials not persisting | Check `git config --global credential.helper` — must be `store` or `cache` |
| Multiple GitHub accounts | Use SSH with different keys per host alias in `~/.ssh/config`, or per-repo credential URLs |
| `gh: command not found` + no sudo | Use git-only Method 1 above — no installation needed |
