# Grand-strategy genre evidence: what retains, what leaks

Distilled from shipped-title reception — Steam review aggregates, retention
curves, review text, and published patch/dev-diary timelines — plus the
*designers' own published statements* about the systems they built (second
section below). Use it to pressure-test pillars and anti-pillars: a source of
*design constraints*, not of features to copy. The patterns are durable; any
figures are point-in-time samples.

## The retention law (design against this)

- New releases in this genre rarely fail at launch; they fail at **retention**. A
  sequel launches on the predecessor's reputation, then bleeds most of its
  concurrent players within months while the finished older title keeps its base.
  A flagship sequel can set a series-record concurrent peak at launch and still
  end the year below a thirteen-year-old predecessor.
- The new game is compared against the old game's *final* version (a decade of
  patches plus mods), not its own v1.0. Broad-but-shallow v1.0 loses to deep,
  stable, finished.
- Design consequence: ship a complete small loop and accrete depth. Do not reset
  the depth that made the predecessor beloved in order to chase scope.

## What retains

- **One legible core verb.** Every long-lived title answers "what am I doing?" in
  one sentence (paint the map / run a war machine / live a dynasty). If you cannot
  state it, the onboarding cliff is unwinnable.
- **Direct, readable agency in the core conflict loop.** War is where the player's
  will meets the world. Automating that loop (auto-resolved fronts, dice-roll
  outcomes) is the single most-cited failure mode in the genre.
- **Legibility over fidelity.** Players must be able to predict outcomes and own
  their mistakes; a deep simulation they cannot read is reported as "spreadsheet
  slop".
- **A finished product.** "Complete, balanced, stable" is itself a praised
  feature, and a finished older title out-draws its own sequels.
- **Modding + structured goals** (mission/focus trees) extend life across every
  survivor — while drawing a "railroading" critique. That trade-off is a decision
  to make explicitly, not a free win.

## What leaks

- **Abstracting the promise.** If the fantasy is X, the player must directly *do*
  X. Abstracting it away (an economy sim sold as nation-building, a society sim
  sold as history) reads as arbitrary and is the most consistent late-review
  complaint.
- **Unfinished at 1.0**, especially sweeping mechanic overhauls shipped with
  regressions. Buyers resent being unpaid testers; "mark it early access" is the
  recurring verdict.
- **Pacing collapse after growth saturates** — systemic to exponential economy
  models. Design the post-scaling phase explicitly or the game "ends" mid-campaign.
- **DLC that reads as cut content.** Core systems sold separately is the most
  common complaint even on beloved titles — a reputational tax that drags
  sentiment on good games.
- **Selling the whole world, shipping the core region.** Non-core-region content
  shipped thin is a standing launch complaint.
- **The onboarding cliff** — universal and unsolved; veterans frame it as a
  compliment, everyone else bounces off it.
- **Late-game performance / turn time** — a design decision, not an engineering
  afterthought; it decides retention.

## Reading the evidence honestly

- A collapsed 30-day score on an old favourite is often an off-topic review bomb,
  not a design verdict — verify the window's negatives before citing it. Procedure
  in the `product-teardown` skill's `references/game-market-metrics.md`.
- Review counts are a sales proxy, never units. Recent-window percentages on
  older titles are tiny-N and noisy: state N.
- Lead with **retention** (concurrent/monthly player trend, recent-review
  recovery, DLC spikes) plus the launch-window story the headline score encodes.
  The all-time score barely moves after launch, so it is a lagging read of
  retention — not of ambition.

## What the designers state in public (the dev-side tier)

The people who build these games have published a decade of admitted trade-offs.
Same pressure-testing job: a pillar that contradicts one of these needs a stated
reason, because the trade-off was already made once and cost something.

- **Legibility is the declared design goal, not depth.** Victoria 3's designer
  frames the whole economy around "understandable and feels empowering", and says
  the open model deliberately gave up fidelity (no stockpiles) to buy
  comprehensibility and a CPU budget. Expect to trade simulation for legibility —
  and defend the trade explicitly rather than by accident.
- **History is a source of mechanics, not a specification.** "Choose the historian
  that gives the most gameplay." A faithful WWII sim means Germany always loses;
  where a historical act was unprofitable (colonising Africa) players and AI
  rationally skip it and the map stays empty. Invent the incentive instead of
  shipping an accurate-but-dead map.
- **One legible unified mechanic beats a dozen systems.** CK2's Opinion is one
  visible −100..+100 number summed from tooltipped reasons, and the AI reasons
  directly off it.
- **Separate expected randomness from weird randomness.** Reasonable random
  outcomes are the point ("infinite replayability"); being surprised by your own
  mechanics means the design was under-specified.
- **Fix the game's identity before production** — how it should feel at 10 minutes
  and at 10 hours. The documented failure is a team drifting between genre poles
  and only discovering it late.
- **Prototype the unfamiliar and risky features first.** The excuse that "you
  can't judge a system until every other system is in" is exactly how fundamental
  problems land in the last months; the postmortem that names it calls skipping
  prototyping indefensible.
- **Fight snowballing with constants that do not scale with territory** — monarch
  points, vassal dependence, influence. Note that the designers who built these
  call it *unsolved*: it needs an explicit design, not a hope.
- **Endgames are decided before the player finds out.** A good strategy wins or
  loses long before the result is revealed and the rest is waiting. Expansion
  mechanics stop working past a unit-count threshold, so detect the decision point
  and end the game rather than grinding out a foregone conclusion.
- **AI capability caps system complexity.** Expose world features for the AI to
  assess. A role-play layer lets a weak AI pass because players read personality
  into it; without one, the AI has to actually be good.
- **Onboarding is a retention metric.** Use progressive disclosure, cut the
  tutorial box count hard, and playtest with people outside the team (designers
  suffer "the curse of knowledge"). Telemetry showed tutorial completion was not
  what kept players.
- **Live-service discipline:** at least one free patch per paid release; QA tests
  the *fantasy*, not just function; every addition must be tested against content
  shipping years later.
- **A real-world setting carries non-design costs.** Place-names are geopolitical
  (naming a disputed sea drew threats and mass store reports), banned symbols go
  beyond the obvious, politics in a contemporary setting is judged asymmetrically
  versus a fictional one, and the mainstream narrative shifts mid-production.
  Budget legal/PR cost, not just research.
