# Authoring starpath docs (specs, ADRs, registers, results)

Depth for the "Phase planning & docs" half of the `starpath` skill: doc placement, the doc gates,
and the four authoring procedures. Repo: `~/repos/starpath` (`silentsea-xyz/starpath`); read the
root `AGENTS.md` router first (`docs/house-rules.md`, then the one spec your task touches). Phase
planning/execution is `references/phase-planning.md` — this file covers the documents a phase
produces and the register/spec changes around it.

## Where each artefact belongs

- Plans, specs, ADRs, registers and runbooks live in `starpath`. Spike code, fixtures,
  orchestration, CSVs and `FINDINGS.md` live in `mariner` (`~/repos/mariner`, sibling).
- Cite across repos as `mariner:<path>` in prose — a cross-repo file cannot be a relative
  link, because the doc-link gate reads `[text](path)` as a path relative to the file that
  holds it (and a `..` target fails: a directory is not a file).
- Authority is set by the status header: **Normative** (code must conform) / **Draft** /
  **Reference** / **Informative**. `docs/specs/inherited/` and `docs/specs/reference/` are
  imported copies with provenance headers — do not edit them into shape; a change there is a
  spec change.
- A working plan authored in plan mode goes in the session workspace's `.hermes/plans/`, not
  the checkout. A phase plan *meant to be committed* belongs beside its milestone overview
  (`docs/submissions/<milestone>/`) — follow the overview's own instruction.
- A new `docs/results/` record is indexed in the same commit: `docs/results/README.md`
  carries a `## Records` list; add the bullet there (topic, date, what was run — not a
  figure, which lives in the record itself).

## The doc gates — run before committing, unpiped

```bash
cd ~/repos/starpath
./scripts/check-doc-links.sh                 # every relative markdown link resolves
./scripts/check-roadmap-reference-policy.sh  # delivery-identifier policy
./scripts/check-acceptance-map.sh            # acceptance map stays consistent
./scripts/check-no-inline-constants.sh       # house rule 1, outside packages/params
```

Two can be **red at HEAD on files nobody in this task touched** — an active roadmap path,
and a `spikes/*/src/*.rs` comment that inlines the 257-layer constant. Run all four, fix only
your own findings, and report the rest. Run them **unpiped**: `./check-doc-links.sh | tail -5;
echo $?` prints `tail`'s status, so a red gate reads green — call the script alone or read
`${PIPESTATUS[0]}`. Commit locally (`docs(<area>): <what changed>`); pushing is a separate,
asked-for action (private repos, per-repo deploy keys, land on `main`). Verify the write
landed with `git show --stat --oneline HEAD`.

## Procedure: a spike or research plan

1. **Find the neighbours.** `ls docs/roadmap/`, read the closest existing plan end-to-end and
   mirror its skeleton — there is a house pattern and matching it is most of the review.
   Skeleton: [templates/spike-plan.md](../templates/spike-plan.md).
