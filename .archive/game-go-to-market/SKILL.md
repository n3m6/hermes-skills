---
name: game-go-to-market
description: "Use when planning game launch marketing or early buzz."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [game-design, marketing, steam, launch, gtm, wishlists]
    related_skills: [product-teardown, grand-strategy-design-docs, wwx-shadow-wars, reddit-mining]
---

# Game go-to-market (early buzz to launch)

Planning the marketing around a game the user is building: what to do at the
design-doc stage, what to switch on when a build exists, what never to spend early,
and which assets are one-shot. Measuring *other people's* games lives in the
`product-teardown` skill - its game-market-metrics reference carries the endpoint
procedure; this skill is the forward-looking plan. It supersedes the archived `go-to-market-strategy`
skill.

## When to Use

- "What marketing should I do for my game?" / "how do I get early buzz?"
- Any wishlist, demo, Steam page, Next Fest, creator-outreach, publisher or
  crowdfunding decision for a game the user is building.
- A pre-launch positioning question (naming, capsule, tags, the one-line hook).
- Re-planning at a new stage: design docs -> build -> demo -> launch window.

## House rules (this user)

- **Verdict first.** One short paragraph naming the single highest-leverage move and
the one strategic fact that reframes the rest, then the detail. He reads the verdict
and skims the rest.
- **Ground every market claim in the platform's own numbers**, and label provenance
in three tiers: fetched directly / seen only as a search snippet / your own
synthesis. Name any load-bearing number that leans on a weaker source than the rest.
- **Never estimate a wishlist, follower or sales count.** Valve does not publish
them; a third-party tracker (steamdata.ai, raijin.gg, SteamDB) is cited as
"per <site>", never as fact. Review counts are a sales *proxy* - label them, never
convert them to units.
- **Tier the options by time horizon** (now / 6-18 months / launch window /
structure). The right answer at the design-doc stage is nearly the opposite of the
right answer inside the launch window; one flat list of "marketing ideas" answers
neither question.
- **Name the incumbent before recommending any positioning.** If a funded competitor
already occupies the genre slot, say so plainly and build the wedge out of the user's
own design document - a wedge stated without a citation is a wish.
- **Deliver the plan in chat and offer to lay it into the repo.** Never write
marketing docs into the game's own repo unprompted: the repo holds design and
history, not GTM. (Same rule as `product-teardown`'s "never write competitor
material into the product's own repo".)
- **Close with what could not be verified**, listed, not glossed.

## Procedure

1. **Establish the stage in one line** - design docs only? a slice? a demo? a date
already announced? Everything below keys off it.
2. **Find the incumbents.** Search the store with the game's own pitch as the query,
pull the same facts the teardown method gives (`storesearch` -> `appdetails` ->
`appreviews`), then read the incumbent's **news feed**: cadence, subject list, and
every public release-date slip. That feed is the competitor's marketing machine
written down, and it is the single most useful fetch in the whole exercise.
3. **Pull the market numbers** - the audience-defining titles, the adjacent-niche
ceiling, the sub-genre medians, and the wishlist-to-sale benchmark for the genre
cluster. Cite each with source and date-of-pull.
4. **Locate the audience where it actually posts**, not where it "should" - see
`references/strategy-genre-reach.md` for the method and the grand-strategy map.
5. **Build the tiered menu**, then a concrete sequence for the next 12 months.
6. **State the one-shot assets out loud** (below). Spending one early is the most
common and most expensive mistake available at this stage.
7. **Offer the written artifact** (a repo doc, a positioning sheet) rather than
producing it unasked.

## The one-shot assets - say which are permanent

- **Steam Next Fest: one participation per game, ever.** Unreleased titles only, a
public Coming Soon page, and a publicly playable demo live before the fest starts.
Take the *last* edition before the planned launch - Next Fest multiplies an existing
wishlist base, it does not create one. Eligibility, deadlines and the preview rhythm:
`references/steam-launch-mechanics.md`.
- **Early Access is a release.** It permanently disqualifies the game from Next Fest.
That is its real cost - state it whenever EA is on the table, because the revenue
argument for EA is never complete without it.
- **The announcement.** A store page that idles for a year spends the spike for
nothing. Valve only requires a Coming Soon page live >= 2 weeks before release; there
is no upper limit. Set the *trigger* (capsule + 5 gameplay screenshots + gameplay
trailer + tags) instead of pulling the page early.
- **Never recommend a release date as a marketing move.** Slides cost nothing before
a date exists and strand the audience after one is public.

## Facts that do not go stale

- Paid wishlists convert **2-4x worse** than organic Steam-discovery wishlists, so
"no paid acquisition before launch" is the standing recommendation, not a budget
opinion.
- Valve rotates themed fest names and dates. Look the current one up on Steamworks'
Upcoming Events instead of recalling last year's name - a "Strategy Fest" existed;
the recent calendar carries a "Real-Time Strategy Fest".
- Name, capsule and tags are the highest-leverage store assets. A tag an incumbent
owns is a tag the newcomer must not claim identically: derive the tag set from the
competitor's by *difference*.
- Publisher fit is a question about their **shipped portfolio**, not their prestige.
- A devlog cadence is the only marketing asset a pre-build game can accumulate:
monthly, a fixed day, in the developer's own voice, mirrored to every channel the
audience actually reads. An incumbent's own news feed is the proof it works in the
genre.
- Crowdfunding is a marketing event, not a funding mechanism: it needs the audience
first, so it is a later-stage decision that people routinely sequence backwards.

## Pitfalls

- **Do not answer a pre-build-stage question with launch-stage tactics.** Creator
outreach, fests and ads are worthless without a build and a base, and recommending
them early burns the one-shot assets the user only gets once.
- **Third-party tracker numbers are estimates dressed as data.** Cite the site; the
user audits provenance.
- **A genre's own subreddit is usually not where its audience is** - grand strategy's
is a rounding error next to the product subreddits. Verify before building a plan on
it.
- **Publisher conflict of interest**: a publisher already shipping a game in the exact
slot is not a neutral home for the pitch. Name the conflict rather than listing them
as a warm lead.
- **Store tags do not come back through a plain curl of the store page** - fetch the
page in a rendered browser. Tags are a positioning decision, so this is worth doing
properly rather than guessing a set.

## References

- `references/steam-launch-mechanics.md` - the Steam funnel in order (Coming Soon ->
wishlists -> demo -> Next Fest -> launch week), eligibility and deadline rhythm,
wishlist-conversion benchmarks by genre cluster, how to read Steam's numbers without
fooling yourself, and the announced fest calendar with a re-check instruction.
- `references/strategy-genre-reach.md` - where the grand-strategy / geopolitics
audience actually lives, creator-outreach rules for the genre, mod-community
adjacency, the publisher-fit table, and a worked example of pitching into an occupied
slot.
