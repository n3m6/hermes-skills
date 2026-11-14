---
name: phased-plan-execution
description: "Use when running a phased plan with subagents."
version: 1.0.1
author: Hermes Agent (curator)
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [delegation, subagents, plans, verification]
    related_skills: [plan]
---

# Executing a phased plan through subagents

## When to Use

- The owner hands over an approved phased plan (a `/plan` output, or one written for an implementer
  with zero context) and says to execute it: "create subagents and complete each phase", "work
  through the phases", "run the plan", "one subagent per phase".
- The plan's phases depend on each other through shared state - a schema bump, a register, a
  document, the gate's own measured numbers - so each phase must land and be verified before the
  next one starts.
- Any long implementation the owner wants split across fresh contexts so one agent's context does
  not have to hold the whole thing.

Not for: independent parallel workstreams (that is one fan-out of children), or a single-phase task
you would finish yourself in a few tool calls.

Companion to the `plan` skill, which writes the plan and hands execution off. The shape this skill
encodes: one subagent per phase, sequentially; one commit per task; a verification pass at the end
that fixes what the round surfaced.

## The shape in one paragraph

A phase is one child's whole job: it reads the plan itself, so the parent does not have to hold the
code in its own context. The parent owns the bundle, the verification, and the deviation ledger. Do
not collapse the plan into one long agent run of your own, and do not parallelise phases that share
state.

## Procedure

**0. Establish the baseline you can re-derive cheaply.** Whatever the project recomputes in one
command: the test count, a content/build fingerprint, artifact or replay hashes, the gate's summary
line. Record it before dispatching anything. Every child's "this changed nothing" claim is checked
against that baseline, and a claim you cannot re-derive is a claim you can only believe.

**When the plan came from the user's own use of the artifact, register the findings before fixing
any of them.** A report of what went wrong in play (or in production, or on their machine) is a
list of symptoms, and the first phase must turn each into a tracked item - one per distinct question,
carrying the user's own numbers, months and commands - so that every fix commit can cite the item it
closes and nothing in the report is silently dropped or silently merged into something else. That
phase writes no code. Where the report is ambiguous about how many questions it contains, split or
merge explicitly and say which; where a finding is another item's question seen from a different side,
record it under that item rather than inventing a new id.

**1. One child per phase, in order.** Phases that share a schema, a document, a register, or a
migration are sequential by construction: each phase's baseline IS the previous phase's output. Send
phase N+1 only after you have verified phase N yourself (step 3).

**2. Write the bundle.** The plan was written for an implementer with zero context, so the child needs
the facts the plan assumes: repo + branch + the push remote, the plan's absolute path AND which phase
to execute, "load <project skill> first", the baseline values, the hard rules, the commit protocol,
the report format. Template: `templates/delegation-bundle.md`. Write every value in the bundle in
FULL: an angle-bracket placeholder left in the goal text (`<new id>`, `<question>`) is refused by the
dispatch call as an unexpanded template marker, and one that slips through inside an illustrative
format gets written into a committed file by a literal-minded child - resolve the id or name
yourself, then mark any example "format illustration, do not write this literally", and if one is
already in flight, `action='steer'` the correction at once.

**3. Verify every phase yourself before building on it.** The child's summary is a self-report.

```bash
git log --oneline -8                  # the phase's commits, in the plan's order
git status -sb                        # in sync with the remote, nothing local
<the project's gate command> > /tmp/pN-verify.log 2>&1; echo "exit=$?"
grep -E "hash|gate: ok|tests? passed" /tmp/pN-verify.log | tail -4
```

`git status -sb` compares against your *local* ref, so before you tell a user who pulls the branch
himself that a commit is on the remote, ask the remote: `git ls-remote origin refs/heads/main`. The
claim he will act on is about the remote's tip, and a local `origin/main` that was fetched before the
last push answers the wrong question.

Expect the gate green and the numbers the child reported. A presentation-only phase must show the
*previous* phase's fingerprints; a phase that touched persisted state must show new ones and say why.

