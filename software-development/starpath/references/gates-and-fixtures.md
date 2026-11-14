# Gates, pins, and local repro

## The Docs job is four cheap gates — run them locally before pushing

```bash
./scripts/check-no-inline-constants.sh      # distinctive protocol literals, comments included
./scripts/check-doc-links.sh                # relative links, tracked and untracked files
./scripts/check-acceptance-map.sh           # responsibilities and dependencies stay consistent
./scripts/check-roadmap-reference-policy.sh # delivery identifiers in paths and content
```

- A literal like the layer cap or the Goldilocks modulus fails `check-no-inline-constants.sh`
  **from a comment**. Name the constant, do not restate its value.
- `check-roadmap-reference-policy.sh` skips `vendor/` for content (pinned upstream bytes cannot be
  reworded) and `docs/roadmap/archive/` entirely; paths are still checked. Semantic substitutes for
  the C/P/S-series identifiers: validation work, the upstream proof.
- Renaming a doc under `docs/` is cheaper than moving it into the archive when its body carries no
  identifier; moving into the archive is right when the body itself is historical.

## A pinned params file is frozen by byte

`packages/epoch-corpus` fixtures pin the **full `packages/params` source surface** plus the
boundary implementation files, so a comment-only edit to `packages/params/src/*` invalidates
them. Two tests then fail with mirrored digests:
`manifest_bound_wire_fixtures::frozen_manifest_bound_wire_artifacts_verify_and_pin` and
`manifest_boundary_provenance::tests::provenance_lists_have_unique_stable_paths`.

`packages/epoch-corpus/AGENTS.md` forbids overwriting a frozen fixture directory: regenerate a
new version, keep the old one asserted.

1. Bump the version in `src/bin/generate_manifest_boundary_wire_fixtures.rs`: the eleven
   filename constants, `schema_version`, `artifact_kind`.
2. Generate into a fresh empty directory (it refuses a non-empty one):
   `cargo run --locked --release -p starpath-epoch-corpus --bin generate_manifest_boundary_wire_fixtures -- --output <empty-dir>`
3. Prove the artifacts are unchanged and only metadata moved: hash every `.bin` against the
   previous version and compare the metadata after normalising the version strings in filenames.
4. Install the new directory under `fixtures/`, point the current `include_bytes!`/`include_str!`
   at it, add a `const <PREV>_METADATA` for the superseded version, and assert both versions'
   `schema_version`, `artifact_kind`, `params_source_sha256`, and
   `boundary_source_files[4]["sha256"]`.
5. Update the current-source constant in `src/manifest_boundary_provenance.rs` to the newly
   computed digest.
6. Verify: `cargo test --locked --release -p starpath-epoch-corpus --lib manifest_bound -- --test-threads=1`

## One fixture port per lane

A V5 manifest's `DeltaPublished -> RelationReady` transition requires an injected V2 tape
relation port; the worker's default is `UnavailableTapeRelationPort`, so the symptom is an
endless `worker tick retryable: Da(Unavailable)`, and in the service a pipeline stage of
`Unavailable` that keeps `/ready` at 503 forever. Every lane that drives such a manifest needs
the CI fixture (`infrastructure::CiTapeRelationFixturePort`, compiled only under
`ci-integration-hooks`): both `exercise-*` binaries and the service's fixture lane
(`TEE_INTEGRATION_FIXTURE_DA_PATH`).

Corollary for required env vars: when a binary starts requiring new configuration (for example
the V6 tape-anchor identities for `bootstrap-local-tee`), every harness that spawns it needs the
same fixture block in the same change. The block the integration scripts use is the reference;
the namespace must match the harness's `deltaNamespace`.

## Local repro prerequisites

```bash
export PATH=$HOME/.foundry/bin:$HOME/.cargo/bin:$HOME/.local/bin:$PATH   # Foundry 1.8.1 is off-PATH
corepack enable pnpm || npm install -g pnpm@<packageManager version>     # package.json pins it
pnpm install --frozen-lockfile
```

**The pinned set is owned by `docs/runbooks/sdk-core.md` ("Pinned prerequisites"): Rust/Cargo
1.91.1 with `wasm32-unknown-unknown`, Node from `.nvmrc`, pnpm from `package.json`
(`packageManager`), `wasm-bindgen-cli` 0.2.127, Foundry 1.8.1, Chrome + the checked-in
Playwright, Docker, OpenSSL, Python 3.** Read that section rather than trusting a list copied
anywhere else, and verify in one command before a long run:
`rustc --version; cargo --version; node --version; pnpm --version; wasm-bindgen --version;
forge --version | head -1; openssl version; docker --version; python3 --version`.

