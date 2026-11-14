# Preparing a starpath validation obligation (O-N)

Depth for the "Paid-validation preparation" section of the `starpath` skill. The always-on rules
live there; this file is the recon procedure and the pitfalls. Repo: `~/repos/starpath`
(`silentsea-xyz/starpath`); read the root `AGENTS.md` router, then only the package/service
`AGENTS.md` the task points at.

## Recon procedure

1. Locate the obligation: `grep -n "O-5" docs/registers/obligations.md` for its closure
   claim, then read the matching `docs/roadmap/*closure-plan.md` plus the handoff/execution
   plan it derives from.
2. Find the code that exists: `git log --oneline -25 -- <paths>` for the feature, and
   filename discovery (`*o5*`) for the binaries, scripts, harnesses and tests.
3. **Read the task graph programmatically.** `manifest-v1.json` / `manifest-v2.json` are
   tens of KB. Load with Python and print only `id, kind, command, working_directory,
   depends_on, exclusive, required_credentials, required_outputs, acceptance_parser,
   timeout_seconds`. Use `scripts/manifest_tasks.py`. Never page the raw file.
4. Read the readiness contract (`scripts/server-validation/external-readiness.md` and
   `external-readiness.py`): which components owe the `runner
   --server-validation-readiness --config /proc/self/fd/N --kind KIND` probe, the exact
   `KIND` strings, and the reserved exit codes (78 = `configuration_unavailable`, plus the
   `CONFIGURATION_UNAVAILABLE_EXIT_CODES` map). Then `grep -rn server-validation-readiness`
   repo-wide to learn which *real* backends implement the flag: the repository-owned Python
   controllers do; a compiled arm binary may not, so "readiness for the real runners" can be
   a code change rather than a staging step.
5. Check `docs/registers/measurements.md` for the obligation's gate record before calling
   anything unmeasured — it usually already distinguishes a recorded gate from a harness
   that merely exists.
6. Before promising a run: check the toolchain, check free disk against the documented
   reserve, and establish the *actual outcome* of any prior attempt (see pitfalls).

## Pitfalls

- **A truncated build/test log reads like a pass.** Trust the wrapper's own completion
  marker (`grep -n '\^### phase-exit\|ALL .*DONE\|### wrapper exit' <log>`) plus
  confirmation that no workload process is still alive. A log that stops mid-compile with no
  marker is an interrupted run — re-run it, do not report it.
- **Generator inputs can embed deployment identities, so preparation has a hidden ordering
  edge.** A sealed validation-work corpus carries a venue configuration (namespace, oracle
  identity, publisher, Inbox, anchor) that rejects placeholder values, so the deterministic
  *predicted* addresses must be fixed before the inputs can be generated — even though the
  broadcast itself stays in the campaign. Sequence the work around that or the expensive
  generation fails late.
- **The production deployment profile rejects historical fixture identities.** A namespace
  (or other domain id) that `packages/params` bakes in as a testnet/fixture value is refused
  by the live adapter. Budget for minting a fresh, non-reserved value and holding it
  byte-identical across genesis manifests, the profile and the environment.
- **Heavy local generation dominates the schedule; measure the cheap case first.**
  Frame-per-trade generators run every frame through the full enclave runtime, so cost
  scales with prints x 2 frames. Time the smallest and a mid case, extrapolate, and only
  then commit to the maximum case — under the documented cgroup envelope (one build job, one
  rayon thread, zero swap, 10 GiB free-disk reserve), never by raising limits.
- **The acceptance harness refuses a dirty or untracked tree and a mismatched
  `--expected-source-commit`.** Commit before running it. Note which generated artifacts are
  *committed* (`packages/params/generated/`) so nobody re-runs a generator already in the
  tree.
- **The devnet half of a matrix needs real provisioning.** Container runtime + pinned devnode
  image + Foundry + the node toolchain for the contracts/Nitro path. Install through
  `scripts/server-validation/provision-tools.py` (pinned, SHA-256-bound, new-only
  destinations) instead of by hand, and confirm availability before promising a devnet run.
- **Cross-check a manifest command against its `working_directory`.** Commands are relative
  to the task's working directory (contracts tasks run under `contracts/`), so a path that
  looks missing from repo root is usually correct — verify before "fixing" the manifest.
- **A drill and a soak are separate obligations, always.** A completed deadline drill never
  closes a multi-day retention soak; keep both visibly open in every answer.
- **Check whether the readiness probe validates anything real.** Some probes only test
  non-empty-and-equal environment values; do not upgrade that into "the endpoints work".

## O-5 depth

[references/tape-publication-readiness.md](tape-publication-readiness.md) — the two-venue
anchor model, the exact live inputs, Celestia endpoint and namespace requirements, funding,
the drill's fault/restart boundaries, and the external unknowns to verify before booking.