2. **Recon what the plan acts on**, in this order: the obligation in
   `docs/registers/obligations.md` that owns the term; the ADR that settled the current
   approach and its reopening condition; the inherited spec section the work would amend;
   the measurements register for what is already measured (put it in a "must not be
   re-measured" table with its source).
3. **Order the work cheapest-falsifier-first** — a first stage that can kill the whole idea
   in an afternoon (a ceiling computation, a paper comparison, a census re-read) before any
   gadget is built; say out loud which stage can stop the work.
4. **Pre-register the gates and the decision rule**, including the prior you expect to fail.
5. **State the layout and provenance:** repo, arm/command name, CSV directory, host-record
   discipline, verified-proof rule; `PATCHES.md` for anything vendored (house rule 8).
6. **Write what it does not decide**, as its own section.
7. **Run the gates, fix, commit, verify.**

## Procedure: a spec change (ADR plus the amendment)

Trigger: a settled claim is wrong, or an inherited document needs its living copy changed.
Do not fix wording quietly — every such change moves through the same steps.

1. **Decide what kind of claim it is.** A *measurement* settles a decision (house rule 2); an
   argument or source reading does not. A reading may correct a *reason* or a false *existence
   clause*, but must not reverse a decision. Write the ADR's `Settled by` as an explicit
   judgement call and say in plain words it is **not** a measurement.
2. **Add the ADR.** Next free number from `ls docs/adr/`; copy `docs/adr/template.md` (Status /
   Date / Settled by, Context, Decision, Consequences, Reopening); add its row to the index
   table at the end of `docs/adr/README.md`. Supersede only when reversing, then mark the old
   one `Superseded by ADR-NNNN`. A single corrected clause gets a short
   `> **Corrected <date> by [ADR-NNNN](...):**` blockquote in the old ADR's body.
3. **Amend the living normative document.** Append `> **Amended in starpath on YYYY-MM-DD:**`
   to the provenance header, naming the ADR and what moved. New sections keep the document's
   own numbering. Never edit the body of `docs/specs/reference/` — a `Reference` snapshot
   records supersession in its provenance paragraph.
4. **Then the register.** Research is not a debt. If the register already lists the topic as
   explicitly out of scope, add a pointer to the corrected basis — do **not** invent an `O-N`.
5. **Keep the proposer honest.** Move a proposing roadmap document's status to
   `**Applied YYYY-MM-DD**` and rewrite the proposal section into what landed, so the two
   documents cannot be read as contradicting each other.
6. **Gates, commit, verify.** One commit may carry the ADR, amendment, snapshot annotation,
   register pointer and proposer update; name each in the message body.

A caution that generalises: **a gated conclusion does not move until its gate's own condition
is met** — correcting the letter is allowed, reversing the conclusion is not.

## Procedure: the obligations register (evidence, not obligation)

`docs/registers/obligations.md` is **Normative**; an entry is a claim with a status, not a
container for findings.

1. **Read the entry whole** before characterising it — body *and* `**Status:**` /
   `**Blocking:**` / `**Owner:**`. An entry whose prose reads like an open gap is routinely
   already discharged elsewhere. One entry:
   `awk '/^### O-6[^0-9]/,/^### O-7[^0-9]/' docs/registers/obligations.md`.
2. **Corroborating an obligation neither reopens nor discharges it.** Add a dated, bold-led
   paragraph (`**Corroborated YYYY-MM-DD by <what, with commit ids>.**`) after the existing
   prose, then state explicitly what did *not* move. Do not reword the obligation or rename
   its heading — other documents cite these anchors.
3. **Name the kind of evidence inside the record** (source reading / diff of another tree /
   unmerged branch / unmeasured projection), so a later reader cannot mistake it for a
   measurement. A comparison that was never executed says so.
4. **Adjudicate a divergence, do not just report it** — decide which of *defect here* /
   *defect there* / *capability they declined* it is. "They differ" is not a finding.

## Pitfalls

- **The delivery-identifier policy is enforced in paths *and* prose.**
  `check-roadmap-reference-policy.sh` rejects the shapes `M1`–`M4`, `S1`–`S9`, `P1`–`P8`,
  `C1`–`C6`, `U1`–`U3`, `H1`–`H4`, `OC1`/`OC2` as standalone tokens in any tracked file
  **except `docs/roadmap/archive/`**, and the same shapes anywhere in a path or filename.
  Only the S-series is case-insensitive, so a lower-case vendor name (`p3-schnorr`) passes
  while `P3` does not. Name work items and arms descriptively (`sigagg`, `premise`,
  `ceiling`) instead of by letter+digit. Do not invent a spike's letter/number — a
  descriptive name also satisfies the policy.
- **A gate can already be red at HEAD on a file you did not touch.** Count its blast radius
  (`search_files` for the filename) and report it; renaming someone's in-flight plan is not
  a side effect of adding a document.
- **Repo-wide `grep -rn <pattern> .` at the starpath root hangs** on the build tree (`target/`
  holds gigabytes). Use the ripgrep-backed search tool (respects ignore files) or scope the
  path to `docs/`, `packages/`, `scripts/`.
- **Doc links are checked; anchors and external URLs are not.** A relative link must resolve
  from the file that holds it; a link to a file you *intend* to add later fails the gate now
  — add the target in the same commit, or describe it as prose until it exists.
- **Do not restate a register figure as a plan constant.** Measured figures are Informative
  and host-specific; a plan that turns one into a decision rule creates the second home for a
  number that house rule 1 exists to prevent.
- **An out-of-scope register entry is not an obligation.** The register's "Explicitly out of
  scope" list exists so those items are not mistaken for oversights; a pointer keeps it
  truthful, an `O-N` contradicts its design.
- **Several edits to one file in one turn can race.** Do a same-file group sequentially
  inside one `execute_code` call (`from hermes_tools import patch`), then read the file back
  once — that call is also where the gates belong, before any commit.
- **A cross-repo file cannot be linked, only cited** (`mariner:<path>` or plain text).
