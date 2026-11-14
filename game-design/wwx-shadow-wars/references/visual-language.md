# WWX visual language (proposed, not ruled)

Status: analysis and recommendation, not owner-ruled. The design's tags govern:
`[DECIDED]` / `[PROPOSED]` / `[OPEN]`. Do not quote this file as a ruling, and
re-read the owning section before acting on any line here.

## Current state (verify before quoting)

- §12 defines four surfaces (`[PROPOSED]`), the operation flow, alert tiers, the
  briefing, numbers-with-tooltips, fog, onboarding and accessibility. It does
  **not** define what any surface looks like.
- §14.6 is `[DECIDED]`: no narrator, documents only. Tone is the standing
  `[PROPOSED]` default; W-052 is open.
- §12.6 proposes "a document, not a dashboard" but is still `[PROPOSED]` and is
  not in the open register. It can drift silently.
- The only implemented visual surface is the SVG map in
  `crates/cli/src/map.rs` (colour-blind-safe constants, legend, a `<title>` per
  province). The playable REPL is monochrome text. `apps/ui` is an economy
  renderer scaffold (`economy.ts`), not a browser client.
- Build order: step 10 is "the briefing, the 2045 reckoning, and the long tail of
  content"; W-006 is the map client, W-072 the browser client. The map is step 5
  and already built.
- §16 risk R5 is legibility. The visual language is mitigation, not decoration.

## The thesis

**The archive of the service that is running the century.** A sober Cold War
documentary register translated into visuals: paper and ink, classification
stamps, source lines, redaction, map annotations, room tone. No chrome, no glow,
no sci-fi HUD, no arcade juice.

## Rules

1. **The map is political, not terrain.** §3.3 says terrain is visual and
   movement-affecting only, with no combat modifiers. Spend contrast on borders,
   control, networks, instability, influence and fog — not mountains.
2. **Graded influence, not painter's fills.** Solid owner fill reads as conquest
   and contradicts Pillars 1–2. Use fills, hatching and patterns for pact tiers,
   networks and control; reserve solid fill for sovereignty. The player must
   distinguish owned / client / penetrated / contested / unknown at a glance.
3. **Fog grammar is the signature.** Three states distinct in greyscale and
   colour-blind: observed (solid), believed (pattern + confidence + as-of),
   unknown (blank/hatch). Never let unknown share a fill with known-zero. The map
   shows the shape of the player's ignorance; the reveal is content.
4. **Contrast by actability.** Terrain/context < own networks and pipeline <
   instability, coup risk, nuclear. Write one cross-mode salience contract; do
   not let each mode invent its own.
5. **One motif library.** The intelligence-document apparatus: redaction bar,
   classification stamp, source line, confidence band, date. Use it on the
   briefing, dossier, ledger, map legend and tooltips. One CSS/SVG file buys a
   coherent identity.
6. **One semantic palette, one source.** Player blue, rival red, unknown grey,
   believed pattern; one reserved danger hue. The palette is currently local to
   `map.rs` and mode-specific; move it to one token source shared by text, SVG
   and the future UI before `apps/ui` grows.
7. **Fix the resistance pair.** The resistance mode uses with-you `#2f855a`
   (green) and against-you `#c53030` (red) — the red/green pair §12.10's
   colour-blind rule exists to prevent. The `<title>` preserves comprehension;
   the fill still fails the rule.
8. **One register across surfaces.** Map, briefing, dossier, economy and
   reckoning must look like the same bureaucracy produced them. The economy
   renderer must not grow its own style.
9. **UI exposes design problems.** Greyed verbs (§12.2) and "no number you
   cannot act on" (§12.7) are this rule. Extend it visually: a fact you cannot
   act on gets a sentence, not a colour or an icon.
10. **Feel is the monthly loop.** Input is time control: acknowledge every order,
    show a readable monthly delta, earn every interrupt, and make a refusal name
    the condition that clears it. Screen shake, particles and squash-and-stretch
    are the wrong register.
11. **The feedback stack is documentary.** Dispatch, ledger, dossier, map change
    and badge must agree on date and wording. A tier move appears in all of them
    with the same sentence.
