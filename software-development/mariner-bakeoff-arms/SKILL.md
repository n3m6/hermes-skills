---
name: mariner-bakeoff-arms
description: Use when running a mariner spikes/bakeoff measurement arm.
---

# Running or extending a mariner bakeoff arm

Class of task: execute a spike plan whose measurement half lives in the `mariner`
spike harness — add an arm (`spikes/bakeoff/src/arms/<name>.rs`), register it, run
it, and land a results directory plus findings. Repo: `~/repos/mariner`
(`silentsea-xyz/mariner`); the plan it executes is a `starpath` roadmap document.

## Layout and the one rule that everything rests on

- Arm: `spikes/bakeoff/src/arms/<name>.rs`, registered in `arms/mod.rs` and as a
  `Command` variant in `main.rs`. Results: `spikes/results/<name>/`, one CSV per
  stage plus `FINDINGS.md`. Register the arm in `spikes/README.md`'s spike table
  **and** in its "Results and scratch space" section.
- `measure_refgkr` proves and verifies before it reports a timing; use it for every
  row. Never report a number for a circuit you did not verify.
- **Field multiplications are exact and host-independent; wall clock is not.** State
  the verdict in field multiplications and read every ratio against a denominator
  measured in the same run, on the same host, the same day.

## Same-day baselines, and how to tell a circuit change from an accounting change

Quoted absolute figures from an earlier spike's CSV are **not** denominators. When
your re-run disagrees with a quoted number:

1. Compare `gates_mul` / `gates_add` / `gates_relay` / `layers` against the old CSV
   for the same variant and `k`. Identical gates + a constant field-mult ratio over
   several `k` means the *prover's accounting* changed, not the circuit.
2. Attribute it from git: `git log --oneline --date=short -- spikes/bakeoff/src/refgkr.rs`,
   then `git show <commit> -- spikes/bakeoff/src/refgkr.rs | grep -E '^[-+].*(mults)'`.
   One such commit moved `self.mults += 3 * half` to `2 * half` and shifted every
   circuit's field multiplications by 0.852 while leaving gate counts identical.
3. Report the shift as a finding with the commit id, and read the gate on the
   same-day numbers. Ratios survive an accounting change; absolutes do not.

## Building a circuit block on top of a gadget

- `Builder` is straight-line: `input`, `mul`, `lc`, `fused`, `relay`, `pow5_shifted`,
  `assert_zero`, `assert_equal`, `expose`, `lift_to`; `finish()` lowers to layers.
  Gadgets expose `build_into(&mut builder, …)` so a block appends to the same
  circuit; a gadget that keeps its wires private means *structural* composition —
  build the block from the same seeds and label the rows `structural`, as
  `spike-o`'s composite leaf does.
- **`LayeredCircuit::is_satisfied` reads slot zero of the LAST layer.** The
  assertion accumulator is that slot only while the accumulator is the deepest
  object in the circuit; if any other gate is deeper, the probe reads that gate and
  reports a false negative. Symptom: a correct block "is not satisfied" at larger
  `k` and satisfied at small `k`.
- Fix: assert at the top. `let top = builder.max_depth();` then
  `builder.assert_equal(builder.lift_to(a, top), builder.lift_to(b, top))`
  (`Builder::max_depth` was added for this). It costs a relay per layer of distance,
  so say on the row that the placement is an upper bound. The probe's precondition
  is written down nowhere else in the harness.
- **An appended block's cost depends on where its gates land.** The same
  construction (a width-3 Poseidon2 sponge, one permutation per two signatures)
  priced 13,312 field multiplications per signature standalone and 1,092 as the
  delta of the batch's own seed expansion — a 12× instrument discrepancy. Price a
  term the way the object it belongs to prices it, cross-check the two shapes, and
  report a bracket rather than a point when they disagree.
- `arms::l::{occupancy, top_slope, copy_uniform}` are `pub(crate)`; re-use them
  rather than copying. Report `occupancy` on every sweep row: a layered prover pads
  each layer to a power of two, so a small-`k` point can sit 60% above the line, and
  the local slope between the two largest counts is the estimator a gate reads.

## Deliverable discipline

- Every CSV row carries `status`: `measured` (a verified proof), `derived`
  (arithmetic over measured rows), `reused-census` (someone else's census, its own
  status preserved), `quoted` (a figure from another spike, in its own unit),
  `reading` (a fact read out of a source). Keep them apart in the file order too.
- A stage that reads another spike's census should read the **CSV**, by column name,
  not a typed constant, and match rows on the whole variant label: `-m` also matches
  `keyed-memory`, which silently gave a ceiling the wrong denominator once.
- Two cost models that disagree in sign for one term (GKR field multiplications vs
  R1CS constraints) must never be divided by each other, in either direction.

## Tooling pitfalls that cost real time here

- `read_file` returns each line prefixed with `N|`. Never write that content back
  to a file — it corrupts the whole tree with prefixes (and a truncated read also
  loses the tail). For whole-file surgery use `python` (read/replace/write) inside
  `execute_code`; use the `patch` tool for targeted edits.
- Terminal calls inside `execute_code` may be escalated to a background process;
  long builds and sweeps belong in a `terminal(background=True, notify=True)` call
  with output to a log file, then `tail` the log.
- A release build of `spikes/bakeoff` takes ~3 minutes on 8 weak cores; a full
  control + ceiling + baseline sweep takes ~25. Do not run an unrelated build while
  a sweep is measuring — wall clock is part of the row.
- Commit locally in **both** repos (arm + results + README in `mariner`; register +
  plan verdict in `starpath`), verify with `git show --stat --oneline HEAD`, and
  offer the push rather than assuming it.
