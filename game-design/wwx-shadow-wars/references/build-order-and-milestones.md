# Build order, milestones, and "what is next?"

Use this when the question is about the state of the build rather than the text of a
design document: "is the economy done?", "what comes next?", "what does milestone 8 do?"

## The authority chain (read in this order)

1. `docs/index.md` — the router. One row per document, including every milestone.
2. `docs/design/16-production-scope-risks.md` §16.3 — **the build order**, normative.
3. `docs/milestone-N-<topic>.md` — the brief for each step and its record after it closes.
   Per W-058 there is **one plan document per milestone, written before the build** and
   kept afterwards; the first deliverable of a step is that document, not code.
4. `docs/status.md` — Informative. Current build, one line per item, 400-line cap enforced
   by `tools/check-status.sh`. Never a source of rules; it lags the code.
5. The milestone's own evidence/acceptance ledger — see `docs/economy-evidence.md`
   ("Acceptance status") for the economy. This is the only honest answer to "is it done?"

## The ladder (§16.3)

1. The covert slice (§16.2)
2. The belief model and the AI that consumes it — a believable rival
3. Autonomy and the pawn system
4. Pacts, alignment and the hegemony index — §9.2's index and §9.3's relationships only;
   the §9.6 diplomatic verbs are not built
5. The map and level of detail
5b. The full 1945 dataset (69 states, 1,977 provinces)
6. Population and instability at full resolution
7. The economy, segmented and set-and-forget (eight sectors, seven goods categories, no per-good prices)
7b. **Political organisations and state power** — inserted before 8a; the layer 8a and 8 consume and
   9 scores (organisations replaced pawns; regimes/institutions own state power, elections,
   repression, insurgency, deposition)
8a. **The technology and research tree** — built BEFORE step 8; step 8 consumes one
   capability-availability interface and must not hard-code era checks
8. **The military, deterrence and the proliferation race (§07 + §10)**
9. Anchors, fallbacks and the figure bank (§14)
10. The briefing, the 2045 reckoning and the long tail of content

Milestone documents use the same numbers as the steps, lettered insertions included.
**A lettered step means "step 8" is not the next step** — 7b and 8a come first, and an
agent that schedules 8 next re-derives a plan the design already superseded.

State of the ladder — re-verify it, never quote it from this file. 1–5b built, 5b
accepted; 6 built with its last design presented rather than formally accepted; 7 built
and still under qualification (the economy advances by numbered laws, so cite the law
from the pin block in `docs/status.md`); 7b built with its acceptance record explicitly
*not* accepting it; 8a and 8 specified and not started; 9 and 10 not started. "Built"
and "accepted" are different words; see the last section.

## Step 8 — what the design already settles

- **War model (§03.6):** army strength + supply + fortification, no terrain modifiers,
  auto-resolved over weeks. The player sets war aims and commits strength/supply; no
  tactical command, no formations, no sieges. Territorial control shifts province by
  province, producing a visible front.
- **Navies and air (§03.7):** national capabilities at the projection layer — sealift,
  blockade, basing, submarine/ASW, strategic reach, airlift, reconnaissance — not fleets.
  Sea zones are geography already; the capabilities arrive here.
- **Nuclear spine (§07):** status is a property, escalation is a judgement; any use by the
  player ends the run, being attacked ends it, no accidental launches, and an AI-vs-AI
  exchange requires a human hand (R4).
- **Proliferation (§10.4):** a five-stage programme — theoretical research → fissile
  material → weaponisation → delivery → second-strike survivability — every stage
  detectable and attackable; counter-proliferation is the primary military/covert seam.
  The player pursues acquisition AND sabotage.
- **Graded deterrence (§07.5):** windows where the bomb is held but retaliation is not
  credible; immunity from invasion only once second strike is survivable.
- **The closing door (§07.6):** the invadable set shrinks as the nuclear set grows —
  the pacing spine, with era brackets as tuning values.
