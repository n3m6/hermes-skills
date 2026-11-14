---
name: wwx-shadow-wars
description: "Use when working in the WWX: Shadow Wars repo."
version: 1.2.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [game-design, grand-strategy, google-drive, docs]
---

# WWX: Shadow Wars - design doc maintenance

WWX: Shadow Wars is the owner's solo game design project: a pausable real-time
grand strategy game, Earth 1945-2045, where nuclear deterrence makes direct war
between great powers impossible, so conquest happens via espionage and hybrid
war. The player is head of state of a rising power aiming at global economic
hegemony. Not a pitch to a publisher - the doc is a build guide for a solo dev.

## Where the docs live

**The design lives in the repo, and the repo is its source of truth:**
`~/repos/wwx/docs/design/`, one file per document as `NN-title.md`, with the
design's own master index at `docs/design/index.md`. Edit those files in place and
commit them.

Google Drive folder **WWX** (`1f91U_wTxRpRMKgjnGoggEe71BxMp61vv`) is a
**HISTORICAL RECORD**: the whole set was imported from it on 2026-09-22 and Drive
is not updated since. Do not write to it, do not pull from it, and never look
there for a newer version. `docs/design/_provenance.json` maps each file to its old
Drive id if a document ever has to be traced back. The Drive-era puller
(`tools/pull-design-docs.py`) is deleted on purpose — running it would overwrite
the source of truth with a stale snapshot. **Doc 18 (`18-economic-sabotage.md`)
was authored in-repo on 2026-10-26 and has no Drive id**; it owns the nine
coercion instruments and the completed inflation loop, and its ten questions
(W-232..W-241) were closed as recommended.

New look-and-feel or competitor research notes belong in the Drive folder
**Grand strategy competitor research** (`1HPPYDhY7QpZDnXaB-81xrCJNHRux0E08`),
which also holds the Paradox, Victoria 3 and Espiocracy studies — not in the
historical WWX folder.

Design documents are read with `read_file` and edited with python in
`execute_code` (never write back `read_file` output: every line is prefixed `N|`).
The design's own conventions still bind: `[DECIDED]`/`[PROPOSED]`/`[OPEN]` tags,
two-digit numbering, the `W-` register in `00-open-questions.md`, and the version
stamp in line 2 — stamp ALL documents when the set version is bumped.

The Drive doc-id list below is kept only as provenance for pre-2026-09-22 history.

## Doc IDs (use these; never retype from memory)

Always re-list the folder before writing if unsure:
`drive.files().list(q="'1f91U_wTxRpRMKgjnGoggEe71BxMp61vv' in parents and trashed=false")`

```
Design                    1lSCRAX4d-fjQ869655vnC6OUPhX3RUog7WHTrkeuZ2k
00 - Open Questions       1yNjZj_OGuuNPeiKvKfmrOkDfincsWZHRKmTWZKujfS4
01 - Vision               167Vd1pKYxr1pkevZ3EY8uV-PydosLFtCERQQvIVmRvI
02 - Core Framework       1zdoqe188chVj1cMsaP1zEfRARqgXZ3bhrCp8K5C01PM
03 - World & Map          1VDJ0dVcaG7tZLsvDypQpNxkTuvInRng6b0QL8SaopuM
04 - States & Rivals      1WZqpmESTGf2a4wIoLo9isklI649FfUPftDMsnxZgddE
05 - Population, Instability & Regime  1dSOfhYwwCKo153n-DuaZjZ-NwPHhOCPx4BXer_sndUo
06 - Economy & Soft Power 1FiW1f2otFAcnUZoYN0IDQTr4WeseEip0JG_nnD_ZN8A
07 - Military & Deterrence  1-lC7WY-xy6-L3xInAbQ24Z3UtYwCb0PaH5MbSo5ZFiM
08 - Covert Action        1FYLDCkQvDH1rIkSMHRLGUW9aROBiEOw4oIZe_iB3ZZw
09 - Diplomacy & Hegemony  1N6hUGFeiE05GCj-Pszr73PKpxgjHb2oFLuTeWPz6u1k
10 - Technology & Proliferation  1BNbT9iqhWXi_HtJmnAeZiy1YHSUphZkf_Kd5wO8cxyo
11 - AI                   1JcPyaC2ZGWcGuPIlSzL3CPrOK7aMA5SiYRT4NiD1Nfg
12 - UX & Onboarding      1LCuX7ZVuLjA8_X6QYpuTb3e1ke84dzhJA8qfJRlfJWU
13 - Simulation & Architecture  1X3tclJfT_a7uZlsRHzmaQE_bBedJn13D9rhIBYkEr2Y
14 - Content Plan & Narrative  1XkGYSxcnPPO9h0IQtZptSdvC80398l6FBBo9TALKXy0
15 - Balance & Tuning     1TpqhaxMJe9ytxDcC_uxOxzb6jNjpNvLpJp3wmPZA1iQ
16 - Production, Scope & Risks  1bHEuhnYxeRxLFyKFyxOhoX9hRmfMT_ogGcQBfZLwczo
17 - System Architecture        1BrI18zvtkRlk5aMI_ccNMBLddDO-f9_xKVPyFaV_OPw
```

Google Doc IDs are 44 chars. A 404 "Requested entity was not found" means the
id was mistyped - re-list the folder rather than guessing. (This has already
happened once: a dropped character in the 02 id.)

## Code repo (git)

`promunb/wwx` on GitHub - the repo is **private** (an unauthenticated
`api.github.com/repos/promunb/wwx` answers 404, so nothing in it is public), cloned at
`~/repos/wwx`.

**The measured block below is a HISTORICAL baseline, not current state.** This repo
moves in large batches - a single `git pull` has carried 48 commits across 299 files.
Re-run `bash tools/gate.sh` before quoting any number here, and re-read the manifests
before quoting the crate list.

