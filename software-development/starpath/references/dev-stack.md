# The development stack tool (`scripts/dev-stack/run-development-topology.mjs`)

Depth for the `starpath` skill's development-stack section: the operator tool for a long-lived
local stack. Subcommands `build | start | status | config | clock-sync | close-epoch | stop |
reset`, with `--root` or `STARPATH_DEV_ROOT`.

- `start` refuses a root whose `artifacts.json` stamp names another commit, so re-run `build`
  before `start` after any mid-session commit: cargo is a no-op and only wasm-bindgen/forge
  and the re-stamp rerun, so that costs minutes. Do not quote a ~58 min figure for it — that
  figure describes a root whose target directory is gone.
- **The guard worth having compares artifact inputs, not commits.** The inputs that decide
  whether the stamped binaries are current are the tree/blob hashes of `packages`,
  `services/api`, `services/sequencer`, `services/tee-node`, `contracts`, `Cargo.toml`,
  `Cargo.lock`, and `rust-toolchain.toml` (`git rev-parse HEAD:<path>`), plus an emptiness check
  on `git status --porcelain -- <those paths>`. Commit equality invalidates a working
  environment on a web-only commit; input equality is stricter about the binaries and stable
  across app work. Keep `packages` deliberately coarse: a TypeScript-only change invalidates
  too, which costs a rebuild but can never present a stale binary as current.
- **`reset` removes the whole root, cargo target included**, so the next fresh demonstration
  pays a cold build again (~58 min on an 8-thread host) unless a retained prebuilt layout is
  staged back. Scope `reset` to private state (`private/`, `public-artifacts/`,
  `public-config.json`, `public-config.env`, `running.json`) so a fresh demonstration stays
  cheap.
- **Look for a retained prebuilt layout before accepting a cold build.** A measured run leaves
  one under its evidence root (`<evidence>/<date>/prebuilt-target/`: `release/` binaries, pinned
  `ci-tools/wasm-bindgen`, `wasm32-unknown-unknown/<profile>/starpath_sdk_wasm.wasm`). Prove
  currency first — `git diff --stat <that layout's commit>..HEAD -- <the artifact inputs above>`
  must be empty — then copy the binaries into `<root>/cargo-target/release/`, re-run
  wasm-bindgen over the retained `.wasm` into `<root>/wasm`, and `forge build`. The glue
  regenerates in seconds because the Rust side is untouched. Record the layout path, its origin
  commit, and the empty diff: a staged environment is only as good as that proof. Mirror the
  retained all-feature WASM into `<root>/cargo-target/wasm32-unknown-unknown/<profile>/starpath_sdk_wasm.wasm`
  as well as regenerating the glue: the acceptance runner's prebuilt mode looks for it inside the
  target directory it is pointed at and fails with `missing prebuilt all-feature SDK WASM artifact`
  otherwise.
- **Check the app in a browser against the stack the operator tool started.** Playwright's own
  `webServer` starts a bare `vite` with none of the stack's asset routes, so run the spec with
  `STARPATH_TOPOLOGY_MANAGED=1` (disables that server),
  `STARPATH_PLAYWRIGHT_BASE_URL=$(node -e 'process.stdout.write(require("<root>/running.json").browserUrl)')`,
  and `STARPATH_PLAYWRIGHT_BUNDLED_CHROMIUM=1` where Chrome is absent; the spec must `test.skip`
  when the base URL is unset, so a bare `test:browser` neither fails nor invents a topology.
- The app-side composition this stack exists to serve — the same-origin contract/WASM routes,
  the once-per-page runtime, the blocked-state contract, and what the browser checker asserts:
  [references/browser-app-runtime.md](browser-app-runtime.md).
- Verify the placement path in same-commit prebuilt mode instead of rebuilding for an hour:
  `STARPATH_CI_PREBUILT_RUST_BINARIES=1 STARPATH_CI_PREBUILT_TARGET_DIR=target/browser-to-ack-dev/cargo-target ./scripts/run-sdk-placement-integration.sh`
  (a ~7 min test against a ~1 h hermetic run, plus the `forge build` the runner performs even in
  prebuilt mode — all 68 contracts recompile under `via_ir`, ~7.5 min on an 8-thread host, so budget
  ~15 min per attempt). It proves the path passes on that revision; it never proves the clean-source
  measured gate passed, and the difference belongs in the record.
- **Move a failed attempt's artifact directory aside before re-running into the same path.** A killed
  attempt leaves `failure.json` and `private-failure/` behind; reusing that directory mixes two runs'
  verdicts (and the preflight can refuse it outright), so `mv <dir> <dir>-attemptN-<why>` first and
  keep both.
- **The acceptance topology decides a sub-100 ms race — run it alone.** After the fault matrix stops
  the tee-node, `topologyServices.integration.spec.ts` requires the sequencer's `/ready` to answer
  `503` on the next request, while the transition itself takes ~45 ms (idle consumer) to ~97 ms
  (frame in flight, during an epoch closure) on an 8-thread host. `TopologyController.stop` already
  awaits the child's exit and the sequencer clears `authenticated_consumer_active` through two
  event-driven sites (`ordering_v2.rs` failed `try_send`, `grpc.rs` request-stream end) with no
  liveness timeout — so the loss is scheduling, never the product. A run stopping at 27 of 37 cases
  with `Expected: 503, Received: 200` is a rerun signal: check `pgrep -af run-sdk-placement` first,
  then run with no dev stack and no browser checks. Do not add a retry to that assertion to get a
  green run; the record is the pass on an idle host, with the host's load average at start and case
  ids diffed against the baseline.
- **Never let two runs share an artifact directory or a log path.** Two supervisors writing one log
  interleave, and whichever finishes last overwrites `topology-result.json`, leaving neither run
  attributable. Verify a prior run is really gone by pid (`ps --ppid <pid>`, `/proc/<pid>/cmdline`)
  before relaunching — a `Hangup` line naming a child subshell is that subshell dying, not the run.
- A supervisor's operator-request poll loop must treat a **removed root as a clean exit**
  (`readdir` ENOENT → return), because `reset` deletes the queue underneath a still-running
  supervisor; otherwise the documented `stop` then `reset --yes` flow ends the session with an
  unhandled ENOENT and exit 1. Any other `readdir` error must still propagate.
- Assert the error *kind* you mean: a nonexistent `/proc/<pid>/fd/...` path raises `EACCES`, not
  `ENOENT`. Use a temp file for the "not a directory" branch of such a guard.
- Keep the downloaded toolchain archives (`/tmp/node-v24.10.0-linux-x64.tar.xz`) so the pinned
  prerequisite stays re-hashable against the vendor's published `SHASUMS256.txt`. A prerequisite
  claim whose digest cannot be re-derived is narration; if an archive was not kept, say which
  check is not reproducible rather than implying it is.
