---
name: private-repo-access
description: "Use when giving an agent/CI access to a private git repo."
version: 1.0.1
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, ssh, deploy-key, github, gitlab, bitbucket, authentication, access-control]
    related_skills: [github-auth, github-repo-management]
---

# Private Repo Access for Agents

Give an agent (or CI process) access to a private git repository, choosing the
least-privilege method and scoping credentials so they never interfere with the
user's other git connections.

## When This Skill Activates

- User asks "how do I give you access to a private repo?" or similar
- User wants an agent/CI to clone, read, or push to a private repository
- A new repo needs agent access alongside the user's existing git setup

## Decision Tree — Pick the Method First

1. **Repo already cloned on the box → no network auth needed.** The agent can
   work on the checkout directly; it never needs the credential. Often the
   cleanest option for a single private repo on the same machine. (Still worth
   setting up a deploy key if the agent will push to a remote.)
2. **Single repo, agent access → SSH deploy key (default recommendation).**
   Scoped to ONE repo, independently revocable, read-only or read-write. Least
   privilege for agent access. This is the method documented below.
3. **Multiple repos / org-wide / API access → fine-grained PAT.** E.g. GitHub
   fine-grained token scoped to select repos with Contents read/write. Bigger
   hammer than a deploy key; only when a deploy key can't cover the need.
4. **Full user-level access → account SSH key or gh CLI.** Only if the agent
   should act as the user across everything. Not appropriate for a scoped agent.

## Method: Per-Repo SSH Deploy Key (Recommended)

Use a DEDICATED keypair per repo — never reuse the user's account key, and
don't share one deploy key across repos (GitHub forbids attaching a deploy key
to more than one repo).

**Step 0 — Repo must exist (decide who creates it):**
- Check the repo exists: `curl -s -o /dev/null -w "%{http_code}" https://github.com/<owner>/<repo>`.
  **A 404 is AMBIGUOUS**: an unauthenticated curl returns 404 both for a
  nonexistent repo AND for a private repo you can't read. Never conclude "the
  repo doesn't exist" from a bare 404 when the repo is expected to be private —
  if the user handed you the URL, assume it exists and let the `ssh -T`
  verification step be the source of truth. (200 only tells you the repo is
  public.)
- Check whether the AGENT can create it: `gh auth status`, or a `GITHUB_TOKEN`
  in `${HERMES_HOME:-~/.hermes}/.env` / `~/.git-credentials`. If none of those
  exist, the USER creates the repo in the browser — tell them to leave it EMPTY
  (no auto-init README/.gitignore) so the agent's initial push is clean.
- **Generate the keypair FIRST** so the public key is ready the moment the repo
  exists — the user can paste it in the same browser session instead of waiting
  on a round-trip.

**Step 1 — Generate a dedicated keypair:**

```bash
ssh-keygen -t ed25519 -C "agent-<machine>-deploy" -f ~/.ssh/<repo_name>_deploy -N ""
cat ~/.ssh/<repo_name>_deploy.pub   # copy this
```

**Step 2 — User adds it as a DEPLOY key (not an account key):**
- GitHub: repo → Settings → Deploy keys → "Add deploy key". Check "Allow write access" ONLY if the agent must push.
- GitLab: repo → Settings → Repository → Deploy keys
- Bitbucket: repo → Repository settings → SSH keys → Deploy keys

**Step 3 — Verify the key before wiring anything:**

```bash
ssh -i ~/.ssh/<repo_name>_deploy -o IdentitiesOnly=yes -T git@github.com
```

- Success for a deploy key prints `Hi <owner>/<repo>! You've successfully
  authenticated...` — the REPO name in the greeting (not a username) is how you
  know it's a deploy key. Exit code 1 is normal (GitHub denies shell access).
- Failure prints `Permission denied (publickey)` — key not added yet, or added
  as an account key instead of a deploy key.

**Step 4 — Scope with a host alias in `~/.ssh/config` (critical if other keys exist):**

A plain global `Host github.com` + `IdentityFile` override would shadow the
user's other GitHub keys. Instead, give the repo its own alias:

```
Host github-<repo-alias>
    HostName github.com
    User git
    IdentityFile ~/.ssh/<repo_name>_deploy
    IdentitiesOnly yes
```

Clone via the alias so the remote is permanently scoped:

```bash
git clone git@github-<repo-alias>:<owner>/<repo>.git
```

**Step 5 — Check git identity before promising commits:**

```bash
git config --global user.name
git config --global user.email
```

If unset, ask the user what name/email to put on commits (or offer a generic
agent identity) BEFORE the first push — otherwise the first commit fails or
commits under the wrong identity.

## Pitfalls

- **Don't paste the public key into account SSH keys settings** when the goal
  is repo-scoped access — that grants user-level access. Deploy keys live under
  the REPO's settings.
- **Don't reuse one deploy key across repos** — GitHub rejects it (key already
  in use). Generate a fresh keypair per repo.
- **Don't put a bare `Host github.com` IdentityFile entry** for the deploy key
  — it hijacks all GitHub connections from that box. Always use a unique host
  alias + `IdentitiesOnly yes`.
- **GitHub's `ssh -T` greeting for a deploy key shows `Hi owner/repo!`** —
  don't mistake that for a username or an error. Exit code 1 with that message
  means auth succeeded.
- **Write access is a checkbox decision** — default to read-only; only enable
  write when the agent must push/PR.
- **Verify before wiring** — test the key with `ssh -T` before cloning; a
  "Permission denied" during clone is harder to attribute.
- **`ssh -T` proves ACCESS, not WRITE access.** A deploy key with the write box
  unchecked authenticates identically. There is no read-only probe: the only
  way to confirm write is an actual push (e.g. a throwaway branch you then
  delete). Don't claim "write access verified" off a successful `ssh -T` — track
  the read/write decision from what the user checked in the repo settings, and
  offer a temp-branch push test if write matters.
- **If the user pastes keys for several repos in one session, re-test each
  alias afterwards** — they will likely add them at different times, so expect a
  partial state (one `Hi owner/repo!`, one `Permission denied`) and just proceed
  with the live one instead of treating the batch as all-or-nothing.
- **Don't put key paths / host aliases into persistent memory.** The Hermes
  memory tool's threat guard rejects entries containing SSH key paths, host
  aliases with `IdentityFile`, or dotfile/env references (observed: blocked
  with `threat pattern 'ssh_access'` / `'hermes_env'`). Keep credentials and
  paths in `~/.ssh/config` and this skill's setup — memory should only record
  the repo name, local path, and that access is configured.
- **First connection may need `StrictHostKeyChecking=accept-new`** on a fresh
  box — otherwise the initial `ssh -T` prompts interactively and hangs a
  scripted run. Pass it once on the verification step; known_hosts then covers
  future connects.
