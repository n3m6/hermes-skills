---
name: game-production
description: "Game design docs, art direction, launch marketing."
version: 1.0.0
author: Hermes Agent (curator)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [game-design, gdd, grand-strategy, art-direction, readability, marketing, steam, launch]
    related_skills: [product-teardown, grounded-citations, wwx-shadow-wars]
---

# Game production: design docs, art direction, go-to-market

Three jobs that recur on the user's game project (a grand strategy / 4X title), and
that share one posture: he wants decisions he can execute, defended by evidence,
delivered in chat rather than written into his repo unasked. Each mode below is
always-on rules; the depth behind it is in the support files.

## When to use

- **Design doc (Mode A)** — "what should the design doc contain", "write the GDD",
  "review this outline", "is this design complete".
- **Art direction (Mode B)** — defining or auditing look and feel, an art bible or
  brief, readability diagnosis ("why is this screen hard to read"), game feel, a
  text/CLI surface that carries the game.
- **Go-to-market (Mode C)** — wishlists, Steam page, demo, Next Fest, creator
  outreach, publisher or crowdfunding decisions, launch-window sequencing.

Not for: measuring other people's games (that is `product-teardown`, whose own
game-market-metrics reference carries the endpoint procedure), or checking a stale
factual claim (`grounded-citations`).

## House rules — all three modes

1. **Verdict first.** One short block naming the structural answer — the highest-
   leverage move, the one fact that reframes the rest — then the detail. He reads
   the verdict and skims.
2. **Ground claims and label the grounding.** Fetch at least one real artifact
   before answering (a published design doc, a store API pull, a first-party
   postmortem). Say which claims come from a fetched source, which only from a
   search snippet, and which are your synthesis; name any load-bearing number
   resting on a weaker source than the rest.
3. **Never invent a market number.** Valve does not publish wishlists, followers or
   sales; a third-party tracker is cited as "per <site>", never as fact. Review
   counts are a sales proxy — label them, never convert them to units.
4. **Never write into the user's repo or design doc unprompted.** Deliver in chat
   and offer to lay it in. "Keep it empty" means empty. Competitor and marketing
   material never goes into the game repo — that repo holds design and history.
