---
name: grand-strategy-design-docs
description: "Use when writing a grand strategy / 4X game design doc."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Game Design, GDD, Grand Strategy, 4X, Documentation]
    related_skills: [blocked-page-recovery, grounded-citations]
---

# Grand Strategy Design Docs

Answering "what should the design doc contain" and turning that into a real
document for a grand strategy / 4X project.

## House rules (this user)

- **Verdict first.** Lead with the structural answer, then the detail. No
  wind-up.
- **Ground it and label the grounding.** Fetch at least one real published
  design artifact before answering, then say which claims come from a fetched
  source and which are domain recall. Never dress a synthesised TOC up as an
  "industry standard" — there is no single standard, and saying so is part of
  the answer.
- **Genre claims rest on shipped-product evidence, not recall.** For any "what
  works / what does not" statement about the genre, pull review aggregates,
  retention curves and review text from the platform's own store API before
  answering — procedure in the `product-teardown` skill's
  `references/game-market-metrics.md`; distilled patterns in
  `references/genre-reception-lessons.md`.
- **Never write into the user's design doc unprompted.** Deliver the outline in
  chat and offer to lay it in. "Keep it empty" means empty.
- Long, tightly-organised structured output is welcome here — this is a
  reference document, so length is a feature. Keep every line scannable.

## Procedure

1. **Separate the two questions** usually asked at once: what a genre-typical
   doc contains (structure) and what *this* game's doc should contain (scope).
   Answer the first fully before touching the second.
2. **Source real artifacts** — see `references/sourcing-real-design-docs.md`
   for where published design docs, dev diaries and design-philosophy pages
   live, and how to fetch them past bot walls.
3. **Lead with the genre signature, not the list:** a grand strategy doc is
   roughly 70% systems specification. The sections generic GDD templates lead
   with (levels, story arc, character development) are small or absent; the
   sections they omit (AI, simulation architecture and determinism, late-game
   performance, balance/tuning, the UX of complexity) are load-bearing.
4. **Give the canonical TOC** from `references/canonical-toc.md`, trimmed and
   reordered to the project rather than pasted whole.
5. **Recommend the doc architecture:** a short frozen *Vision* doc (1-3 pages:
   pillars + anti-pillars) plus living per-system docs plus the spreadsheets
   where the numbers actually live. One monolithic design doc is a known
   anti-pattern — it goes stale and nobody reads it.
6. **Ask the framing questions that change the TOC** before drafting anything:
   turn-based vs pausable real-time; historical/Earth vs fictional setting;
   player is a state vs a person/dynasty; single-player-first vs
   multiplayer-comparable.

## Pitfalls

- **Generic GDD templates are a trap for this genre.** They have the writer
  polishing character arcs and level flow while the four things that decide
  whether the game ships — AI quality, late-game turn time, onboarding into a
  40-hour system, and balance — get a paragraph each.
- **Pillars must carry a negative.** A pillar without "what this means we do
  *not* do" is a slogan; it cannot settle a design argument later.
- **Pacing gets its own document,** structured phase-by-phase x system-by-system
  (what the player is doing and thinking at turn 1, turns 2-6, and so on).
  Progression pacing is the hardest thing to retrofit.
- **AI is a design section, not an engineering detail.** It needs an explicit
  cheat contract (what the AI may see and do at each difficulty) plus a CPU
  budget, written down as decisions.
- **Do not admit micro-heavy systems on the grounds that they are optional.**
  Optional micro still disadvantages anyone who declines it, and a system
  boring enough that players automate it was not worth adding. Sliders are the
  canonical offender — the player ends up choosing between 5% and 6%.

## References

- `references/canonical-toc.md` — the full genre-typical table of contents.
- `references/sourcing-real-design-docs.md` — where to find real published
  design docs, dev diaries and design philosophy pages, how to fetch them past
  bot walls, and how to mine an industry publication (gamedeveloper.com) at scale.
- `references/genre-reception-lessons.md` — durable what-retains / what-leaks
  patterns for the genre, grounded in shipped-title reception *and* the
  designers' own published statements; use to pressure-test pillars and
  anti-pillars.
