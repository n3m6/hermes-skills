# Defect report → grounded fixes — procedure and evidence rules (Mode B)

## Procedure

1. **Anchor every quoted symptom in the code before planning anything.** Reports quote what the user
   saw, and those strings are usually literal in the source:
   `grep -rn "<the quoted phrase>" src/ --include=*.rs --include=*.py` (or the repo's language). One
   call turns "the screen contradicts itself" into a file, a function and a mechanism. A plan written
   from the symptom alone names no mechanism, and an implementer with zero context cannot act on it.
   If a quote is not literal, grep the distinctive fragment, then the surrounding words. **Search with
   word boundaries** (`rg -w`): a bare substring makes the count meaningless ("tribute" matches
   *contribute*), so a hit count reported from one becomes a fabricated finding. When the question is
   "does this project even have concept X?", the word-boundary sweep of source and docs is what
   settles it — settle it there before reporting the concept absent or present.
2. **Ask for the artifacts you do not have.** Transcripts, recordings and saved inputs often live on
   the reporter's machine, not this one. If a step needs a word or a number the report does not give,
   ask for it — do not reconstruct it, and never write a plan step that depends on it.
3. **Classify each finding** (table below). The classification decides both the record and whether
   code may change at all.
4. **Confirm the mechanism or mark it unconfirmed.** Read the code path end to end. Where the
   mechanism is not visible, write the task as *diagnose first*: the exact repro, the numbers to print
   side by side, and which component is the authority.
5. **Plan in the reporter's priority order,** and state what is deliberately out of scope. Close by
   aiming the next round at what this report could not exercise.
6. **Answer "what does it actually do?" from the code path, and separate designed from built.** Read
   the function that decides it, not the document that describes it, and cite file:line for each step.
   A concept in the design is not evidence that it is built, and the design's own amendment or trap
   list is the evidence that it is deliberately not. The honest answer usually has two halves — what
   exists in code today, and what is designed and unbuilt — and both belong in the reply.

## Classification, and what each class gets

| class | test | what it gets |
| --- | --- | --- |
| **Defect** | the code does not do what the spec/design already says | fix it; the record is the commit message |
| **Behaviour choice** | the code does something the spec never specified (a rule invented in passing) | a registered item, ruled by the owner BEFORE any code |
| **Open design question** | the report says "this establishes X, not proof of Y" | an item on the register, left open; do not close it in a commit |
| **Trade-off already accepted** | the cost was ruled on knowingly | nothing; do not relitigate |

A repo whose stated rule is "code may not silently redefine the design" makes this split load-bearing:
shipping a behaviour *choice* as a bug fix is the cardinal sin, and it is the easiest mistake to make
because a choice and a defect look identical from the outside.

## Evidence rules

- **Never present a guess as a diagnosis.** A wrong mechanism in a plan costs a whole implementation
  round, and the reporter checks. Write "unconfirmed — reproduce first" and say so plainly.
- **Distinguish an inconsistency from a proven leak.** "Value and date disagree" is a consistency
  defect you can fix. "The player can see something they have no instrument for" is a fog/leak claim
  that needs its own argument. Report the stronger claim only when the code path proves it.
- **Name the authority for every disagreement.** When two components print different numbers, the one
  that owns the state (the simulation, the database, the charges) is right; the renderers are wrong.
  Say which is which per task instead of letting the implementer pick.
- **Repro before repair** for anything numeric or timing-dependent: give the seed/input, the months or
  iterations, and the exact values to compare. "Test it works" is not a step.
- **Verify a "no longer says X" fix by absence, in a captured run.** Run the real thing end to end with
  the whole output kept in a file, assert the count of the quoted phrase is zero, then read the block
  the report complained about in full. Looking at a screen and concluding is not verification, and a
  line truncated while inspecting it hides the very clause under test.
- **Check what the project's fingerprint does NOT cover.** Where a state hash, golden file or snapshot
  is quoted as proof that "nothing moved", confirm the artefact you changed is inside it. A journal,
  log or stored record the state hash omits can change while the hash stays byte-identical — and a
  fix to what is *recorded* is exactly that case — so make both claims separately: the world did not
  move, and the recorded evidence did (or did not) change.
- **A phrase naming a neighbouring price or phase is the usual source of a phantom defect.** A report
  saying "it promised one a month and charged nothing" has often read the object's *other* price (an
  upkeep, a completion fee) as the running rate. Reproduce before repairing, and let "no defect" be
  the reported outcome when every number agrees.

## Plan shape for this class of work

- **Facts first.** The plan's context section carries the measured baseline (hashes, goldens, test
  counts, version constants) read from the last real run — not from memory or an old note.
- **Register/IDs first** if the repo has an item register: create the items in Phase 0, before code,
  so later commits can cite them.
- **One baseline-moving change per commit.** When several steps each move a recorded baseline (state
  hash, golden file, snapshot, fixture), splitting them is what keeps "this change moved the numbers"
  answerable. Batched, it becomes unknowable.
- **When the report calls text redundant, fix the list's SHAPE before its wording.** A list that
  prints the same authored block once per row is a rendering defect: group the rows by the entity that
  owns the block, print the block once, and let each row carry the fact that distinguishes it. Check
  whose words the block is first — if the owner already ruled on that authored text, trimming it to
  satisfy a legibility report is a silent design change, and the shape was the defect all along.
- **A presentation-only fix must be provably inert**: identical hashes/snapshots before and after, and
  that identity belongs in the commit message as the evidence.
- **A layout change to a numbered list must keep the numbers pointing where they pointed.** When the
  reporter also *types* the identifier — a row number, a menu index, an id — renumbering silently
  re-aims every habit they have built, and no hash or snapshot can see it. Require a test that each
  index still resolves to the object it named before, and that every entry is still reachable by its
  own name.
- **Say what is out of scope** (the repo's own trap list) and **what the round could not exercise**,
  so the next round aims there instead of re-confirming.

## Anti-patterns

- Planning from symptoms; a plan that never names a function.
- A symmetric list of every finding with no verdict about which one is the real defect.
- "Fix the tests" as a response to a failing test that encodes the old behaviour correctly.
- Silently implementing a design choice the reporter only described.
- Reproducing the reporter's words as fact, including their guesses at cause.
