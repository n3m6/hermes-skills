# Population code map (design §5, milestone 6)

Read this before answering any "how do pops / instability / cleavages work?"
question about the repo. It is the population counterpart to
`economy-code-map.md`; re-deriving it costs a dozen greps.

**Status: built, not a demonstration.** The model is milestone 6 (D3/D4) plus
W-151 (exact intersections at every LOD), W-157 (material deprivation), W-179
(dispossession), W-193 (grey arms + enforcement). The regime axis (§5.9–5.12) is
not built and that decides what is missing (below).

## Where it lives

| Concern | Path |
| --- | --- |
| Group + province content | `content/groups/groups.json`, `content/provinces/provinces.json` |
| Marginal crossing → cells | `crates/session/src/composition.rs` (`province_cells`, `cell_key`) |
| Cell / aggregate / profile / fingerprint types | `crates/core/src/truth/pop.rs` |
| `Province` (cells, aggregate, drift_cause) | `crates/core/src/truth/mod.rs:639` |
| The monthly law | `crates/core/src/systems/pops.rs` |
| Category aggregates (231 constituencies) | `crates/core/src/category.rs` |
| Condition score + rungs + funded road | `crates/core/src/pawns/rung.rs` |
| Cleavages (derived, output phase) | `crates/core/src/systems/output.rs`, `derived.rs` |
| Ladder transitions journalled | `crates/core/src/population_journal.rs` |
| LOD promote/demote | `crates/core/src/systems/lod.rs` |
| Player surfaces | `crates/cli/src/play/screen/population.rs`, `crates/cli/src/map.rs` |
| Tests | `crates/core/tests/population.rs`, `crates/cli/tests/population.rs` |

## Shape

- Content authors **three marginals** per province (ethnicity, religion, class),
  never cells. `province_cells` crosses them: share = product of the three ppm
  values over 1e6^2, truncation residual given out largest-raw-product-first,
  ties by cell key. Cell key is `group:<ethnicity>+<religion>+<class>`.
- Each cell is a `PopGroup { kind, size, grievance, organisation, radicalisation,
  loyalty }`. **Income is not a field** — it is derived by
  `truth::income_of` as `class SoL × (0.55·development + 0.45·infrastructure)`,
  read through `ProvinceIncome`. Attention/LOD can never move it.
- Per-cell `GroupProfile` (the grievance datum) combines the cell's three category
  profiles: income from the class only; grievance, organisation and
  radicalisation = **max** of the three; loyalty = mean.
- `Province.aggregate` is the population-weighted mean of the five over actual
  cells; `Province.drift_cause` is the current dominant cause, hashed.
- `state.population` is overwritten each month as the sum of provinces **by
  owner** (occupation is not nationality). The branch for states with no
  provinces is live-code-but-dead-data: all 69 states have provinces.
- Two representations, `Focused(Vec<PopGroup>)` and `Reduced(Vec<ReducedCell>)`,
  differ only in struct shape. Since W-151 demotion **retains every cell's exact
  count and all four conditions**, so LOD is lossless for population and the same
  law runs at both levels. The fingerprint survives as the share summary and as
  the initial split of a never-focused province. Do not repeat the older claim
  that demotion merges pops or loses history.
- Hashed truth includes cell sizes/conditions, province aggregates and profiles;
  category aggregates, condition scores, rungs and cleavages are **derived** and
  never hashed. Grep `TRUTH_DOMAIN` in `crates/core/src/hash/world.rs` and
  `VIEW_SCHEMA` in `crates/projection/src/view/dto.rs` rather than quoting these.

## The month (order matters)

1. **Growth** — `pops.monthly_growth_permille` (0.1 %/mo) × a derived per-province
   draw in [0.5, 1.5]; increment = `floor(total × rate)`; split across cells by
   largest remainder. Every cell in a province grows at the same rate.
