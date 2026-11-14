# Economy circuit: where the code is and how a month flows

Read this before answering "how is trade / money / FX implemented?" — it saves
the full re-derivation. **It is a map, not a measurement.** Names and files are
stable; coefficients move often. Read every number from
`content/balance/balance.json` (keys are listed below) and every schema id from
the code. When behaviour and this file disagree, the code wins.

## Where things live

- `crates/core/src/systems/economy.rs` — the month owner: `month()` /
  `month_observed()`. Expires `supply_cuts`, `currency_attacks`,
  `devaluation_until`, `default_until`, runs `abroad::lose_clients`, then
  `trade::routes` → `monthly::clear` → `crisis::advance`.
- `systems/economy/trade.rs` — the world goods snapshot (`GoodsRow`), opening
  `TradeLink` derivation, per-month `routes()`, `bloc()`, `embargoed()`,
  dependence helpers (`patron_share`, `largest_import_partner`,
  `essential_dependence`).
- `systems/economy/monthly.rs` — the big monthly owner: budgets, households,
  producer import cohort, taxes, `completed_trade` writing `Economy.imports /
  exports / trade_balance / import_tax / export_tax`.
- `systems/economy/circuit.rs` (~10k lines) — the prepared domestic monetary
  circuit and the sole `economy::month` cutover; the price law is here.
- `systems/economy/circuit/foreign.rs` — matched trade and foreign claims:
  `Link`, `route_weights`, `competitive`, `home_first_shares`, deliveries,
  ownership, `Rent`, `Loan`, `Transfer`, `FoodAid`.
- `systems/economy/circuit/external.rs` — stage 7 external settlement:
  facility service, pool payouts, redemption, recycling, write-off, M̄ trend.
- `systems/economy/circuit/fiscal.rs | investment.rs | payment.rs | planner.rs |
  assessment.rs` — the other stages.
- `crates/core/src/finance/funding.rs` — `Funding` cohorts (the cross-border
  funding order). `finance/external.rs` — F, pool, facility, `reserve_months`.
  `finance/mod.rs` — `FinanceBook`, postings, instruments.
- `crates/core/src/economy_balance.rs` — `EconomyBalance`, every `economy.*`
  key as a typed field with its `Default`.
- `content/balance/balance.json` — authored values; `crates/content/src/balance.rs`
  — the key enum with domain per key; `crates/session/src/balance.rs` — the
  content→core mapping.
- `crates/projection/src/view/dto.rs` — economy and external view blocks.
- `crates/econ-harness/` — scenarios, sweeps, invariants, traces, monetary
  explorer; the place to measure a balance claim.

Long-form design records: `docs/international-money-proposal.md`,
`docs/monetary-circuit-build-brief.md`, `docs/economy-evidence.md`,
`docs/economy-circulation-*`. Design law: `docs/design/06-economy-soft-power.md`
§6.2–§6.4 and `docs/design/00-open-questions.md` W-155…W-179.

## Trade (imports/exports) — built

- **One aggregate clearing price per state**, `truth.domestic.price(state)`; not
  per good and not per pair. It moves by `demand_price·excess +
  cost_price·growth`, clamped to ±`price_step` per month and bounded by the
  authored floor/ceiling (`circuit.rs`, the block computing `unit_cost` →
  `next = c.price * (1 + change)`). No relative prices between goods exist.
- **Links** (`trade.rs::initialise`): pairwise state links kept if the opening
  weight clears `trade_link_floor_ppm`. Weight = `trade_adjacency_weight_ppm`
  (if bordering) + `trade_sea_weight_ppm` (shared sea zone) +
  `trade_bloc_weight_ppm` (same patron, or same alignment when Player/Rival)
  + `trade_complement_weight_ppm · complementarity`, all minus
  `(tariff_a + tariff_b) · tariff_link_penalty_ppm`. Complementarity =
  `opposed()`, an integer cosine of each state's supply−demand vector.
- **Routing**: home-first (`home_first_shares`); the foreign shortfall is shared
  by `weight × seller's exportable surplus`; then `foreign::competitive`
  multiplies each foreign weight by
  `clamp(1 + competitiveness_gain·(P̄ − P̂_j)/P̄, min, max)`, where P̂_j is the
  **seller's own price index**. The docstring says "landed price" — the code
  does not add tariff or transport. Do not repeat the docstring.
- **Invoice**: `units × seller's domestic price`. Import levy =
  `buyer's tariff lever · import_tariff_max_ppm`, paid to the buyer's own
  treasury. Export levy = `seller's tariff lever · export_tariff_max_ppm`, taken
  from the selling sector's receipt. `trade_cost_ppm` destroys a share of the
  shipped units; the invoice still pays the supplier in full.
- **Tariffs do not reallocate trade.** The import rate is per buyer and equal
  across that buyer's routes, and neither levy enters a route weight. A tariff
  changes affordable volume and revenue, never which seller is chosen. Only
  `devaluation_export_bonus_ppm` shifts selection.