**Last measured 2026-09-22 at
`fcce6c2` (after the "Remove obsolete code" cleanup): 7 crates, 32,583 lines of Rust
across 99 files (each crate's `src/` + `tests/`), 249 tests pass, gate green,
content fingerprint `dd43c22a26b01d39`, century replay `d1d9c44386039266` (1200
months, 66 commands), stored campaign `556ead8fc284dae2` (240 months, 45 decisions).**

**Observed at the next pull (`1f10869`, economy-circulation work, W-155..W-158 /
W-177..W-179) and not yet re-measured:** the crate set is **eight**, not seven -
`crates/econ-harness` (the economy harness: scenario catalogue, sweeps, invariants,
traces, monetary explorer) now sits alongside the seven in the table below; the
monetary circuit moved to `crates/core/src/systems/economy/circuit/` and split into
fiscal/foreign/investment/external/payment; `content/economy/`, `content/provenance/`,
an in-repo economy verification skill under `.agents/skills/`, and a large
`docs/economy-circulation-*` doc set are new. The schema constants below predate this
and were NOT re-verified - grep the code.
**For any "how is X implemented?" question about trade, external money, currency,
inflation or economic coercion, read `references/economy-code-map.md` first** - it
carries the module layout, the funding order, the trade weights, the inflation
chain, the coercion instrument gates and the documented dead keys; re-deriving it
costs a dozen greps.
**For any "how is X implemented?" question about populations, the instability
ladder, cleavages or condition scores, read `references/population-code-map.md`
first** - it carries the cell model, the exact monthly law and its coefficients,
the two rungs' arithmetic, the derived readers and the honest gaps; re-deriving
it costs a dozen greps and invites quoting a stale intersection count.
Schema constants — read them from the code, never from the register and never
from this file (both lag by many versions): truth in `crates/core/src/sim.rs`
(written into the state hash), view in `crates/projection/src/view.rs`, protocol
in `crates/protocol/src/message.rs`, campaign in `crates/cli/src/campaign.rs`,
save in `crates/session/src/bundle.rs`, content schema in
`crates/content/src/lib.rs`. `docs/status.md` carries a snapshot worth grepping
as a starting point, but it is Informative, not proof. Push/pull over the scoped
ssh host alias `github-wwx` (dedicated deploy key, write access granted) — the
remote is already `git@github-wwx:promunb/wwx.git`, so plain `git push` works.
The design **lives in this repo** at `docs/design/` and is the source of truth — imported from Drive on 2026-09-22, one file per document. Edit those files in place and commit; Drive is history (see "Where the docs live").

**The rival loop is BUILT and its plan doc is DELETED** (W-085..W-092, authorized
2026-09-22). `docs/first-slice-rival-loop-plan.md` was removed at `fcce6c2`; do not
cite that path — code comments now cite the register ids. Where each stage went:
W-086 explicit patronage and exclusive allegiance (tier + named patron, public outcome
/ hidden sponsorship); W-087 the persistent authored rival policy — a real content
type, `content/policies/policies.json` + `policy:rival-1945`, **one decision producer
per actor** (policy | script | demonstration planner), with targeted
counter-intelligence (roll-up by default, `turn_intruders` deliberate, silence is the
*tell*); the scripted opponent is retired from the active slice but kept and tested
(W-065's sabotage move is its record). W-088 contest legibility and player-facing
dates. W-089 persistent government attention and bounded recurrence (attention is
world state; a warned response is not erased by dropping the funding). W-090 post-coup
consolidation and political residue. W-091 proxy independence with a fair deadline and
the intelligence channels to see it. W-092 three authored opening theatres — Frontier
(unstable, accessible, the player's only network), Proxyland (a funded party already
in place and committing two units), Holdfast — chosen **through ordinary commands**,
not a config selector, plus the combined economy (twelve units opening, eight a
month).

**The gate:** `bash tools/gate.sh` — fmt check, clippy at `-D warnings`,
`check-deps.sh` (core is a leaf), `check-determinism.sh` (no float / unordered
collection / clock / IO in the core), the test suite, `wwx validate`, and a
1,200-month replay. CI runs exactly that script (`.github/workflows/ci.yml`).
Never report the repo's state without running it. **Last measured 2026-09-22 at `fcce6c2`: 249 tests pass,
gate green in 1m14s, century replay hash `d1d9c44386039266`, content fingerprint
`dd43c22a26b01d39`, stored campaign `556ead8fc284dae2`, 32,583 lines across 99 files.**

**Content (`content/`, 11 JSON files, sorted path order from an explicit list, plus
one JSON Schema per type in `content/schema/`):** `balance/{balance,phases}.json`,
`events/`, `groups/`, `policies/`, `programmes/`, `provinces/`, `scenario/`,
`scripts/`, `states/`, `verbs/`. The dataset is the REAL 1945 world, not the fiction: milestone 5b replaced the slice's
twelve fictional states, so the roster is 69 states, 1,977 provinces and 231 authored
groups, and the verb file holds 21 entries (the design's 20 plus §18's `counterfeit`).
Count verbs from `content/verbs/verbs.json` and treat `mechanic: null` as unbuilt; never
describe the current build in the fiction's terms. Four guards are structural, not comments — build on
them rather than around them: `slice: true` on exactly six verbs across the four
families that need code (E absent); every value authored in §16.2.5 must exist in
balance.json; a condition may only test a closed attribute vocabulary; a
programme on a non-family-A verb is refused.

**Content runs the world.** `crates/session` reads the scenario, programmes, scripts,
events, verbs' `mechanic` and verbs' `exposure_a_month_ppm`; the real phase bodies are
`networks` (the programme engine *and* `pawns::run`), `attribution` (the three layers
and the duel in `ci.rs`) and `ai` (the scripted opponent). Family B (coup) and family D
(pawns) are built in `pawns.rs` + `truth/pawn.rs`; the state's tier (9.1) is its own
field. `pops` is a **full model** (milestone 6, W-151/W-157/W-179/W-193), not a
demonstration; `output` builds the derived category snapshot and the cleavages
the ladder reads.

Crates (dependency order — the table is enforced by
`crates/core/tests/architecture.rs`, which parses every manifest):

```
crates/core        wwx-core       NOTHING, not even serde. fixed point, ids, idmap,
                                  time, derived RNG, state hash, balance, truth,
                                  belief, commands, events, derived, ledger, phases
                                  + contract guard, systems/*, ai, sim (the tick)
crates/content     wwx-content    serde. schemas, sorted-path loader + fingerprint,
                                  one validator
crates/projection  wwx-projection core+serde. the view DTOs and project()
crates/protocol    wwx-protocol   projection+serde. versioned envelopes, size cap,
                                  handshake negotiation, refusals
crates/session     wwx-session    core+content+projection+protocol. content -> world,
                                  key <-> handle interning, the tick, save manifest
crates/cli         wwx-cli        the ONLY crate that does IO: validate, autoplay,
                                  replay, hash, view
crates/server      wwx-server     the host: handshake/refusals/projections/advances
                                  over line-delimited JSON
crates/econ-harness               (added since this table was written) the economy
                                  harness: scenario catalogue, sweeps, invariants,
                                  traces, monetary explorer. Read its own manifest
                                  and `crates/core/tests/architecture.rs` for its
                                  position in the dependency graph.
apps/ui            renderer scaffold only (economy.ts); no browser client,
                                  projections only.
```

`make gate | build | test | content | autoplay | replay`; run the Rust binary as
`cargo run -p wwx-cli --bin wwx -- <cmd>`.

**`docs/status.md` is the honest ledger** — it names what is measured against what is
DELIBERATELY a placeholder, and the five engineering questions the design does not
answer (invented month→week mapping, no save compression, no WebSocket,
EVENT-vs-PROJECTION, whether content may narrow a phase contract). It also LAGS: its
verb line still read "six have real mechanics / fourteen unbuilt" long after §18 and 7b
moved both numbers, and its economy bullets are dated to an older law. Read it for the
shape of the gaps it names; take every countable fact from the mechanised source —
`content/verbs/verbs.json`'s `mechanic` field for verbs, `tools/evidence.py questions`
for the register, the generated pin block for versions.

**Docs in the repo** (`docs/`): index, house-rules, architecture, determinism,
conventions, design-docs (maps the Drive set), content-pipeline, build-and-test,
protocol, glossary, decisions, first-slice, status + `AGENTS.template.md`; `docs/design/` (19 design documents, 290k chars, imported at design v1.8); plus a
per-crate `AGENTS.md` and a root router `AGENTS.md`. House style copied from
`~/repos/starpath`.

**The REPL playtest skill is project-level and model-agnostic**: `.agents/skills/wwx-first-slice-repl/` in the repo (added `4dfc0ac`): `SKILL.md` plus a REPL guide under its references directory, pointed at from the root `AGENTS.md` "Where to read next" table. Any `wwx play` interaction goes through it (PTY, fog preserved, disposable campaigns outside the repo). It replaces an earlier codex-local copy; do not create per-agent copies.

**Running a playtest from Hermes has four traps; all four cost a run (2026-10-26):**
1. **The iteration budget is 150 and one screen per `terminal` call eats it.** A full
   1→1965 playtest is ~2h and ~130 tool calls; the run was cut off mid-campaign by the
   cap with the ending unshot. Write a driver script once (`repl.py send` into a tmux
   pane, `digest.py` to read captures back) and run batches in background — one call per
   batch, not per screen. Build first (`python3 tools/job build -p wwx-cli`, ~384 s ci
   profile), and know that replay is **3.05 s/month** (240 months ≈ 12 min) so a full
   campaign is scripted, never typed. **Always prefix `python3`**: executed directly
   (`tools/job receipt`), the lifecycle guard cannot scan it and blocks the whole call
   ("scan budget was exhausted (remote reads at depth 1)") — `python3 tools/job receipt`
   runs fine. Verified 2026-11-07 and again 11-08.
2. **`~/.hermes/cache/scratch` is deleted after 24 h idle.** Campaigns, captures and
   drivers written there are gone the next day. Put the playtest workdir under `~/tmp/`,
   and quote anything you must keep (the final verdict text especially) into the message.
3. **Killing the driver does not stop the game.** `process_manage kill` reports
   `status: killed` for the python driver while the `wwx play` process inside tmux keeps
   running — 51 unattended minutes and 11 months in the 10-26 run, ended only when the
   owner said "stop the run". Kill the tmux pane/session, then verify with `ps` and
   `tmux ls` that no game process remains.
4. **Parse the LAST match in scrollback, not the first.** A driver that greps the first
   occurrence of a label in a captured pane silently reads an old month; that made one
   full CSV column untrustworthy and forced a disclaimer in the report.

## Status

All seventeen sections (00-16) are drafted and the set is well past v1.7 — the
version stamp in line 2 of each document is the only count that matters, and
stamping them ALL when the set is bumped is mandatory or the set drifts. The
register's pending count is likewise a moving number: read it with
`python3 tools/evidence.py questions` and never quote a count from this skill (a
stale copy of this file has said 55 where the tool said 69). The doc set is a
BUILD GUIDE, not a read-through.

**Where the build is, and what is next:** the build order is §16.3 of
`docs/design/16-production-scope-risks.md`, and the milestone documents in `docs/`
use the same numbers as its steps (6 = population, 7 = economy, 7b = political
organisations, 8a = technology, 8 = military, deterrence and the proliferation race).
Read `references/build-order-and-milestones.md` BEFORE any "where are we" answer —
"what have we implemented", "what is still remaining", "what is done from the first
slice", "what is next" — or any milestone plan: it carries the ladder with the 7b and
8a insertions, each step's built-vs-accepted state, the sequencing conflict (W-014 vs
the closing door) and the honest commands. Skipping it means re-deriving the answer
from a 1,200-line design doc and getting the next step wrong.

Two cheap checks come before any claim of progress:
`python3 tools/evidence.py questions` (the pending count and ids — never quote a count
from prose) and `python3 tools/current_campaigns.py` (whether a 240-month recording
under the shipped law exists; it refuses by name when one does not, and that refusal
means the acceptance machine half cannot be cited today). Never report the build as
green without the second one.

## The first slice: BUILT (v1.10, 2026-09-22)

All eight 16.2.8 steps are done and `bash tools/gate.sh` was green at that revision. The
six assertions of §16.2.7 are implemented in `crates/cli/tests/acceptance.rs` as
`full_world_item_1..6` plus four more riding the same replay (population conservation,
W-090 retention, the ending, W-112's scoreboard); they are `full_world_`-prefixed and
need the owner-granted long tier. **They cannot be re-run today**, because no 240-month
recording exists under the shipped economy law — `tools/current_campaigns.py` refuses by
name — so the machine half is implemented, not currently witnessed. Cite the law and
pins from the generated block in `docs/status.md`, never from this file.

The human half is not closed either: the twelve questions live in
`crates/cli/src/play/mod.rs` and print at the ending, and the owner's playtest rounds fed
W-items, but no document records the twelve answers — there is no single acceptance
artifact for the slice. Say that plainly instead of implying both halves passed.

Also: the twelve fictional states and one-province map specified below are the SPEC the
slice was measured against. Milestone 5b shipped the real 1945 world (69 states, 1,977
provinces), so never describe the current build in the fiction's terms.

The v1.10 rulings, all closed in `docs/design/00-open-questions.md`: **W-075** (i) family
D does need one mechanic — the `fund-opposition-party` party→MOVEMENT conversion — and
§8.9's D row now carries the amendment; **W-076** the builder's numbers are accepted;
**W-077** (a) `cultivate-asset`'s third stage spends 0.3 of network cover, which is what
makes `event:asset-escapes` fire at all; **W-078** the verdict says both halves when both
hold; **W-079** (a)+decay, exposure capped at 1.0 and aged 5% a month.



**16.2 is the build spec, and as of v1.10 it is BUILT**: all eight 16.2.8 steps are done
and the acceptance test's seven items pass. W-069..W-073 (the slice's own questions) were
closed at v1.8 and W-075..W-079 at v1.10. The specification below is kept because it is
what the built slice is measured against.

The slice, in one paragraph: 1945-1965, TWELVE states (PLR player, RIV rival,
FRT the contested state, PRX the prize, GAL/HOL + 6 minors), one province each, no
map, no figures, no economy (a black budget of 12 units a month), a scripted
opponent. The player starts with one network in FRT (pen 25/sec 50/reach 30) and
DOES NOT KNOW the rival has a network inside them (pen 40).

**THE SIX VERBS — drawn from every family that needs code; family E is absent on
purpose because by the v1.4 ruling it needs no mechanics, so there is nothing to
test.** A: `cultivate-asset` (3 stages/4 months) and `run-a-mole` (5 stages/18
months) — the contrast is the shared stage engine under test. B: `coup-detat`
(not staged: preconditions reach>=60, a group at ladder>=3, an ORGANISED pawn —
a funded party is not enough — then a derived-draw resolution). C:
`counter-intelligence` (an allocation, not an operation; detection yields a
BELIEF at 0.35, and at 0.7 the player may roll up or TURN it — silent, per 12.8).
D: `fund-opposition-party` and `media-ownership` (AMENDED v1.10: `fund-opposition-party`
 DOES need one mechanic — the party→MOVEMENT conversion at the second autonomy threshold
 — and §16.2.9's D row carries the exception. `media-ownership` still needs none.)

**Acceptance = two halves, neither optional.** Machine: a stored campaign
1945-01->1965-01 whose assertions are that all three attribution layers fire,
blowback costs something real, a network is LOST at least once, the coup
resolves, and 240 months replay in under 10s. Human: the owner plays it and
answers twelve questions; Q11 ("would you start another run straight away?") is
the verdict, Q6 (false flags are NOT in the six verbs) and Q12 are where the
next design work comes from.

**The trap list in 16.2.9 is load-bearing** — no map, no named people, no
 economy, no seventh verb, no refactor, no UI. Each of those has killed a build
 like this and an agent will be tempted by all six.

## Register bookkeeping (00-open-questions.md) - rules that are easy to break

- **An item's answer belongs under that item's own `W-nnn` line.** Inserting a new item ABOVE an
existing one silently re-parents the lower item's paragraph to the upper item's heading: W-100's
economy recommendation ended up reading as part of W-101 (the stability reading) that way. Append
below the id line, never above.
- **The count convention is `pending + deferred = the items the PENDING section lists`**, and it is
checked by counting `^W-\d{3}\s` lines between the PENDING banner and the next banner. Do not
compare the pending number against the list alone - that misreading produced a false "counts are
broken" report. "SECTIONS AND THEIR ITEMS" indexes the items the register CARRIES (decided ones
with their own `## ... (W-nnn; ...)` heading included), so a closed item keeps its table row.
- **Closing an item takes four edits**: its own heading says decided/built, its answer is in the
section that owns it, its entry leaves the PENDING list, and the count is re-derived with
`python3 tools/evidence.py questions`. Do **not** rewrite the dated "N pending" sentences
scattered through the file: they are historical records, and a blind replace corrupts the
history. `[OPEN]` tags and "neither is ruled" sentences in an item's body go stale the moment
it is ruled - fix them in the same pass.
- **The pending section ends at the first line beginning `CLOSED`, not at the blocking-rules
banner.** `tools/evidence.py` splits the text at `^PENDING - NEEDS THE OWNER'S DECISION` and
then at the first `^CLOSED`, and counts `^W-\d{3}\s` lines in between. An item appended below
that first `CLOSED` line (for example after a late `W-150` block) is silently not counted and
not listed. Append new items immediately before that line, then re-run the tool and check the
new ids appear.
- **A blanket "all as recommended" is a ruling, not a note.** When the owner answers a
numbered block that way, write each answer into its owning subsection, flip the doc's
`[OPEN]`/`[PROPOSED]` tags on the ruled items to `[DECIDED]`, and add a
`DECISIONS TAKEN IN THIS SECTION` block listing the ten answers. Deleting the register lines
alone leaves the doc still claiming the questions are open.
- **These files end lines with two trailing spaces** (markdown hard breaks). A python splice that
uses `.strip()` silently drops them; re-indent with the original tail intact.
- **A measurement belongs where the design owns it, not only in the register.** The float matrix
went into §15.4's degenerate-strategy list next to THE TURTLE, the strategy it measures; the
register's W-100 keeps the finding and the reasoning.
- **A recommendation is not a ruling.** The plan's `Recommended answer:` wording means the item
stays pending until the owner rules; writing "Ruling: ..." into the register claims a decision he
did not make.

## Pitfalls when changing the mechanics

- **Belief writes belong to the phase that owns beliefs.** `phases.json` gives `networks`
  (the programme engine AND `pawns::run`) `reads: [truth], writes: [truth]` — a
  `beliefs_mut()` there panics the phase contract. A report a network produced (W-096's mole)
  is written in `attribution`, which owns beliefs and already reads `protected_until`. Same
  phase **cannot READ beliefs either**, so any "only report when the value moved" rule needs
  its memory in truth (`Network.mole_report`), not in the belief store.
- **A QUIET network holds a programme instead of serving it** (`programme.rs`: a held
  programme serves no stage and `months_served` stays put). An 18-month placement therefore
  needs 18 ACTIVE months, with cover recovered in quiet spells between them — played straight
  in quiet, the mole sits at "stage 1 after 0 months" for as long as you like and looks like a
  bug. Cover drift (`network.active_cover_cost_ppm` 1%, `quiet_recovery_ppm` 3%) is what makes
  the alternation work.
- **Adding a truth field bumps `wwx-truth-vNN` by hand** (`crates/core/src/sim.rs`, written
  into the hash) and the recorder must run again; the century and campaign hashes WILL move
  even when no behaviour did, because the hash covers truth. Say that in the commit.
- **A design doc that adds persisted fields must not promise an unchanged century hash.**
  New hashed fields move the state hash even with every new coefficient at zero, so
  "neutral values reproduce today's hash" is a false acceptance test and an implementer
  will chase it. Specify a **paired observable-series comparison** instead: price,
  inflation, output, trade, GDP, SoL, every campaign decision and projection field must
  match the pre-change run, with the `wwx-truth-vNN` bump recorded in the commit and the
  stored campaign re-recorded (its readings, not its hash, are the proof).

- **Re-record the stored campaign after ANY rule change**: `cargo test -p wwx-cli
  --test record -- --ignored --nocapture` rewrites `tests/replay/first-slice.{json,play}`.
  Until it is re-run, `item_1_the_campaign_replays_month_by_month` fails on the old
  hashes — that is the designed signal, not a bug.
- **Prove the `.play` transcript still reproduces**: feed it back through
  `wwx play --seed 3 --campaign /tmp/regen.json < tests/replay/first-slice.play` and
  compare the two JSON files. The recorder prints the campaign's own facts (losses,
  refusals, scoreboard) — read them rather than describing what should have happened.
- **Adding a tuning value is a four-file chain, and the compiler only names three of
  them**: core `balance.rs` (the field + its `Default`), `content/balance/balance.json`
  (the value *and* the `$comment` that says whether it is authored or the builder's),
  the validator's two lists in `crates/content/src/validate.rs` (authored in §16.2.5 vs
  chosen under W-073 — a value in neither list is a validation error), and
  `crates/session/src/balance.rs` (the `content.balance_or("key", default)` mapping).
  Miss the validator and `wwx validate` fails; miss the session and it does not compile.
- **Passing the four-file chain proves a key is DECLARED, not that anything READS it.** Grep
  the field name in `crates/core/src` excluding `economy_balance.rs`; hits only in
  `session/`, `content/` or tests are the mapping, not a reader (`economy.devalue_inflation_ppm`
  is authored, validated, mapped and dead). For a tuple or struct field, check **each**
  component: `currency_attacks` stores `(until, inflation, flight)` and the monthly fold reads
  only `flight`, so the attack's inflation leg silently does nothing. Confirm the reader sits on
  the monthly path from `systems/economy.rs` (or a command in `systems/inputs/`), not only in a
  fixture, before saying a mechanic works.
- **A second coup in one campaign IS reachable (W-085), but the rebuild is fragile.** The failure
  burns the network, so `net` re-establishes it and the party is funded again — but the failure also
  leaves the government's attention high, and a channel left ACTIVE through the whole rebuild burns
  its cover below 20% within ~40 months and takes the second attempt with it. The working transcript
  is `TO_A_SECOND_ATTEMPT` in `crates/cli/tests/slice_loop.rs` (seed 4: attempts at months 82 and
  123, `quiet` spells between the cultivations).
- **An order queued in the same month as a coup is processed BEFORE the burn.** `net state:X`
  beside `coup state:X` is refused ("a network already exists") because the resolution happens
  later in the tick: put a blank line (run a month) between them in a `.play` transcript.
- **An assertion on a line that has a twin proves nothing: isolate the line first.** `preparation:`
  is followed on the next line by the same reading's confidence and date, so a `text.contains("as of
  month")` for the band passes whatever the band says. Flatten, cut from the anchor to the next `·`,
  then assert on that. Same trap for any line printed beside the terms it repeats.
- **A new `StateCore` field lands in ~17 fixtures at once**: each has an `aftermath: None,`-style
  line, so append the new field after every one of them in a single scripted pass (find the sites
  with `cargo test --workspace --no-run`); by hand you will miss some.
- **The CLI test binary prints whole campaigns**: redirect `cargo test` to a file and grep the file
  rather than piping through `tail` - a pipe throws away the exit code and floods the context.
- **The core's test harness has no `truth_mut()`.** `Sim` exposes `truth()` only, so a
  core test cannot repair the world between attempts — and the coup's test needed that:
  `BurnNetwork` *removes* the network (`effect.rs`), `EstablishNetwork` only raises reach
  *through* a network that exists ("no network there to build it through"), and the inputs
  phase refuses any order in a country the player has nothing in. Build the world's
  starting position in the `Truth` before `Sim::new`, and expect a second coup in one
  campaign to be out of reach (recorded as W-084).
- **A core test fixture must fill `verb_roles`.** `SimConfig`'s `verb_costs` gives a verb
  its price but `verb_roles` gives it its *kind*; without `VerbRole::FundParty` /
  `VerbRole::Political` the inputs phase refuses the order and the test measures nothing.
  `Fixed::from_ppm` takes `u32`.
- **Editing Rust source through `execute_code` can mangle `\n` inside string literals in
  your *anchors*.** An anchor containing a `\n` escape silently matches nothing (found 0,
  expected 1) while reads of the same text look right. Prefer the `patch` tool for
  anything spanning string literals, or anchor on backslash-free prefixes and compose new
  escapes at runtime (`chr(92) + "n"`). Verify every write with `touch <file> && cargo
  build`, because a 0.07 s "Finished" is a cache hit, not a compile.
- **A new field on a core struct breaks every test fixture.** Find them with
  `cargo test --workspace --no-run` and fix them with one `execute_code` rewrite
  (`StateCore`, `SimConfig`, `TickContext`, `VerbCost`, `ScriptEntry` are the usual
  suspects).
- **Projection functions are capped at 7 arguments by clippy.** Threading a third
  namer in means bundling the closures (see `Names` in `crates/projection/src/view.rs`).
- **Bump `VIEW_SCHEMA` whenever the view's shape changes** (now `wwx.view/5`) and update
  the projection/protocol tests with it.
- **A new view block must obey the fog rules**: the coup readiness reads the observer's
  *own* book only (its network, its pawns, its faction's rung) so it can say "not yet"
  where the world would accept the order and never the reverse.
- **Another patron's pawns are invisible unless an instrument reads them** (T8.2, view/14).
  `SecretView.movements` carries a foreign-funded faction only where the observer has an
  *unturned* network inside that country, as `Attribute::through(value, confidence, as_of)`
  — believed, confidence = the network's penetration (W-101's rule for a stability reading,
  same instrument). No network, no entry; a turned network reads nothing. This replaced the
  older absolute rule ("never visible"), because a rival's contest of a client is years of
  build-up the player must be able to see; keep the "believed, not verified" half of it.
- **Expose read-only rule readings from the core rather than re-deriving them**:
  `pawns::coup_readiness` reads the same `COUP_RUNG` the world tests, so screen and world
  cannot drift.
- Shadowing a function with a local (`let mut rung = 0` above `fn rung`) is `E0618`.
- `SecretSet` has no `iter_mut`: collect the ids, then `entry_mut(id)`.
- **§12.2's "no odds anywhere" binds CONTENT PROSE, and prose is where it breaks**: when
authoring a verb's `effect`/`risk` (W-097, content schema 4), writing the risk naturally
reaches for the number that makes it feel precise ("a 10-20% chance a stage fails"). That
is the rule the coup's screen comment calls out, and the M1 sequence test catches it
(`!text.contains("% chance")`) before a reviewer does. State the failure's CONSEQUENCE
(what it costs, what it leaves behind, who ends up suspicious) and no probability.
- **Bumping `SCHEMA_VERSION` silently disarms tests that spell the version**: the content
pipeline test replaced a literal `"3"` with an unsupported one; with the literal left
behind it tested nothing. Read the constant (`wwx_content::SCHEMA_VERSION` — which also
has to be re-exported from `lib.rs`) instead of spelling it. `content/**/*.json` all carry
`schema_version`; bump them with one script (`json.dumps(d, indent=2, ensure_ascii=False)\n`
round-trips these files byte-identically, so a programmatic rewrite is safe).
- **`screen::wrap` collapses whitespace**, so a new block cannot arrive as one string with
embedded newlines: return the extra lines as a `Vec<String>` (`parse::explain`) and let
caller print each through `wrap`.
- **A content-only change still moves the stored campaign**, because the campaign records
the content fingerprint even when no rule moved. Regenerate with the recorder and then
CHECK THAT THE WORLD HAS NOT MOVED: an interface/prose pass must leave the century hash
and the campaign's final hash identical — that identity is the proof the round changed only
what the player reads, and it belongs in the commit message.
- **An attention item must be an order the player can follow.** `is_exposed()` is
  `reach > cover`, so a channel cultivated past the cover it can hold can NEVER be
  un-exposed by quieting: printing "quiet it to recover cover" for it is asking for the
  impossible, every month, forever. Gate such advice on the action being able to help, and
  state the structural case as a fact about the channel in the dossier. The same rule covers
  a *clock*: "withdraw funding to delay it while fidelity remains" is not an order for a
  faction nobody is paying, so read the advice off the pawn's own fields (`funded`,
  `fidelity`) and name the commitment that does persist (the timetable was set when it armed,
  W-091, W-109).
