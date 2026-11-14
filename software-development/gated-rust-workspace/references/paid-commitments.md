# Paid commitments: what happens when a bill cannot be paid

A sim whose holdings, services or bought actors cost money a month has a failure path that
is built last and described least, and it is where the money system becomes a decision.
Worked example: `~/repos/wwx` (operations, holdings, kept-up services, bought actors — four
books, four words for the same event).

## Decide the shape before you write it

| Book | Word for the loss | What else happens to it |
| --- | --- | --- |
| in-flight operation (a cost a month) | `aborted` | no charge; the infrastructure it ran through survives; no extra cost |
| finished holding (an upkeep) | `dropped` | same — no burn, no penalty |
| kept-up service (an upkeep) | lost, removed | whatever it produced (beliefs, files, evidence) survives |
| bought actor (an upkeep) | lost, removed | the actor is gone from the world |

- **The check is `budget < price` — no partial payment, ever.** Money cannot go negative,
  and every debit sits behind an affordability check; a saturating subtraction is the
  belt, not the policy.
- **An order you cannot afford is refused, not taken into the red** — and the refusal names
  the price and the balance (`"not affordable: a network costs 1 units, and 0 is all there
  is"`). A bare "refused" is a bug report waiting to happen.
- **Deliberately stopping payment must be gentler than being unable to pay.** An actor you
  stop funding is kept and decays; one you cannot pay is gone. If both are the same event,
  the player's own choice and the world's coercion are indistinguishable on screen.
- **Loss is not punishment, unless you decide it is.** Settle explicitly whether an unpaid
  commitment leaves consequences behind (evidence, a defection, a scandal). Most designs
  say no; adding them silently is a design change, not a bug fix.

## The order money is spent in is a mechanic

Income lands first, then commitments are paid in a deterministic order — and which order
is what the player actually feels:

- by book, in the tick's phase order (in the example: the operation/holding pass, then the
  kept-up services, then the bought actors, all inside one phase);
- within a book, in **start or creation order**, so the oldest commitment is safe and the
  newest is the first to go.

Write both consequences down: a bought actor can be lost because an operation was paid
first, and "the newest thing is the first to die" is a rule the player only discovers by
losing something. Also record whether the path is *tested*: in the worked example no bill
was ever unpayable across 240 months, so the behaviour is a reading of the code rather
than an observed run — say so rather than implying it is exercised.

## Verifying any of it

- Dump the run's records and grep for the exact detail strings; count occurrences per
  month and per cause. Never report a cause the records do not name.
- Capture the terminal transcript as well: a renderer cap can hide the record from the
  player entirely, in which case the mechanic exists and is invisible.
