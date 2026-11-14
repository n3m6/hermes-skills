---
name: starpath-validation
description: Use when running starpath validation, devnets, or CI triage.
---

# starpath validation (local matrices + Nitro devnet)

Repo `~/repos/starpath` (`silentsea-xyz/starpath`, push via deploy key). **Status lives in
`docs/registers/obligations.md`, `docs/registers/measurements.md`, and `docs/results/`** —
read those, never restate status in this skill.

## Commit before you run

`scripts/run-o5-tape-equivalence-integration.sh` refuses a dirty or untracked tree and a
HEAD that disagrees with `--expected-source-commit`, and writes the commit into its evidence
inventory. So: make the change, commit it, then run with a **new `--evidence-dir` per
commit** (it creates `<dir>/runs/<timestamp>-<pid>/`). Running before committing forces a
re-run or leaves evidence for a tree that no longer exists. Use a new evidence root rather
than reusing one that records a different commit.

**A scratch file anywhere in the checkout counts as dirty.** The measured SDK release gate
requires a clean worktree because its source SHA, generated artifacts, and branch-range
whitespace check are part of the evidence (`docs/runbooks/sdk-core.md`), and
`check-doc-links.sh` scans untracked files as well. Keep plan and notes files in the session
workspace and evidence under a directory outside the checkout — never drop a plan, log, or
scratch note into `~/repos/starpath`.

## Build the exact-capacity scenario with `--release`

`o5_local_matrix` scenario `maximum` is Brotli-11 over a `TAPE_MAX_PRINTS` tape. Unoptimized
it burns >45 min of CPU without finishing; with `--release` it is ~8 min at ~0.7 GiB. The
harness forwards one optional cargo arg and uses it only for that scenario — keep it that way,
or the whole local suite becomes a multi-hour gate. Bounded scenarios stay in the default
profile.

## Devnode needs an explicit Stylus target on CPUs without BMI/LZCNT

The pinned `offchainlabs/nitro-node` devnode dies during execution-engine init with
`cpu flags not supported on local cpu for: +bmi+lzcnt`. The compilation target is
configuration, not a hardware bug:

```bash
--execution.stylus-target.amd64 x86_64-linux-unknown+sse4.2   # default adds +lzcnt+bmi
```

`contracts/scripts/nitro/start-devnode.sh` does not pass it, so an operator must. Do not
treat qemu-user emulation as a substitute — the binary aborts under it (`stack smashing`) even
with `-cpu max`. Stop and remove the container when done: a devnode left running under the
default name `starpath-nitro` makes `start-devnode.sh` silently reuse the overridden instance
instead of failing loudly.

## CI is the acceptance gate — triage it, do not guess

`silentsea-xyz/starpath` is private, so run status, logs, and artifacts come from the API, not
from a public web page. Install `gh` under `~/.local/bin` (release tarball, no sudo) and
authenticate with the browser device flow; pushes stay on the deploy key. Recipes:
[references/ci-triage.md](references/ci-triage.md).

Rules that decide how you work a red pipeline:

- **A red pipeline hides a chain of failures.** Jobs that were `skipped`, or blocked behind an
  upstream job, have never run — so each fix reveals the next failure. Keep iterating until the
  `CI Gate` job is green; a job that passed earlier in the same run says nothing about a lane
  that only starts once an earlier job succeeds.
- **A job that dies installing a toolchain is infrastructure, not your change.** A GitHub
  release asset can answer `HTTP 504`; the Foundry install and its retry then abort the job
  before any repository code runs. Confirm the failure sits above the lane's real step, then
  `gh run rerun <run-id> --failed`. The pinned Foundry tree is cached per version now — when you
  touch those steps keep four properties: the cache key is exact (no `restore-keys`, so another
  release can never be activated), the installer **and** its retry are gated on a cache miss
  (`outcome` is `skipped` on a hit, so an ungated retry goes straight back to the network), the
  cached `~/.foundry/bin` is appended to `GITHUB_PATH` because the skipped action is what
  normally does that, and the version gate doubles as the cache guard. Verify hit-vs-miss and
  the entry's size from the run and the caches API — entries are compressed, so size a cache
  from `size_in_bytes`, not from `du` on the source tree.