- **Funding order** (`finance/funding.rs::cohort_with_draws`, and `keep()` which
  unwinds in the same order): F (the payer bank's external reserves, pro rata
  within its cohort) → bilateral line (capacity = last month's export receipts
  to that partner, `set_line_limit`) → pool facility draw (borrower headroom ∧
  pool cash, shared across the cohort by remaining shortfall) → **refusal**: the
  order is cut, the buyer keeps its cash, no goods ship, and the cancelled
  invoice is added to `result.external_refused`. Authority advances and R_d are
  never sources for external payments.
- **Accounts**: `Economy.imports / exports / trade_balance / import_tax /
  export_tax`; per-delivery `TradeDelivery { seller, buyer, goods, units,
  arrived, paid, import_paid, export_paid, formal }`. Projection prints
  imports, exports, trade_balance per state.

## External money (the FX-shaped layer) — built

- At the opening F is split out of settlement assets: `R = R_d + F`,
  `F = min(R, opening_reserve_ppm · 12 · monthly nominal GDP)`. Only F funds
  cross-border payments; R_d keeps authority interest/advance service and
  Treasury advances.
- Limits refresh every month in `refresh_external` (`circuit.rs`), from M̄ (trend
  external payments) and trend GDP:
  `facility_limit = facility_months · max(M̄, facility_gdp_ppm · trend GDP)`;
  `floor = floor_months · M̄`;
  `ceiling = max(ceiling_months · M̄, ceiling_gdp_months · trend GDP)`.
  Keys: `external.*` in `balance.json`.
- `circuit/external.rs::external_settlement` runs facility interest then
  scheduled principal from F, passes pool receipts to claimants pro rata,
  redeems below the floor, recycles `recycling_ppm` of the excess above the
  ceiling into pool cash against a named claim, and writes off a facility after
  `default_months` with the haircut borne by claimants. The pool never mints.
- Reading: `ExternalReading::reserve_months` = F / M̄, `None` while M̄ = 0.
  Foreign reserves are fogged (believed/unknown); facility drawings are public
  fact. The view block carries reserves, reserve months, M̄, floor, ceiling,
  facility limit, pool claim, facility, arrears, draw/receipt/recycle/refusal.

## No exchange rates, no conversion

There is **no parity, currency or conversion field anywhere in `crates/`**.
One unit, one `FinanceBook`, all cross-border legs settle at 1:1. The design
adopted reserves + an adjustable peg (W-173) and the owner cut it back to
reserves only (W-176); the peg, the reserve-currency issuer, the post-1971
float and capital flows are deferred modules D1–D3, each needing its own
adoption. `docs/design/06-economy-soft-power.md` §6.4 carries the deferral.

- **`devalue` is not a parity change.** `BroadDecision::Devalue` gets duration 3
  from `broad_admission`, sets `devaluation_until`, and logs `Devalue {
  previous, current }` with both equal to the current inflation. Its only
  effect is in `trade.rs::routes`: the seller's route weight is multiplied by
  `1 + devaluation_export_bonus_ppm` for those clearings. The declared
  `economy.devalue_inflation_ppm` is mapped and validated but **read by no core
  code**.
- **Rivals devalue on any negative trade balance** (`ai/policy/economy.rs`),
  with no reserve condition — W-176 reverted that.

## Currency attack — built, but only one leg is wired

`programme:currency-attack` on `verb:economic-warfare` (family E, two stages:
position capital, then attack). The era gate is a hard-coded `year < 1971`
refusal in `systems/inputs/programme.rs` (the verb's own `era_from` field is
authored and unread; `SupplyCut` and smuggling are the same pattern with 1960).

`EffectKind::CurrencyAttack` (`effect.rs`) scales by the **attacker's**
`financial_depth` and pushes `(until, inflation, flight)` onto the target for
`currency_attack_months`. Only the flight leg is consumed: the monthly owner
sums the third element into `currency_attack_pressure`, which feeds the crisis
flight trigger. The inflation element is stored and hashed but never applied to
`e.inflation` or the price level. A successful attack currently raises crisis
pressure and cannot move prices.

## Verifying that a balance key is actually live

The four-file chain (core field + `balance.json` + validator list + session
mapping) proves a key is *declared*, not *read*. To test a claim about
behaviour:

1. Grep the **field** name in `crates/core/src`, excluding
   `economy_balance.rs` (the declaration) — hits only in `session/`, `content/`
   or tests are not readers.
2. For a tuple/struct field, check **each component** has a consumer; a fold
   over one element of a 3-tuple leaves the other two dead.
3. Confirm the consumer is on the monthly path from `systems/economy.rs` (or a
   command in `systems/inputs/`), not only in a test fixture.

## Inflation

`Economy.inflation` is set once a month in `monthly.rs`: `previous_price` is read
before `domestic.finish`, `next_price` after it, and inflation is their ratio
change, Q32. **It is a monthly rate.** The field's doc comment says "Annual price
pressure" — stale; every threshold compared against it is monthly
(`crisis_inflation_trigger_ppm` ≈ 1.67%/month).