- **A view field holding a `Tick` is not a month: convert with `player_month_for_tick`
  everywhere the screen says "month".** When two blocks print the same deadline and disagree
  by one or two, this is why - `screen.rs` converts and `parse.rs`'s funding row printed
  `pawn.proxy_due` raw ("mobilises at month 60" against the dossier's month 62 in the same
  second). Grep every print of a `*_due` / `protected_until` field, not just the one in the
  report.
- **Prose assertions break on the screen's own wrap.** `screen::wrap` breaks at 78 columns,
  so `text.contains("a long sentence")` fails for a sentence that is present. Flatten first:
  `let flat = text.split_whitespace().collect::<Vec<_>>().join(" ");`
- **Bumping a version string across the docs: replace only CURRENT-STATE claims.** A blind
  `sed`-style replace over `docs/` rewrites history too — a W-item's "this changes persisted
  truth to v13" must stay v13 while the status/protocol lines move to v15. Grep every hit and
  classify (owning-section claim vs status claim) before replacing.
- **The remote is `origin`, not the ssh alias.** `git remote -v` shows
  `git@github-wwx:promunb/wwx.git`; `git push github-wwx main` fails with "does not appear to
  be a git repository". Push with `git push origin main`.
- **Never force-push, and never rewrite a commit already on `origin/main`.** The owner pulls
  this branch himself, so a rewritten tip strands him on a commit that no longer exists. Amend
  before the push or make a follow-up commit — a "let me fold that note in" amend after the push
  is the exact move that breaks it.
