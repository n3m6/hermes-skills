# Source and docs recon (when the target publishes code)

Upgrades a teardown from "what the site says" to "what the pipeline is". Every command here is read-only.

## 1. Find the org's repos (one call, highest value)

```bash
curl -sL -H "Accept: application/vnd.github+json" \
  "https://api.github.com/orgs/<ORG>/repos?per_page=100&sort=updated"
```

Filter in python, never dump JSON into context. Fields that matter: `name`, `language`, `pushed_at`, `description` — the description sometimes carries the audit-report link. A public prover/circuits/contracts repo is the whole prize; SDKs and chart components are noise for a teardown.

## 2. Read a repo without cloning it

```bash
# directory inventory (batch these, print only names+types)
curl -sL -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/<org>/<repo>/contents/<path>"

# language byte counts  .../repos/<org>/<repo>/languages
# last commit + date     .../repos/<org>/<repo>/commits?per_page=1
# file text              https://raw.githubusercontent.com/<org>/<repo>/<branch>/<path>
```

## 3. What to read, in order of signal

1. **Manifests** (`Cargo.toml`, `package.json`, `go.mod`) — dependency names disclose the field, curve, hash, backend and wrapper libraries. This is the stack, verbatim.
2. **Build scripts** (`build_*.sh`, `Makefile`) — the artifact inventory and its real knobs (`TX_PER_PROOF`, SRS path, `PUBDATA_MODE`, curve/chain ids). A build script is more honest than a whitepaper diagram.
3. **Top-level source dirs of the circuit / verifier crates** — the noun list is the design surface (`matching_engine.rs`, `liquidation.rs`, `blob/`, `recursion/`, `poseidon_bn128`).
4. **The final-wrap entry point** — which backend, which curve, which SRS. `gnark/backend/plonk` + a universal SRS from a public ceremony is a different trust story from `groth16` + a per-circuit ceremony; always report which one the target chose.
5. **The crate's own doc comment is the statement.** A module-level `//!` block at the top of a crate's `lib.rs` usually states, in the authors' words, exactly what that crate proves — quote it rather than paraphrasing a whitepaper. Then **grade every conclusion**: *read from source* (a doc comment, a constraint list, a manifest, a test name) versus *inferred from the layout* (a crate's name implies its purpose, a directory implies a mechanism). Say which, per claim. An inferred mechanism presented as read is the one failure a teardown cannot recover from.
6. **Licence per crate, not per repo.** A workspace `license` can differ per crate — a BSL-1.1 product often ships permissively licensed (MIT/Apache) helper crates. That difference decides whether vendoring the component is even legal, so read the `license` field of the specific crate before recommending a port, and never carry the repo-level licence over to a crate that states its own.

A **two-proof-system split** announces itself as a pair in the crate graph: a standalone prover crate for one term, plus a `recursion` / `bridge` crate whose optional dependencies include the main circuit's framework. It means the target pays for that term in a separate proof and only proves the verification of it inside the main one — a structural decision, not a detail, and usually the most transferable idea in the repo. Read what the pair actually binds (public inputs, digest layout, hash profile) before describing the architecture.

## 4. Doc sites and papers

- Append `.md` to any docs page URL for markdown; fetch `/llms.txt` for the full page index. Works for GitBook and most doc generators.
- Whitepaper: `curl -sL -A "Mozilla/5.0" <pdf-url> -o wp.pdf && pdftotext -layout wp.pdf wp.txt`, then jump straight to the terms that matter:
  `grep -n -i -E "plonk|groth|plonky|aggregat|recursi|blob|gas|tps|prover|witness|field|poseidon|audit" wp.txt`
- Read the footnotes, the limitations asides, and the "future work" section. That is where a design admits what it gave up.

## 5. Cross-checking against our own stack

- Grep their manifests for the names we depend on (verifier forks, hash/curve libraries). A shared vendored component is the strongest comparison available: independent validation of our choice, or a divergence that is a defect on one side.
- When both sides fork the same upstream, diff the forks and note the pinned version/commit on each — a fix we carry that they do not (or vice versa) is actionable in both directions.
- Label their throughput/gas/cost numbers as claims until reproduced; state what the paper covers and the build script does not confirm.
- **A committed real-data fixture is shipped-and-exercised evidence; the same claim in prose is not.** A circuits directory shipping the blobs or witnesses of a named, linked on-chain batch (plus a build script that consumes them) proves that path has run against production data. Look for it before believing any "the escape hatch works" sentence, and treat its absence as an open question rather than a defect.

## Pitfalls

- Do not treat the paper's architecture as the shipped one — reconcile against the build script and source inventory before repeating it.
- Do not quote a docs page's own summary of a circuit as evidence the circuit does that; the source directory list is the evidence, the prose is the claim.
- A shell loop that parses a URL with a `:` split (`${u%%:*}`) mangles `https://` — pass full URLs to `curl` directly instead of building `key:value` pairs.
