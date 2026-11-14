---
name: starpath
description: "Use when working in the starpath repo: validation, CI, docs."
version: 1.0.0
author: Hermes Agent (curator)
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [starpath, rust, validation, devnet, ci, planning, docs]
    related_skills: [gated-rust-workspace, gated-repo-workflow, private-repo-access]
---

# starpath

Repo `~/repos/starpath` (`silentsea-xyz/starpath`, push via the `github-starpath` SSH deploy key).
Sibling `~/repos/mariner` holds spike code, fixtures, orchestration, CSVs and `FINDINGS.md`; cite
across repos as `mariner:<path>` — a cross-repo file cannot be a relative link.

**Status lives in the repo, never here.** Read `docs/registers/obligations.md`,
`docs/registers/measurements.md`, `docs/results/`, and the root `AGENTS.md` router; do not restate
status in this skill.

Two halves, both below: **validation & environment** (local matrices, the Nitro devnet, the dev-stack
tool, CI triage, paid-validation preparation) and **phase planning & docs** (milestone phases, plan
authorship, spec/ADR/register authoring).

## When to Use

- Any task in `~/repos/starpath`: running the local validation matrices, the Nitro devnet, the
dev-stack tool, or the integration scripts.
- Working a GitHub Actions run: "why is CI red", triaging a failing lane, pricing or suspending a
push trigger.
- Preparing a validation obligation (O-N) to "operationally ready", or answering what is left before
an operator-authorized paid campaign.
- Planning a milestone phase, writing a phase plan, or authoring the docs it needs (a spike plan, an
ADR plus spec amendment, an obligations-register entry, a `docs/results/` record).
- Breaks that only show up locally (readiness stuck at 503, an epoch never accepted, an assertion
that decides a state flip).

Not for: the sibling `mariner` repo on its own (its spike code and CSVs are cited here, but a
mariner-only task is not this skill), or a generic multi-crate Rust build (that is
`gated-rust-workspace`).

## Rules that hold across the repo

`gated-repo-workflow` holds the cross-cutting discipline — verdict first, facts from the tree at HEAD,
word boundaries before claiming absence, commit-locally/push-separately, lettered owner decisions,
scope-wide `search_files` over a recursive `grep`, never weakening a gate. Apply it as written; do not
restate it here. The rules below are what this repo adds to it.

- **Commit before you run; keep the checkout clean.** The measured gates refuse a dirty or untracked
  tree, and `check-doc-links.sh` scans untracked files. A plan, log or scratch note anywhere under
  `~/repos/starpath` counts as dirty: session plans live in `.hermes/plans/`, evidence under a
  directory *outside* the checkout, with a new evidence dir per commit.
- **Gate edits are semantic, never loosened.** Replace delivery identifiers with semantic names
  (ADR-0056) and regenerate frozen fixtures rather than overwrite them; a policy carve-out is the
  owner's call, not a local threshold change.
- **No fabricated completion or passes.** No phase is complete without integrated gate output plus a
  dated record; local success is not obligation closure; an interrupted run is "no passing record",
  never the tail of the log. Report the shortfall inside the deliverable's own numbering.
- **Never invent a constant, a duration basis, or a mechanism.** Constants come from
  `packages/params`; a duration estimate comes from a measured comparable phase, else "unknown".

## Validation & environment (always-on)

- **The exact-capacity scenario must run with `--release`.** `o5_local_matrix` scenario `maximum` is
  Brotli-11 over a `TAPE_MAX_PRINTS` tape; unoptimized it burns >45 min of CPU without finishing,
  with `--release` ~8 min at ~0.7 GiB. The harness forwards one optional cargo arg and uses it only
  for that scenario — keep it that way, or the whole local suite becomes a multi-hour gate. Bounded
  scenarios stay in the default profile.
- **`scripts/run-o5-tape-equivalence-integration.sh` refuses a dirty/untracked tree** and a HEAD that
  disagrees with `--expected-source-commit`, so make the change, commit it, then run with a **new
  `--evidence-dir` per commit** (it creates `<dir>/runs/<timestamp>-<pid>/`).
- **The Nitro devnode needs an explicit Stylus target on CPUs without BMI/LZCNT** — it dies during
  execution-engine init with `cpu flags not supported on local cpu for: +bmi+lzcnt`:
  `--execution.stylus-target.amd64 x86_64-linux-unknown+sse4.2`. `start-devnode.sh` does not pass it,
  so an operator must. Stop and remove the container when done: a running devnode under the default
  name `starpath-nitro` makes `start-devnode.sh` silently reuse the overridden instance instead of
  failing loudly.
