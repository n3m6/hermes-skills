# Browser app runtime (`services/web` → the Browser-to-Ack journey)

Scope: work where the React app in `services/web` must initialize the SDK against the development
stack and show verified readiness — composing the browser adapters, getting the published contract
and the WASM into the browser, and blocking order entry with a reason when something is missing.
Environment and gates stay in the `starpath` skill; this file is the app side.

## Getting configuration into the browser

- The operator tool writes the browser-visible contract to `<root>/public-config.json`
  (`schemaVersion: 1`, published by `services/web/tests/browser/fixtures/publicConfiguration.ts`).
  It lives in the private development root, so nothing serves it by default: the app must be given
  a route, not a build-time environment value. Stack ports are allocated per run, so build-time
  `VITE_*` would mean a rebuild per stack start.
- Serve it from a vite plugin (`services/web/devServerAssets.ts`) reading `VITE_DEV_CONFIG_PATH`
  and `VITE_DEV_WASM_DIR`, wired into both `server` and `preview`. Two routes: `GET /dev-config.json`
  and `GET /dev-wasm/<file>`. Neither exists when the variables are unset — a plain `vite` run and a
  production build have no contract, which is the correct behaviour, not a bug.
- Content types are load-bearing: wasm-bindgen glue must be `application/javascript` and the binary
  `application/wasm`; `application/octet-stream` makes the browser refuse to instantiate. The glue
  fetches its `_bg.wasm` sibling relative to the JS URL, so serve the whole staged directory.
- Refuse `..`, any nested path, a leading `.`, and an unset route by falling through (404) — never by
  resolving the path anyway. Keep the resolver pure so `node --test` can assert the refusals.
- The browser's API base is the same-origin `/api` proxied to the api service, **not** the contract's
  absolute loopback `apiUrl`: a remote desktop session tunnels one port, and an absolute
  `127.0.0.1:<api-port>` URL is unreachable from the founder's machine. `apiUrl` stays published for
  operator tooling.
- A published `wasmUrl` of `/@fs/...` is a dev-server filesystem path and cannot exist in a build;
  the app-side contract parser should reject anything but a same-origin path, which pins the
exit-gate requirement in code.

## Composing the runtime

- Compose **once per page**. `main.tsx` renders under `StrictMode`, so mount effects run twice and
  two runtimes mean two `BrowserVault` instances and two writer-capable clients. Use a module-scope
  single-flight loader (cache the promise; a rejection must clear it so a retry is possible) and do
  not dispose on unmount — a close breaks an in-flight operation. Disposal belongs to the phase that
  introduces a changeable account.
- Adapters to compose, all in `src/shared/sdk` (do not modify them):
  `BrowserVault({ databaseName })`, `BrowserEntropy()`, `WasmProtocolKernel(loader)`,
  `FetchOperationTransport(baseUrl)`, `FetchAttestationPort(baseUrl)`,
  `BrowserAckRegistry({ rpcUrl, registryAddress })`,
  `BrowserAccountChain({ rpcUrl, settlementAddress, deploymentBlock })`.
  Compose `BrowserAckRegistry` **only when the contract publishes a non-empty `registryAddress`**: the
  adapter refuses an empty address (`adjudication registry address is malformed`) and the published
  contract keeps it empty until a browser journey registers an ack signer, so composing it eagerly
  fails the whole readiness check as `runtime-unavailable` — which reads like a stack fault and sends
  you to the services. Leave that port undefined and let the placement phase construct it.
  `BrowserPriorityAuthorizer({ rpcUrl, settlementAddress, accountAddress, walletClient })`.
  The WASM loader is `const facade = await import(/* @vite-ignore */ wasmUrl); await facade.default();`.
  Constructing an adapter does no I/O; the keepless/lazy distinction matters because it is what keeps
  a readiness view from mutating anything.
- The reference composition to translate is `services/web/tests/browser/fixtures/sdkPlacement.ts`
  (`accountLifecycle()` and `placement()`): it shows the exact adapter wiring, the clock as the
  chain's pinned head timestamp, and the development trust root as bytes. It is Playwright test
  code — **never import it from `src/`**.
