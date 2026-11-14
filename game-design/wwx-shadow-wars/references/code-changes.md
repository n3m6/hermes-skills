# Changing wwx code (not just the design docs)

Applies to `/home/faraz/repos/wwx` (`promunb/wwx`, ssh host alias `github-wwx`).
The repo is the design's source of truth; `docs/design/` is the owner's prose — do not
edit it unless asked, and never invent a `W-` ruling (the register is
`docs/design/00-open-questions.md`, ruled by the owner).

## The gate (all four must be green before claiming done)

```
cargo fmt --all
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace --no-fail-fast
bash tools/gate.sh          # ends in 'gate: ok'; runs deps + determinism + tests +
                            # content validate + a 1200-month replay + the stored campaign
```

`tools/gate.sh` runs the first three itself, so a single `gate: ok` line proves all of it;
re-run it *after* the tree stops changing, because a co-agent editing the same tree can
leave it red between your runs.

## Determinism, which is what actually bites

- Core state changes move the hash. The tag lives in `crates/core/src/sim.rs`
  (`wwx-truth-vN`) — bump it and hash the new fields in handle order, then re-run the gate.
  Hashes that must be updated with it, in this order:
  1. `cargo run -q -p wwx-cli --bin wwx -- play --seed 3 --campaign tests/replay/first-slice.json < tests/replay/first-slice.play`
     (regeneration command is documented in `tests/replay/README.md`), then
  2. `cargo run -q -p wwx-cli --bin wwx -- campaign tests/replay/first-slice.json`
     → updates nothing, tells you the new hash + months + decisions,
  3. `wwx autoplay --seed 20260921 --months 1200` for the century hash.
  Write both into `tests/replay/README.md` and `docs/status.md`.
- New randomness appends a `Purpose::new(0xNNNN)` in `crates/core/src/rng.rs`; never
  renumber, and draw only when the mechanic is actually live (a conditional draw shifts
  every campaign's stream and the stored fixture moves for no reason).
- Do not add a phase to the content phase table without checking `crates/content`'s
  validator tests; hang a pass off an existing phase's `run()` instead.
- `cargo test -p wwx-core --lib`, not the workspace, while iterating.

## Places that must agree when a command or view field is added

`crates/core/src/command.rs` → `crates/protocol/src/message.rs` (`CommandDto`,
`PROTOCOL_VERSION`) → `crates/session/src/session.rs` → `crates/cli/src/commands.rs` →
`crates/cli/src/play.rs` (catalog, `parse`, `apply`, `help`, dossier). View changes:
`crates/projection/src/view.rs` (`VIEW_SCHEMA`) plus `crates/cli/src/ledger.rs` for any
new `LedgerKind`. Test fixtures construct `SimConfig` literally — a new field there
breaks `crates/core/tests/*` (`programmes.rs`, `attribution.rs`, `contracts.rs`,
`scripts.rs`, `determinism.rs`) compile-time, which is cheap to find with
`cargo check --workspace --all-targets`.

## What the owner expects in the reply

Every file touched, the final test count, the gate line, the new hashes when the fixture
moved, and every design decision the design did not state (those also belong in
`docs/status.md` → "Open implementation decisions"). Commit only when asked; the message
style is a lowercase title with the citation (`(... §16.2.3)`), then long `CODE.` /
`WHY THE HASHES MOVED.` paragraphs citing §-numbers, and a closing test-count line.
