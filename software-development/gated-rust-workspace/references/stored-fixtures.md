# Stored fixtures as gates

A golden artifact CI replays: one input, one expected output, and a hash chain
between them. This is what defends behaviour that a change could alter without any
unit test noticing. Worked example: `tests/replay/` in `~/repos/wwx`, where a played
240-month campaign is replayed month by month as the gate's last step.

## What goes in the file

- the **seed** every draw descends from;
- the **content fingerprint** it was played against, so a fixture cannot be silently
  replayed against a world it was not played on;
- the **input stream** — the decisions a person made, in order, each tagged with the
  step it was made in;
- a **hash of the state after every step**, plus the final hash. Per-step hashes turn
  "the century differs" into "month 137 differs": the difference between a bisect and
  an afternoon.

## What must NOT go in the file

Anything the seed plus the content already determine — an opponent's moves, derived
values, the state itself. Storing them hides a non-determinism: the fixture would
replay its own copy of the opponent instead of re-deriving it, and stay green while
the opponent drifted. A campaign that has to store the enemy's moves is a campaign in
which the enemy is not deterministic.

## Recipe

1. **Play it through the real interface**, not a test-only path, and have that
   interface write the artifact. Commit the *input* script that produced it beside the
   artifact — a playthrough should be readable as the thing a person did, and a
   generated JSON alone is not.
   - **One recorder writes both the machine file and the human transcript**, from the
     same decision stream: two generators for two views of one playthrough drift, one
     generator cannot. Keep the recorder as an `#[ignore]`d test of the CLI crate
     (`cargo test -p <cli> --test record -- --ignored`) with a scoped
     `#[allow(clippy::print_stdout)]` because its output is the deliverable; the
     `#[ignore]` is what keeps the gate from rewriting the fixture under it.
   - **Verify the pair by round-trip**: feed the human transcript back through the
     binary into a throwaway file and compare the two JSON files field by field. A
     command that exits 0 proves nothing; identical parsed files prove the transcript
     *is* the campaign.
2. **Regenerating is a deliberate act.** Put the exact regeneration command in a
   `README.md` next to the fixture, and state in the commit message which change
   legitimately moved a hash — including, explicitly, when *nothing* moved because the
   file is new. A golden file that moves silently is the gate switched off.
   - **A change to the hashed state moves *every* hash in the file.** The fixture
     diverges at step 0, and so does every command whose output quotes a state hash —
     including the plain long run that other documents cite. Re-run them, re-measure
     every number a doc repeats (the fixture's own table, the status doc's test count,
     line counts, hash), and correct the docs in the same change.
   - **Prove it was a schema change and not a behaviour change.** After regenerating,
     compare the fixture's *input stream, verdict and scoreboard* with the previous
     file: identical means the hashes moved because the hashed shape grew, and saying so
     is what makes the regeneration reviewable. If any of the three moved, behaviour
     moved and that needs explaining before the new fixture is stored.
   - **Localise it yourself when the input stream DID move.** Copy the old transcript
     aside before regenerating (`cp <fixture>.play ~/.hermes/cache/scratch/old.play`),
     regenerate, then `diff` the two: the first differing line is the month a decision
     changed, which is where to start reading.
     - **Per-step state hashes cannot localise.** A hashed-shape change is written in as a
       domain separator (a version tag bumped alongside the new fields), so *every* step's
       hash differs from the first step onward and the hash diff says only "after the
       change". The decision transcript is the localisable artefact; the hashes are the
       alarm, not the compass.
     - **Isolate by neutralising one call.** With the divergence month in hand, disable
       the single call you suspect (a one-line revert, uncommitted), re-run the recorder,
       and compare the outcome counts: if the stored result returns, that call is the
       cause. A diffs-only reading of a collapsed campaign tempts you to retune values;
       the disable-and-replay test names the one line at fault.
   - **The recorder's own policy is part of the probe, and it is deliberately crude.** The
     transcript's decisions come from a fixed policy inside the recorder — it takes every
     action that appears available and never declines a thin one. Tuning that policy until
     the acceptance items pass is test-tuning, not a fix: verify it actually plays better
     first and revert it when it does not (one such "improvement" cost the stored campaign
     15 of its 26 networks and was reverted, with the reasoning written into the fixture's
     README rather than into the test). When a rule change makes the stored line *worse*
     rather than refused, that is a finding about the mechanic: report it, record the new
     scoreboard with its cause in the same change, and never re-record silently. Expect the
     stored line to get harder as the mechanics bite — a fixture that only ever wins is not
     probing anything.
   - **A new random purpose must not shift an existing draw.** Appended, and drawn only
     when the new mechanic is live, a purpose leaves centuries that do not use it
     byte-identical — the unchanged scoreboard above is the evidence that held.
   - **An additive content change moves the fingerprint with no rule change at all.** Adding
     one value to the content dataset invalidates a fixture that records the fingerprint it
     was played against, and the replay exits non-zero saying which fingerprint played it and
     which is current — that is the fixture doing its job, not a broken fixture. Regenerate,
     then confirm with `git diff` that **only** the recorded fingerprint line changed and the
     project's long end-to-end run still prints the same hash: that pair is what separates
     "the content grew" from "the behaviour moved", and it is the sentence the commit message
     owes. If anything else in the file moved, a rule moved with it.
3. **Add it to the gate as its own step**, after the existing end-to-end run:
   `cargo run --quiet -p <cli> --bin <bin> -- campaign tests/replay/<fixture>.json`.
4. **Read numbers out of the artifact, never from memory.** Any count that appears in
   a README, a status doc or a commit message is loaded from the file (`json.load` +
   print) or copied from tool output. A scoreboard line is three numbers away from
   being wrong in a way nobody will check.
5. **Choose a seed that exercises the ending you must prove.** Verify the branch is
   reachable *before* storing the fixture: a scripted opponent can resolve the problem
   on its own, so the ending may be unreachable at a seed that looks perfectly
   reasonable. Record why the chosen seed is not the default, in the file's README.
6. **Write the acceptance test against the replayed world, not the artifact's summary
   of itself.** Load the input stream, replay it in-process, and observe the world as
   it goes; the artifact's own scoreboard is a claim, the replayed world is evidence.
7. **Parse by hand when the crate's dependency budget forbids a derive.** A versioned
   `serde_json::Value` reader with a small `field`/`number`/`string` helper set is
   short, costs no dependency, and reports a missing field by name.
