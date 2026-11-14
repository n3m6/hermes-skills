---
name: game-art-direction
description: "Use when defining a game's look and feel."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Game Design, Art Direction, Visual Design, Readability, Game Feel]
    category: game-design
    related_skills: [grounded-citations, grand-strategy-design-docs]
---

# Game Art Direction

Defining, documenting and defending a game's look and feel. The output is not
"inspiration" — it is a small set of decisions, rules and a document another
person can execute.

## When to Use

Use when the task is any of:

- defining or revising a game's visual identity, art direction or "look and feel";
- writing, reviewing or auditing an art bible, style guide or art brief;
- diagnosing why a scene, UI or character is hard to read;
- making the moment-to-moment feel match the visual promise (juice, feedback,
  responsiveness);
- evaluating whether a proposed style fits the game's emotional target and
  audience;
- designing the visual client for a map-based strategy or management game — map
  modes, fog, graded influence, tooltips, music and the text-to-visual
  transition (see `references/strategy-game-visual-language.md`);
- designing or improving a text interface — CLI, TUI or REPL — that carries the
  game before the visual client exists (see `references/text-interfaces.md`).

Not for: producing the final 2D/3D assets, rigging, or shader implementation.

## House rules (this user)

- **Verdict first.** Lead with the structural answer — look and feel is one
  communication system, not a coat of paint — then the procedure and detail.
- **Every rule must be checkable.** "Moody" is not direction; "midtones
  saturated, shadows cool, one warm source per room" is. If a rule cannot be
  used to accept or reject an asset, rewrite it.
- **Constrain, don't decorate.** The most useful art direction is a small set of
  positive rules plus explicit anti-rules ("if it didn't hurt, frighten or
  protect, it had no place in the world") that settles future decisions without
  the director in the room.
- **Ground claims in shipped-work evidence.** Cite first-party postmortems and
  deep dives by studio/designer, not listicles. The distilled 37 practices and
  their sources are in `references/look-and-feel-best-practices.md`.
- **For a map game, the map is an instrument.** Decide what the player must read
  and act on before what the map depicts. A beautiful map that teaches the wrong
  verb is a failed art direction.
- **When asked what applies to an existing project, filter — do not recite.**
  Audit the repo/design first, name what is already decided and must not be
  broken, then split the practices into apply-now, decide-now/build-later, and
  does-not-apply. Dumping the full list onto a specific game is noise.

## Procedure

1. **Name the emotional target before the style.** Ask what the player should
   feel, moment to moment and at the story's turns. Leading with genre or a
   reference game reproduces conventions instead of producing meaning.
2. **Write a one-paragraph visual thesis.** State the period/inspiration, the
   fidelity target and the originality constraint — "inspire, not imitate" —
   plus what the game explicitly rejects. The thesis is the tie-breaker for
   later asset decisions.
3. **Fix the presentation before the assets.** Camera, framing, viewing distance
   and target screen define the canvas and therefore where detail is worth
   spending. Decide these before commissioning character or environment work.
4. **Set the stylization point and the audience deliberately.** Pick a position
   on the cartoony-to-realistic scale and name the shelf neighbours. If you do
   not choose it, the style defaults to whatever the team happened to be able
   to render.
5. **Research with annotated references.** Build mood boards where every image
   says what to take from it; include what you do *not* want; pull from outside
   games (industrial design, film, fashion, architecture, nature). A mood board
   without annotations is decoration, not direction.
6. **Explore in silhouette order.** Primary read = silhouette, secondary = shape
   breakup via colour/line, tertiary = surface detail last. Generate several
   directions before converging. If it does not read at thumbnail size, detail
   will not save it.
7. **Lock the language.** Set a gold standard for each asset class (character,
   environment, prop, UI, VFX), define the pillars/leitmotifs, and spec the
   checkable parameters: shape language, silhouette rules, palette roles,
   value range, edge/line treatment, material language, proportion, perspective,
   level of detail, plus technical budgets and naming conventions.
8. **Design for readability.** Build a contrast hierarchy (background <
   interactable < threat); give gameplay-relevant entities unique silhouettes;
   protect a consistent interaction language with no false positives; test at
   the real camera distance and on the target screen; let UI inherit the visual
   language and treat UI confusion as evidence of design complexity.
9. **Design the feel as its own discipline.** Separate input, response, context,
   polish, metaphor and rules; prototype them in a test space; add feedback
   early rather than in the polish phase; keep the feedback stack (animation,
   VFX, sound, camera, UI, haptics) saying the same thing in the same style;
   tune to the metaphor and prefer responsiveness over literal animation.
10. **Document and run it.** Produce an art bible/brief with premise, audience,
    camera, pillars, annotated mood board, do's/don'ts, fidelity scale, palette,
    technical specs, deliverables and deadlines. Run alignment rituals (art
    town halls, in-context reviews, everyone plays the build), audit against the
    gold standard, and keep the document living.

## Pitfalls

- **Assuming a visual language exists because a UX doc does.** Surface lists,
  accessibility rules and tone notes are not art direction. Grep the design set
  for a visual thesis, palette, type and surface treatment before claiming one
  exists; the absence of that document is itself a finding, and usually the
  highest-value one.
- **Style by default.** If nobody chose the stylization level, the game inherits
  "whatever the art team could manage", which is not a direction and cannot be
  defended in a review.
- **Detail before silhouette.** Surface detail added to a shape that does not
  read at gameplay distance is wasted work; fix the primary read first.
- **A style guide with no negatives.** Positive references alone cannot settle
  an argument about a new asset; write the anti-rules and the do-not list.
- **Gameplay cue colours used decoratively.** If the same high-saturation red
  marks both a threat and a poster, players learn to ignore it; reserve cue
  colours and enforce the reservation.
- **Judging assets in isolation.** A turntable, a Maya shaded view or a
  full-screen beauty shot lies about readability; review in the real camera,
  in motion, with the surrounding assets and UI.
- **Feedback left to the end.** The button-to-response loop is the thing the
  player experiences most; retrofitting it late is expensive and usually
  produces effects that fight the art direction.
- **A style guide that stops at stills.** World, UI, VFX, animation and
  cutscenes must share one emotional register; treating UI or FX as separate
  products is how games end up looking assembled from parts.

## References

- `references/look-and-feel-best-practices.md` — 37 distilled practices across
  definition, exploration, visual language, readability, game feel and
  documentation, with the 22 Game Developer articles they come from.
- `references/strategy-game-visual-language.md` — the strategy-specific
  application: map modes as verbs, fog grammar, graded influence, tooltips,
  audio, onboarding, visual LOD, production traps and the text-first trajectory.
- `references/text-interfaces.md` — the same hierarchy and readability rules
  applied to a CLI/TUI/REPL: screen grammar, semantic style layer, glyph and
  colour vocabulary, status prompt, command receipts, progressive disclosure,
  numeric tables, terminal testing and golden screens.