2. **State reconciliation** — modelled states take their provinces' sum.
3. **Attribute law**, per province then per cell:
   - grievance → `0.45·profile + 0.20·inequality + 0.10·control deficit +
     0.25·material deprivation`, plus additive dispossession and enforcement
     terms, relaxed at 5 %/mo;
   - organisation → `max(funded autonomy, natural)` at 10 %/mo, or −2 %/mo
     absolute when both are zero; natural = profile capacity ×
     (1 − 0.8·(1 − concentration)) × (1 − 0.6·(1 − development));
   - radicalisation → `g × o + arms`, 4 %/mo up, 1 %/mo absolute down;
   - loyalty → `1 − grievance` at 3 %/mo (deliberately lagging).
   Province mean income is read **before** any write; g and o update before r and
   loyalty. All five are clamped.
4. **Aggregate refresh** from the actual cells.
5. **Rung-5 roll** — 60-month per-state cooldown, then a cheap necessary-condition
   gate, then the most advanced category; a derived draw pays 40/35/25 as
   stability shock / government falls (tier→independent, patron cleared) / an
   independent armed movement. Fires for the player's own state too, but cannot
   end the campaign (deposition §5.12 unbuilt).

A province's drift cause is journalled only when it **changes**, not monthly.

## Readers a player sees

- Condition score = `min(g, o, r) × (1 − 0.25·loyalty)`; rung = 1 + thresholds
  cleared (15/30/45/65 %). Funded road = 1 + autonomy / `pawn.party_threshold_ppm`.
  Higher road wins; the supporting road is recorded (`population_journal`).
- Cleavages: gains 0.40 inequality / 0.30 exclusion / 0.25 cultural / 0.20
  historical / 0.35 geographic, reported above 0.40. **Exclusion is a hard zero
  until §5.9 exists.**
- A network that looked this month writes a believed `PopulationCondition` = max
  condition score over the target's categories, confidence = penetration. No
  network, no belief; foreign composition stays public, foreign conditions unknown.
- `population [STATE] [--provinces]`: composition by kind with shares; own country
  gets ladder + sharpest fault line + province rows; foreign gets composition plus
  a believed scalar or an explicit "unknown".
- Map modes: `ethnic`, `religious`, `cleavages`, `instability` (four of nine).

## Gaps to state honestly

- **No demography.** No births/deaths by cohort, no migration, expulsion, massacre
  or urbanisation; a province's composition shares barely move over a century.
  Growth is one uniform random rate per province.
- Growth is `floor()`ed: a province under ~667 people grows by zero every month,
  and 17 provinces are under 1,000. Check content before claiming otherwise.
- Regime axis (§5.9–5.12), named leaders (§5.7), institutions (§5.10–5.11) and
  mass violence (§5.14) are absent, so 5 of §5.6's 8 state outcomes are
  undecidable and unbuilt; civil war is re-deferred to that milestone.
- Income is class SoL × a province factor, not an observed labour-market outcome;
  no cell-level employment.
- Zero-share cells still exist and still drift; they just hold nobody.

## Counts

Recompute, never quote. Current content: 231 groups (199 ethnicity / 27 religion
/ 5 class), 1,977 provinces, 69 states, ~160k cells, opening population 2.241 bn.

```python
import json, collections
p = json.load(open('content/provinces/provinces.json'))['provinces']
g = json.load(open('content/groups/groups.json'))['groups']
kind = {x['id']: x['kind'] for x in g}
cells = sum(
    collections.Counter(kind[s['group']] for s in pr['groups'])['ethnicity']
    * collections.Counter(kind[s['group']] for s in pr['groups'])['religion']
    * collections.Counter(kind[s['group']] for s in pr['groups'])['class']
    for pr in p
)
print(len(g), len(p), cells, sum(pr['population'] for pr in p))
```

Code comments and the design doc carry older measured figures (159,329 and
160,113) from earlier content revisions. Treat any cell count in prose as stale
until recomputed.