- **CI is the acceptance gate — triage it, do not guess.** The repo is private, so run status, logs
  and artifacts come from the GitHub API via an authenticated `gh`; pushes stay on the deploy key.
  - A red pipeline hides a chain of failures (skipped/blocked jobs have never run) — keep iterating
    until the `CI Gate` job is green.
  - A job that dies installing a toolchain (e.g. a release asset answering `HTTP 504`) is
    infrastructure, not your change: confirm the failure sits above the lane's real step, then
    `gh run rerun <run-id> --failed`.
  - A green lane must have exercised its matrix — count the evidence-manifest rows before reporting.
  - A push to `main` is not free (~125 job-minutes, billed per job rounded up to the minute); for a
    change CI cannot validate, cancel the run it starts.
  - Suspending CI is a file edit (comment the pipeline out under a `workflow_dispatch`-only stub),
    never `gh workflow disable` — the disabled state attaches to the workflow id and survives a
    file restore.
  - End a CI report with HEAD, `origin/main`, and whether the tree is clean.
- **`cargo check` is not the gate.** The Rust lane runs `cargo fmt --all -- --check` and
  `cargo clippy --locked --release --workspace --all-targets --all-features -- -D warnings`; any
  warning fails it.
- **A pinned source file is frozen by byte** — a comment-only edit to `packages/params/src/*`
  invalidates the `packages/epoch-corpus` fixtures; the remedy is a new versioned fixture directory
  from the versioned generator, never an in-place edit of the old one.
- **Every lane driving a V5 manifest to `RelationReady` must inject the V2 tape boundary** (the
  worker's default is `UnavailableTapeRelationPort`); adding a required env var to a binary breaks
  every harness that spawns it — update them in the same change.
- **Reproduce locally, but match the lane's profile** — integration scripts schedule epochs against
  anvil's wall clock, so use `STARPATH_INTEGRATION_BUILD_PROFILE=release` (debug trips
  `Timestamp error: ... lower than previous block's timestamp`).
- **A long-lived local stack must be detached from any pty** (`setsid --fork --wait <runner>
  </dev/null` inside tmux) — a pty-attached run takes a kernel `SIGHUP` and exits cleanly, which
  reads exactly like an implementation regression. Never edit the spec or its fixtures while a run is
  in flight; bracket every literal in a cleanup pattern (`pkill -f '[a]nvil --chain[-]id'`); a local
  JSON-RPC endpoint is not reachable through a bare GET (POST `eth_chainId`).
- **Assertion scope: never overclaim.** A local devnet pass is a pass of `run-tests.sh` only — never
  the pinned-configuration measurement; gas/timing figures quoted from CI are not reproduced locally.
- **Paid-validation preparation never performs a paid or public action** (local/devnet only). Staged
  inputs are data, never argv, and never secret-bearing evidence; `ready` means parseable, not wired;
  re-read the obligation in `docs/registers/obligations.md`, its closure plan, and `measurements.md`
  rather than restating status. Read a task manifest with `scripts/manifest_tasks.py`, never by hand.
- **The host runs deployed stacks as `starpath-<stack>-<role>.service`** — one nologin account per role
  (`starpath-api`, `-sequencer`, `-readiness`, `-tee`; there is no `starpath` user, so `ps -u starpath`
  fails), state under `/srv/starpath/<stack>/`, immutable builds under `/opt/starpath/<commit>/`,
  public entry at `caddy.service`. Inventory, port mapping and the two memory figures:
  `references/deployed-stacks.md`. A stack with only `archive`/`*-rpc` units alive is a leftover, not a
  live deployment.
- **Stop, disable and delete are three separate scopes; a stop is not a decommission.**
  `systemctl stop 'starpath*'` leaves every enabled unit to return at boot and leaves `caddy.service`
  running — the public front door is not named `starpath*`, so a full stop must name it explicitly.
  Disabling, `reset-failed`, and container/`/opt`/`/srv` cleanup are separate, asked-for steps. Verify
  closure from outside (no process, no active unit, ports closed, `free -m` delta) — `stop` returning 0
  is not evidence. Procedure: `references/deployed-stacks.md`.

## Phase planning & docs (always-on)

- **The phase overview is the authority; a phase plan is a proposal.**
  `docs/submissions/<window>/<milestone>-plan.md` owns scope, sequencing, checks and schedule
  decisions. Quote its phase section; never widen scope because something looks cheap.
