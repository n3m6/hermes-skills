# Repo conventions (starpath)

Depth for the `starpath` skill: local commands, Node-side tooling against the browser fixtures, and
how results are documented.

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

## Node-side tooling against the browser fixtures

When a task needs a Node process that drives the same services the browser specs drive (an operator
stack, a topology supervisor, a one-off probe):

- **Import the fixtures directly.** They are plain TypeScript importing only `node:*` builtins plus
  `@starpath/params`, and Node runs `.ts` by type stripping (default on Node ≥22.18 and 24;
  `--experimental-strip-types` on 22.x). Keep anything you add erasable-syntax-only — no `enum`,
  `namespace`, or parameter properties — or stripping fails at import time.
- **`@starpath/params` resolves only from inside `services/web`.** There is no root-level
  `node_modules/@starpath` link, so resolution is decided by the *importing file's* location: put a
  new Node-side file that imports PARAMS under `services/web/…`, not `scripts/`.
- **`services/web/tests/**` is not type-checked** (`tsconfig.app.json` includes only `src`,
  `tsconfig.node.json` only `vite.config.ts`), so `pnpm --filter @starpath/web run check` says nothing
  about a spec/fixture change — lint (`pnpm --filter @starpath/web run lint`) and read the diff by
  hand; only the acceptance run proves behaviour.
- Prefer a `node --test` lane for the pure parts (config building, argument parsing, guards) and let
  the real acceptance run cover the rest. Name it explicitly (`test:node`) — do not add it to a
  package lane the repo has not agreed to.
- **`node --test <dir>/` is not a valid invocation on Node 24.** A trailing-slash directory is loaded
  as a module, so every test "fails" with `Cannot find module '.../tests/node'` while the runner still
  reports `tests 1 / fail 1`. Pass a glob (`tests/node/*.test.mjs`) or name the files.
- **A module that uses bundler-style `.js` specifiers pointing at `.ts` files cannot be imported by
  `node --test`.** Vite resolves `./browserSettlementAbi.js` to its `.ts` source; Node's ESM resolver
  does not, so importing a composed runtime throws `ERR_MODULE_NOT_FOUND`. Keep the pure helper in
  its own module so the test imports only that, and do not delete the `.js` specifier to make a test
  pass — that is the form Vite builds.

## Documenting results

- **A stale status claim is never in only one file.** When what a package *is* changes, the same
  sentence survives in its `README.md`, its `AGENTS.md`, the local runbook's command comments, and
  the Informative `docs/architecture/architecture.md` (diagram node labels and the responsibility
  table included). Fix the one you were told about, then sweep for the phrase
  (`git grep -n -i '<phrase>' -- '*.md'`) and fix the rest — but leave the *historical* mentions alone
  ("is no longer the …", "was the …"). Checking one file and reporting "one stale claim" is how the
  same defect ships twice.
- Every file under `docs/` carries a status header. Measured results and dated external-state
  observations are **Informative** and belong in `docs/results/` (one file per topic and date, stating
  what the record does **not** establish).
- Register-level figures belong in `docs/registers/measurements.md`; obligations own closure. A
  results note is the evidence behind a register entry, not the entry.
- `check-roadmap-reference-policy.sh` rejects delivery identifiers in paths and content; grep your own
  additions before committing. Vendored third-party sources under `vendor/` are skipped for content;
  paths are still checked.
- `check-no-inline-constants.sh` rejects distinctive protocol literals anywhere outside
  `packages/params`, **comments included** — name the constant instead of restating its value.

## Other pitfalls

- Generated artifacts need no handling: `contracts/out` and `contracts/cache` are already ignored,
  and the harness's unclean-tree check still passes with them present.
- `contracts/lib/forge-std` is a pinned submodule; a checkout without
  `git submodule update --init --recursive` cannot build or test the contracts at all.
- Keep evidence, corpora, configs, and credentials outside the source checkout.
- **`mkdir -p` the evidence directory inside every script that writes into it.** A
  `$(date -u +%F)`-derived path changes at a UTC date rollover, so a script that assumes a directory
  created earlier in the session dies at its first redirect/`tee` — after the expensive work it was
  capturing.
- **After `stop`, `start` refuses while `private/topology-manifest.json` exists** — run `reset --yes`
  first (cheap: it keeps the pinned artifacts); the refusal is checked *before* the artifact guard.
- `gh run view`'s job list can lag while a run is in progress (a job shown `in_progress` may already
  be `completed/success`); confirm job and step verdicts through the jobs API before reporting.
- Never run an unbounded `grep -rn` over fixture, vector, or base64-heavy directories: one command
  can put ~100 KB of transcript into context. List or count matches first, then read the lines.