- **A rule change moves the hashes, so the docs move too**: `tests/replay/README.md`,
  `docs/status.md`, `docs/first-slice.md` and the W-item in `docs/design/00-open-questions.md`
  all carry measured numbers. Read them from the recorder's own output, never from memory.
- **"Is this news?" must never be a latch over the belief store's history.** The store keeps its
  corrections (R11), so "no earlier reading about this subject was actionable" becomes a one-time
  trigger: once a month-39 intrusion was dealt with, every later intrusion on that subject read as
  old news and a 12-month batch ran past a month-81 one. Resolution lives in the world's own record
  of the response — `ci::resolve` closing the file plus the successor reading (`value = 0`, "nothing
  there") written the same month, mirrored in the ledger's `network-turned`/`network-rolled-up`.
  Read resolution, not history.
- **A cause names the same faction, not the same country.** `journal_about(state, ...)` matched any
  report about the country, so an investigation into the player's OWN faction was printed as what
  "explained" the rival faction's 39-point rise. Keep the honest absence ("nothing we did explains
  it") for anything that does not bear on the pawn that moved.
- **A projection must price the plan in the order it runs, from the same function the world
  charges with.** `orders` priced each order against the view as it already was, so a faction funded
  through a merely *queued* network came out at 0: the plan read 7/month and the world charged 9.
  One function (`programme::charge_a_month` and its callers), programme and holding phases shown
  apart, and a test that reads the promise off the screen and the charge back out of the world.
- **A comparison must be like with like, and a delta must reconcile with the pair beside it.**
  `StateCore::previous` kept the service's last attempt *anywhere*, so a Holdfast failure was shown
  against a Frontier success; it is now one attempt per country, and a first attempt in a new
  theatre names the theatre and the terms that differed instead of printing a delta.

## Older status note (v0.8)

All seventeen sections (00-16) were drafted as of v0.8; each section carries its
own [DECIDED]/[PROPOSED]/[OPEN] tags.

## Two architectural rules that bind the mechanics

- **Belief states** are required from the start: the AI (and arguably the
player) reasons from suspicion + confidence + provenance, never from truth.
Do not design a system that assumes anyone can read the world state.
- **Level of detail**: FOCUS (player has networks) / ACTIVE / AMBIENT,
promoted and demoted automatically. This is what makes a century at a monthly
tick over ~190 states affordable.

## Visual language (proposed, not ruled)

The repo has a UX spec but no visual-identity spec (grep `docs/design/` for a
visual thesis before repeating that): §12 defines the surfaces,
§12.10 accessibility and §14.6 voice, but not what anything looks like. The
palette lives in `crates/cli/src/map.rs`; the playable REPL is monochrome text;
`apps/ui` is an economy renderer scaffold. Treat the look as undecided, and do
not quote an analysis as a ruling.

- **The map is political, not terrain.** §3.3 makes terrain visual/movement-only.
  Spend the art budget on fog, networks, instability and graded influence.
- **Fog is the signature visual.** Observed / believed / unknown must be distinct
  in greyscale and colour-blind, with confidence and as-of on believed. Never let
  unknown share a fill with known-zero.
- **Do not paint ownership as solid fills.** It teaches conquest and contradicts
  Pillars 1–2. Use fills, hatching and patterns for tiers and networks; reserve
  solid fill for sovereignty.
- **The unruled decision that gates the look:** §12.6's document-not-dashboard is
  `[PROPOSED]` (and absent from the register), and W-052 (tone) is open. Rule both
  before the visual client starts.
- **Palette defect to check:** the resistance mode uses with-you `#2f855a`
  against against-you `#c53030` — red/green, the pair §12.10's colour-blind rule
  exists to prevent. The `<title>` preserves comprehension; the fill still fails
  the rule.
- **Build order:** step 10 is the briefing/reckoning; W-006 is the map client and
  W-072 the browser client. Decide the language now; do not build the client now.
- Detail, staging and the audit: `references/visual-language.md` (includes the
  current CLI/REPL screen audit). Class-level text-interface rules live in
  - Class-level rules: the `game-art-direction` skill's `text-interfaces`
    reference.

## Conventions (owner-agreed, do not drift)

- Every statement is tagged `[DECIDED]` (owner ruled), `[PROPOSED]` (design
draft to argue with), or `[OPEN]` (unresolved).
- **Every `[OPEN]` item is also mirrored into `00 - Open Questions`**, which is
the single source of truth. An item leaves that list only when answered and
written into its own section.
- Every section ends with an OPEN QUESTIONS block repeating its unknowns.
- Numbers belong in data files, not prose; sections point at spreadsheets.
- Pillars are written as a commitment AND a refusal - the refusal is the
load-bearing half.
- Numbering is two digits; later insertions take a letter (`08a`).

## Workflow

1. Read the document in `docs/design/` before editing it - never edit from memory.
2. Edit the markdown in place (whole-file rewrite through python in `execute_code`),
   keep the tags/numbering/stamp conventions, and commit. The Drive-era workflow
   (`deleteContentRange` + `insertText` batchUpdate, `documents().create` +
   `addParents`) is obsolete and must not be revived.
3. Verify by reading the file back and confirming the char count and opening lines
   actually changed.
4. To add a NEW design document: number it at the next free `NN`, register it in
   `docs/design/index.md` (section index AND the `STATUS: ALL N SECTIONS` count),
   in `docs/design-docs.md` (a row; the id column takes `— (authored in-repo)`
   because it has no Drive source), and in the `docs/index.md` "all N documents"
   row. Do **not** add a `_provenance.json` entry: that file maps Drive ids only.
5. **The set's version stamps are drifted** (docs sit at different `v1.x` and
   dates). Do not bump the whole set to write one new doc - that is a 20-file
   claim that every section was re-reviewed. Stamp the new doc at the newest
   content-document version, leave the rest alone, and update only the index's
   "last updated" date.