Two prerequisites commonly need installing, and both have a pinned, no-sudo path:

```bash
# Node at the .nvmrc version, if the system node differs — verify against the published sums.
curl -fsSLO https://nodejs.org/dist/v<version>/node-v<version>-linux-x64.tar.xz
curl -fsSL https://nodejs.org/dist/v<version>/SHASUMS256.txt | grep 'linux-x64\.tar\.xz$'
sha256sum node-v<version>-linux-x64.tar.xz          # must equal the published line
mkdir -p ~/.local/node-v<version>
tar -xJf node-v<version>-linux-x64.tar.xz --strip-components=1 -C ~/.local/node-v<version>
export PATH="$HOME/.local/node-v<version>/bin:$PATH"

# wasm-bindgen at the Cargo.lock version. Only the musl x86_64 asset is published (no -gnu).
gh release download <version> --repo rustwasm/wasm-bindgen \
  --pattern 'wasm-bindgen-<version>-x86_64-unknown-linux-musl.tar.gz*' --dir /tmp/wbg --clobber
# compare sha256sum of the tarball with the published .sha256sum asset, then:
tar -xzf /tmp/wbg/wasm-bindgen-<version>-x86_64-unknown-linux-musl.tar.gz
cp wasm-bindgen-<version>-x86_64-unknown-linux-musl/wasm-bindgen ~/.local/bin/
cargo install --locked wasm-bindgen-cli --version <version>   # slow fallback
```

Do not install Foundry ad hoc: `~/.foundry/bin` already holds the pinned 1.8.1, and a second
version on PATH is how a run silently measures a different toolchain.

Browser lanes need the SDK built first, both variants, before the Playwright specs run:

```bash
pnpm --filter @starpath/sdk run build && pnpm --filter @starpath/sdk run build:validation
cd services/web && STARPATH_PLAYWRIGHT_BUNDLED_CHROMIUM=1 \
  STARPATH_PLAYWRIGHT_OUTPUT_DIR=/tmp/pw pnpm exec playwright test --config playwright.config.ts
# add `pnpm exec playwright install chromium` when no system Chrome is present
# point STARPATH_PLAYWRIGHT_OUTPUT_DIR outside the checkout so traces stay untracked
```

- Run the integration scripts with `STARPATH_INTEGRATION_BUILD_PROFILE=release`. In the debug
  profile the epoch schedule outruns anvil's wall-clock block timestamps and the script aborts
  with `Timestamp error: ... lower than previous block's timestamp` — that is the profile, not
  the code under test.
- Playwright: `route.fulfill({ body: ... })` accepts `string | Buffer` only. A plain
  `Uint8Array` never settles the fulfilment, so the page's `fetch` hangs and the test dies on a
  timeout with no error in the handler; pass `Buffer.from([...])`.
- Reproduce a single spec with `--grep "<test title>"`, and prove a suspected cause with an A/B
  pair of scratch tests before changing the real one.
- `STARPATH_PLAYWRIGHT_BUNDLED_CHROMIUM=1` is the documented hatch for a host without system
  Chrome (bundled Chromium lives under `~/.cache/ms-playwright/`). It still runs the real
  pinned engine, so it reproduces the *path* — but the recorded O-36 measurement ran a specific
  Google Chrome build, so a bundled-Chromium run is a different browser and cannot advance that
  record. Say which browser a run used when reporting it.

## The SDK placement topology runner

`scripts/run-sdk-placement-integration.sh` is the heaviest single-key command in the browser
SDK work: it builds the exact binaries and the all-features WASM, deploys the fixture topology,
starts anvil + sequencer + tee-node + api + vite, and drives the real browser spec
(`topologyServices.integration.spec.ts`, `STARPATH_SDK_PLACEMENT_TOPOLOGY=1`).

- **It builds into a private temporary cargo target (`mktemp -d`), so every run pays a full
  release rebuild.** Budget accordingly and start it in `tmux` with `tee` into a log: the
  recorded whole-gate run was ~26 min on a fast host, while this workstation's release build
  alone measured 33 min — 60–150 min per run is a reasonable estimate, and a silent window is
  not a hang (`ps -o pid,time=,etime=,cmd= -C cargo -C rustc -C anvil`).