12. **Don't over-detail.** LOD (§3.5) and fog are the aesthetic. Coarse
    provinces, unknown regions and unlabelled minors are features.

## Audio

- Register: room tone, teletype, radio fragments, sparse strings; silence as the
  default.
- Restraint: a bed, not a narrator. Save the crescendo for the 2045 reckoning and
  threshold crises.
- **Honesty: no sting for an unobserved event, no triumph for an unconfirmed
  success.** The "map never lies" rule extends to sound.
- Vocabulary: one chime for INTERRUPT, one softer tone for NOTIFY, one teletype
  or stamp for a committed order, one dry click for a refusal.
- Budget: a few long ambient tracks and a small SFX set, not an orchestral score.
  §12.5's alert tiers are the timing contract.

## Staging

- **Now (text):** write the one-page visual spec (§12.11 or a new 12a); rule W-052
  (tone) and §12.6 (document versus dashboard); fix the resistance pair; define
  palette tokens; test the reading order briefing → map → dossier → pipeline.
- **Step 9 (figures):** decide a portrait policy before authoring. Real figures
  plus generated portraits is a licensing, dignity and style problem. A stylised
  archival treatment (duotone, halftone, silhouette, document photo) is cheaper
  and more coherent than photoreal likeness. Make one gold-standard portrait and
  one event illustration.
- **Step 10 (briefing/reckoning):** build the briefing as a document page, not a
  dashboard; it is the first true visual surface and sets the quality bar. Treat
  the reckoning as the one designed cinematic moment.
- **W-006 (map client):** build the map grammar and visual LOD before the art
  pass; no labels at world zoom; the legend states the fog grammar in words.
- **W-072 (browser):** add the audio bed and the interrupt vocabulary; make the
  case-study scenario the first hour; test it on someone who is not the
  developer.

## CLI / REPL (the current playable surface)

- The only playable interface is the terminal REPL (`crates/cli/src/play/`);
  `apps/ui` is an economy renderer scaffold, not a browser client. The SVG map is
  the only colour surface.
- Facts to re-check before quoting: `PROMPT` is `"\n> "` (`play/mod.rs`);
  `screen::format::wrap` wraps at 78 columns; `screen/month.rs` documents the
  month budget (~46 lines at month 0, 44–48 on a quiet middle month). There is
  no ANSI/style layer — headers, prose and commands all render at the same
  weight.
- The seed-3 first screen orders `NEEDS ATTENTION → DISPATCH → OPENING THEATRES →
  MIRROR → THEATRES → governments → money/economy → footer`. The actionable list
  sits below four paragraphs of opening prose; money prints twice (dispatch and
  books); `governments:` repeats its label on every line; the footer lists about
  a dozen commands.
- Static first-screen capture without a PTY:
  `printf 'quit\n' | cargo run -q -p wwx-cli --bin wwx -- play --seed 3`.
  For an interactive playtest use the repo's
  `.agents/skills/wwx-first-slice-repl/` PTY workflow; a piped capture is not a
  playtest.
- Priority changes: (1) a style layer at the print boundary with `NO_COLOR` and
  non-TTY handling; (2) reorder the opening screen and dedupe money/governments;
  (3) a status prompt plus a one-line command receipt.
- Class-level rules: `game-art-direction/references/text-interfaces.md`.

## Open rulings that gate this

- **W-052** — tone (sober/understated versus more licence).
- **§12.6** — document versus dashboard (`[PROPOSED]`, absent from the register).
- **W-006** — which map modes are default, and whether two can layer.
- The figure bank's portrait treatment is not yet registered; raise it before
  step 9 authors figures.

## Evidence

- General principles: `game-art-direction` →
  `references/look-and-feel-best-practices.md` and
  `references/strategy-game-visual-language.md`.
- Paradox/Victoria 3 lessons: the "Grand strategy competitor research" Drive
  folder. The Paradox feedback study names legibility as the designer's job, the
  onboarding cliff, late-game performance and "one clear verb", and lists 3D
  art, voice work and broad localisation as production values not to chase.
