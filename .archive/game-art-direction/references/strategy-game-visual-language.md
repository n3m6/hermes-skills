# Visual language for map-based strategy games

Scope: grand strategy, 4X and management games whose primary surface is a map —
especially a text-first project growing into a visual client. Use with
`references/look-and-feel-best-practices.md`; this file is the strategy-specific
application of those practices.

## 1. The map is an instrument, not a backdrop

- Decide the questions the map must answer before its art: who controls what,
  where the fault lines are, where I am exposed, what I can do here. Every mode
  and legend serves one of those questions.
- **Map modes are verbs.** Keep three or four primary modes and make the rest
  layers; a grid of twelve equal modes is a menu, not an instrument.
- **The map must teach the game's verb.** A conquest game's map shows armies and
  territory; an influence game's map shows tiers, networks and leverage. If the
  map looks like the genre default, it teaches the wrong game.
- Terrain earns art budget only if terrain changes decisions. If terrain is
  visual or movement-only, do not spend the map's contrast on mountains.

## 2. Show knowledge, not truth

- If the simulation separates truth from belief, **fog is the signature visual**,
  not a filter. Render three states distinctly: observed (solid), believed
  (pattern or hatch, with confidence and as-of), unknown (blank or hatch). They
  must differ in greyscale and under colour-blind simulation.
- Never let "unknown" and "known zero" share a fill; that is the visual version
  of lying.
- State the grammar in words in the legend. Colour alone is never the message.
- The reveal is content: a map that fills in as observation improves is a story,
  not a loading screen.

## 3. Graded influence, not painter's fills

- Solid owner colour reads as sovereignty and conquest. If victory is influence,
  use fills, hatching, borders and patterns to grade tiers, control and
  penetration; reserve solid fill for sovereignty.
- A player should distinguish owned / client / penetrated / contested / unknown
  at a glance, without opening a tooltip.
- Keep one grammar per concept across modes: a network must look like a network
  in the network mode and in the dossier.

## 4. Visual LOD mirrors simulation LOD

- World → region → province → dossier. At world zoom aggregate; at focus show
  provinces and networks. Do not label every province.
- Visual LOD is a performance contract, not a graphics option. Late-game lag is
  the genre's shared failure; a client that renders full detail everywhere will
  die at the end of the campaign.
- Coarse geography and unknown space are features. Resist making the map
  "complete".

## 5. Contrast hierarchy by actability

- Terrain and context lowest; interactables, networks and pipeline in the
  middle; threats, opportunities and crises highest.
- Apply one cross-mode salience contract: the thing the player can act on is
  always the most salient thing on screen. Do not let each mode invent its own
  hierarchy.
- If a fact cannot be acted on, give it a sentence, not a colour or an icon.

## 6. Tooltips are a first-class surface

- One number, its range, its direction and rate, the threshold it is moving
  toward, the reasons that moved it, and its source/confidence/as-of. One level
  deep.
- Avoid nested tooltip sprawl; it is a symptom of an illegible model, not a
  feature.
- Adopt the "one legible number" discipline: a single number with visible
  reasons beats a hundred opaque ones.
- Never show false precision. Use bands and ranges where the model is uncertain.

## 7. Decide the register: document or dashboard

- Before the client, decide whether the product is a **document** (typography,
  paper, source lines, stamps, redaction) or a **dashboard** (panels, charts,
  glow). They imply different layout, onboarding, audio and art production.
- A briefing is an intent surface; the map is a browsing surface. Keep both, and
  make the briefing the entry point.
- Put the same institutional voice in every surface: map legend, dossier, ledger,
  economy, ending. A surface with its own style reads as a different product.
- UI confusion is design evidence: if a mechanic cannot be explained in the
  interface, the mechanic is too complex.

## 8. Audio

- Pick the register with the visual thesis: room tone, radio fragments, sparse
  strings, silence. Music is identity, not decoration.
- Restraint: a dense strategy UI needs quiet. Use music as a bed, not a
  narrator; save the crescendo for the climax.
- **Honesty: audio must not reveal information the player has not observed.** No
  ominous sting for an unseen event, no triumph for an unconfirmed success.
- Build a small consistent vocabulary for interrupt / notify / commit / refusal,
  and use diegetic document sounds where they fit. Not arcade juice.
- Budget a few long ambient tracks and a small SFX set; do not chase a licensed
  orchestral score.

## 9. Onboarding and progressive disclosure

- Teach one surface at a time; never show a system the player cannot use yet.
- A bounded case-study scenario is the cheapest first hour: a real situation, a
  defined success condition, a clear subject.
- Greyed options with the requirement stated teach capability better than a
  tutorial popup.
- Test the first hour on someone who is not the developer.

## 10. Production traps

- Do not copy the genre leader's production values (3D art, voice work, broad
  localisation) unless the fantasy requires them; copy their legibility
  discipline instead.
- Avoid tooltip sprawl, notification spam, map-mode proliferation, the painter's
  map, and a static world.
- The world must feel alive within the fog: show drift, crises and rival action
  through reports and changed readings, not omniscience.
- Decide the identity before the client is built. A visual language retrofitted
  after the UI exists becomes a reskin.

## 11. Text-first trajectory

- A text interface is the wireframe and the content model: typographic
  hierarchy, wording, surface order and refusal text all transfer. Get them
  right while they are cheap.
- Write the visual thesis and the semantic palette now; build the client later.
  Keep one palette/token source shared by text, SVG and the future UI — never let
  each surface grow its own.
- Use the text phase to test the reading order: briefing → map → dossier →
  pipeline. The visual client should reproduce that order, not invent a new one.

## Checklist

- Can a new player state the game's verb after one screen?
- Does the map show what the player knows, not what is true?
- Are observed, believed and unknown distinct in greyscale?
- Is influence graded rather than painted?
- Is the actionable thing the most salient thing?
- Does every number have a reason, a direction and a source?
- Do all surfaces share one register?
- Does the audio ever reveal something the player has not observed?
- Does the first hour teach one surface at a time?
- Does the client respect the simulation's LOD and performance budget?