- **Use a fresh, empty `STARPATH_O36_ARTIFACT_DIR` per run.** It exits `2` if the directory
  already holds a topology result, and that guard is protecting evidence — pick a new directory
  instead of deleting the old one. A successful run prints
  `SDK placement topology smoke passed; secret-free evidence: <dir>` and leaves
  `o36-topology-acceptance-manifest.json` plus `topology-result.json`.
- **On failure it keeps development-sensitive artifacts** under `<dir>/private-failure/`
  (sealed SQLite, keys, logs, Playwright traces). Never commit, upload, or paste them; the
  secret-free `failure.json` is the shareable part.
- **Same-commit prebuilt fast path:** `STARPATH_CI_PREBUILT_RUST_BINARIES=1` with
  `STARPATH_CI_PREBUILT_TARGET_DIR=<dir>` skips Cargo entirely, but it requires release
  binaries for every named tool, the all-features WASM at
  `<dir>/wasm32-unknown-unknown/release/starpath_sdk_wasm.wasm`, and
  `<dir>/ci-tools/wasm-bindgen` reporting the pinned version. Repeated development runs want a
  persistent cargo target of their own rather than the temp one, plus a recorded source commit
  to refuse a stale artifact/HEAD mix.

  **A persistent layout that satisfies all three (verified):** one `CARGO_TARGET_DIR` serves
  both the host and `wasm32-unknown-unknown` builds, so `<target>/release/<bin>` and
  `<target>/wasm32-unknown-unknown/release/starpath_sdk_wasm.wasm` coexist and
  `STARPATH_CI_PREBUILT_TARGET_DIR=<target>` validates; copy the pinned `wasm-bindgen` to
  `<target>/ci-tools/wasm-bindgen`; keep `wasm-bindgen --target web` output in its own
  directory for the `VITE_EXTRA_FS_ALLOW`/wasmUrl path; and write a stamp naming the source
  commit plus tree state, refusing to start when the stamp's commit is not HEAD. Measured on
  this CPU: the cold first build (nine binaries + all-features WASM + contracts) is ~58 min,
  while a rebuild after commits that touch only TypeScript or docs is a cargo no-op — so
  refreshing the stamp after a commit is cheap, and the topology itself then runs in ~6–7 min.
  Drive the *official* runner in this mode rather than hand-running Playwright, so the evidence
  layout, the artifact guard, and the row counting stay the ones the runbook owns.
  When a run fails for a chain/timeout reason, work
  [local-topology-failure-triage.md](local-topology-failure-triage.md) before touching code.
- Count the rows before calling a run green (the live topology manifest is 37 sorted cases;
  the aggregate catalog is 73). A different count is a finding, not a rounding detail.

## Advancing a local epoch by hand

Interval evidence only exists after an epoch closes, so a hand-driven session needs a clock
step. The mechanism, in this order:

1. Move chain time and the sequencer's file clock together: `evm_setNextBlockTimestamp` +
   `evm_mine` over the anvil RPC, then write the u64 big-endian millisecond value (params-owned
   byte width) to the path in `SEQUENCER_CI_CLOCK_PATH`, atomically (temp file, fsync, rename,
   fsync the parent). The timestamp must be aligned to a whole anvil second. Skipping the RPC
   half leaves the head-age check and the clock disagreeing.
2. Submit a fresh reference frame through the **public ingress** — build it with
   `create-sdk-integration-reference-envelope`, then `POST` the exact bytes to `/v1/orders` as
   `application/octet-stream`. `202` means accepted; `503` is retryable backpressure while a
   priority/deposit prefix drains, and the retry must resend the *same* bytes with the oracle
   sequence unadvanced. Never mutate protocol state or a tee-only store directly.
3. Wait on published facts, not on the process: the tee `/ready` must show a *new*
   `last_durable_boundary` **and** a *new* `last_accepted_epoch` (a runtime checkpoint alone is
   not custody visible to the browser), then the sequencer's readiness must report
   `consumer_processed_through` at that boundary frame before dependent work continues.
4. After any wallet-signed or otherwise auto-mined transaction, re-sync the file clock to the
   finalized head before the next admission, or the freshness allowance trips.

Expose these as documented operator steps around the running stack (a command queue the
supervisor polls is enough) rather than leaving an operator to hand-edit sealed state.
