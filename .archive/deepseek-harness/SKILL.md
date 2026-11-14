---
name: deepseek-harness
description: "Install, run and supervise DeepSeek Harness profiles."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [DSH, DeepSeek Harness, Bundles, Profiles, Systemd, Agents]
    related_skills: [github, hermes-agent, coding-agent-session-inspection]
---

# DeepSeek Harness (dsh): profiles, bundles, supervision

`dsh` is a launcher, not an agent. Every agent behaviour lives in a **profile**: a directory of
plugins composed from ordered patch layers. Installing a product "into DSH" means creating a profile
and adding that product's bundle to it. Everything below follows from that.

## When to use

- Installing, upgrading or running a DSH plugin bundle (dsh-superagent and similar)
- Running a bundle from a local checkout or fork rather than a package
- Keeping a DSH-based agent alive across reboots
- Reading a DSH profile's composed configuration before changing anything

Not for: reading or nudging a session that is already running — locating the process, reading the
agent's own state store and classifying working/parked/wedged is `coding-agent-session-inspection`.

## Entry points

| Command | Does |
| --- | --- |
| `dsh <name>` / `dsh --profile <name>` | Boot that profile from `$DSH_HOME/profiles/<name>` |
| `dsh --profile <name> --from-default-profile <template>` | Replace the profile with a fresh copy of a shipped template, then boot it. **Destructive** |
| `dsh plugin --profile <name> add <pnpm spec>` | Forward to pnpm inside the profile dir (install/remove plugins) |
| `dsh --profile headless "job"` | One fresh persisted session, print the answer, exit |
| `dsh web` | Boot the shipped Web profile |
| `dsh --profile <name> --no-open` | Boot without opening a browser; what service scripts use |
| `--dump-config`, `--dump-default-config`, `--dump-config-schema` | Inspect the composed tree without booting |

Shipped profiles auto-initialize on first use: `web`, `headless`, `sdk`, `sdk-minimal`, `acp`.
Any other name (`superagent`, `work`, ...) must be created once with `--from-default-profile <template>`.
The launcher parses only its own flags; the first token it does not recognize starts the app's
arguments (`dsh --profile web --port 8080`).

## Layout and layer order

```
$DSH_HOME/                     # default ~/.dsh; relocate with DSH_HOME
  profiles/<name>/
    package.json               # deps + dsh.profile.bundles (ordered)
    cordis.patch.yml           # the user's own patch layer
  cordis.patch.yml             # home-level patch
```

Composition order: bundles in `dsh.profile.bundles` order → profile `cordis.patch.yml` → home
`cordis.patch.yml` → `--patch` overlays. A bundle row can be `disabled: true`; that is how optional
Sources are shipped.

Version gates are enforced at startup: a plugin's `engines.dsh` (or its DSH peer ranges) must match
the running CLI, otherwise boot/install fails and demands an explicit version exemption. Check
before blaming the bundle.

## Running a bundle from a local checkout or fork

This is the normal path for any bundle whose `package.json` is `private: true` — there is no npm
package to install, so a `link:` is the only way.

1. `pnpm install && pnpm build` in the checkout. `main`/`exports` point at `lib/`, so the **compiled
   output is what runs**; editing `src/` alone changes nothing.
2. `dsh plugin --profile <name> add "link:$PWD"` with an absolute path. Use `link:`, not `file:`,
   so the profile resolves the live checkout instead of a snapshot copy.
3. Copy the bundle's example profile patch over `~/.dsh/profiles/<name>/cordis.patch.yml` and
   replace every placeholder. Most bundles require an absolute `stateDir` and refuse to start
   without it; the webserver row sets host/port (keep `127.0.0.1`).
4. Start with `dsh --profile <name> --no-open`, then open the panel on the configured port.
5. Development loop: edit → `pnpm build && <restart>` as one command. Never build while the service
   is running: a partially written `lib/` can be loaded mid-boot.
