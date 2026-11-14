# Benchmark Run Cost Modeling

Estimate the cost of a fixed-model benchmark run at a model provider's
list prices. Worked example: deepseek-v4-flash, 2026-08-09.

## Step 1 — Capture the pricing page

`web_extract` may be search-only (DuckDuckGo backend errors on URL
fetch). Use curl + tag-strip:

```bash
curl -sL -A "Mozilla/5.0 ..." <pricing-url> -o /tmp/pricing.html
# strip <script>/<style>/tags, unescape entities, collapse whitespace
```

Record per model: input price per 1M (cache miss), input price per 1M
(cache hit), output price per 1M, context length, max output, thinking
mode default, concurrency limit. Also record any **price-rise warning**
on the page and the model VERSION string (e.g. DeepSeek-V4-Flash-0731).

Worked numbers (deepseek-v4-flash, official page 2026-08-09):
- input cache miss $0.14/M, **cache hit $0.0028/M (50× cheaper)**,
  output $0.28/M; 1M context; 384K max output; thinking default ON;
  concurrency 2500; page warns of a near-term "significant" price
  increase.

## Step 2 — Per-task-run cost model

Split assumption (state it explicitly): ~20% input cache-miss, ~65%
input cache-hit, ~15% output per task-run. Cache-hit ratio is the
biggest lever after output volume — harnesses that rewrite the whole
context every turn collapse the hit rate and multiply cost.

```python
P_MISS, P_HIT, P_OUT = 0.14, 0.0028, 0.28
def task_cost(total_tokens, miss_frac=0.20, out_frac=0.15):
    miss = total_tokens * miss_frac
    hit  = total_tokens * (1 - miss_frac - out_frac)
    out  = total_tokens * out_frac
    return miss/1e6*P_MISS + hit/1e6*P_HIT + out/1e6*P_OUT
```

Token bands per task family (THE uncertainty — report low/mid/high, never
a false-precision single number):
- SWE-bench-style repo tasks: 200K / 750K / 1.5M tokens → $0.014 / $0.054 / $0.108
- Terminal tasks: 60K / 150K / 300K → $0.004 / $0.011 / $0.022

Total = task_cost × tasks × configs × runs. Worked (10 configs = 9
subjects + baseline, 298 tasks, 2 runs + pilot): ≈ 2,980 task-runs ≈
**$50 (mid) – $160 (high)**. At these prices money is NOT the binding
constraint — wall-clock is (1,788+ task-runs × 10–30 min each; concurrency
2500 means parallelize freely).

## Output-token dominance

Output at $0.28/M is 100× the cache-hit input price. Thinking mode ON by
default for reasoning models means agent loops churn output tokens —
that's the cost center, and it's why cost-per-resolved-task is a real
differentiator metric, not noise.

## Deliverable pattern

Present: pricing table → per-task-run table (low/mid/high per family) →
scenario totals (pilot / scale / stretch) → the 3-4 numbers that move the
estimate → caveats (price-rise warning, token-band uncertainty). Snapshot
the pricing page into the project's docs (it drifts) and re-check before
pilot.