6. A new section still ends with a decisions/open block, and every `[OPEN]` item
   it raises must be mirrored into the register in the same pass - the draft
   document is not allowed to carry an unmapped open question.
7. Verify with `python3 tools/evidence.py questions` (the new ids must appear and
   the count must move by exactly the number added) and `git diff --stat` before
   committing.

## The step-8 war model (2026-10-17) — read before citing §03.6/§07.7

`docs/milestone-8-military-preplan.md` (commit `d2d4f3e`) replaces one-shot
auto-resolution with **conduct without command**. The build brief is
`docs/milestone-8-military-deterrence.md` (commit `6942010`); the pre-plan is the
shape, the brief is the W-058 build spec. The seven items it raised are RULED (2026-10-17): W-023, W-024,
W-025, W-038, W-039 and W-040 are closed (register 69 -> 64 pending: six closed,
plus W-205 added pending for the deferred umbrella) and W-014
is annotated with the split (annexation + W-027 handover now; full redraw later).
The answers are written into §03.6, §06.7, §07.3, §07.6, §07.7, §10.3 and §10.4,
and the alignment commit `dbdeb93` carries the rest (02.7, 06.2, 07.1/7.9, 08.9,
10.1/10.6, 11, 12, 13, 15, 16, 17) plus the second pass `fc06855`.

