# Interface legibility (often the actual deliverable)

Depth for the SKILL.md section of the same name: the failures that make a screen unable to say what
happened and why. The always-on rules stay in SKILL.md; this is the case detail and the worked numbers.

The definition of done usually includes some form of *a human can tell what happened and why*. That is a
build requirement, not polish, and these failures cost the most:

- **A renderer with a cap silently drops the rest.** A dispatch or feed that takes the first N records
  of a period and prints no "and N more" line makes the newest fact invisible exactly when the period
  was busy. Measured on the worked example: 1 of 4 ladder messages and 0 of 8 loss records ever reached
  the screen. When you add a fact, find where the interface slices the list, and prove visibility by
  capturing a run and grepping it — never by reading the code path that writes the record.
- **An enum that merges the player's choice with the world's coercion cannot answer "why".** One value
  meaning both "you let it go" and "you could not pay" makes the reason unrecoverable from the screen
  even though the ledger holds it. Give the coerced case its own value, or carry a reason beside the
  state, at the moment it is written.
- **Publish the rule's own verdict instead of recomputing it in the interface.** When a screen must say
  why an order would be refused, add a read-only function in the core that shares the constants the
  world itself tests (the same threshold constant), read it off the observer's own store, and let the
  interface render why. The screen can then say "not yet" where the world would accept the order and
  never the reverse; a rule recomputed in the projection is a second definition that will drift. Show
  the preconditions — never an odds estimate the draw may contradict.
- **A screen may only read what the observer is entitled to know.** Where the engine keeps the world and
  what actors *believe* in separate stores, a display path that reads the world store is a fog leak
  through the interface instead of through a number — and so is a plan or a doc that calls another
  actor's fact "public". Read the belief store, print a believed value with its confidence, provenance
  and date, render a reading the observer does not hold as unknown, and make any derived judgement
  resting on it answer *cannot say* rather than banding a guess. Check how the engine's own projection
  already treats that field before building on it: its verified/believed/unknown split **is** the fog
  rule, written once, and a plan written before that check can be wrong about what is public.
- **If no channel produces the reading the screen needs, the missing channel is a mechanic, not a
  display bug.** Filling the gap from the world store is the leak; the fix is a producer, registered and
  ruled like any other (worked example: a standing agent network reads the country it sits inside, at a
  confidence equal to its penetration, and reports nothing at all once it has been turned). Say so in
  the commit message and in the project's decision register, and give any judgement derived from the
  reading a third answer — "cannot say yet" — for when the reading is absent.
- **A filter that is too tight reads as a rule.** When the interface offers no option the fiction
  plainly wants, probe the engine before writing a design story: type the command by hand and see
  whether it is accepted. If the world records it, the defect is in the interface's catalogue. The
  classic shape is a decision list gated on the actor's *agents* in a place, while instruments bought
  *in* that place need no agent at all — so losing an agent silently removes every option but "abandon".
  Keep two sets (what needs an agent, what does not) where the catalogue is built, and check the mirrored
  "no agent here" entry still tests the agent rather than membership in the catalogue.
- **A new block prints when it is the news of the interval just run, not on every screen thereafter.**
  A report that repeats for the rest of a century is exactly the "warnings became permanent noise"
  complaint it was written to answer. Gate it on the interval the player just advanced through, give it
  a reprint command, and let the standing copy state its own age so it is never read as this month's
  news. Where the mechanic resolves by a draw, the block reports the terms it held and says outright
  that it cannot separate good preparation from bad luck — inventing a cause is the engine lying through
  the interface. An estimate the model does not support is worse than no estimate: when a rate is zero
  or points the wrong way, print a dash or drop the clause.