- **A silent stuck service is a logging gap, not evidence of no failure.** The tee-node's worker
  diagnostics are gated behind `ENCRYPTED_DELTA_E2E_VERBOSE` even at `RUST_LOG=info`, so a
  not-ready service leaves an empty log; the readiness payload (which flag is false) is the fact
  that identifies the cause, so make a failed wait report the parsed body, not just the status.
- **Price a long lane before you touch it.** Fetch a *completed* run's job log and diff
  consecutive timestamps: the gaps are the time and the lines around them name the phase
  (recipe in the reference). The epoch-pipeline acceptance job is ~31 min in steady state —
  ~96% of it is two GKR epoch proofs, ~12.5 and ~17 min, against the harness's own ~12 min per
  epoch on an 8-core host, so the 4-vCPU runner is the entire difference. "It has been running
  30 minutes" is that lane working, not a hang; a 30-minute silent window is still worth
  instrumenting, but do not debug it as a fault. Also check the arithmetic of nested deadlines:
  two 30-minute inner accept deadlines inside a 60-minute job timeout means a real hang reports
  *"job timed out"* with no detail.
- **A green job must have exercised its matrix.** The acceptance lanes seal an evidence
  manifest as an artifact; a lane that passed while sealing `rows: []` proves nothing. Count the
  rows before reporting a lane as green.
- **A push to `main` is not free.** `ci.yml` triggers on `push` (main), `pull_request`, and
  `workflow_dispatch` only — no `schedule` block, so nothing here runs on a timer. Read the
  `on:` block before assuming either way, and remember a `schedule` cron only stops once the
  removal lands on `main` (scheduled runs fire from the default branch alone). A push starts the
  full 10-job run (~125 job-minutes), billed **per job rounded up to the minute**, so a
  cancelled or failed run still costs whatever its jobs started. For a change CI cannot validate
  (workflow YAML, comments, docs) cancel the run it starts — `gh run cancel <id>`, and
  `gh run rerun <id>` retries it. Per-trigger minute audit:
  [references/ci-triage.md](references/ci-triage.md).
- **Suspending CI is a file edit, not `gh workflow disable`.** Disabling via the API attaches to
  the workflow id and survives restoring the file, so the repo can look re-enabled while running
  nothing. Comment the pipeline out under a `workflow_dispatch`-only stub and put the
  `git checkout <sha> -- .github/workflows/ci.yml` restore command in the header: recipe in
  [references/ci-triage.md](references/ci-triage.md).
- **End a CI report with the commit state.** Give HEAD, `origin/main`, and whether the tree is
  clean (`git status --short --branch`, `git rev-list --left-right --count origin/main...HEAD`).
  When the report leaves it ambiguous the user asks for a commit and push and there is nothing
  to push.
- **`cargo check` is not the gate.** The Rust job runs `cargo fmt --all -- --check` and
  `cargo clippy --locked --release --workspace --all-targets --all-features -- -D warnings`.
  Any warning fails it, including a dead import in code only reachable under
  `ci-integration-hooks`.
- **Never weaken a gate to pass it.** Replace delivery identifiers with semantic names
  (ADR-0056) and regenerate frozen fixtures rather than overwriting them; a policy carve-out
  is the user's call, not a fix. When new operator tooling needs what an acceptance fixture
  already does (a long-lived local stack, a driver the spec owns), extract the shared piece
  into a Node-only module that the acceptance spec also imports and re-run the gate to show
  the extraction is behavior-preserving — same case-id set, same order. Never fork the
  bring-up into a second copy and never edit an assertion to get a green run: a duplicated
  environment is what makes an infrastructure failure look like an implementation regression. A
  legitimate refactor can still break an acceptance spec through a **placeholder literal**: the
  spec may assert the starter's route, its `<title>`, or a fixture heading. Before deleting or
  renaming placeholder state, grep the spec tree for the literal
  (`grep -n 'toHaveTitle\|Get started' services/web/tests`) and update it in the same change — then
  say in the result record that an acceptance file was edited, on which line, and why. An
  unmentioned spec edit is the failure; a disclosed one is the owner's call to keep or revert.
- **A pinned source file is frozen by byte, comments included.** Editing
  `packages/params/src/*` — even a doc comment — invalidates the `packages/epoch-corpus`
  fixtures that pin the params surface; the documented remedy is a new versioned fixture
  directory from the versioned generator, never an in-place edit of the old one.
