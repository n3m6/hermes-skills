# Look and feel: 37 distilled practices

Source base: 22 Game Developer (ex-Gamasutra) articles on art direction, art
bibles, readability, palette, UI language and game feel. Numbers in brackets
map to the source list at the bottom.

**Verdict:** look and feel is one communication system, not a coat of paint.
Decide what the player must feel and read, lock a small set of rules with a
gold-standard asset, document them so other people can reproduce them, test
readability at the real camera, then tune the feedback until it feels right.

## 1. Decide what it has to do before what it looks like

1. **Start with the emotional experience, not the genre or the style.** Ask
   "what is the emotional experience?" before picking a visual idiom; leading
   with genre reproduces conventions instead of producing meaning.[4]
2. **Write a one-paragraph visual thesis.** Double Fine's Headlander doc states
   the period, the fidelity target and the originality constraint in a few
   lines: "we look to the work of that era to inspire — not to imitate."[22] A
   thesis also tells you what to reject.
3. **Define the presentation before the assets.** Camera, framing and viewing
   distance "give you the edges of your canvas" and determine where detail is
   worth spending.[2] An isometric game needs detail on the tops of characters;
   a side-scroller may need less detail so points of interest stay readable.[1]
4. **Choose your point on the stylization-to-realism scale deliberately.** If
   you don't choose it, you default to "however realistic the art team happened
   to manage," which is not a direction.[17] A coherent stylized language can
   feel more credible than mixed fidelity, because everything belongs to the
   same world.[5]
5. **Know the audience and the shelf, then decide which convention to break.**
   Pokémon, World of Warcraft and Killzone target different audiences and read
   differently at first glance.[1] The strongest styles usually keep the genre's
   grammar while changing one or two load-bearing rules, as Forge did by mixing
   Norse and Inuit references instead of another generic medieval Europe.[13]

## 2. Explore before you commit

6. **Build annotated mood boards, not image dumps.** Every reference should say
   what to take from it; include what you explicitly do *not* want, which is
   often more useful than another positive example, and use a 1–10
   cartoony-to-realistic scale with examples.[11]
7. **Pull references from outside games.** The industry is too self-referential;
   art directors are urged to hire outside artists and to look at opera,
   fashion, industrial design and street art.[5] Practical references for a
   sci-fi prop might come from motorcycles, engines, speakers or rockets — if
   the form has to look functional, study functional things.[1]
8. **Explore in silhouettes and thumbnails, and work in orders of read.**
   Primary read is silhouette, secondary read is how shapes are broken up by
   color or line, tertiary read is pores, scratches and dirt — and tertiary
   detail comes last.[1] Forge ran several silhouette rounds per character and
   only took the best few to tonal rough.[13] If it doesn't read at thumbnail
   size, detail won't save it.
9. **Generate variety before you converge.** Iterating one idea feels productive
   but produces a style by accident; deliberately explore several directions
   before choosing one.[1]
10. **Get it into the engine early and judge it in the player's view.** A model
    "isn't finished until it is in the game and moving," and something rough
    should be in-game as soon as possible.[2] Evaluate with the other assets
    integrated and from the player's perspective — not in a Maya shaded view.[18]

## 3. Lock the visual language

11. **Set a gold standard for each asset class.** One approved piece defines the
    quality, shape language, rendering style and palette for everything that
    follows; characters, environments, props, UI and VFX may each need their own
    standard.[1]
12. **Turn the look into rules that generate answers.** Convey underlying
    motivations rather than fixed solutions, so artists can solve new problems
    consistently without you in the room.[3] Forge's rule was brutal and useful:
    "if it didn't hurt, frighten, or protect, it had no place in the game
    world."[13]
13. **Specify the checkable parameters.** The style guide should pin down shape,
    size, line, color, perspective and anatomy,[12] and the art spec should add
    texture and polygon budgets, animation lists, construction methods, naming
    conventions and visual examples.[21] "Make it moody" is not a spec;
    "midtones saturated, shadows cool, one warm light source per room" is.
14. **Choose a shape language and use it semantically.** Circle reads as
    innocent/youthful, square as stable/mature, triangle as aggressive/forceful;
    harmony comes from echoing the character's shape in the environment,
    dissonance from contrasting it.[4] Use this as a diagnostic, not a formula —
    the article explicitly warns against applying it mechanically.[4]
15. **Give the palette a job description.** Decide whether color is doing
    wayfinding, safety/danger signalling, story or mood, and build the palette
    around that job.[10] Warm, cool, desaturated, noir and monochrome palettes
    carry conventions you can use or deliberately subvert.[10]
16. **Use a small indexed palette and reserve cue colors.** An indexed palette
    keeps every element harmonious and lets you re-theme globally by swapping
    the list.[7] Keep the highest-saturation, highest-contrast colors for
    gameplay-relevant things; if a cue color also appears decoratively, players
    learn to stop trusting it.[20]
