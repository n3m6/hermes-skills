# Canonical grand strategy / 4X design doc TOC

The genre-typical structure. Trim and reorder per project; do not paste whole
into a vision-level doc.

**0. Front matter** — doc conventions, version history, status legend
(decided / proposed / open), glossary, reference-and-competitive analysis
(which system is borrowed from which game, and why).

**1. Vision** — high concept; player fantasy and core verbs; 3-5 design pillars,
each with "what this means we do" and "what this means we won't";
anti-pillars; audience, platform, session length; scope statement (map scale,
time span, entity counts); the first hour described in prose.

**2. Core framework** — who the player *is* (state / dynasty / species /
corporation); time model (turn vs pausable real-time vs simultaneous) and tick
order; macro / meso / micro loops; action economy per turn; victory, defeat and
end states; game length targets and the pacing curve; emergence doctrine
(simulated vs scripted); snowball control and feedback loops.

**3. Map and world** — topology and scale with hard counts (N provinces, N
systems); terrain, climate, resource distribution; regions, movement,
chokepoints; mapgen rules and validation; fog and exploration; intel model
(what the player knows vs what is true).

**4. Factions** — faction model and asymmetry axes; the roster, each with
fantasy plus mechanical hook; starting conditions and scenarios;
traits/civics/ethics combinatorics; AI personalities expressed as data.

**5. Population and internal politics** — the subject model (pops, provinces,
estates); classes, culture, religion, ideology; interest groups and how they
gain or lose power; the internal health model (legitimacy, stability, unrest,
corruption); government, laws, succession; revolution and civil war rules;
character/dynasty layer where applicable.

**6. Economy** — resources (stock vs flow, tiers, sinks); production chains and
buildings; trade routes, markets, tariffs, supply and demand; taxation, debt,
maintenance; automation and governors; balance targets plus a pointer to the
numbers spreadsheet.

**7. Technology and progression** — tech model (tree / DAG / era / emergent)
and research generation; diffusion, adoption, obsolescence; ideas, traditions,
doctrines, focus trees; institutions and reform; non-tech progression
(culture, prestige, religion).

**8. Military** — combat model and resolution; unit design vocabulary and the
space it spans; manpower, morale, supply, attrition, logistics; movement,
fronts, zones of control, occupation; sieges; naval/air/space layers and how
they interact; war goals, war score, peace deals, casus belli; military AI and
automation; espionage and intel.

**9. Diplomacy and international systems** — the full diplomatic action
inventory; relations model (opinion, trust, attitude, favours); treaties and
their enforcement and breaking; subject-overlord, vassalage, unions,
federations; international institutions and law; diplomatic AI acceptance logic
and exploit resistance.

**10. AI** — architecture (strategic / operational / tactical) and planning
horizon; goal selection and budgeting; the explicit cheat contract per
difficulty; CPU budget; validation methodology (mirror matches, sim harness,
regression suite).

**11. Content and narrative** — event system and chains (triggers, weights,
cooldowns); decisions and missions; narrative voice and tone;
historical-vs-fictional framing; content inventory and budget (N events, N
techs, N units); localization requirements.

**12. UX** — the information problem stated explicitly (what the player must
know, when, and how); screen and map-mode inventory; alert architecture with
priority tiers and "show me why this happened" tracing; tooltips and number
provenance (show the maths); onboarding, tutorial, advisors; the anti-micro
automation surface; accessibility and readability standards.

**13. Simulation architecture** — determinism and tick order, sim/render
separation; data-driven content and the scripting/mod API; save format,
versioning, patch compatibility; performance targets (turn time, entity
counts) — the late-game problem; modding tooling.

**14. Multiplayer** — model (simultaneous / turn / hotseat / co-op) and
drop-in; netcode, determinism, desync handling; pause and order-resolution
rules; MP-specific cheese and balance.

**15. Presentation** — art direction and visual pillars; map readability and
iconography; unit and character art; adaptive music and audio; UI style guide.

**16. Production** — content budget and staffing; milestones (prototype,
vertical slice, alpha); scope control and cut discipline; expansion/DLC hooks;
playtesting and telemetry plan.

**17. Balance and tuning** — balance philosophy and designer's intent per
system; tuning levers and the single source of truth for numbers; known
degenerate strategies watchlist; metrics (snowball curves, decision density,
turn-time budget).

**18. Risks and open questions** — top risks with mitigations; explicitly
unsolved problems; assumptions to validate, each paired with the test that
would validate it.

**Appendices** — glossary, spreadsheets, mockups, references, changelog.