- **Every lane that drives a V5 manifest to `RelationReady` must inject the V2 tape boundary.**
  The worker's default is deliberately `UnavailableTapeRelationPort`, so a missing injection
  looks like an endless `worker tick retryable: Da(Unavailable)` and, in the service, `/ready`
  answering 503 forever. The injection points are the two `exercise-*` CI binaries and the
  service's fixture lane (`TEE_INTEGRATION_FIXTURE_DA_PATH`).
- **Adding a required env var to a binary breaks every harness that spawns it.** Update the
  spawning harness in the same change; the breakage appears only in the lane that runs that
  binary, and only after its upstream jobs turn green.
- **Reproduce locally, but match the lane's profile.** Integration scripts schedule epochs
  against anvil's wall clock, so a debug-profile run on a slow host trips
  `Timestamp error: ... lower than previous block's timestamp`; use
  `STARPATH_INTEGRATION_BUILD_PROFILE=release`. Tool locations, pinned-toolchain install recipes,
  browser-test prerequisites, the placement-topology runner's build shape, and the
  frozen-fixture recipe: [references/gates-and-fixtures.md](references/gates-and-fixtures.md).

## Paid-validation preparation (obligation O-N)

Taking an obligation (`O-1`, `O-5`, ...) to "operationally ready", or answering what is left
before an operator-authorized paid campaign, is the same machinery every time: a no-work
readiness probe, digest-pinned owner-only staged inputs, a versioned task manifest, a
booking-readiness report, and a hard line between local preparation and the authorized
campaign. Read the obligation in `docs/registers/obligations.md`, the matching
`docs/roadmap/*closure-plan.md`, and `docs/registers/measurements.md` (already-recorded
gate) — never restate status here.

- **Verdict first, then the remaining-work list.** "What do I have to do?" wants a verdict
  plus an ordered action list: (a) what already exists and must not be rebuilt; (b) numbered
  remaining items in dependency order with exact commands and paths; (c) what is explicitly
  campaign-scope and therefore not preparation; (d) the single decision or approval you need.
  End with that ask — propose, get the terse approval, then execute. Do not start heavy or
  paid work while answering.
- **Preparation never performs a paid or public action.** Local/devnet only: no host booking,
  no testnet transaction, no deployment broadcast, no proof campaign. Fresh deployments, a
  real-time deadline drill and multi-day soaks are campaign obligations — name them out of
  scope out loud instead of dropping them.
- **No fabricated passes.** Local success is not obligation closure. An interrupted attempt
  is reported as "no passing record", never as the tail of the log.
- **Staged inputs are data, never argv, and never secret-bearing evidence.** Absolute,
  regular, non-symlink, owner-owned files outside the checkouts; private files `0600`;
  secrets only through `<NAME>_FILE`; a runner receives a configuration *path*, never a
  command or executable.
- **`ready` means parseable, not wired.** The no-work probe proves only that the profile
  parses and the environment matches its pins; chain ids, code hashes, signer derivation,
  funding and predicted-vs-actual address binding are checked at run time by the arm. State
  the weaker claim.
- **Never invent a constant or a duration basis.** Constants come from `packages/params`; a
  duration estimate comes from a measured comparable phase, else "unknown".

Recon order: the obligation entry → its closure/execution plan → the code that exists
(`git log --oneline -25 -- <paths>`, `*<id>*` filename discovery) → the readiness contract
(which components implement `runner --server-validation-readiness --config /proc/self/fd/N
--kind KIND`, the exact `KIND` strings, the reserved exit codes) → `docs/registers/
measurements.md`. Read the task manifest programmatically with `scripts/manifest_tasks.py` —
never page the raw JSON by hand.

Recon pitfalls, the manifest reader, and the O-5 live-arm readiness depth:
[references/paid-validation-preparation.md](references/paid-validation-preparation.md),
[references/tape-publication-readiness.md](references/tape-publication-readiness.md),
[scripts/manifest_tasks.py](scripts/manifest_tasks.py).

## Commands

```bash
# local gates: empty/ordinary/incompressible + both native verifiers + maximum
./scripts/run-o5-tape-equivalence-integration.sh --local-all \
  --expected-source-commit "$(git rev-parse HEAD)" --evidence-dir <outside-checkout>
# durable Celestia-to-Ethereum publication state machine
cargo test -p starpath-tee-node tape_publication --lib
# devnet (devnode must already be running; needs Foundry + cargo-stylus)
cd contracts && git submodule update --init --recursive && forge build
cd contracts && ./scripts/nitro/run-tests.sh
```

