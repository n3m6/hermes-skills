# Recurring bug classes in simulation/strategy code with a presentation layer

Each entry is symptom -> mechanism -> where to look. Check these before reading broadly; in practice
they account for most of a defect report.

1. **A value that changed under a fixed date; a reading fresher than its own timestamp.**
   Mechanism: one attribute assembled from two sources — the *value* from authoritative state and the
   *confidence/timestamp* from the instrument that is supposed to have observed it. It is both an
   inconsistency and a leak: the observer sees a live value through a channel that has not looked.
   Fix shape: one reading — value, confidence and date taken from the same observation, stored where
   the phase that took it is allowed to write, refreshed only when contact actually happened.
2. **A date/month that is wrong by a constant offset.** Mechanism: a raw internal tick rendered as a
   user-facing month (or a UTC/non-UTC mix). Find the one display that skips the conversion helper.
   Watch for a deliberate two-convention split — fix the crossing display, not the split.
3. **A confirmation's arithmetic that does not match the ledger.** Mechanism: a rate/price helper
   computed from the verb or product definition instead of the current state ("stop" subtracting a
   charge that is not being paid). Fix by consulting the live rows, the way the sibling path already
   does.
4. **A counter reporting zero against visible events.** Mechanism: the counter sums one event/record
   kind, and some producer path never writes that kind — the mutation happened, the journal entry did
   not, because journalling belonged to the caller. Enumerate every producer before trusting a count.
   The mirror-image failure reads HIGHER than the events: two producers each write a record for the
   same event (the action, plus every process that died with it), so the count must be of distinct
   events — key it on (subject, timestamp) — not of records.
5. **A sentence that asserts a state or cause it never checked.** Mechanism: a hardcoded clause whose
   data came from an empty collection ("nothing stands here" because no action was offered, not
   because nothing stands). Derive the sentence from facts the function holds, and branch on the
   cases that actually differ.
6. **A warning whose advice cannot be followed.** Mechanism: advice text with no precondition —
   telling the user to undo something already undone, or to perform an action that cannot succeed
   from their state. An alert must be an order the user can carry out; where nothing can be done,
   state the fact instead.
7. **A batch/long run that steps over a condition it should have stopped for.** Mechanism: the stop
   predicate keys on *freshness* (the reading is stamped this tick) rather than on the condition
   *becoming* true, so a reading stamped when the instrument last looked can never fire. Check
   whether a separate "was it already known" guard already prevents re-firing — if so the freshness
   term is both redundant and harmful. Such a guard has the opposite failure, and it is just as
   silent: if it asks whether ANY earlier reading about the subject was actionable, an episode
   resolved months ago suppresses the next, genuinely new one for ever. The guard needs the evidence
   of resolution (the record of the user having dealt with it), not the existence of history.
8. **A declared target or schedule that is impossible.** Mechanism: the request is validated against
   nothing, so a threshold above the achievable cap is accepted. Validate against the binding
   constraint at declaration time and refuse naming the cap.
9. **A threshold comparison that contradicts the number printed next to it.** Mechanism: the
   comparison uses raw precision while the sentence uses the rounded value, or the code conflates two
   different quantities (a level with a tier/rung). Compare the same quantity the sentence shows.
   Both sides must come from the *authoritative* arithmetic, because a count taken from displayed
   precision promises a step the authority never takes: an authored decimal rate often has no exact
   binary form (a 3% step on a power-of-two fixed-point base, say), while the threshold it is
   compared against is exact — so the displayed value appears to cross a month before the stored one
   does. Derive every count from the authoritative units through one function that the display and
   the predicate both call.
10. **An alert that repeats unchanged for years.** Mechanism: the alert block is rebuilt every tick
    from the view, and "say it only when it changed" needs memory of what the user was told. Put that
    memory where the phase is allowed to write (often the authoritative store, not the belief/fog
    store) and suppress the unchanged case at the source, not at the print site.
11. **A comparison drawn across incomparable subjects.** Mechanism: the "last attempt" / "previous
    run" record is kept PER ACTOR rather than per subject, so a failure in one place is compared
    against a success somewhere else with near-equal numbers, and the difference that actually
    decided it (a different regime, a hidden adversary present, a different price) is omitted. The
    comparison teaches a false lesson, which is worse than printing nothing. Key the record by
    whatever the comparison holds constant, or make the line name the difference it is glossing over.
    The same report usually adds that the printed deltas do not add up — that is the neighbouring
    rounding defect and a separate fix.
12. **A cause attributed from evidence about the wrong subject.** Mechanism: the evidence lookup is
    scoped to the PLACE (any record mentioning that country/entity in the window) instead of to the
    subject whose change is being explained, so an event about the observer's own side gets printed
    as the cause of the counterpart's move. Scope the lookup to the subject's own terms, and print
    the honest "nothing we did explains it" otherwise.
13. **One sentence generated in several places, each written for the common case.** Mechanism: the
    same phrasing exists in N generators and every one of them describes the majority object, so a
    rarer type (a passive variant, a holding, a media asset) inherits a claim that is false for it.
    When a line must read differently by type, enumerate every generator first, then collapse them
    into one renderer keyed on the object's type — a sentence that two screens both print belongs in
    one function.

Also seen in the same family: a headline that hardcodes a narrative the scenario does not support
(the state was never in the bloc the sentence names) while the detail line — built from the world's
own recorded sentence — is correct. Prefer the recorded sentence; hardcoded narrative is where
precision goes to die.