6. Files the package reads at runtime rather than compiling — `prompts/*.md`, `skills/*/SKILL.md`,
   `locale/*.json` — take effect on restart without a rebuild. Use that for prompt/behaviour work.

Pitfalls:

- `--from-default-profile` deletes the profile's `cordis.patch.yml`. On an existing installation,
  edit the patch file; do not run the creation command again.
- The bundle's `engines.dsh` pin is a tested version, not a floor. A newer `dsh` may satisfy semver
  but is untested by that bundle — pin the documented version for first boot and upgrade deliberately.
- `dsh plugin` forwards to pnpm inside the profile directory, so the profile's `packageManager` pin
  and your global pnpm can differ; let corepack resolve it instead of forcing your version.
- `private: true` also means no upgrade path via npm. Upgrades are `git pull` + rebuild + restart.
- State is one-way: a bundle that changes its schema version writes a database an older build cannot
  open. Back up `stateDir` before upgrading or changing schema code.

## Keeping it running across reboots

Use a **systemd user unit**; `nohup`/tmux sessions die at reboot and hide failures. Linger must be
on (`loginctl show-user $USER | grep Linger`; `loginctl enable-linger $USER` if not) so the unit
starts without a login session.

`~/.config/systemd/user/<bundle>.service`:

```ini
[Unit]
Description=dsh <profile>
After=network-online.target

[Service]
Type=simple
WorkingDirectory=/abs/path/to/checkout
ExecStart=/abs/path/to/dsh --profile <profile> --no-open
Restart=always
RestartSec=5
KillSignal=SIGINT
TimeoutStopSec=300

[Install]
WantedBy=default.target
```

`SIGINT` + a long `TimeoutStopSec` because agent bundles finish in-flight work on SIGINT: an
Executor turn can run for minutes and cutting it off loses work. Check the bundle's own stop
handler before choosing a signal.

- If the bundle ships a control script (`scripts/<name> start|stop|status`) that launches tmux, let
  systemd own the process and use the script only for `status`/health. Its `stop` would kill the
  process that `Restart=always` immediately brings back.
- Enable and verify: `systemctl --user daemon-reload && systemctl --user enable --now <unit>`, then
  `systemctl --user status <unit>` and a reboot test.
- Panels bind loopback by default. Reach them from another machine with
  `ssh -L <port>:127.0.0.1:<port> <host>`; do not widen the bind to publish an agent's UI.

## Before you characterize or deploy a bundle

- Read the manifest first, not the README prose: `name`, `private`, `engines`, `peerDependencies`,
  the `exports` map (each entry may be a separate plugin), and the `dsh` block (bundle patch path,
  client platform, manifest version).
- Verify provenance from the API, not the README: `gh repo view <owner>/<repo> --json
  isFork,parent,visibility,pushedAt,stargazerCount`. A repo can describe itself as an unofficial
  prototype while being published under the vendor's own org as a fork of a single upstream commit
  — both facts matter when deciding whether to track upstream.
- Numbered `docs/` read in order are usually the real spec; test files enforce parts of it (class
  JSDoc coverage, architecture tables listing every module, model-facing surface size budgets).
  `pnpm check` is the honest gate before trusting a fork.

## Safety gate (do this before starting one)

Proactive coding agents run shell commands **as the operator's OS user with no sandbox**. The blast
radius is the credential set, not the watched repository. Before installing: enumerate what the
process can read (`~/.ssh`, agent configs, tokens, private repos), which account/CLI it acts as and
what scope that token carries, and whether a dedicated OS user is warranted. State this plainly to
the operator before the first start rather than after.

**A plan and a set of setup questions are not approval.** Collecting answers (repository, agent
account, model provider, isolation) is reconnaissance; do not create profiles, services or account
wrappers until the operator explicitly says go. When they push back ("wait", "not yet"), stop
cleanly, state what — if anything — was changed on the machine, and leave it alone until asked again.

## Reference

- `references/dsh-superagent.md` — the dsh-superagent bundle: domain model, authorization, execution
  and the customization traps (schema version, documentation tests, Source plugins).