The only price equation is in `circuit.rs` (the `unit_cost` → `next = c.price *
(1 + change)` block):

- `excess = clamp((affordable_demand − supply) / supply, −1, +1)`; `supply == 0`
  with demand gives 1.0.
- A basic food/energy shortage withholds `supply.price_control_ppm` of *positive*
  excess — rationing absorbs the shortage instead of the price.
- `growth` = unit-cost change month over month, clamped ±100%.
- `change = demand_price·excess + cost_price·growth`, clamped ±`price_step`;
  price clamped to `[price_floor, price_ceiling]`.

**There is no money-stock term, no velocity, no expectations and no wage
indexation.** Inflation is a goods-market and unit-cost statistic; money moves it
only by being spent into `affordable_demand`.

Readers: the crisis axis, the AI remedy/phase, the projection (`OwnEconomyView`),
the CLI screen and the hash. Inflation is **own-only** on the wire — a foreign
observer does not see another state's inflation or price index; only
`EconomyView.crises` is public. A covert attack on prices is therefore steered by
a believed reading or noticed only as a started inflation crisis.

Four inflation keys are declared, mapped, validated and read by nothing:
`economy.monetary_inflation_ppm`, `economy.inflation_decay_ppm`,
`economy.inflation_sol_erosion_ppm` (plus `economy.devalue_inflation_ppm`). Never
describe them as behaviour.

Counterfeit consequence: forged units must become spendable demand. Openness
leaks extra demand into imports (and later into `external_refused` refusals); at
`demand_price_ppm` 0.10 the full `price_step` move needs ~50% excess demand; the
price ceiling caps cumulative damage; and there is no cash/notes channel, so
"inject money" means crediting deposits and choosing who bears the unbacked
liability.

## Coercion instruments: what exists and what gates it

- `Command::Sanction` / `LiftSanction` — `Economy.sanctions`; `trade::embargoed`
  zeroes the whole link in both directions, all goods, and a patron's sanctions
  bind its clients one level deep. `sanction_alignment_ppm` fires only when the
  target is your own client. No sender cost, no tiers, no third-country evasion,
  no rival rule; the projection carries the owner's own list, so the target does
  not see who sanctions it.
- `Command::CutSupply` — food or energy only, `leverage_months` duration,
  hard-gated 1960+, refused unless the actor supplies `leverage_threshold_ppm` of
  the target's imports of that category; resentment only if the target is your
  client.
- `Lever::Tariff` — one global phased lever; the import levy is capped by
  `import_tariff_max_ppm` and the export levy by `export_tariff_max_ppm`. No
  quota, no import ban, no per-partner rate, no retaliation rule.
- `Command::Invest`, `SetExtractionTerms`, `ForceLoan` — all `patron`-gated: the
  host must be a government you installed. Invest covers only
  extraction/industry/finance/services; `ForeignAsset` carries equipment titles,
  installed capacity and the last return. No purchase from a non-client, no
  concession market, no strategic-stockpile command, no exclusivity.
- `TakeForeignDebt` (own borrowing), `GiveAid` / `GiveFoodAid`,
  `RestructureExternal`, `BroadDecision::Default` — default writes off
  `default_haircut_ppm` against named creditors; **no collateral, no asset
  transfer, no debt-for-equity**. `abroad::loss` on losing a client removes the old
  patron's `ForeignAsset`s (`AssetLost`) and may repudiate client loans — a de
  facto expropriation on relationship loss, not an instrument.
- Currency attack: see the section above. `EffectKind` has no other economic
  coercion kind.

## Substrates that block new instruments

- **No foreign-claims register.** One `FinanceBook`; accounts belong to a state's
  sectors/classes/treasuries with no owner-state or residence tag, and `Creditor`
  is a bank handle. `ForeignAsset` is physical titles only. Freezes, seizures,
  capital flight as a flow, collateral and debt-for-equity all need this first.
- **No coercion cost / legality / status layer.** Sanctions and cuts are booleans;
  there is no war-or-crisis status machine, no legitimacy price, no
  counter-measures and no evasion.
- **No sea control.** Sea zones are geography (`truth/map.rs`); there is no navy,
  no blockade and no war phase — §07 step 8 is unstarted.
- **No cash, no money stock, no securities market, no bank run.** Money is
  deposits; there is no note issue, no M0/M1 reading, no equity market or secondary
  trading, and no depositor-run mechanic. "Crash their market" has nothing to
  crash; only the crisis flight axis exists.
- **No AI rules for any coercion instrument.** The rival's whole economic policy
  is: nationalise when hosting foreign assets in deficit, devalue on any deficit,
  take foreign debt when broke.
- Every new instrument still needs the command → inputs admission → truth (+hash
  bump) → ledger action/fact → projection + fog test → content effect (if covert)
  → four-file balance chain. A covert seizure cannot write beliefs from the economy
  phase; belief writes belong to `attribution`.
