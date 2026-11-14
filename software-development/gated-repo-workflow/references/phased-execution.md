# Executing a phased plan through subagents — detail (Mode C)

Companion to the `plan` skill, which writes the plan and hands execution off. The shape: one subagent
per phase, sequentially; one commit per task; a verification pass at the end that fixes what the round
surfaced.

## The shape in one paragraph

A phase is one child's whole job: it reads the plan itself, so the parent does not have to hold the
code in its own context. The parent owns the bundle, the verification, and the deviation ledger. Do
not collapse the plan into one long agent run of your own, and do not parallelise phases that share
state. Parallel fan-out is for independent workstreams (research, probes, read-only surveys) — anything
that commits, migrates or bumps a version is a sequence.

## Procedure

**0. Establish the baseline you can re-derive cheaply.** Whatever the project recomputes in one
command: the test count, a content/build fingerprint, artifact or replay hashes, the gate's summary
line. Record it before dispatching anything. Every child's "this changed nothing" claim is checked
against that baseline, and a claim you cannot re-derive is a claim you can only believe.

**When the plan came from the user's own use of the artifact, register the findings before fixing any
of them.** A report of what went wrong in play (or production, or on their machine) is a list of
symptoms, and the first phase must turn each into a tracked item — one per distinct question, carrying
the user's own numbers, months and commands — so every fix commit can cite the item it closes and
nothing in the report is silently dropped or silently merged into something else. That phase writes no
code. Where the report is ambiguous about how many questions it contains, split or merge explicitly
and say which; where a finding is another item's question seen from a different side, record it under
that item rather than inventing a new id.

**1. One child per phase, in order.** Phases that share a schema, a document, a register, or a
migration are sequential by construction: each phase's baseline IS the previous phase's output. Send
phase N+1 only after you have verified phase N yourself.

**2. Write the bundle.** The plan was written for an implementer with zero context, so the child needs
the facts the plan assumes: repo + branch + the exact push command, the plan's absolute path AND which
phase to execute, "load <project skill> first", the baseline values, the hard rules, the commit
protocol, the report format. Template: `templates/delegation-bundle.md`. The bundle is not a summary of
the plan — do not paste the phase's content back at the child: give it the plan path and the section
name, plus the hard rules and the baseline. Children read files well; they cannot guess your
conventions.

**3. Verify every phase yourself before building on it.** The child's summary is a self-report.

```bash
git log --oneline -8                  # the phase's commits, in the plan's order
git status -sb                        # in sync with the remote, nothing local
<the project's gate command> > /tmp/pN-verify.log 2>&1; echo "exit=$?"
grep -E "hash|gate: ok|tests? passed" /tmp/pN-verify.log | tail -4
```

`git status -sb` compares against your *local* ref, so before telling a user who pulls the branch
himself that a commit is on the remote, ask the remote (`git ls-remote origin refs/heads/main`).
Expect the gate green and the numbers the child reported. A presentation-only phase must show the
*previous* phase's fingerprints; a phase that touched persisted state must show new ones and say why.