- **W-038/W-039 changed the plan: the owner wants unlock/research trees**, not
  era-scheduled availability. The tree is **step 8a**, its own milestone built
  BEFORE step 8; step 8 consumes one capability-availability interface. The
  design's earlier "technology level is a reserved zero" is dead. The tree spans
  §10.2's three domains and shares scarce research capacity; development stays an
  investment. AI states select by authored doctrine (continental, naval, autarkic,
  ideological) with a bounded 2-3 line / 2-node lookahead, not an exhaustive
  solver; the autoplay farm must gate AI competence on it (pre-plan §8.1).
- **W-040** is hybrid: historical anchors for AI states, moved by capability,
  sabotage, assistance and patron pressure; the player's programme is
  capability-driven.
- **W-024 / 7.9 THE THRESHOLD CRISIS**: direct attack on a nuclear state is NOT a
  conventional war - it is a THRESHOLD CRISIS: possible in principle, rationally
  suicidal in practice, legible before the player commits. The player chooses a
  nuclear doctrine (no first use / flexible response / massive retaliation /
  minimum deterrence); immunity from invasion is GRADED at second-strike
  credibility, not at the first warhead. A crisis can settle in concessions. The
  hard wall is the default doctrine, not an engine rule. A nuclear umbrella over
  clients is DEFERRED by name (W-205). Do not write a great-power war model.
- **Defeat boundary (2.7)**: a conventional defeat short of annexation, conquest
  or deposition is a SETBACK, not a run-end; those three remain loss conditions,
  and a threshold crisis that escalates to nuclear use ends the run.

### The step-8a technology tree (2026-10-17)

`docs/milestone-8a-technology-preplan.md` (commit `6675bdb`) is the pre-plan for
the capability layer step 8 consumes; the build brief is
`docs/milestone-8a-technology.md` (commit `6942010`). Binding shape:

- **Broad and shallow:** <=3 prerequisite layers, <=12 nodes per domain per era,
  one effect per node, closed effect vocabulary (unlock a capability / modify a
  named balance parameter / unlock a production method / enable an adoption). No
  new economic law, no labs or buildings, no random breakthroughs.
- **One universal tree**, three domains (covert, nuclear/military,
  social/economic). Knowledge is NOT exclusive - scarcity of capacity and
  adoption is the exclusivity; a few adoption forks only.
- **Research capacity is a monthly flow** from human capital (the ceiling),
  education priority, funding (diminishing), openness (absorption). Money cannot
  exceed the human-capital ceiling; one to three active lines; unspent capacity
  is wasted.
- **Research and adoption are separate**: knowing a design does not field it; the
  "know but cannot afford" reading names the binding constraint.
- **Five diffusion channels (anti-snowball):** espionage (existing covert
  actions, no new verb), trade/investment absorption, education, patron transfer,
  licensing.
- **AI:** doctrine (continental/naval/autarkic/ideological/nuclear/insurgent) +
  3-5 node programmes + bounded re-evaluation on binding constraints; same
  commands and beliefs; visible orientation; competence gate on the autoplay
  farm; historical band (W-040).
- **First build authors 1945-65 only (<=36 nodes).** Step 8 reads
  `Capability::available`; never hard-code era checks in the war model.
- **Phase order after both milestones:** inputs -> pops -> economy -> research ->
  networks -> war -> attribution -> lod -> ai -> output. `research` is 8a, `war`
  is 8; each adds a PhaseId and a phases.json entry. Research runs after economy
  and before networks; war runs after networks and before attribution.
- **All ten implementation questions are RULED (2026-10-17) as W-195–W-204** and
  written into design §10.6: capacity flow/ceiling, knowledge non-exclusive,
  research vs adoption, five diffusion channels, no randomness, tree size, AI
  historical band, derived scalar, whole tree visible, no obsolescence system.
- **The design alignment is written (commit `dbdeb93`)**: era-gated is dead
  (instruments are era-anchored and research-unlocked, 10.1/10.6); auto-resolved
  is conduct without command (02, 03.6); §07.9 is the threshold crisis; research
  funding is an investment earmark (W-207); civil war is re-deferred to the
  regime-axis milestone (W-208); the tick order is named in two tiers (W-209).
  Pending is 64.
- **Peripheral docs aligned (commit `2e75785`)**: design/index.md and 01-vision.md
  say great-power war is suicidal and rare, not impossible; glossary.md carries
  the technology/war vocabulary; decisions.md records the alignment; milestone
  6/7 carry explicit amendments; status.md names 8a/8 as specified, not started.
  The historical milestone text is preserved, not rewritten.

The research notes behind the reframe sit in the Drive folder **Grand strategy
competitor research** (`1HPPYDhY7QpZDnXaB-81xrCJNHRux0E08`): the Paradox feedback &
design-lessons study (10 Oct 2026), two Victoria 3 documents, two Espiocracy documents.
Fetch a doc with `google_api.py drive download <fileId>` under
`~/.hermes/skills/productivity/google-workspace/scripts/`. Do not re-search Drive for
them — finding that folder cost ~6 calls on 2026-10-17.

- The player commands **theatres and plans** — aims, force allocation,
  objectives, tempo, reserves, supply priority, rules of engagement, peace —
  monthly. **R2 stands: no units, formations, battles or tactical orders.**
  The §03.6/§07.7 amendment is WRITTEN (2026-10-17); do not describe the game as
  one-shot auto-resolve.
- Resolution keeps the design's three terms (strength + supply + fortification).
  The verdict is deterministic given truth; **upset comes from beliefs (unknown
  enemy reserves/supply/morale), enemy agency, and a bounded friction term**
  that cannot flip a decisive margin (an authored band).
- War has **three modes across the century**: conquest (1945–55 / non-nuclear),
  coercion and crisis (nuclear peers), proxy war. The milestone's verb is
  "close the door"; proliferation is the agency.
- **Mobilisation is part of the war model and consumes the economy** (manpower
  by class, military goods, supply, treasury). Implementation rule: war reads
  existing economy interfaces and adds no new economic law.
- **The one nuclear rule is unchanged**: any player nuclear use ends the run,
  a nuclear attack on the player ends it, no accidental launches, AI-vs-AI
  exchange needs a human hand (R4).
- Non-nuclear states are invadable; **conventional defeat is a setback, not a
  run-end**. Crisis responses are graded and RULED (W-024, 2026-10-17): the
  pre-plan's §9 ladder is the binding shape.
- Acceptance gates include **AI competence** (the rival must declare, conduct
  and terminate a war; if it cannot use a lever, cut the lever) and the
  legibility contract (war estimate, monthly front dispatch, decision-point
  notice, ledger; no odds anywhere).

## Design state you must not contradict

Settled frame: pausable real-time; player is the STATE via a chosen fictional
leader with traits, no ageing, deposition = campaign loss; all sovereign 1945
states playable, difficulty emergent from the start; US 1945 = easiest,
occupied Germany/Japan = hardest; SP first; playability beats realism.

Nuclear spine: nuclear status is a PROPERTY (untouchable), escalation is a
JUDGEMENT; any use by the player ends the run; being attacked ends the run;
NO accidental launches; nuclear war between two other states is survivable.
Seed `"The bomb is armour, not artillery"`. The player races for a bomb AND
sabotages others' programmes.

Covert action is the core system: three-layer attribution (op resolves ->
suspicion -> investigation hardens evidence), false flags both ways,
blowback international AND domestic, agency-vs-agency moles, 20 confirmed
verbs, abstract networks (no named agents at launch), real + black budget.

**Economic coercion (doc 18) - the settled shape, do not contradict it:**
one unit, no FX, no parity (the peg is deferred); the freezable/seizable set is
foreign asset titles and cross-border loans **only** (no offshore deposits, no
foreign bond holdings); counterfeiting is a covert 1971+ programme that credits
private deposits, and the **banking system's equity** bears the detected
write-off (the bounded last-resort recapitalisation covers a shortfall);
blockades are **held** until step 8a/8's naval capability, with no stand-in
scalar; capital flight is the reserve-and-liquidity channel only - there is no
asset market to crash; coercion cost lives in the existing relationship fields,
not in the hegemony index; the new overt acts are discrete commands with a
status and a lift, not levers. The inflation loop's shape is ruled (money
overhang, wage-lag erosion, one-time devaluation step, detection write-off);
its coefficients are builder calibration, not adopted values.