- Vault availability probe: `BrowserVault.persistenceCapability()` — it throws when IndexedDB is
  unavailable, which is the storage failure to surface. Do not key on `persisted === false`.

## Verifying the development identity

1. `attestation.fetchDevelopmentEvidence()` (`<api>/v1/attestation/dev-bundle-v2`, `503`/`404` while
   the stack is not ready).
2. `kernel.verifyDevAttestationV2({ bundle, expectedSignerPublicKey: <dev-attestation.pub bytes>,
   chainId, settlementHex })` — the same verification `PlacementEngine` performs; never a second
   implementation of a protocol rule.
3. `JSON.parse(await kernel.devAttestationV2Claims(bundle))` and compare `chain_id` and
   `settlement_address_hex` against the pinned contract, and require `hardware_isolated === false`.
4. Hand React only public fields (profile, isolation flag, chain id, settlement, ack-signer
   identity, evidence digest, descriptor **count**). Recipient descriptors are not consumed until the
   placement phase.

One blocked reason per failure (`configuration-unavailable`, `storage-unavailable`,
`wasm-unavailable`, `evidence-unavailable`, `evidence-invalid`, `identity-mismatch`,
`runtime-unavailable`), each rendering the cause **and** the detail, is what makes a blocked screen
useful: the reason names the owner, the detail names the fact. `data-testid` names are the contract
between the panels and the browser checker.

## Repo mechanics that bite

- `scripts/check-sdk-source-guard.sh` scans `services/web/src/shared/sdk/` and fails on
  `localStorage`, any `console.*`, and `JSON.stringify` of secret material. Put new composition or
  error-mapping code that may log outside that directory (e.g. `src/shared/runtime/`).
- `tsconfig.app.json` includes only `src`, and it is `erasableSyntaxOnly` + `noUnusedLocals` +
  `verbatimModuleSyntax` (type-only imports need `import type`) with `allowImportingTsExtensions`
  (import with the `.ts`/`.tsx` extension). A vite plugin or a fixture is outside that include: keep
  it erasable, and test its pure parts with `node --test`.
- Assert that ordinary loading never requests the exit-proving module (`exitProofWorker`,
  `exitClaim`) by collecting `page.on("request")` URLs — an assertion, not a promise in prose.
- **Run one spec by passing it to `npx playwright test <spec>` from `services/web`.** A spec path
  appended through `pnpm --filter @starpath/web run test:browser -- <spec>` does not filter: the whole
  suite runs, and since `STARPATH_TOPOLOGY_MANAGED=1` disables the config's own `webServer`, unrelated
  `browserVault` specs then fail for want of a dev server — a false red that costs a triage round.
- The dev server's own `/@fs` route serves any path under `fs.allow`, which
  `searchForWorkspaceRoot` sets to the repository root, so `<root>/private/**` is readable over
  loopback while the stack runs. Narrowing it is blocked by the workspace-linked `@starpath/*`
  packages living outside `services/web`; treat it as a known local gap rather than reshaping the
  plugin.
- A request the asset routes refuse still answers **200 with the SPA HTML shell**, so a traversal or
  nested-path check must assert on the body (`<!doctype html>`), never on the status code.
- Build the preview's `VITE_API_PROXY_TARGET` with `new URL(<readinessUrl>).port`. `readinessUrl`
  carries its path, so `split(":")` yields `<port>/health`, every `/api` request answers 404, and the
  app reports `evidence-unavailable` — indistinguishable from a stack serving no attestation.
- Package lanes: `check` (`tsc -b`), `lint` (`oxlint`), `build` (`tsc -b && vite build`),
  `test:node` (`node --test tests/node/*.test.mjs`), `test:browser` (Playwright). Pure logic
  (contract parsing, identity mapping, readiness derivation, the asset resolver) belongs in the
  `node --test` lane; the rendered screen is verified in a real browser, since no component-test
  library is installed and adding one is a decision, not a detail.
