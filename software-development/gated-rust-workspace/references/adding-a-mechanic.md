# Adding a mechanic through every layer

Depth for the SKILL.md section of the same name. The always-on rules stay in SKILL.md; this is the
full sweep, kept because the compiler names none of these extension points.

A workspace of this shape is one straight line — content → session → core ← projection ← protocol → cli
— and a new mechanic travels it in one direction. Work from the inside out and the tree compiles at
every step:

1. **Types first:** the command variant, the entity and the book that stores it, the helper that
   starts/stops it, then the monthly pass as its own module in the systems directory, registered and
   called from the phase that already owns that subject.
2. **Do not add a row to the ordered phase table** for a mechanic. The table is the tick order and its
   contract guard is what keeps each phase's reads and writes legal; a mechanic is a pass inside a
   phase, not a new phase.
3. **Sweep every extension point in one pass**, because each is a place the compiler will otherwise
   find later: the RNG purpose enum, the balance struct (authored values only — inventing one is a
   design change, not an implementation detail), the ledger kinds, the belief attributes and provenance,
   the per-phase context struct, the sim config struct, and the state-hash tag with the new fields hashed
   in handle order.
   - **One authored value, four places, and the compiler only names three.** A new tuning value travels:
     the core's balance struct *and* its `Default`, the content JSON (the value **and** the comment saying
     whether it is authored or the builder's), the validator's authored-vs-chosen lists (a value in
     neither list is a validation error — a *runtime* content check, so no build step finds it for you),
     and the session's `balance_or("key", default)` mapping. Miss the validator and the content check
     fails; miss the session and it does not compile. Adding the value also moves the content fingerprint
     even though no rule moved — see `references/stored-fixtures.md`.
   - **A whole new *store* is more than a field.** In order: the key type implementing the crate's
     `Interned` trait (its `NAMESPACE` is the id prefix content uses), the store on the world struct, an
     arm in the effect applier or the module of the phase that owns the subject, the store hashed in
     handle order with the hash tag bumped, and — if any phase reads or writes it — a matching entry in
     the content-side phase table, whose runtime guard panics on an undeclared store and whose loader
     refuses to open when the declaration and the registry disagree. An unhashed store is a divergence
     nobody sees until it matters.
   - **Content is often already authored for the mechanic you are about to build.** Grep the content
     tree for the effect and attribute names before deciding where to implement: an effect the applier
     currently records as an unbuilt note ("no home in the world yet") is a written-down to-do, and
     giving it a real arm is part of the mechanic, not a follow-up. The applier's `EffectUnbuilt` arm is
     the project's own list of mechanics the data model promises and the code has not delivered.
   - **A precondition the design's data model cannot express is a question, not a local decision.**
     Where the mechanic you are implementing needs a field, a link or a threshold the design never gives
     (an entity that must belong to another entity, a precondition no content value can satisfy), put it
     to the owner with a recommended reading and register the answer where the project registers
     decisions. Settling it silently in code is how the design stops being the source of truth.
   - **A design statement that can be falsified is meant to be.** When the design says a family of rules
     needs no special code and the build finds one that does, the finding is the deliverable: implement
     the mechanic, then register the contradiction where the project registers open decisions — the
     evidence, two or three options, one recommendation — and leave it open for the owner to rule.
     Coding around it silently wastes the test; stopping to ask before the evidence exists stalls the
     build.
   - **When the decision is already the owner's and it is the *mechanism* that cannot work, implement
     the ruled outcome and amend that entry in the same commit.** A ruling can name a mechanism the
     code's own gates forbid (start a clock by seeding a value an existing gate then acts on — where
     that gate only runs for the entities the ruling has just disqualified, so the promised clock never
     starts). The ruled outcome binds; satisfying the letter while the intent silently fails is the same
     failure with worse paperwork, and the register entry is where a later reader finds out why.
4. **Then the boundary:** the wire DTO plus a protocol-version bump, the session translation (and a
   reader for any new content value), the projection with its schema bumped when the shape changes, and
   the CLI's action, parser, catalogue, help, dossier and kind→string table. A published schema number
   does not grow new fields — a consumer that negotiated it cannot tell — so take the NEXT number when
   the old one has already shipped, and correct every document that quotes the version line in the same
   change. Bump the stored-campaign schema when a campaign's *semantics* change, not only when its wire
   form does. Every one of those bumps is a documented version target: write the list down before
   starting and check it off at the end, because the compiler names none of them.
5. **Grep the test tree for the config literal before running.** One new field on the config or context
   struct breaks every hand-built literal in the crate's tests — one compile error per file, one round
   trip each. `grep -rn "Config {"` / `"Context {"` across the repo, fix them all in the same edit, then
   run the suite once.
   - **That cost is avoidable: ask whether the value belongs to an entity or to the world.** A knob on a
     table only one layer constructs (a per-verb cost struct, a per-entity record) lands in one
     construction site and a couple of literals. The same value as a new field on the shared config or
     tick context lands in *every* hand-rolled fixture in the test tree, and each fixture it touches
     stops meaning what its name says. Per-verb exposure as a config field: seven fixtures; hung on the
     verb cost table: three literals and one session site.
6. **Test the rule with its negative control.** Prove the pass by the same world *without* the mechanic
   producing none of its effects — a test that only shows the new path working cannot tell the mechanic
   apart from something else doing it.

## Draws: adding a random purpose safely

- **Append, never insert or renumber.** Purposes are permanent ids because every stored stream is keyed
  by them; inserting one shifts every existing draw.
- **Draw only when the mechanic is live.** A purpose that draws unconditionally changes the stream for
  every run, including ones that never use the mechanic, and the stored fixture then diverges while
  behaviour did not.
- **Derive the draw's entity from what the draw is about** — the pair of handles, the programme, the
  state — so two consumers cannot collide on one value.
- **Let an ordered map give you the ordering.** A `BTreeMap`/`IdMap` iterates in handle order, so "one
  draw per pair, in handle order" is free and cannot drift; a sort of your own is a second thing to keep
  deterministic.