## The two flags the owner still owes an answer on

The **lifespan problem** (a leader who must live 100 years) and the **closing
door** framing (proliferation removes targets all century and is the pacing
spine). Re-read `04.3` and `07.6` before extending either.

## Last four items closed in v0.9

- **Turned service goes silent** (12.8): a penetrated service never lies, it
stops producing. Silence is the tell. The player is never deceived, only
un-informed by omission.
- **Victory threshold**: 100% of great + regional powers at tier 1, plus **80%**
coverage of all other states (9.2). A campaign ending near 60% is a
"respectable loss".
- **No narrator** (14.6): the game speaks only through documents - the DISPATCH,
the LEDGER, the RECKONING. Tone (sober/understated) is still the standing
default, not owner-ruled.
- **Three deliberate deferrals**, none of them blocking: the real-figure bank's
size (grow a pilot, size it from use), concrete performance numbers (set when
there is a build to profile), and the tone of voice.

## Settled technical decisions (section 17)

- **Stack: Rust** (simulation + AI, no engine, fixed-point arithmetic, single
threaded first) **+ TypeScript** presentation. Owner's own preferred languages.
- **Browser build first**, desktop (Electron) later — BUT THE CORE NEVER RUNS IN
THE BROWSER. The Rust core runs as a PROCESS: on a server for the browser
build, locally as a sidecar for the desktop build. The UI is a thin client over
a versioned protocol (17.14). An earlier draft wrongly claimed the core would
compile to WASM; the owner corrected this in v1.2. Consequences: the core stays
native (no WASM 32-bit ceiling), the autoplay farm runs the same binary, one
protocol serves both deployments, and the shape is already MP-ready.
- **Built on the owner's laptop**; the Avoton server is an assistance machine.
- **Projections only**: the UI may never read world state. This enforces the
"map never lies" rule structurally.
- **Condition logic = JSON condition trees**, not a scripting language.
- **Geodata (licences verified at source, do not re-research):**
  - Natural Earth — **public domain**, commercial OK, no obligations. Backbone
.
  - OpenHistoricalMap — **CC0/public domain**.
  - Cliopatria (Seshat), geoBoundaries — **CC BY 4.0** (attribution only).
  - **AVOID: GADM** (non-commercial only), **CShapes 2.0** (CC BY-NC-SA),
    **aourednik/historical-basemaps** (GPL-3.0). OpenStreetMap is ODbL — usable
    but unnecessary.
- **Multiplayer: not now.** Solo play first; the command stream keeps lockstep
feasible for free.
- **Repo layout: deferred** — design first.

## Recording a design correction

The owner corrects design inferences he disagrees with, and the correction is
always right to record in the doc as a CORRECTION rather than silently edited
away — he re-reads. When he corrects an architectural inference, name the wrong
version explicitly in the doc so it cannot creep back.

## The open-item register (v1.2 — read this before citing any item id)

`00 - Open Questions` is the register and the single source of truth for what is
UNRESOLVED. It uses **opaque, permanent ids `W-001`…`W-063`**, assigned by
appending only — never reused, renumbered or sorted into place.

- **The old `Q-nn` ids are DEAD.** They were assigned in elicitation order while
the docs were numbered by topic, so `Q-5.5`, `Q-11.x`, `Q-13.x`, `Q-14.4` and
`Q-16.2` each meant two different questions in two different documents. Never
cite them; never reintroduce the pattern.
- **Closed decisions live in their owning section, not in 00.** A section ends
with an `OPEN ITEMS FOR THIS SECTION` block that is a convenience index and
carries NO status; 00 is authoritative. Sections that have decisions worth
recording (17) also carry a `DECISIONS TAKEN IN THIS SECTION` block.
- **Blocking rules are marked R1–R8** in the register. R1 (the programme model,
W-029) gates the first slice.
- When adding an item: append a new W-id, add the row to the section table in 00,
and add the id to that section's index block. Never restate status outside 00.

## Technique that works here

A full-set review (all 19 docs) found the highest-value defects were NOT missing
design — they were **drift between the register and the sections**: decisions
recorded closed in one place and still shown open in another, and cross-refs to
sections that had moved. Mechanical checks that paid off, in order:
1. every cross-reference `N.M` validated against the target doc's section list;
2. every number appearing in 2+ docs, with context, side by side;
3. every `[OPEN]` / `[DECIDED]` / `[PROPOSED]` tag counted per doc, then each
   open item checked for whether its answer already existed elsewhere;
4. spelled-out numerals ("six tiers", "fourteen types") — digit-only scans miss
   contradictions phrased as words.

When a `[DECIDED]` line and a `[PROPOSED]` line in the same section disagree,
delete the superseded one — do not leave it above the decision it contradicts.
When an earlier draft of a doc is wrong, record the correction in place
("CORRECTED in v1.2: …") rather than silently editing; the owner re-reads.

## Ruling log (do not re-litigate these)

- **v1.3:** R2 combat (03.6 binds — strength+supply+fortification, no terrain
modifiers, auto-resolved, player sets aims only; no formations/sieges/orders),
R4 (AI-vs-AI nuclear war requires the player's hand), R5 (instability is
TWO-level: per-group ladder 1–5 with a downward path, plus a state-level outcome
table), R6 (annexed states count as won and leave the coverage denominator;
index has a 6th negative term OCCUPATION BURDEN), R7 (the figure bank fills the
player's own government — every post except head of state), R8 (actor roster is
TWELVE; foreign intelligence services removed as a state actor).
- **v1.4:** R1 — the 20 covert verbs fall into FIVE FAMILIES and the family
decides the mechanics (8.9): **A** programmes (7 verbs, one shared stage engine),
**B** political endgame — coup + election interference (bespoke), **C** the duel
— counter-intelligence (bespoke), **D** pawn actions (8 verbs, no new mechanics —
AUTONOMY/instability already implement them), **E** instruments (2 verbs, belong
to 06/07). Eight of twenty verbs need no new code. Residue: W-065 (sign-off on
the assignments).
- **v1.4:** W-064 — POLE-HOLDER starts (US, USSR) play DENIAL AND RETENTION, not
acquisition: dissolve the rival bloc, hold your own sphere at or above its
starting coverage. The acquisition threshold (100% great/regional + 80%) is the
RISING POWER's win condition.
- **v1.7:** **16.2 THE FIRST SLICE taken to buildable depth** (doc 16 grew
  7,742 -> 25,333 chars). Sub-sections 16.2.1 why (three questions the slice must
  answer) / 16.2.2 the scenario / 16.2.3 the six verbs with stages, costs and
  effects / 16.2.4 the month in play / 16.2.5 the numbers (authored in
  content/balance/balance.json) / 16.2.6 the data model (Programme, Stage,
  Investigation, Pawn, Blowback, Script) / 16.2.7 the executable acceptance test
  / 16.2.8 deliverables in order / 16.2.9 the trap / 16.2.10 what it cannot
  prove. Registered W-069..W-073; register now 55 pending / 6 deferred. The whole
  set was re-stamped v1.7 (281,599 chars).
- **v1.8:** **ALL FIVE SLICE RULINGS LANDED** (16.2, register closed; 50 pending /
  6 deferred). W-069 fictional states. W-070 "all of the above, maybe" read as
  LAYERED in 16.2.7b — the scenario stops at 1965, a scoreboard line prints, a
  provisional win/lose is evaluated (win = a state's tier moved to friendly; lose
  = a hostile network still inside the player's own service), and the campaign may
  continue unscored. **This reading is the register's, not the owner's words —
  confirm it before 16.2.7b is treated as settled.** W-071 the rival's network
  starts inside the player. W-072 the slice's interface is a terminal REPL.
  W-073 the 16.2.5 numbers are authored.
- **v1.8 build:** 16.2.8 step 1 done (commit `cdba9b0`): four content types
  (programmes, events, scripts, scenario) with schemas, Rust support in
  wwx-content, and the slice dataset. Six new validator guards make the rulings
  structural. Then steps 2-8 were built, finishing at v1.10.
- **v1.9:** family rulings while building the pawns: a funded party's autonomy drifts
  with the pay; holding costs money and an unpaid holding is LOST, not burned (W-074);
  the coup gets no new phase (it is hosted in `networks`); content names each verb's
  mechanic (`mechanic` in `verbs.json`) and the session maps it to the core's `VerbRole`.
- **v1.11 (2026-09-22):** the screen learned to say *why* and the three family B/D verbs
  were examined. Legibility: `EndReason` on the programme (truth v7, view/6) so a dossier
  says `dropped (it could not be kept up)` and not just `dropped`; the dispatch now ranks
  the month instead of taking its first three records and counts what it did not print;
  `ledger` prints the month in full. Content: `event:newspaper-nationalised` no longer
  pays the player's home exposure back (§16.2.3 verb 6 says the exposure is kept).
  W-080 the coup's blowback fires on **every** failed attempt (it was borrowed from a
  once-per-pair standing rule) and the ladder precondition's world-reading is written
  down; W-081 disinformation is named as out of the slice; W-082 the party's pace halved
  (3%/month growth, 1% decay); W-083 the ladder has exactly one reader (the coup) and
  funding one is invisible; W-084 nothing but cultivation can build a network where none
  exists. `crates/core/tests/pawns.rs` is the evidence for W-080.