17. **Repeat a few motifs everywhere, at every scale.** Dead Cells was built on
    three pillars — saturated palette, Celtic architecture and alchemy — and
    applied them to levels, props and progression elements.[8] Forge
    commissioned a custom library of wolf, bear and crow motifs so no environment
    artist ever googled "medieval border" again.[13] Beastieball uses
    parallelograms and scrolling patterns in essentially every UI element.[7]
18. **Make the art carry meaning, not just polish.** Art direction is "a
    message, a direction, a flavor," not a competition over shader quality.[5]
    Give props and spaces a Where/Why/How even if the backstory never ships; the
    considered history gives them weight.[13] Prefer show-don't-tell detail that
    rewards attention without announcing itself.[5]
19. **Enforce one emotional register across world, UI, FX, animation and
    cutscenes.** Serious cutscenes over goofy gameplay graphics break the
    player's ability to hold the world together; the feeling has to be in sync
    even when the fidelity differs.[6] FX are not a separate art problem — they
    follow the same rules and should be developed in context, not in
    isolation.[2] A game's art is the sum of UI, UX, animation and VFX, not just
    the environments.[16]

## 4. Design for readability

20. **Build a contrast hierarchy, not a beauty contest.** Backgrounds should
    have the lowest contrast and fade into each other; interactive elements sit
    in the middle; enemies, projectiles and spells get the highest saturation,
    contrast and brightness.[8] That hierarchy is what makes difficulty feel
    fair instead of arbitrary.
21. **Silhouette first for anything the player must identify fast.** Team
    Fortress 2 gave each class a distinct shape so players could recognize
    opponents instantly,[1] and Forge treated "silhouette, silhouette,
    silhouette" as its character-design battle cry.[13] Test the silhouette at
    gameplay distance, in motion, not in a character turntable.
22. **Have a protected interaction language — and no false positives.** Tomb
    Raider marked climbable ledges with white paint, rope-arrow spots with rope
    coils and axe walls with cracks, and the team protected those patterns so
    they always meant the same thing.[2] Teach the language, repeat it, and
    never use a gameplay signal decoratively; exceptions are "dangerous and
    confusing to the player."[2] The signal must also predict the outcome every
    time — if red means "cannot be blocked," it has to mean that on every enemy
    of every size — because readability is what makes a fight feel fair.[19]
23. **Check readability at the real camera and on the real screen.** XCOM had
    to read from both a top-down gameplay camera and close-up cinematics, which
    drove its chunky "miniatures" look and explicit modeling and texturing
    rules.[2] Mobile games must read on a small, glaring screen and often with
    no audio, so visual confirmation has to carry more of the feedback load.[15]
24. **Let the UI inherit the look — and use it to expose design problems.** UI
    is "the player's window into the soul of your game," so it should share the
    world's motifs and palette rather than looking like a different product.[7]
    If a mechanic cannot be explained cleanly through the UI, that is evidence
    the mechanic is too complex, not just that the UI needs another icon.[7]
25. **Leave gaps; don't bludgeon the player with detail.** Less visual detail
    gives the player's imagination room to project mood, and constant flashiness
    works against atmosphere.[6] Use spectacle as contrast and reward rather
    than as the baseline; Cave Story and Knytt are atmospheric because of what
    they leave out.[6]
26. **Use perspective and composition as rules, not accidents.** Ikenfell fixes
    an orthographic camera at roughly 60 degrees and makes large flat blocks of
    color solid and textured ground walkable, so rooms read clearly despite
    clutter.[9] Dynamic composition ties character shape, character animation,
    environment shape and pathways into one emotional statement.[4]

## 5. Make the feel match the look

27. **Prototype feel as its own discipline, in layers.** Break it into input,
    response, context, polish, metaphor and rules, and tune each separately so
    feel problems don't get tangled with design problems.[14] Build a "garden" —
    a test space with primitives, platforms and varying spacing — and tune
    movement against it before content production.[14]
28. **Treat feedback as core, not as end-of-project polish.** The loop between
    pressing a button and the game responding is the beating heart of the game;
    add it early and often.[15] "Every game needs a 'feel like a badass'
    button."[15]
29. **Layer the feedback stack coherently.** Animation, VFX, particles, sound,
    camera shake, FOV changes, UI response and haptics should all say the same
    thing about what just happened.[15] Match the intensity and style of that
    feedback to the art direction, or the effects will feel bolted on.[2]
30. **Tune the feel to the metaphor.** The same mechanics feel completely
    different when the avatar is a car versus a sweating man running; players
    bring preloaded expectations about how cars, horses and bodies should
    move.[14] The look sets a promise that the feel has to keep.