- **Proxy war (§07.8):** a logistics pipeline (money, arms, advisors, training), the
  proxy can win or lose, the escalate-or-cut decision is real, and a winner becomes a
  client by handover (W-027).
- **Civil war** belongs to this step (deferred from population), because it needs an army,
  a front and supply. Secession, collapse and foreign takeover stay with W-014.

## Step 8's questions are ruled — do not re-open them

W-023, W-024, W-025, W-038, W-039, W-040 and W-195–W-204 were ruled and written into
§03.6, §06.7, §07.3, §07.6, §07.7, §10.3, §10.4 and §10.6: the technology layer is an
unlock/research tree (not era-scheduled availability) and is built as step 8a; war is
conduct-without-command with a threshold crisis rather than a great-power war model;
W-014 is annotated with the annexation-now / full-redraw-later split; W-205 carries the
deferred nuclear umbrella and is the only item still pending in that cluster.

What remains here is build work, not rulings: the 8a tree, then step 8's war model,
proliferation and the closing door. Any agent that presents these as open questions is
reading a stale copy of this file.

## The W-014 sequencing wrinkle (raise it before planning step 8)

The closing door assumes decolonisation floods the map with new states in 1955–75. State
creation and dissolution are **not built**: the world is fixed at 69 states for all 1,200
months. W-014 owns secession, collapse and foreign takeover; the boundary is that civil
war went to step 8 because it needs an army. So either W-014 (at least annexation and
secession) is sequenced with step 8, or the door closes by proliferation alone and the
decolonisation half of the spine is decorative. Do not present the closing door as fully
achievable without stating which of the two applies.

## Hooks the economy already left for step 8

- Military investment buys **defence-sector capacity and military goods**, with no force
  behind them (§6.2).
- **Technology is no longer a reserved zero** (§6.7): W-039 ruled an unlock/research tree,
  built as step 8a, and step 8 consumes its capability-availability interface rather than
  an era check. The economy still ships era-gated production methods, which is a different
  mechanism — do not treat those gates as the technology layer.
- **Arms radicalisation** and **proxy-war flow** are deferred by name to step 8 (§8.15).
- Grey pawns already sell **military lots**, so arms trafficking has a stub.
- Every province already carries `controller`, `control` and `fortification` in truth.
- Intelligence capital improves paid counter-intelligence detection, bounded at certainty
  (milestone 7 §8.10) — the counter-proliferation duel plugs into an existing machine.

## Is the economy done? Read the acceptance table, do not infer from commits

`docs/economy-evidence.md#acceptance-status` is an evidence inventory with an explicit
Pass/Fail per axis, plus an "unmeasured is not a pass" convention. Recent commits and
`docs/status.md` bullets describe implementation, not acceptance. The axes that have been
failing or unmeasured: price duration, basics when physically sufficient, the weak-state
tail, funded recovery at all three seeds, the rival/tending/sustained/payback matrices,
the full-world gate (blocked on re-recorded campaigns), and unoptimized performance
against the 700 s century ceiling. Re-read the table; never quote these from a skill.

## The covert verb inventory (what "built" means for a verb)

`content/verbs/verbs.json` is the roster. The only field that answers "is it built?" is
`mechanic`.

- **`mechanic: null` = no code path.** Such an entry is a placeholder in every field —
  no `effect`, no `risk`, no `exposure_a_month_ppm`, only a cost. It is not half-built;
  nothing reads it.
- **A non-null `mechanic` = wired**, and `crates/session/src/verb_roles.rs::role_of_mechanic`
  is the proof the session maps it to a `VerbRole` the inputs phase accepts. A mechanic
  present in the content gate's closed vocabulary but with no role arm is a validator pass
  and a dead verb.
- Regenerate the table in one call; never quote a count from prose (`docs/status.md` still
  said "six have real mechanics / fourteen unbuilt" long after §18 and 7b moved both):

```sh
python3 -c "import json;[print(v['id'],v['family'],v.get('mechanic'),v['era_from'],v.get('cost')) for v in json.load(open('content/verbs/verbs.json'))['verbs']]"
```