- **v1.10 (2026-09-22):** the slice is built and its five residue items are ruled —
  W-075 (i) the family D exception, written into §8.9's D row; W-076 the builder's
  numbers accepted; W-077 (a) the asset's cover cost, so `event:asset-escapes` fires;
  W-078 the verdict reports both endings; W-079 (a)+decay, exposure capped and aged.
  The projection gained the pawn dossier and one coup-readiness line per country
  (`wwx.view/5`), which is what makes the ninth human question answerable on screen.
  Register: everything the slice raised is closed; what is left is tuning and the
  target's half of the duel.
- **Nothing blocks the first slice.** Next act is 16.2.8 steps 2-5: the stage
  engine, the attribution layers, blowback, and the scripted opponent.

- **v1.5:** §17.15 THE RUST CORE: STRUCTURE AND ORGANIZING PRINCIPLES — written and
owner-approved, now binding; resolves A-17.6 (repo layout, previously deferred).
The five commitments: the core is a **library** (no `main`, no IO/async/clock in
the sim crate); determinism lives in the **types** (float arithmetic and
hash-ordered collections are build errors); **truth / belief / derived** are
three separate stores (so the AI is handed beliefs and structurally cannot reach
the truth — AP4/AP5 enforced by capability handles); **plain typed tables, not an
ECS** (stable iteration order + serialization + agent legibility); the **wire sees
DTOs, never internal structs** (this is what stops fog leaking over the process
boundary). Plus AP10–AP18 in §17.15.2 (command stream is the only doorway in;
strings are identity, integers are runtime handles; no code plugins in mods; no
parallelism yet). Crate graph: content ← core (time/ids/fixed/truth/belief/
systems/ai/command/ledger) ← projection ← protocol/session ← cli/server, one-way
only. Registered residue: **W-066** (lost detail when a demoted province is
promoted), **W-067** (derived randomness, amends 13.1), **W-068** (save carries
its own content, makes 13.6 keepable).
- Doc 13's index key is '13 - Simulation & Architecture' (not '...Architecture'
alone) — check `_index.json` keys before addressing docs by name.
- **v1.6:** **W-066 COMPOSITION FINGERPRINT** (5.2) — the LOD loss problem. Demotion
merges province pops into region aggregates and promotion can't un-merge them. Key
insight: while demoted the groups **weren't being simulated, so no history was
lost** — the job is to produce a deterministic distribution consistent with the
aggregate, not to recover state. Each province writes a fingerprint on demotion
(fixed-point `(group, share)` list summing to exactly 1); promotion re-splits along
it, so totals are exact and only the distribution quantises. **No randomness** in
the re-split, so promotion is bit-exact; repeated demotion doesn't accumulate
error; never-FOCUS provinces fall back to authored composition. A fingerprint
(rather than authored composition alone) is required because the game tracks
expulsions/massacres — a province whose minority was exterminated in 1951 must not
repopulate itself if the player looks away until 1974.
- **v1.6:** **W-067 DERIVED RANDOMNESS adopted** (AP17; 13.1 amended) —
`hash(campaign_seed, purpose_tag, entity_id, tick)` per draw, not one shared stream.
Purpose tags are a fixed versioned enum. Not immunity to code change —
*localisation* of it. Also what makes deterministic partitioning possible later.
- **v1.6:** **W-068 SAVE CARRIES ITS CONTENT adopted** (AP18; 13.6 amended) — one file
is one complete campaign; makes 13.6's frozen-content promise keepable.
- Register now at **50 pending / 6 deferred**. 17.15.7 records the four
core-structure proposals (A–D) and their resolutions.

## Pitfalls

- **Google's markdown export over-escapes punctuation** (`cost\_a\_month`, `\[DECIDED\]`).
  Un-escape `\- \= \[ \] \( \) \* \# \.` and `\_` *between word characters* (mid-word
  underscores are identifiers, never emphasis); leave `\|` and backticks alone. The
  puller does this; do not re-derive it by hand.
- **Writing the code: generate it with a script, never by hand.** The core was
  built by numbered generator scripts (`~/.hermes/cache/scratch/wwx_*.py`), each
  writing whole files, then `cargo fmt` + the gate. Re-runnable, reviewable, and a
  failure costs one script run instead of a hand-edit.
- **Run the generator before patching what it writes.** Two `patch` calls failed
  with "Failed to read file" because the script that creates the file had not been
  run yet. Order: run script → then patch.
- **Docs written ahead of code drift aspirational.** `docs/status.md` originally
  described crates that did not exist yet (a TCP listener, a stub `autoplay`).
  After any build, re-measure every claim in the docs and correct it — the docs are
  read by the next agent as fact.
- **`read_file` prefixes every line with `N|`.** Never write that content back; a
  whole-file edit goes through python in `execute_code`/heredoc.
- **`search_files` returns one of two shapes**: `{matches: [{path, line, content}, ...]}` or,
  when it formats for reading, `{matches_text: "..."}` — read both keys, and drop `file_glob`
  if you need the structured list (a filtered call came back with the text shape and zero
  matches while the unfiltered one had hits).
- **A test failure is not always a test bug.** Two "LOD" test failures turned out to
  be real: pops grew a province inside the tick that promoted it, and states with
  modelled provinces did not track them. Read the numbers before "fixing" the test.
- Do not write a section that is still `[OPEN]`-blocked without tagging it;
- Do not silently resolve a contradiction: surface it in chat AND in
`00 - Open Questions`.
- Your memory of the schema versions is worthless; the code is the source. The register's
  prose lags the code (it still asserted `wwx-truth-v9` stood where `sim.rs` hashes
  `wwx-truth-v12`). `grep -rn "wwx-truth-v\|wwx.view/\|wwx/5\|wwx.campaign\|wwx.save"`
  over `crates/` before quoting any schema id.
- The owner answers questions in bulk and terse. Ask in numbered blocks, put
recommended defaults inline where a decision is cheap, and never re-ask a
closed item. When he answers "all as recommended", treat every one as ruled and
close the whole block in one pass - answers into the owning sections, tags
flipped, register entries moved to the closed history.
- **The persistent terminal session's cwd can point at a deleted scratch directory,
  and then even `cd ~/repos/wwx` fails while the target exists** — the error names the
  OLD path, not the target. Pass `workdir=/home/faraz/repos/wwx` on the terminal call
  instead of prefixing with `cd`; the next call inherits the good cwd.
- **"Is it done?" is answered by the milestone's acceptance table, not by commits or
  status bullets.** Code in `main`, a green routine gate and a stack of phase documents
  can coexist with failing acceptance axes (`docs/economy-evidence.md` has an explicit
  Pass/Fail/unmeasured table). Say which axes fail; never call a milestone finished
  because its implementation landed.
- **`content/balance/balance.json`'s `$comment` is an append-only rationale log,
  not a description of the current numbers.** It still explains the superseded
  60/26/14 grievance split while `values` carries W-157's 45/20/10/25, and it
  narrates every retired key. Read `values` for behaviour, `$comment` only for why
  a number was once chosen; when prose and `values` disagree, `values` is the
  world and the prose is history.
- **Any count in prose is stale by the next content revision.** Cell counts in
  code comments and design docs (159,329 / 160,113) predate the current content;
  recompute from `content/` before quoting a world size. The same applies to
  "how many groups/provinces/states".
- **A "what is missing to implement X?" answer grades each ask against its GATE and
  its SUBSTRATE, not against a feature list.** Foreign investment, extraction terms and
  forced loans are `patron`-gated (installed client only); supply cuts are 1960+ and
  food/energy only; currency attacks are 1971+ hard-coded in `inputs/programme.rs`.
  Freezes, seizures, capital flight as a flow and collateral have no substrate at all —
  there is no foreign-claims register — and blockades have no navy (§07 step 8 is
  unstarted). Calling a feature "built" without its gate, or proposing one without the
  substrate it needs, sends the next session building on sand.
