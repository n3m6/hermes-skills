---
name: starpath-validation-preparation
description: Use when preparing a starpath validation obligation (O-N).
---

# Starpath paid-validation preparation

Class of task: take a starpath / Silent Sea validation obligation (`O-1`, `O-5`,
`O-10`, `O-11`, `O-34`, ...) to "operationally ready" — or answer what is left to
prepare before an operator-authorized paid campaign. Same machinery for every
obligation: a no-work readiness probe, digest-pinned owner-only staged inputs, a
versioned task manifest, a booking-readiness report, and a hard line between
local preparation and the authorized campaign.

Repo: `~/repos/starpath` (github `silentsea-xyz/starpath`). Read the root `AGENTS.md` router, then only the package/service `AGENTS.md` the task points at. Behavior is owned by `docs/specs/`, `docs/adr/`, the acceptance map, and `docs/registers/obligations.md`; roadmap docs are Informative schedules and their `O-N` ids are not requirement names.

## Always-on rules

1. **Verdict first, then the remaining-work list.** "What do I have to do?" wants a verdict plus an ordered action list, not a narration of the investigation. Answer in this shape: (a) what already exists and must not be rebuilt, one line each; (b) numbered remaining items in dependency order with exact commands and paths; (c) what is explicitly campaign-scope and therefore *not* preparation; (d) the single decision or approval you need. End with that ask — propose, get the terse approval, then execute. Do not start heavy or paid work while answering.
2. **Preparation never performs a paid or public action.** Local/devnet only: no host booking, no testnet transaction, no deployment broadcast, no quote acquisition, no proof campaign. Fresh deployments, a real-time deadline drill, and multi-day soaks are campaign obligations — name them as out of scope out loud instead of quietly dropping them.
3. **No fabricated passes.** Local success is not obligation closure, and every governing doc here says so. If a prior attempt was interrupted, report "no passing record", not whatever the tail of the log happens to say.
4. **Staged inputs are data, never argv, and never secret-bearing evidence.** Absolute, regular, non-symlink, owner-owned files outside the Starpath and Mariner checkouts; private files `0600`; public executable/asset files with no group or other write bit; secrets only through `<NAME>_FILE`; a runner receives a configuration *path*, never a command or an executable.
5. **`ready` means parseable, not wired.** The no-work probe proves only that the profile parses locally and the environment matches its pins. Chain IDs, contract code hashes, signer derivation, funding, and predicted-vs-actual address binding are checked at run time by the arm. State the weaker claim.
6. **Never invent a constant or a duration basis.** Constants come from `packages/params`; a duration estimate comes from a measured comparable phase, otherwise say "unknown".

## Recon procedure

1. Locate the obligation: `grep -n "O-5" docs/registers/obligations.md` for its closure claim, then read the matching `docs/roadmap/*closure-plan.md` plus the handoff/execution plan it derives from.
2. Find the code that exists: `git log --oneline -25 -- <paths>` for the feature, and file-name discovery (`*o5*`) for the binaries, scripts, harnesses, and tests.
3. **Read the task graph programmatically.** `manifest-v1.json` / `manifest-v2.json` are tens of KB — load them with Python, filter `tasks` by id prefix, and print only `id, kind, command, working_directory, depends_on, exclusive, required_credentials, required_outputs, acceptance_parser, timeout_seconds`. Never page the raw file. Use `scripts/manifest_tasks.py` for this.
4. Read the readiness contract (`scripts/server-validation/external-readiness.md` and `external-readiness.py`): which components owe the `runner --server-validation-readiness --config /proc/self/fd/N --kind KIND` probe, the exact `KIND` strings, and the reserved exit codes (78 = `configuration_unavailable`, plus the `CONFIGURATION_UNAVAILABLE_EXIT_CODES` map). Then `grep -rn server-validation-readiness` repo-wide to learn which *real* backends actually implement the flag: the repository-owned Python controllers do; a compiled arm binary may not, so "readiness for the real runners" can be a code change rather than a staging step.
5. Check `docs/registers/measurements.md` for the obligation's gate record before calling anything unmeasured — it usually already distinguishes a recorded gate from a harness that merely exists.
6. Before promising a run: check the toolchain, check free disk against the documented reserve, and establish the *actual outcome* of any prior attempt (see pitfalls).

## Pitfalls

- **A truncated build/test log reads like a pass.** Trust the wrapper's own completion marker (`grep -n '\^### phase-exit\|ALL .*DONE\|### wrapper exit' <log>`) plus confirmation that no workload process is still alive. A log that stops mid-compile with no marker is an interrupted run — re-run it, do not report it.
- **Generator inputs can embed deployment identities, so preparation has a hidden ordering edge.** A sealed validation-work corpus carries a venue configuration (namespace, oracle identity, publisher, Inbox, anchor) that rejects placeholder values, so the deterministic *predicted* addresses must be fixed before the inputs can be generated — even though the broadcast itself stays in the campaign. Sequence the work around that or the expensive generation fails late.
- **The production deployment profile rejects historical fixture identities.** A namespace (or other domain id) that `packages/params` bakes in as a testnet/fixture value is refused by the live adapter. Budget for minting a fresh, non-reserved value and holding it byte-identical across genesis manifests, the profile, and the environment.
- **Heavy local generation dominates the schedule; measure the cheap case first.** Frame-per-trade generators run every frame through the full enclave runtime, so cost scales with prints × 2 frames. Time the smallest and a mid case, extrapolate, and only then commit to the maximum case — under the documented cgroup envelope (one build job, one rayon thread, zero swap, 10 GiB free-disk reserve), never by raising limits.
- **The acceptance harness refuses a dirty or untracked tree and a mismatched `--expected-source-commit`.** Commit before running it. Also note which generated artifacts are *committed* (e.g. `packages/params/generated/`) so nobody re-runs a generator that is already in the tree, or assumes a missing package manager blocks the harness.
- **The devnet half of a matrix needs real provisioning.** Container runtime + pinned devnode image + Foundry + the node toolchain for the contracts/Nitro path. Install through `scripts/server-validation/provision-tools.py` (pinned, SHA-256-bound, new-only destinations) instead of by hand, and confirm availability before promising a devnet run.
- **Cross-check a manifest command against its `working_directory`.** Commands are relative to the task's working directory (contracts tasks run under `contracts/`), so a path that looks missing from repo root is usually correct — verify before "fixing" the manifest.
- **A drill and a soak are separate obligations, always.** A completed deadline drill never closes a multi-day retention soak; keep both visibly open in every answer.
- **Check whether the readiness probe validates anything real.** Some probes only test non-empty-and-equal environment values; do not upgrade that into "the endpoints work".

## Support files

- `references/tape-publication-readiness.md` — O-5 depth: the two-venue anchor model, the exact live inputs, Celestia endpoint and namespace requirements, funding, drill fault/restart boundaries, and the external unknowns to verify before booking.
- `scripts/manifest_tasks.py` — dump a server-validation manifest's tasks (optionally filtered by id prefix) with the scheduling, credential, and acceptance fields that decide the work; avoids paging an 80 KB JSON by hand.