- **Group the unbuilt half by the system each verb needs, not by family.** That is the
  answer the owner is actually asking for: buildable now on existing systems (autonomy,
  the ladder, organisations, the economy's infrastructure and labour state), blocked on
  8a's technology tree, blocked on step 8's military/nuclear programme, blocked on step 9's
  figure bank. A "family D verbs need no new code" claim is an expectation the build has
  already broken once (W-075).
- **21 entries against the design's 20.** `verb:counterfeit` is the extra one, added by
  §18's "content schema bump (new effects and verb)"; §8.9 still reads "no twenty-first
  verb is added". The code follows §18 — raise the contradiction, do not quietly change the
  count in either direction.
- Watch for authored-data gaps that look like code gaps: `verb:election-interference` has a
  mechanic but no `exposure_a_month_ppm`, which ruling 4 says every verb must state.
- Era gates live on the entry (`era_from`/`era_to`). As authored, almost every verb is open
  from 1945, so the closing-door progression is not expressed in this table yet — 8a's era
  anchors are where it is supposed to arrive.

## Investigation commands

```sh
git -C ~/repos/wwx log -1 --format='%h %ci %s'
cd ~/repos/wwx && python3 tools/evidence.py questions        # pending W-items + count
python3 tools/current_campaigns.py                          # does a current-law 240-month recording exist?
grep -n "16.3 BUILD ORDER" -A 60 docs/design/16-production-scope-risks.md
sed -n '1,14p' docs/milestone-*.md                          # each header states built/accepted/not started
sed -n '/## Acceptance status/,/## Experiment contracts/p' docs/economy-evidence.md
```

`python3 tools/evidence.py questions` is the only authoritative pending list. The
"SECTIONS AND THEIR PENDING ITEMS" block near the end of `00-open-questions.md` is a
hand-maintained index of the items the register CARRIES (closed ones included) and it is
not regenerated: read it for the section grouping, never for the count, or you will quote
a number roughly half again too large.

`tools/current_campaigns.py` is the one command that answers "may I say this build is
green?": it refuses by name, listing the missing recording and transcript, when no
240-month pair exists under the shipped law. A refusal there means the §16.2.7 machine
half cannot be re-run, however much code has landed since.

## Answer shape the owner expects

Verdict first, then the evidence, then a numbered sequence. He asks "what is next" to
get a scheduling answer, not a summary: name the step, name what gates it, name the
one decision that changes the plan, and propose the order. Flag a milestone that has
code but no acceptance rather than calling it done.

For the broader "what have we implemented, what is remaining, and what is done from X"
question, answer in three labelled parts and keep them apart:

1. **Implemented**, by §16.3 step. Say built, not accepted, unless an acceptance record
   closed it, and mark the cross-cutting holes the steps hide (the verbs with no
   mechanics, W-014's dynamic map, the absent browser client, the weekly clock).
2. **Remaining**, in two bins: steps with no code at all, and steps with code that
   still owe acceptance. Add the pending register count from the tool, not from prose.
3. **The named slice or milestone**, against its own definition of done, with each half
   marked honestly. Then one short paragraph on why the build cannot be called green
   today (missing current-law recording, no gate receipt, the door tier) and an explicit
   statement of what you did NOT run — the owner reads that as part of the answer, not
   as a hedge.

   When the question is **"what should we work on next?"**, put the evidence gate in front of
   the build. If `tools/current_campaigns.py` refuses, nothing about the current build can be
   tested, so restoring a current-law recording and a playtest of the shipped tree precedes
   starting the next system; recommending a new milestone on top of an unrecorded tree is the
   mistake to avoid. Then say what you would NOT do yet — he treats the exclusions as part of
   the recommendation, not as hedging.

   When he asks for **"the list of X"**, give every authored field, not the interesting
   columns. Inventory answers here get used as reference data, and he will ask for the full
   dump on the next turn if the first answer filtered.
