# Simulation semantics, guards, fixtures and IO: traps

Failures that no single unit test catches: behaviour that is wrong-but-compiling, guards that
protect nothing, and verifications that report a world that no longer exists. Toolchain-level
failures (`E0502`/`E0592`, `-D warnings`, `cargo fmt` moving anchors) are in `tooling-traps.md`;
the fixture file format and its regeneration procedure are in `stored-fixtures.md`.

## Stocks, thresholds and balance

- **A stock with an authored inflow and an authored decay settles at `inflow / decay`; check every
  threshold that reads the stock against that steady state.** Adding a decay to a pile that
  previously only grew is a balance change to every event that tests the pile's level: at a
  5%-a-month decay and a 1%-a-month charge the pile settles at 20%, so a 40% threshold stops firing
  and the whole ladder reads as dead. Put the steady-state arithmetic in the commit message; if a
  threshold is now unreachable, report it as a finding rather than quietly retuning it.

## Guards

- **Document a grep guard's exclusions inside the script, with the reason.** A test that
  deliberately reads the filesystem (parsing manifests, building fixtures) trips a "no IO" scan;
  exclude that one file and say in the comment that the check is about simulation code.
- **Narrow a guard that fails legal code; never delete it.** "Nobody may write what anybody read"
  flags two phases mutating the same store in sequence, which is intended. Narrow to "read
  **without** writing" and keep a test asserting the legal sequence passes, so the narrowing cannot
  silently become no guard at all.
- **A guard on a helper with two callers must hold for BOTH.** A precondition only one caller
  performs before calling is silently bypassed by the other, and the symptom is a different century
  rather than a crash or a compile error. Put the cooldown/armed/once-per check inside the shared
  function, and search its call sites (`search_files`) whenever you add one — the new caller is
  usually the one you just wrote.

## Tick, phase and store contracts

- **Decide the phase before choosing the API.** In an ordered tick an early phase (the one that
  applies orders) may write world state and the journal but may neither read nor write the belief
  store, and the guard panics rather than warns; a helper written against the belief store and
  called from the early phase panics, and the fix is to move the caller, not widen the contract.
  When two callers need the same *announcement* but only one may write a belief, share the
  state-plus-journal part in one function and leave the belief to the phase that owns beliefs — two
  copies of an announcement drift, and the player-facing wording drifts with them.
- **A tick's phases run in the tick the clock advances ONTO, and the player-facing month is not the
  tick.** From tick T, advancing n months runs the phases of T+1..T+n and leaves the sim standing on
  T+n, so standing on a due tick is still the month *before* the thing at that tick fires. Derive
  every expected tick or month in a test (from the project's label helper, or as a difference
  between two ticks); hand-counted constants are where the off-by-one hides. Inside one tick, order
  changes *values* too: entities that take their own monthly turn after a mechanic resolves have
  already decayed what it wrote, so assert the written value minus one step, derived from the
  constants rather than hardcoded.
- **Reconcile a level-of-detail promotion with its parts in the same tick.** Promote the parts,
  recompute the parent from them, and let unmodelled parents grow on their own — otherwise totals
  drift apart within a single tick and the divergence is invisible until someone sums a century.
- **A store that never deletes has no "is this true now?" by default.** Where a correction is a new
  record rather than an edit, every decision that reads the store must take the *latest* record per
  key: reading "any" record keeps offering an action for a state a later record already resolved.

## Tests and fixtures

- **Do not assert authored numbers exactly once the tick has run.** Per-tick growth has already
  moved the aggregate by the time the fixture looks; assert *shares/proportions* within a tolerance,
  or drive that test with a zero-growth content fixture.
- **Narrow an absence assertion when a new producer legitimately fills it; never delete it.** A
  blanket `beliefs(x).is_empty()` guards "nothing reached this actor from someone else's mind";
  once the actor gains a legitimate reading of its own, rewrite it as the narrowed claim (every
  entry is this actor's own observation of the thing it is inside) with a comment saying why it is
  no longer `is_empty()`. Assert the *derivation*, not a literal (`reads == the source entity's own
  value`, never `== 0.5`) — a literal passed in by hand is how a reader-of-the-wrong-store bug hides
  as a rounding difference.
- **Start arithmetic from the fixture's own conditions.** A hand-built world in a unit test is not
  the world the open path builds: whatever the loader grants at open (an opening budget, a
  scenario's starting assets) is absent from it, so expect the first assertion to be wrong by
  exactly that amount if you assume otherwise.

## CLI and IO

- **A REPL that buffers its transcript looks hung, and piped input hides it exactly.** A loop that
  collects output in a `String` and prints it after the loop ends is perfect under `prog < script`
  (EOF flushes everything, so reading the transcript tells you nothing) and prints nothing on a
  terminal, where the prompt the player waits for sits in an unflushed buffer. Write every chunk to
  a sink as produced and flush before the loop reads again; verify with a silent stdin
  (`sleep 10 | timeout 4 prog` must already show the first screen and its prompt when the timeout
  fires), and make the regression test assert *when*, not *what* — a `Read` impl recording how much
  the sink held at the first line request must see a non-zero count.

## Verification by captured run

- **Loop seeds before building a test on one run, and remember the queue.** The same script is
  refused, killed or succeeds depending on the seed: loop seeds and search for the marker the outcome
  prints, pin the seed in the test's comment, and assert the outcome's *shape* rather than a value a
  tuning pass moves. Queued orders resolve when the clock advances, not when they are submitted, so
  an input script must advance (even a blank line) before reading the outcome screen. Read the
  refusal text rather than your expectation: it names the precondition actually tripped and
  separates a refusal from a rule you never reached.