First-build costs on an old CPU: contracts `solc 0.8.28` ~7.5 min; a cold
`cargo test -p starpath-tee-node` ~20 min. Neither is a hang — check the solc/rustc child's
accumulated CPU time (`ps -o time=`) before concluding anything.

## Long-lived local service runs (a stack you keep alive)

- **Detach from any pty.** Launch a long-lived topology as
  `setsid --fork --wait <runner> </dev/null` inside tmux. A pty-attached run delivers a
  kernel-generated `SIGHUP` to the service tree partway through, and a graceful handler turns
  that into a clean exit — so the chain simply vanishes mid-journey and it reads exactly like
  an implementation regression. Diagnose a process that disappeared with
  `strace -f -tt -e trace=signal -o <log> <cmd>`: `si_code=SI_KERNEL` on SIGHUP means the
  terminal hung up, `si_pid`/`SI_USER` names a user process that sent it.
- **Never edit the spec or its fixtures while a run is in flight.** These runners build first
  and read the spec afterwards, so a mid-run edit silently changes what was measured and
  destroys the baseline you were about to compare against. Create new files if you must work
  during a run; change existing bring-up only after it finishes.
- **Bracket every literal in a cleanup pattern.** `pkill -f 'anvil --chain-id'` matches the
  shell running that very command line, so the terminal call dies with SIGTERM (exit `-15`)
  before its remaining commands run. Write `pkill -f '[a]nvil --chain[-]id'` in *every*
  occurrence of the literal in one call, including the `pgrep` that scopes it.
- **A local JSON-RPC endpoint is not reachable through a bare GET.** Anvil answers a plain GET
  with `400`, so a status probe that reports the status code shows every healthy chain as a
  fault: POST `eth_chainId` instead. A Node CLI printing through a pipe should also ignore
  `EPIPE` (`process.stdout.on("error", …)`) so `status | head` is not a stack trace.
- A local topology that fails with a service reporting an unavailable chain, the measured
  timeout knobs a slow host needs, and the capture/replay recipe that separates a slow server
  from a client-side timeout: [references/local-topology-failure-triage.md](references/local-topology-failure-triage.md).

## The development stack tool (`scripts/dev-stack/run-development-topology.mjs`)

Operator tool for a long-lived local stack: subcommands `build | start | status | config |
clock-sync | close-epoch | stop | reset` (`--root` or `STARPATH_DEV_ROOT`). The load-bearing
rules — the artifact-input staleness guard (inputs, never commit equality), retained-prebuilt
staging, browser checks against the managed stack, same-commit prebuilt placement mode, the
sub-100 ms acceptance race (run it alone), and single-writer artifact/log paths — are distilled
in [references/dev-stack.md](references/dev-stack.md).

## Assertion scope — never overclaim

`run-tests.sh` asserts values and mined status only: no gas, no timing; and it compares the
Yul and Stylus header-digest vectors against each other. So a codegen-target override cannot
satisfy or defeat it, and any gas/timing figure quoted from CI is not reproduced locally. A
local devnet pass is a pass of that script — never the pinned-configuration measurement.

## Node-side tooling against the browser fixtures

When a task needs a Node process that drives the same services the browser specs drive
(an operator stack, a topology supervisor, a one-off probe):

- **Import the fixtures directly.** They are plain TypeScript importing only `node:*`
  builtins plus `@starpath/params`, and Node runs `.ts` by type stripping (default on Node
  ≥22.18 and on 24; `--experimental-strip-types` on 22.x). Keep anything you add there
  erasable-syntax-only — no `enum`, `namespace`, or parameter properties — or stripping
  fails at import time.
- **`@starpath/params` resolves only from inside `services/web`.** There is no root-level
  `node_modules/@starpath` link, so resolution is decided by the *importing file's* location:
  a module under `services/web/tests/**` resolves the package even when a script in
  `scripts/` imports that module by relative `.ts` path. Put a new Node-side file that
  imports PARAMS under `services/web/…`, not `scripts/`.
- **`services/web/tests/**` is not type-checked.** `tsconfig.app.json` includes only `src`
  and `tsconfig.node.json` only `vite.config.ts`, so `pnpm --filter @starpath/web run check`
  says nothing about a spec or fixture change — an unused import or stale call site survives
  it silently. Lint (`pnpm --filter @starpath/web run lint`) and read the diff by hand; only
  the acceptance run proves behavior.
