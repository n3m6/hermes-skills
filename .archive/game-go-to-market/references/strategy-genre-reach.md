# Grand strategy: where the audience is, who covers it, who publishes it

The method generalises to any niche; the map below is the grand strategy /
geopolitics one, which is where the user's own project sits. **Every number is a
snapshot - re-pull before quoting**, and keep the raw pull in
`~/.hermes/cache/scratch/<project>-gtm/`.

## The shape of the market (Steam's own API)

Three different scales, and mixing them is the analytical error:

- **Audience-defining titles** (the ceiling the genre's audience reaches): Hearts of
  Iron IV ~261k reviews, Stellaris ~139k, CK3 ~93k, EU4 ~92k, Victoria 3 ~41k;
  owner bands 1-10M.
- **The adjacent-niche ceiling** - closest to "you are the state and the systems are
  the game": Terra Invicta ~9.1k reviews (80% positive, 200-500k owners; Early
  Access 2022, 1.0 only in 2026, now on paid DLC), Norland ~9.0k, Old World ~6.1k.
- **The politics/geopolitics-sim lane, badly served:** Phantom Doctrine ~3.8k (74%),
  Shadow Empire ~1.4k (82%), Crisis in the Kremlin ~1.4k (84%), Power & Revolution
  2022 ~0.8k (61%, $49.99), Sigma Theory ~0.9k (78%), **Realpolitiks II ~0.5k at
  47%**.
- **Medians:** the median grand-strategy-tagged game grosses ~$14.7k / ~1,550 copies
  across ~1,300 games; 4X median ~$50k; top decile >$1.5M. Genre-wide, grand strategy
  is roughly 9.7% of the Strategy category's lifetime revenue among
  million-dollar-plus titles.

Read: the genre audience is enormous while its *thematic niches* are served at the
1-4k-review level. That gap is a positioning and onboarding problem, not a feature
problem - say it that way.

## Where the audience actually lives

- **Product subreddits carry the audience; the genre's own subreddit does not.**
  Mirror-snapshot sizes: r/hoi4 ~439k, r/eu4 ~370k, r/paradoxplaza ~255k,
  r/victoria3 ~136k, r/Kaiserreich ~124k, **r/TNOmod ~77k**, r/wargame ~45k,
  r/4Xgaming ~42k, r/StrategyGames ~17k, **r/grandstrategy ~1.3k**. Confirm sizes
  before building a plan on a subreddit; use the mirror API, not the front door (see
  the `reddit-mining` skill).
- **Alt-history total-conversion mods are the strongest free adjacency.** Those
  communities want exactly what a 1945+ hybrid-war game sells - documents, ideology,
  espionage, no named heroes. Recruit playtesters there, not from the dev subs.
- Developer-audience subs (r/gamedesign ~251k, r/IndieDev ~249k, r/IndieGames ~227k)
  are for a *design-notes* cadence - credibility, not customers. Say which one you
  mean when recommending a channel.

## Creator outreach in this genre

- The audience is specialist and committed: long-form video (2h+), creators with
  thousands of hours in the incumbents. **A shallow system is caught inside one
  video**, and the creator will say so on camera.
- Pitch rules: lead with **the one mechanic that is genuinely novel**, shown in
  mechanical detail. Never lead with cinematics or a story trailer.
- Channels covering the space (subscriber counts from a third-party ranking - treat
  as approximate): PotatoMcWhiskey ~543k, Orbital Potato ~192k, Nookrium ~190k,
  Pravus, JumboPixel, LT Gaming, Easily Distracted Games. Add the Paradox-side
  channels (Quill18, and the HOI4/EU4 mod-and-exploit crowd) for reach.
- Pitch before launch, with a build - not at launch with a store link.

## Publisher routes

Fit is a question about the **shipped portfolio**, checked against the game's genre:

- **Hooded Horse** - the deep-strategy house (Against the Storm, Manor Lords, Old
  World, Norland, Terra Invicta). Best genre fit by far. **Check what they already
  publish in the game's own slot first**: a publisher that owns the exact niche is a
  conflict of interest for that pitch, and saying so is more useful than listing them
  as a warm lead.
- **Paradox Arc** - open pitch form, "Paradox DNA" framing, but the portfolio is
  roguelites, colony sims and survival. Weak fit for a grand strategy game.
- Others worth naming: Firesquid, Kasedo, Iceberg, Slitherine/Matrix (Shadow Empire),
  Goblinz.
- Frame the trade honestly: money and marketing muscle against revenue share,
  milestones, and sometimes the IP.

## Worked example: pitching into an occupied slot

The espionage-grand-strategy slot is already taken: **Espiocracy** (Hooded Horse,
appid 1670650) - lead an intelligence agency across 74 playable countries,
1946-2023, store target pushed 2025 -> 2026 -> Q3 2027. Two durable lessons came out
of reading its own news feed rather than its store copy:

- **A monthly dev diary, fixed week, published for years before launch** is the
  genre's proven pre-build marketing machine. Their diary subjects are the same
  systems any competitor is designing (nuclear programmes, economy, SIGINT,
  counter-intelligence, false intelligence, onboarding, UI). Copy the cadence, not
  the format.
- **The release-date slip cost them nothing because the audience existed first** -
  which is why "never recommend a date as a marketing move" is a rule here and not a
  preference.

Positioning consequence for any similar project: the wedge must be a *different level
of abstraction* (state vs agency, a century vs decades, economy and deterrence
included), sourced from the design document - never "a better version of X".