- **Recon order before writing anything:** the phase section → the previous phase's result record in
  `docs/results/` → the runbook's "Known gaps and owners" table (carryover debt) → the governing
  spec/acceptance-map entry. Then verify each claim against the tree — a gap table is a snapshot and
  the tree moves under it.
- **Cost claims must be measured, and the mechanism checked.** Never carry a measured figure to a
  situation it does not describe; say "unknown" rather than reason from a number taken elsewhere.
- **A phase plan cannot amend a protocol rule, constant, wire format or gate.** New behaviour is
  resolved in the governing spec first; a plan that appears to need a spec change stops and raises it,
  or changes the gate in its own "Decisions" section in the strict direction with the fallback.
- **Grep for consumers before replacing an exported helper** (a fixture helper is typically imported
  by an operator tool, a `node --test` lane, and a runbook); update every consumer in the same task,
  or the tool breaks while its unit test still passes.
- **Provenance dies on a squash; the tree hash is the durable handle.** Before calling a candidate
  "the qualified one", match the record's recorded tree to a reachable commit and pin the reachable
  SHA; report unreachable anchors as evidence-integrity debt.
- **Plan shape:** Goal · Current context/assumptions · Architecture · **Decisions fixed by this plan**
  (each naming the alternative it rejects) · Layout/provenance · Scope and non-goals (including the
  next phase's work) · Tasks (objective · exact paths · numbered steps with the exact command *and its
  expected output* · full TDD cycle · copy-pasteable code) · Tests/validation summary ·
  Risks/tradeoffs/open questions · exit-gate mapping · handoff. Flag `[LONG]` tasks for detached
  start; state what the phase does NOT establish.
- **Branch before reading** (`git fetch origin && git pull --ff-only`, then
  `git checkout -b abdulla/<topic-slug>`); execute task-by-task, committing locally per task
  (`type(area): what changed`); close with a dated `docs/results/` record plus the README index row, a
  result/re-estimate section appended to the milestone overview, and the runbook updated.
- **"What do we do next?" turns:** name the plan family you read (two share the word "server" — see
  `references/server-side-plan-families.md`); a handoff's state is in its appended paragraphs, not its
  checkboxes; split remaining items into operator-gated and local.
- **Doc authoring:** plans/specs/ADRs/registers live in starpath, spike code in mariner; authority is
  set by the status header; a plan is Informative and names what it does not amend; every number is
  cited to the file that owns it. Run the four doc gates before committing, **unpiped**
  (`check-doc-links.sh`, `check-roadmap-reference-policy.sh`, `check-acceptance-map.sh`,
  `check-no-inline-constants.sh`) — some can be red at HEAD on files you did not touch, so run all
  four and fix only your own findings. `AGENTS.md` is write-protected (an edit needs explicit user
  approval).

## Where the depth lives

- `references/ci-triage.md` — `gh` setup, reading runs, per-trigger minute audit, suspending/restoring CI, gap analysis over a finished job log.
- `references/gates-and-fixtures.md` — the four doc gates, frozen-fixture regeneration, pinned prerequisites, the SDK placement topology runner, advancing a local epoch by hand.
- `references/dev-stack.md` — `run-development-topology.mjs` subcommands, the artifact-input staleness guard, retained-prebuilt staging, the sub-100 ms acceptance race.
- `references/deployed-stacks.md` — the systemd stacks deployed on this host: unit→stack→port map, per-role accounts, RSS vs cgroup accounting, failed/leftover stacks, the Caddy front door.
- `references/local-topology-failure-triage.md` — readiness/topology failure triage, loopback capture, signal attribution, the no-retry assertion.
- `references/browser-app-runtime.md` — `services/web` SDK composition, config routes, identity verification, repo mechanics that bite.
- `references/paid-validation-preparation.md` — obligation recon and the preparation pitfalls.
- `references/tape-publication-readiness.md` — the O-5 live-arm inputs, Celestia/Blobstream requirements, drill boundaries.
- `references/phase-planning.md` — explaining a phase on request, the full plan procedure, planning pitfalls.
- `references/docs-authoring.md` — where artefacts belong, the doc gates, the four authoring procedures (spike plan, spec change, obligations register, delivery-identifier policy).
- `references/server-side-plan-families.md` — the two "server" plan families and where their state lives.
- `references/peer-fork-comparison.md` — diffing a peer's fork of a vendored dependency.
- `references/repo-conventions.md` — local commands, Node-side tooling against the browser fixtures, documenting results.
- `scripts/manifest_tasks.py` — summarize a server-validation manifest without paging the raw JSON.
- `templates/spike-plan.md` — the spike/research plan skeleton.