- Prefer a `node --test` lane (`node --test tests/node/*.test.mjs` — a glob or explicit files)
  for the pure parts of such a tool — config building, argument parsing, guards — and let the
  real acceptance run cover the rest. Do not add it as a `test` script in a package whose lane
  the repo has not agreed to; name it explicitly (`test:node`).
- **`node --test <dir>/` is not a valid invocation on Node 24.** A trailing-slash directory is
  loaded as a module, so every test "fails" with `Cannot find module '.../tests/node'` while
  the runner still reports `tests 1 / fail 1` — pass a glob (`tests/node/*.test.mjs`) or name
  the files, and confirm the count is the number of cases you actually wrote.
- **A module that uses bundler-style `.js` specifiers pointing at `.ts` files cannot be imported by
  `node --test`.** Vite resolves `./browserSettlementAbi.js` to its `.ts` source; Node's ESM resolver
  does not, so importing a composed runtime (anything reaching `src/shared/sdk`) throws
  `ERR_MODULE_NOT_FOUND` in the unit lane. Keep the pure helper in its own module so the test imports
  only that, and let the browser check cover the composed graph — do not delete the `.js` specifier to
  make a test pass, because that is the form Vite builds.

## Documenting results in this repo

- **A stale status claim is never in only one file.** When what a package *is* changes, the same
  sentence survives in its `README.md`, its `AGENTS.md`, the local runbook's command comments, and the
  Informative `docs/architecture/architecture.md` — diagram node labels and the responsibility table
  included. Fix the one you were told about, then sweep for the phrase
  (`git grep -n -i 'vite starter' -- '*.md'`) and fix the rest; leave the *historical* mentions alone
  ("is no longer the …", "was the …", "the starter's placeholder"). Checking one file and reporting
  "one stale claim" is how the same defect ships twice.

- Every file under `docs/` carries a status header. Measured results and dated
  external-state observations are **Informative** and belong in `docs/results/` (one file per
  topic and date, stating what the record does **not** establish).
- Register-level figures belong in `docs/registers/measurements.md`; obligations own closure.
  A results note is the evidence behind a register entry, not the entry.
- `./scripts/check-doc-links.sh` resolves relative links in tracked **and untracked** files.
- `./scripts/check-roadmap-reference-policy.sh` rejects delivery identifiers (`M0-M4`,
  `S1-S9` case-insensitive, `P0-P8`, `C1-C6`, `U1-U3`, `H1-H4`, `OC1`/`OC2`) in paths and in
  content. Grep your own additions before committing. Vendored third-party sources under
  `vendor/` are skipped for content (their bytes are pinned upstream and cannot be rewritten);
  paths are still checked.
- `./scripts/check-no-inline-constants.sh` rejects the distinctive protocol literals anywhere
  outside `packages/params` **including in comments**. Name the constant instead of restating
  its value.
- `AGENTS.md` is write-protected: an edit requires explicit user approval. If the approval
  prompt times out, do not retry it and do not route around it via another tool.

## Pitfalls

- Generated artifacts need no handling: `contracts/out` and `contracts/cache` are already
  ignored, and the harness's unclean-tree check still passes with them present.
- `contracts/lib/forge-std` is a pinned submodule; a checkout without
  `git submodule update --init --recursive` cannot build or test the contracts at all.
- Keep evidence, corpora, configs, and credentials outside the source checkout.
- **`mkdir -p` the evidence directory inside every script that writes into it.** A
  `$(date -u +%F)`-derived path changes at a UTC date rollover, so a script that assumes a directory
  created earlier in the session dies at its first redirect/`tee` — after the expensive work it was
  capturing. Create the directory in the script, not once in the session.
- **After `stop`, `start` refuses while `private/topology-manifest.json` exists** — run
  `reset --yes` first (cheap: it keeps the pinned artifacts). A deliberate staleness test needs the
  same order, because that refusal is checked *before* the artifact guard.
- `gh run view`'s job list can lag while a run is in progress (a job shown `in_progress` was
  already `completed/success`); confirm job and step verdicts through the jobs API before
  reporting a result.
- Never run an unbounded `grep -rn` over fixture, vector, or base64-heavy directories: one
  command can put ~100 KB of transcript into context. List or count matches first, then read
  the specific lines.