**When a child dies on its iteration cap, the phase is usually unfinished rather than lost.** The
common shape is the last task complete and gate-green in the working tree but never committed. Treat
that tree as a partial phase: read the diff yourself (`git diff --stat`, then the code diff - do not
take the summary's word for what is in it), re-run the project's gate on it, and only once it is green
commit and push it yourself, in a message that says the orchestrator finished it after the phase's
child ran out. That provenance belongs in the record; a commit that pretends a child finished the task
misleads the next reader. Then dispatch the remainder as a fresh child with the same bundle.

**4. Keep a deviation ledger.** Children hit anchors that moved and make choices the plan did not
anticipate; they must say so in the commit message and their report. Log every deviation, every task
left undone, and every defect the child surfaced on the way - children are the best bug-finders in
this loop because they read the neighbours of the line you sent them to. Do not interrupt the
sequence to chase these: close the list in one pass at the end.

**5. The final pass.** On the real tree, after the last phase: re-run the full gate, walk the ledger,
fix what is fixable, and re-verify. Then **exercise the artifact the report was about, end to end,
and read the lines it complained about in that output** - a green suite proves only that you did not
break what its authors thought to assert. The real run is where a round's remaining defects surface
(a counter that passes its unit test while printing an impossible number to the user). If the
artifact's own stored fixture never reaches a line the round changed - a per-entity view the fixture
never opens, a branch its scenario cannot enter - extend a copy of that fixture: append the missing
step, replay it, and read the line. A changed line only a unit test has seen is not verified, and the
fact that it was never reachable in the stored run is itself worth reporting. Report
per-phase commits, the final measured numbers, what moved
and why, and anything still open. If a fix turns out to need a rule the user owns, do not invent it:
leave it flagged with the options.

Two habits make that pass real rather than ceremonial. **Assert absence, from a captured file**: when
the round's point is that the artifact no longer says something, keep the whole run's output, count
the quoted phrase (zero is the proof) and read the block the user complained about in full - looking
at a screen and concluding is not verification, and a line truncated while inspecting it hides the
clause under test. **Recompute anything the children only asserted**: if a diagnosis rests on
arithmetic (a rounding step, a rate, an off-by-one), redo it in a few lines yourself before reporting
it as fact - a child's mechanism is a hypothesis until your own run agrees with it. **Sweep the
documents for the vocabulary the round deleted.** A round rewrites the words the artifact uses, and
each child amends only the item it was sent for, so the phrases the round removed survive as
current-state claims in other items and docs. Grep the whole documentation set for each deleted phrase
and for every note the round itself invalidated ("this is the user's to rule", written before the
build that answered it; a quoted screen line the build replaced) - zero hits in the code with one hit
in a doc is the shape. Correct each with an amendment marker beside the claim rather than rewriting
the history around it, and call the round done only when that sweep is empty.

**Then dispatch the verified leftover list as one child, with your own evidence inlined.** Once your
probes have turned each leftover into a defect with a location and a measured number, that is a
bundle like any other: the file, the value you measured, the authority to fix against, and the
requirement to change nothing else. Hand it the evidence so it does not re-derive it, make each item
its own commit, and verify that child like any other phase.

**6. Parent's loop discipline.** While a child runs, do not poll its transcript - end the turn with a
one-line status and act on the result when it arrives. You can steer a drifting child mid-run
(`delegate_task action='steer'`) or stop one that is out of scope (`action='stop'`, partial results
still return); use it rather than letting a child finish work you will have to revert.

## Sizing a phase for one child

Budget roughly 5-8 minutes and a few dozen API calls per plan task. Observed: a 7-task phase ran ~30
minutes and ~240 calls; a 1-task phase ~6 minutes; a 3-task phase ~13 minutes. If a phase looks much
bigger than that, split it into two dispatches rather than letting a child run to the edge of its
budget - a child that runs out has its phase half-written and you verify a partial tree.

The number that actually bites is the call count, not the task count: phases that hit the cap did so
around 250 calls whether they carried two items or seven, because reproducing the symptom, reading the
neighbours of the line and re-gating after each item dominate the cost. So cap a multi-item phase at
~4 tasks AND make commit-per-item a hard rule of the bundle: a child that commits as it goes loses only
the uncommitted tail to a cap, where one that batches loses the phase.

## Pitfalls

- **A child's summary is a self-report, not a fact.** "Uploaded", "all tests pass", "hashes
  unchanged" are claims about work you did not see. Verify with the project's own command, and read
  the numbers off your own run.
- **Report your own writes to the same standard: only after they exist.** Telling the user
  "registered", "fixed", "committed" about a document or commit you have not made yet is the same
  unverified claim you refuse from a child, and worse here because he acts on it. Say it after the
  commit, and check the remote rather than your local ref (`git ls-remote origin refs/heads/main`
  against `git rev-parse HEAD`). If you catch yourself having said it early, correct it plainly in the
  next message and make the write - a quiet backfill leaves the false claim standing. And when the user
  says "commit and push" and the tree is already clean, answer with the proof (empty
  `git status --porcelain -uall`, HEAD equal to the remote's tip, and which commit is already up);
  manufacturing an empty commit to look responsive is the worse answer.
- **Never let a child implement a task the plan marks as awaiting the user's ruling.** Children cannot
  ask questions, so a ruling-shaped task will be silently decided if you send it. Carry it as its own
  phase that only registers the question and proposes the options, and say in the report that the
  mechanic is deliberately unimplemented. Rulings that arrive mid-round are the same shape in reverse:
  give them their own phase, record each one in the owner's own words against that item's own id, mark
  which part is now to be built and which parts stay deferred, and keep the item visible until the
  build lands - a ruling is not a build, and a recommendation is not a ruling.
- **"Built in part, question left in writing" is a correct outcome - require it when the honest scope
  cannot close the item.** A legibility fix whose remaining half needs new persisted state, a schema
  field, or a fact the world never recorded cannot be finished by the child; the right move is to build
  the half that is provable, mark the item built-in-part, and state the open question and what closing
  it would cost, in the item itself. Tell children this is expected: a child that cannot see the
  boundary will either invent the missing field or silently drop the half it cannot do.
- **Ban history rewrites in the bundle.** A child's instinct is to amend a commit to fold in a note it
  thought of a minute later, even after the push; if the user pulls that branch himself, a rewritten
  tip strands him on a commit that no longer exists. Amend before the push, make a follow-up commit
  after it, and never force-push - and check the phase's `git log` against `origin` during
  verification, because a force-pushed tip looks locally clean.
- **One commit per task, never one commit per phase.** Batching destroys attribution: if two changes
  in one commit move the same measured artifact, nobody can say which one moved it - which is exactly
  the claim the next phase's "unchanged" depends on. Give each task the plan's own commit message.
  Where the project treats a document as the contract ("the code may not silently redefine the
  spec"), a change to the SHAPE is two commits: the document or amendment FIRST, docs-only, with the
  cheap fingerprint required byte-identical on it to prove nothing else went in; the build second.
  That order is what lets the next reader see the decision before the code that embodies it.
- **A presentation-only change must prove it changed nothing.** If the project has a cheap whole-state
  fingerprint, require the byte-identical value in the commit message. That identity is the proof; a
  passing test suite is not (it proves you did not break what it covers, not that the world did not
  move). And when the presentation change touches an IDENTIFIER the user also types as input - row
  numbers, menu indexes, ids - require a test that every index still resolves to the object it named
  before: renumbering silently re-aims every habit the user has built, and no fingerprint catches it.
- **Children patch shared documents and skills too.** Each phase's child records what it learned. So
  re-read the project skill before adding rules to it, and strengthen an existing rule rather than
  appending a second copy of the same lesson.
- **A child that cannot state the baseline will report a bogus "unchanged".** Put the baseline values
  in the bundle and make "verify these first, stop and report if they do not match" the child's first
  action. A child that starts from the wrong baseline reports changes as unchanged and vice versa.
- **The bundle is not a summary of the plan.** Do not paste the phase's content back at the child -
  give it the plan path and the section name, plus the hard rules and the baseline. Children read
  files well; they cannot guess your conventions.
- **A symptom in the plan is not a diagnosis - make those tasks reproduce-then-fix.** When a task
  comes from a human's report rather than a confirmed line of code, tell the child to print the
  numbers first and then fix whichever side disagrees with the project's own authority (the world,
  the recorder, the spec). If every number agrees, the symptom was a misreading and the correct
  outcome is to change nothing and report that: a diagnosis that ends in "no defect" is a valid
  result, and inventing a fix to look productive is not. Mark which of the plan's tasks are in this
  class when you write the bundle.
- **A phrase you know printed can match nothing in a raw search or a wrapped capture.** Terminal
  captures, formatted reports and wrapped screens break at a column, so a multi-word match over the
  capture returns nothing while the phrase sits right there, split across two lines - and the false
  "the fix did not land" that follows is expensive to unwind. Flatten the capture's whitespace before
  matching (save the output, then `search_files` it), or match one distinctive word; when a phrase you
  read with your own eyes matches nothing, suspect the line break before the code. `search_files`
  itself answers in one of two shapes - `{matches: [{path, line, content}, ...]}` or, when it formats
  for reading, `{matches_text: "..."}` - so read both keys before concluding "no hits", and drop
  narrowing filters when a filtered call looks empty while the unfiltered one had hits. The same trap
  applies to assertions in tests over wrapped text.
- **A bare-term search over prose invents hits as easily as it misses them.** Word boundaries, or it is
  not a count: "tribute" matches `contribute`/`distribute` and "reparation" matches `preparation`, so a
  scan reporting two dozen hits can mean the concept is absent entirely - and the inverse (dismissing a
  concept as absent because the term you guessed is not the one it is written as) costs a round of
  rework. Use `rg -iw`, read the hits, and treat "the docs say nothing about X" as a claim that needs a
  word-boundary search behind it.
- **Read the artifact's own command surface before scripting probes at it.** The help/usage output -
  the CLI's help command, the tool's `--help`, the module's command table - is authoritative. A
  guessed subcommand fails as "no verb matches", which reads like a missing feature rather than a
  typo and costs a round trip; one read of the help surface is cheaper than three guesses. The same
  holds for a surface that has moved: check the directory rather than a path list from an older note.
- **Do not run children that mutate the same repo in parallel.** Parallel fan-out is for independent
  workstreams (research, probes, read-only surveys). Anything that commits, migrates, or bumps a
  version is a sequence.
