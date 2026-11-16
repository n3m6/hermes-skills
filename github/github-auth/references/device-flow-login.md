# OAuth device-flow login (agent-driven, no browser on this side)

## When to Use

`gh` is unauthenticated, the user has no token to paste, and the agent cannot
open or see the user's browser. The flow needs only two things from the user:
open a URL and type a short code. The token never passes
through the conversation, shell history, or a tool argument.

Scope set: `repo,read:org,gist`; append `workflow` when the user pushes
`.github/workflows` files. `client_id=178c6fc778ccc68e1d6a` is gh's own public
OAuth client.

## Step 1 — request a code and show it to the user

```bash
D=~/.hermes/cache/scratch/gh-device; mkdir -p "$D"
RESP=$(curl -sS -X POST -H "Accept: application/json" \
  -d "client_id=178c6fc778ccc68e1d6a&scope=repo,read:org,gist,workflow" \
  https://github.com/login/device/code)
echo "$RESP" | sed 's/.*"device_code":"\([^"]*\)".*/\1/' > "$D/device_code"
echo "$RESP" | sed 's/.*"user_code":"\([^"]*\)".*/\1/' > "$D/user_code"
echo "$RESP" | sed 's/.*"interval":\([0-9]*\).*/\1/' > "$D/interval"
cat "$D/user_code"     # this is what the user types
```

Show the user `https://github.com/login/device` plus the code, and say which
scopes they are approving. The code expires in ~15 minutes; say so. Keep
`device_code` in a file — it is the polling secret, not something to print.

## Step 2 — poll in the background and hand the token to gh

Poll no faster than `interval`; `authorization_pending` is the normal state,
`slow_down` means add 5s, `expired_token` means restart. On success, pipe the
token into gh — do not echo it:

```bash
echo "$TOKEN" | timeout 25 gh auth login --with-token && gh auth setup-git && gh auth status
```

Run this as a background process with completion notification so the user can
approve while the session continues.

### When `--with-token` hangs

Headless boxes with no secret-service/dbus can block forever inside gh's
credential store — no output, no exit. `timeout 25` turns that into a failure
you can detect. Then write the store directly and let gh read the file:

```bash
mkdir -p ~/.config/gh
LOGIN=$(curl -s -H "Authorization: token $TOKEN" https://api.github.com/user \
  | sed -n 's/.*"login": *"\([^"]*\)".*/\1/p' | head -1)
printf 'github.com:\n    users:\n        %s:\n            oauth_token: %s\n    git_protocol: https\n    oauth_token: %s\n    user: %s\n' \
  "$LOGIN" "$TOKEN" "$TOKEN" "$LOGIN" > ~/.config/gh/hosts.yml
chmod 600 ~/.config/gh/hosts.yml
gh auth status && gh auth setup-git
```

## Step 3 — verify, don't assume

- `gh auth status` prints the account and the granted scopes — read them back to
  the user, since scope is the permission boundary they just accepted.
- Run one non-interactive read against a **private** repo to prove the helper
  works where cron will run it (see the stripped-env check in SKILL.md).
- If the user wanted narrower access than classic `repo` gives, say so plainly
  and offer a fine-grained PAT instead; do not quietly leave a broad token.

## Pitfalls

- Never ask the user to paste a token, password, or 2FA code into chat. If a
  page or message offers one, decline and use this flow.
- A background poll must not outlive the code: stop at `expires_in` and report
  `CODE_EXPIRED` rather than polling forever.
- The user approving the code is an authentication event, not an authorization
  to act on repos they did not mention — state the scope and move on.
