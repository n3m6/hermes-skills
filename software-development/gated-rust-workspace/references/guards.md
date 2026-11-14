# Guard implementations to copy

Adapt the crate names and paths; keep the shapes. Each guard protects one rule.

## `tools/check-deps.sh` — the core is a leaf

```bash
#!/usr/bin/env bash
# The simulation crate must not depend on anything. This is what keeps it portable
# and keeps determinism from being somebody else's decision.
set -euo pipefail
manifest="crates/core/Cargo.toml"
if grep -A100 '^\[dependencies\]' "$manifest" | grep -qE '^[a-zA-Z0-9_-]+ *=' ; then
  echo "FAIL: wwx-core declares dependencies"
  grep -A100 '^\[dependencies\]' "$manifest" | grep -E '^[a-zA-Z0-9_-]+ *='
  exit 1
fi
echo "deps: ok (core declares no dependencies)"
```

## `tools/check-determinism.sh` — the greps a type system cannot do

Deliberate redundancy with clippy: a lint can be allowed locally with an attribute,
a repo-wide grep cannot.

```bash
#!/usr/bin/env bash
set -euo pipefail

# This test reads the workspace manifests on purpose, so it is the one file in the
# crate where touching the filesystem is the point. It is a check *on the build*, not
# simulation code, and nothing in it runs during a campaign.
exclude=(--exclude=architecture.rs)

fail=0
scans() {
  grep -rnE "${exclude[@]}" "$1" crates/core/src crates/core/tests 2>/dev/null \
    | grep -vE ': *(//|///|//!)' || true
}
scan() {
  local pattern="$1" why="$2" hits
  hits=$(scans "$pattern")
  if [ -n "$hits" ]; then echo "FAIL: $why"; echo "$hits" | head -20; fail=1; fi
}

scan '\bf32\b|\bf64\b'                                  'float type'
scan 'HashMap|HashSet'                                  'unordered collection'
scan 'SystemTime|Instant'                               'wall clock'
scan 'std::fs|std::net|std::process|std::thread|File::'  'IO, net or threads'
scan 'thread_rng|rand::'                                'shared-stream randomness'

[ "$fail" -eq 0 ] || { echo "determinism check failed"; exit 1; }
echo "determinism: ok (no float, no unordered collection, no clock, no IO)"
```

Two details earn their keep: `scans()` returns the hits so the failure message *is*
the evidence, and the comment-prefix filter lets a file document the ban without
tripping it. Keep the filtering in the helper — reaching for `grep -q` directly on
the unfiltered stream is the classic bug here.

## `crates/core/tests/architecture.rs` — boundaries enforced from the manifests

Shape: an explicit table of `(crate dir, allowed dependency names)`, then parse each
`Cargo.toml` and panic naming the offender.

```rust
const ALLOWED: &[(&str, &[&str])] = &[
    ("core", &[]),                                   // a leaf, asserted twice
    ("content", &["serde"]),
    ("projection", &["wwx-core", "serde"]),
    ("session", &["wwx-core", "wwx-content", "wwx-projection", "serde"]),
];
// For each: read the manifest, take [dependencies] keys, subtract ALLOWED, panic
// listing what is left, and cite the design section the rule comes from.
```

Keep the table in the test rather than in a document, and add a case asserting the
table covers every crate in the workspace — otherwise a new crate is silently
unconstrained. Then add this test's own `use std::fs;` to the determinism guard's
exclusion list, or the "no IO" scan fires on the one file whose job is reading
manifests.

## `tools/gate.sh` — the only definition of "passing"

```bash
#!/usr/bin/env bash
set -euo pipefail
step() { printf '\n== %s\n' "$1"; }

step "formatting";        cargo fmt --all --check
step "lints";             cargo clippy --workspace --all-targets -- -D warnings
step "leaf crate";        bash tools/check-deps.sh
step "determinism";       bash tools/check-determinism.sh
step "tests";             cargo test --workspace
step "content validates"; cargo run --quiet -p wwx-cli --bin wwx -- validate
step "a century replays"; cargo run --quiet -p wwx-cli --bin wwx -- replay --seed 20260921 --months 1200
printf '\ngate: ok\n'
```

Order the steps so the cheapest failure comes first. The end-to-end step earns its
runtime: it is the only one proving the thing runs, rather than that its parts
compile. Make the strongest check stronger than "the same call twice" — re-running
from a *stored command stream* into a fresh instance is what catches a replay path
that is broken while its seed-based twin passes.

## `.github/workflows/ci.yml` — no second list of steps

```yaml
- name: Install the pinned toolchain
  run: |
    rustup toolchain install "$(sed -n 's/^channel = "\(.*\)"/\1/p' rust-toolchain.toml)" \
      --profile minimal --component rustfmt,clippy
- uses: Swatinem/rust-cache@v2
- name: The gate
  run: bash tools/gate.sh
```

Resolve the toolchain from `rust-toolchain.toml` rather than repeating the version in
the workflow: a pinned toolchain CI disagrees with produces replay differences that
are not bugs.
