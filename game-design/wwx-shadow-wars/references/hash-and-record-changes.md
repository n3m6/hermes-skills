# Changing a rule, and keeping the stored evidence true

Every rule change moves hashes, and four artefacts quote them. The order that works:

1. **Make the change**, then `cargo fmt --all && cargo build --workspace`. Bump the truth
   hash version string when the *truth schema* changed (`wwx-truth-vN` in
   `crates/core/src/sim.rs`), and `VIEW_SCHEMA` when the view's shape changed
   (`wwx.view/N` in `crates/projection/src/view.rs`).
2. **Run the suite**: `cargo test --workspace`. Expect
   `item_1_the_campaign_replays_month_by_month` and its siblings to FAIL on old hashes —
   that is the designed signal.
3. **Re-record**: `cargo test -p wwx-cli --test record -- --ignored --nocapture` rewrites
   `tests/replay/first-slice.{json,play}` and PRINTS the campaign's own facts (verdict,
   scoreboard, final hash, the refusals by message and first month). Read them from that
   output; never reconstruct them from memory.
4. **Prove the transcript still reproduces**: `wwx play --seed 3 --campaign /tmp/regen.json
   < tests/replay/first-slice.play`, then diff the regenerated JSON against the stored one.
5. **Check whether the campaign's decisions still make sense.** A pace or price change
   can make a stored decision refused (v1.11: the party needed 24 months to arm, so the
   coup order at month 24 became a refusal and the campaign ended LOST). The decision
   stream lives in `crates/cli/tests/record.rs` — move the order to the month the world now
   supports and say why in a comment. A test that fails only because the *player* moved
   too late is a real finding, not a nuisance.
6. **Update every measured number**: `tests/replay/README.md` (fingerprint, final hash,
   scoreboard, the month-by-month narrative), `docs/status.md` (the measured table, the
   crate line counts, the acceptance line), `docs/first-slice.md`, and the W-item in
   `docs/design/00-open-questions.md`.
7. **`bash tools/gate.sh`** — green, then commit. The commit message has to say which
   change legitimately moved the hash; a golden file that moves silently is the gate being
   switched off.

Line counts:
`for d in core content projection protocol session cli server; do find crates/$d -name '*.rs' | xargs cat | wc -l; done`,
or compute them with pathlib in `execute_code`.

## Evidence beats assertion

For a mechanic change, add or extend a test that would FAIL on the old code, and say in
its doc comment which assertion does that. `crates/core/tests/pawns.rs` is the model: it
builds its own world, funds the party through the command stream, and asserts costs the
old code had no way to charge (one `CoupFailed`, one `Blowback`, -5% home stability, the
4 units, with the month's income and the attempt's price named in the arithmetic).

## Legibility is part of the mechanic

The screen's vocabulary is what makes a mechanic answerable: `EndReason` exists so the
dossier can say *why* a programme stopped; the dispatch ranks the month so its three
items are "what changed"; `ledger` exists so nothing the world knows lives only in a
file. When a fix is "the world knew and the player's document did not", it belongs in
this list, and the register section `What the screen could not say` is where it is
recorded.