5. **Every rule must settle a future decision.** An adjective ("moody", "deep",
   "fun") is not direction; a checkable rule ("midtones saturated, shadows cool,
   one warm source per room") is. A pillar without a negative — what this means we
   do *not* do — is a slogan and cannot settle an argument later.
6. **Filter to this project; do not recite.** Audit what is already decided and
   must not be broken, then split the practices into apply-now,
   decide-now/build-later, and does-not-apply. Dumping a full best-practice list
   onto a specific game is noise.
7. **Close with what could not be verified**, listed, not glossed.

## Mode A — the design document

A grand strategy doc is roughly 70% systems specification. The sections generic GDD
templates lead with (levels, story arc, character development) are small or absent;
the ones they omit — AI, simulation architecture and determinism, late-game
performance, balance/tuning, the UX of complexity — are load-bearing. Separate the
two questions usually asked at once: what a genre-typical doc contains (structure),
then what *this* game's doc should contain (scope). Answer the first fully before
touching the second.

Procedure: source real artifacts → lead with the genre signature → take the
canonical TOC from `references/canonical-toc.md`, trimmed and reordered rather than
pasted whole → recommend the doc architecture (a frozen 1–3 page *Vision* of
pillars and anti-pillars, plus living per-system docs, plus the spreadsheets where
the numbers actually live; one monolithic design doc is a known anti-pattern that
nobody reads) → ask the framing questions that change the TOC: turn-based vs
pausable real-time; historical/Earth vs fictional; the player is a state vs a
person/dynasty; single-player-first vs multiplayer-comparable.

Pitfalls: generic templates applied to this genre; pacing left as a subsection
instead of its own phase-by-phase × system-by-system document (what the player is
doing and thinking at turn 1, turns 2–6, …) — progression pacing is the hardest
thing to retrofit; AI treated as an engineering detail (it needs an explicit cheat
contract per difficulty *and* a CPU budget, written as decisions); micro-heavy
systems admitted as "optional" (optional micro still disadvantages anyone who
declines it, and a system boring enough to automate was not worth adding — sliders
are the canonical offender).

Pressure-test the pillars against shipped-title reception and the designers' own
published statements in `references/genre-reception-lessons.md` — a source of
design constraints, never of features to copy.

## Mode B — art direction and readability

The output is not inspiration; it is a small set of decisions, rules and a document
another person can execute. Look and feel is one communication system, not a coat
of paint: world, UI, VFX, animation and audio share one emotional register.

Procedure: name the emotional target before the style → write a one-paragraph
visual thesis (period/inspiration, fidelity target, "inspire, not imitate", what it
rejects) → fix camera, framing and viewing distance before commissioning assets →
choose the stylization point and the shelf neighbours deliberately → annotated mood
boards (every image says what to take from it; include what you do *not* want; pull
from outside games) → explore in read order: silhouette, then shape breakup by
colour/line, then surface detail last → lock the language (a gold standard per
asset class; shape language, palette roles, value range, edge treatment,
proportion, LOD, technical budgets, naming conventions) → design readability
(contrast hierarchy background < interactable < threat, unique silhouettes for
anything identified fast, a protected interaction language with no false positives,
tested at the real camera and target screen, UI inheriting the visual language and
UI confusion read as evidence the mechanic is too complex) → design feel as its own
discipline (input, response, context, polish, metaphor, rules; feedback early, not
in the polish phase; the whole feedback stack saying the same thing; responsiveness
over literal animation) → document and run it (art bible, alignment rituals, audit
against the gold standard, keep it living).

Pitfalls: assuming a visual language exists because a UX doc does — grep the design
set for a thesis, palette, type and surface treatment, and treat the absence as the
finding; style by default (nobody chose the stylization level, so the team's
capability chose it); detail before silhouette; a style guide with no negatives;
cue colours used decoratively (players learn to ignore the signal); judging assets
in a turntable instead of in context and in motion; feedback left to the end.

For a map-based strategy game the map is an instrument: decide what the player must
read and act on before what the map depicts — `references/strategy-game-visual-language.md`.
For a CLI/TUI/REPL that carries the game before the visual client exists, the same
hierarchy expressed in characters — `references/text-interfaces.md`. The distilled
37 practices and their sources: `references/look-and-feel-best-practices.md`.

## Mode C — go-to-market

This is the forward-looking plan; measuring other people's games belongs to
`product-teardown`. Establish the stage in one line first (design docs only? a
slice? a demo? a date already announced?) — the right answer at the design-doc stage
is nearly the opposite of the right answer inside the launch window, so tier every
recommendation by horizon: now / 6–18 months / launch window / structural.

Procedure: find the incumbents by searching the store with the game's own pitch;
pull store search → app details → reviews, then read the incumbent's **news feed**
(cadence, subject list, every public release-date slip) — it is the competitor's
marketing machine written down and the single most useful fetch in the exercise →
pull the market numbers, each cited with source and date-of-pull → locate the
audience where it actually posts, not where it should → build the tiered menu and a
concrete sequence for the next twelve months → state the one-shot assets out loud
→ offer the written artifact rather than producing it unasked.

One-shot assets — say which are permanent. **Next Fest is one participation per game,
ever** (take the last edition before the planned launch: it multiplies an existing
base, it does not create one). **Early Access is a release** and permanently
disqualifies the game from Next Fest — that is its real cost, and the revenue
argument for EA is never complete without it. The announcement is spent by an early
store page, so set the trigger (capsule + five gameplay screenshots + gameplay
trailer + tags) instead of pulling the page early. Never recommend a release date as
a marketing move: slides cost nothing before a date exists and strand the audience
after one is public.

Durable facts: paid wishlists convert 2–4x worse than organic Steam-discovery ones,
so "no paid acquisition before launch" is a standing recommendation, not a budget
opinion; name, capsule and tags are the highest-leverage store assets, and a tag an
incumbent owns must be derived by *difference*; publisher fit is a question about
their shipped portfolio, and a publisher already shipping in the exact slot is a
conflict of interest to name rather than a warm lead; a devlog cadence is the only
marketing asset a pre-build game can accumulate; crowdfunding is a marketing event,
not a funding mechanism — it needs the audience first.

Mechanics, deadlines and the fest calendar: `references/steam-launch-mechanics.md`
(re-check dates — Valve rotates the themes yearly). Genre reach, creator outreach
and publisher routes: `references/strategy-genre-reach.md`.

## Support files

- `references/canonical-toc.md` — the genre-typical design doc table of contents.
- `references/sourcing-real-design-docs.md` — where published design docs, dev
  diaries and design-philosophy pages live, and how to mine them at scale past bot
  walls.
- `references/genre-reception-lessons.md` — what retains and what leaks in the
  genre, grounded in shipped-title reception and the designers' own statements.
- `references/look-and-feel-best-practices.md` — the 37 distilled look-and-feel
  practices with their 22 sources.
- `references/strategy-game-visual-language.md` — map modes as verbs, fog grammar,
  graded influence, tooltips, audio, visual LOD, the text-first trajectory.
- `references/text-interfaces.md` — screen grammar, semantic style layer, glyph and
  colour vocabulary, receipts, numeric tables, terminal testing, golden screens.
- `references/steam-launch-mechanics.md` — the Steam funnel in order, Next Fest
  eligibility and deadlines, wishlist-conversion benchmarks, fest calendar.
- `references/strategy-genre-reach.md` — the genre's market shape, where its
  audience lives, creator outreach rules, the publisher-fit table, a worked
  occupied-slot pitch.
