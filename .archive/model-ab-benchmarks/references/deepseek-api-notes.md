# DeepSeek API notes (verified 2026-09-08)

## Connection facts
- Base URL: `https://api.deepseek.com/v1` (`/models` also works without `/v1`).
- Key: env var `DEEPSEEK_API_KEY` (origin recorded in Hermes auth.json credential_pool as `env:DEEPSEEK_API_KEY`; value lives in the Hermes dot-env file).
- `GET /models` lists **public names only**. As of 2026-09-08:
  `deepseek-v4-pro`, `deepseek-v4-flash`, `deepseek-v4-flash-vision-exp`.

## Staging aliases
- Early-access models exist **unlisted**: `deepseek-v4.1-flash-expires-on-0910`
  was callable and functional. Naming convention `*-expires-on-DDMM` = dated
  staging alias (expiry 2026-09-10); presumably replaced by the public name
  (e.g. `deepseek-v4.1-flash`) at launch, which did NOT resolve yet.
- POSTing a chat completion with an invalid model name returns an error that
  lists every supported name — a free model catalog. Use it as the definitive
  availability check; /models alone under-reports.

## v4-line behavior (both v4-flash and the v4.1 alias)
- Accept `temperature=0.2` (not restricted like older reasoners).
- Emit `reasoning_content` (hidden CoT) alongside content.
- **Reasoning tokens count against `max_tokens`** (verified: `max_tokens=5`
  → `finish_reason=length`, 5 reasoning tokens, empty content). Budget
  >=8192 for code generation or long reasoning tasks.
- Same `system_fingerprint` across models/aliases (e.g. `6d641ab04c479a91a8f79fb96f1d69c0`) — one serving fleet.
- v4-flash and the v4.1 alias use **different tokenizers**: identical 40
  prompts tokenized to 10,138 vs 8,018 prompt tokens.

## Anchor A/B result (HumanEval n=40, temp 0.2, budget 8192, 2026-09-08)
| metric | v4-flash | v4.1 alias |
|---|---|---|
| pass@1 | 39/40 (97.5%) | 40/40 (100%) |
| mean latency | 6.6 s | 2.3 s (~2.9x faster) |
| completion tokens | 32,940 (30,229 reasoning) | 22,930 (20,005) |
- Accuracy delta within noise at n=40; efficiency favors the alias.
- v4-flash entered a **reasoning runaway** on HumanEval/163 twice (>8192
  reasoning tokens, zero content, at both 4096 and 8192 caps); alias solved
  it both runs. Also: at a 4096 budget ~5% of tasks (both models) produced
  empty content purely from budget exhaustion.

## Pricing
- v4-line per-token pricing unpublished at check time — report raw tokens and
  relative ratios, never invented $ figures.