**When a child dies on its iteration cap, the phase is usually unfinished rather than lost.** The
common shape is the last task complete and gate-green in the working tree but never committed. Treat
that tree as a partial phase: read the diff yourself (`git diff --stat`, then the code diff — do not
take the summary's word for what is in it), re-run the project's gate on it, and only once it is green
commit and push it yourself, in a message that says the orchestrator finished it after the phase's
child ran out. That provenance belongs in the record; a commit that pretends a child finished the task
misleads the next reader. Then dispatch the remainder as a fresh child with the same bundle.

**4. Keep a deviation ledger.** Children hit anchors that moved and make choices the plan did not
anticipate; they must say so in the commit message and their report. Log every deviation, every task
left undone, and every defect the child surfaced on the way — children are the best bug-finders in
this loop because they read the neighbours of the line you sent them to. Do not interrupt the sequence
to chase these: close the list in one pass at the end.

**5. The final pass.** On the real tree, after the last phase: re-run the full gate, walk the ledger,
fix what is fixable, and re-verify. Then **exercise the artifact the report was about, end to end, and
read the lines it complained about in that output** — a green suite proves only that you did not break
what its authors thought to assert. If the artifact's own stored fixture never reaches a line the
round changed (a per-entity view the fixture never opens, a branch its scenario cannot enter), extend a
copy of that fixture: append the missing step, replay it, and read the line. Report per-phase commits,
the final measured numbers, what moved and why, and anything still open. If a fix turns out to need a
rule the user owns, do not invent it: leave it flagged with the options.

Two habits make that pass real rather than ceremonial. **Assert absence, from a captured file**: keep
the whole run's output, count the quoted phrase (zero is the proof) and read the block the user
complained about in full. **Recompute anything the children only asserted**: if a diagnosis rests on
arithmetic (a rounding step, a rate, an off-by-one), redo it yourself before reporting it as fact — a
child's mechanism is a hypothesis until your own run agrees with it. **Sweep the documents for the
vocabulary the round deleted**: each child amends only the item it was sent for, so the phrases the
round removed survive as current-state claims in other items and docs. Grep the whole documentation set
for each deleted phrase and for every note the round itself invalidated — zero hits in the code with
one hit in a doc is the shape. Correct each with an amendment marker beside the claim rather than
rewriting the history around it, and call the round done only when that sweep is empty.

**Then dispatch the verified leftover list as one child, with your own evidence inlined.** Once your
probes have turned each leftover into a defect with a location and a measured number, that is a bundle
like any other: the file, the value you measured, the authority to fix against, and the requirement to
change nothing else. Hand it the evidence so it does not re-derive it, make each item its own commit,
and verify that child like any other phase.

**6. Parent's loop discipline.** While a child runs, do not poll its transcript — end the turn with a
one-line status and act on the result when it arrives. You can steer a drifting child mid-run
(`delegate_task action='steer'`) or stop one that is out of scope (`action='stop'`, partial results
still return); use it rather than letting a child finish work you will have to revert.

## Sizing a phase for one child

Budget roughly 5-8 minutes and a few dozen API calls per plan task. Observed: a 7-task phase ran ~30
minutes and ~240 calls; a 1-task phase ~6 minutes; a 3-task phase ~13 minutes. If a phase looks much
bigger than that, split it into two dispatches rather than letting a child run to the edge of its
budget — a child that runs out has its phase half-written and you verify a partial tree.

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
  unverified claim you refuse from a child, and worse here because he acts on it. And when the user
  says "commit and push" and the tree is already clean, answer with the proof (empty
  `git status --porcelain -uall`, HEAD equal to the remote's tip, and which commit is already up);
  manufacturing an empty commit to look responsive is the worse answer.
- **Never let a child implement a task the plan marks as awaiting the user's ruling.** Children cannot
  ask questions, so a ruling-shaped task will be silently decided if you send it. Carry it as its own
  phase that only registers the question and proposes the options, and say in the report that the
  mechanic is deliberately unimplemented. Rulings that arrive mid-round are the same shape in reverse:
  give them their own phase, record each one in the owner's own words against that item's own id, mark
  which part is now to be built and which parts stay deferred, and keep the item visible until the
  build lands — a ruling is not a build, and a recommendation is not a ruling.
- **"Built in part, question left in writing" is a correct outcome** — require it when the honest scope
  cannot close the item. Tell children this is expected: a child that cannot see the boundary will
  either invent the missing field or silently drop the half it cannot do.
- **Ban history rewrites in the bundle.** A child's instinct is to amend a commit to fold in a note it
  thought of a minute later, even after the push; if the user pulls that branch himself, a rewritten
  tip strands him on a commit that no longer exists. Amend before the push, make a follow-up commit
  after it, and never force-push — and check the phase's `git log` against `origin` during
  verification, because a force-pushed tip looks locally clean.
- **One commit per task, never one commit per phase.** Batching destroys attribution. Give each task
  the plan's own commit message. Where the project treats a document as the contract ("the code may
  not silently redefine the spec"), a change to the SHAPE is two commits: the document or amendment
  FIRST, docs-only, with the cheap fingerprint required byte-identical on it to prove nothing else
  went in; the build second.
- **A presentation-only change must prove it changed nothing** — the byte-identical fingerprint in the
  commit message. When it touches an IDENTIFIER the user also types as input (row numbers, menu
  indexes, ids), require a test that every index still resolves to the object it named before.
- **Children patch shared documents and skills too.** Each phase's child records what it learned, so
  re-read the project skill before adding rules to it, and strengthen an existing rule rather than
  appending a second copy of the same lesson.
- **A child that cannot state the baseline will report a bogus "unchanged".** Put the baseline values
  in the bundle and make "verify these first, stop and report if they do not match" the child's first
  action.
- **A symptom in the plan is not a diagnosis — make those tasks reproduce-then-fix.** When a task comes
  from a human's report rather than a confirmed line of code, tell the child to print the numbers first
  and then fix whichever side disagrees with the project's own authority. If every number agrees, the
  symptom was a misreading and the correct outcome is to change nothing and report that.
- **A phrase you know printed can match nothing in a raw search or a wrapped capture.** Flatten the
  capture's whitespace before matching (save the output, then `search_files` it), or match one
  distinctive word; when a phrase you read with your own eyes matches nothing, suspect the line break
  before the code. `search_files` answers as `{matches: [...]}` or `{matches_text: "..."}`, so read
  both keys before concluding "no hits", and drop narrowing filters when a filtered call looks empty
  while the unfiltered one had hits. The same trap applies to assertions in tests over wrapped text.
- **A bare-term search over prose invents hits as easily as it misses them.** Word boundaries, or it is
  not a count ("tribute" matches `contribute`/`distribute`). Treat "the docs say nothing about X" as a
  claim that needs a word-boundary search behind it.
- **Read the artifact's own command surface before scripting probes at it.** The help/usage output is
  authoritative; a guessed subcommand fails as "no verb matches", which reads like a missing feature
  rather than a typo.
- **Do not run children that mutate the same repo in parallel.** Anything that commits, migrates or
  bumps a version is a sequence.