31. **Choose responsiveness over realistic animation.** Cropping the first few
    attack or jump frames, testing at 1.5x speed and prioritizing feel over
    literal animation often makes a game feel dramatically better.[15] A dead
    button — one that gives no visible or audible response — is worse than an
    ugly one.[15]

## 6. Document it and defend it

32. **Write an art bible or brief a stranger could execute.** Cover the premise
    and themes, the audience, the camera and mechanics, the style pillars, an
    annotated mood board, explicit do's and don'ts, the fidelity level, the
    palette, technical specs (engine, budgets, file formats), the deliverable
    list and the deadlines.[11][21]
33. **Show, don't just tell, in the brief.** Annotate screenshots with callouts,
    color-pick exact values from reference, include napkin doodles, and show
    what you don't want as well as what you do.[11]
34. **Convey intent so the team can make predictable decisions without you.** A
    ruleset that gives similar answers to similar problems scales better than
    constant art-director intervention; let go of the small things and trust the
    team inside the boundaries.[3] "Have a vision, be able to articulate it."[3]
35. **Run alignment rituals, not just document distribution.** Hold art town
    halls and open forums about why the direction was chosen, review work in
    context, and make sure every artist plays the build.[12] Alignment is a
    living process, not a PDF you send once.[12]
36. **Audit against the gold standard and kill drift.** The art bible becomes
    essential when you scale up or outsource,[16] and documentation goes stale
    as production wears on, so it needs re-review.[3] Judge the whole product —
    UI, UX, animation, VFX — rather than defending individual assets.[16]
37. **Protect the schedule from perfectionism.** Expect 80% of the work to take
    20% of the time and the last 20% to take 80%, and budget accordingly.[2]
    "More is lost through indecision than wrong decision"; when it feels right,
    move on to what needs attention.[12]

## The one-page version

- Emotional target → visual thesis → camera/presentation → stylization point.
- Annotated mood board, including negatives; references from outside games.
- Silhouette and thumbnail exploration before detail.
- Gold standard per asset class; rules that generate answers; spec the checkable
  parameters.
- Shape language, indexed palette, reserved cue colors, repeated motifs.
- Meaning and backstory in the props; one emotional register across world, UI
  and FX.
- Contrast hierarchy; unique silhouettes; protected interaction language; test
  at the real camera.
- UI inherits the style and exposes design problems; leave gaps for the player's
  imagination.
- Prototype feel in layers; add feedback early; tune to the metaphor;
  responsiveness beats realism.
- Art bible with annotated references, do's/don'ts, fidelity scale, specs,
  deliverables and dates.
- Alignment rituals, audits against the gold standard, and a bias to finish.

## Sources

[1] https://www.gamedeveloper.com/design/creating-an-art-style
[2] https://www.gamedeveloper.com/production/art-direction-bootcamp-an-expert-roundtable-q-a-2
[3] https://www.gamedeveloper.com/art/art-direction-bootcamp-an-expert-roundtable-q-a
[4] https://www.gamedeveloper.com/design/the-aesthetics-of-game-art-and-game-design
[5] https://www.gamedeveloper.com/art/a-cyber-renaissance-in-art-direction
[6] https://www.gamedeveloper.com/art/atmosphere-in-games---part-2---visuals
[7] https://www.gamedeveloper.com/art/deep-dive-developing-a-clear-and-consistent-visual-language-in-the-ui-of-beastieball
[8] https://www.gamedeveloper.com/production/art-design-deep-dive-giving-back-colors-to-cryptic-worlds-in-i-dead-cells-i-
[9] https://www.gamedeveloper.com/design/the-art-visual-language-of-ikenfell
[10] https://www.gamedeveloper.com/design/color-in-video-games-how-to-choose-a-palette
[11] https://www.gamedeveloper.com/design/crafting-the-perfect-game-art-brief
[12] https://www.gamedeveloper.com/art/art-direction-in-video-games-a-roadmap-for-finishing-your-projects
[13] https://www.gamedeveloper.com/art/forge-developer-diary-art-direction
[14] https://www.gamedeveloper.com/design/game-feel-the-secret-ingredient
[15] https://www.gamedeveloper.com/design/the-single-most-useful-advice-i-can-give-for-making-any-game-better-feedback
[16] https://www.gamedeveloper.com/design/who-needs-an-art-bible-game-art-direction-from-indie-to-aaa
[17] https://www.gamedeveloper.com/design/designing-games-with-style
[18] https://www.gamedeveloper.com/art/function-the-key-to-good-game-art-direction
[19] https://www.gamedeveloper.com/game-platforms/designing-for-difficulty-readability-in-arpgs
[20] https://www.gamedeveloper.com/design/visual-cues-in-level-design
[21] https://www.gamedeveloper.com/production/common-methodologies-for-lead-artists
[22] https://www.gamedeveloper.com/design/tuck-into-the-art-direction-doc-for-double-fine-s-cosmic-adventure-i-headlander-i-
