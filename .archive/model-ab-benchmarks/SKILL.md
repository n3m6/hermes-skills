---
name: model-ab-benchmarks
description: "Quick A/B benchmarks of API-hosted LLMs (OpenAI-compatible): model availability/discovery, mini auto-graded evals, code-completion assembly pitfalls, honest reporting."
---

# API Model A/B Benchmarks (lightweight, auditable)

## When to use
- Compare two API-hosted LLMs: prod vs early-access/staging alias, upgrade candidate vs incumbent.
- Check whether a model name is real/available on a provider.
- Get a quality + efficiency signal in 5–15 minutes with zero heavy deps (stdlib-only runner, API-side inference so weak local CPUs are fine).

**If you need standard academic numbers across many tasks (official MMLU/GSM8K/HumanEval prompts/metrics) and have time to spare → use the `evaluating-llms-harness` skill (lm-eval) instead.** This skill is for fast, controlled A/Bs where you also want latency/token/cost deltas and a per-item audit trail.

## Workflow

### 0. Availability & discovery
1. `GET {base}/models` with the key → lists **public** names only.
2. Staging/early-access aliases are frequently **unlisted but callable** (DeepSeek pattern: `*-expires-on-0910` = temporary alias, expires Sep 10).
3. Definitive check: POST a tiny `/chat/completions`. Bonus: an invalid model name returns an error listing **all supported names** — a free catalog.
4. Key sourcing on Hermes: `~/.hermes/auth.json` credential_pool shows key origin (e.g. `source: env:DEEPSEEK_API_KEY`); the actual value usually sits in the Hermes dot-env file. Source it with `set -a; . <envfile>; set +a`. Never print the key.

### 1. Smoke test each model before any batch
- Parameter compatibility (does it accept `temperature=0.2`? reasoning models sometimes reject temp≠1).
- Does it emit `reasoning_content` (hidden CoT)?
- **Do reasoning tokens count against max_tokens?** Probe: send `max_tokens=5`. If `finish_reason=length` with `reasoning_tokens==5` and empty content → yes → budget ≥8192 for codegen, or you get silent empty outputs mid-batch.

### 2. Design the eval
- **Auto-graded tasks only** (executed unit tests, exact match). No LLM judge for a model A/B — it re-introduces the bias you're measuring.
- Identical prompts + sampling params + subset seed across models. Small N is fine (40 items ≈ 5–10 min at 4–8 concurrent).
- Record per request: latency, prompt/completion/reasoning tokens, finish_reason. **Prompt-token counts differing on identical text ⇒ different tokenizers between model versions** — report it, don't debug it.
- Scope: offer runtime as the decision fork; default to the smallest meaningful test.

### 3. Assemble code completions — pitfalls (each one cost real false failures)
1. **NEVER `text.strip()` a completion before assembly.** It strips leading indentation of body-only outputs → `return` lands at column 0, closes the def → fake `SyntaxError: 'return' outside function`. `rstrip()` only; preserve leading whitespace.
2. **Full-function responses drop the prompt's import header** (`from typing import List`) → `NameError: name 'List' is not defined` at the def line. If the completion contains no import lines, prepend the prompt's text before its first `def `.
3. **Body-only responses**: stitch as `prompt.rstrip() + "\n" + body`. If the first non-blank body line is unindented, indent ALL lines uniformly (+4) — preserves relative structure.
4. After assembly verify `def <entry_point>(` is present; if not, mark as assembly artifact with the reason.
5. **Empty content + finish_reason=length + reasoning_tokens==max_tokens = reasoning runaway**, not a wrong answer. Report the empty-output rate separately — it's real behavioral signal (an agent turn that returns nothing after 8k thinking tokens is a failed turn).

### 4. Audit before you believe — and before you report
- Cross-tab per task: both-pass / A-only / B-only / both-fail. Inspect **every** failure's full stderr + raw completion.
- Store raw content + assembled candidate + full stderr per item in the results JSON.
- Reconstruct/compile a candidate manually when a failure smells like an artifact (NameError at line 1, SyntaxError at a dedent, IndentationError).
- Single-sample runs at temp 0.2 are noisy: a 1-item delta on n=40 is NOT a conclusion about accuracy. Report pass@1, conditional-on-output pass rate, empty-output rate, latency and token deltas.

### 5. Report honestly
- Never present numbers from an un-audited harness run as results. (Real case: run 1's 35/34 was garbage from two assembly bugs; caught by auditing; the audited run flipped the conclusion to 39/40 vs 40/40.)
- Cost: relative cost at equal $/tok ≈ total-token ratio. Don't invent per-token pricing for unpublished models — report raw tokens.

## Support files
- `scripts/humaneval_ab_runner.py` — generic HumanEval A/B runner (stdlib only): parallel requests, indentation-safe assembly, import-header prepend, local unit-test execution, per-item audit JSON with full content/candidate/stderr. Edit MODELS / N / SEED / MAX_TOKENS at the top; BASE/KEY adapt to any OpenAI-compatible provider.
- `references/deepseek-api-notes.md` — DeepSeek specifics: key location, alias conventions, v4-line behavior (reasoning models, budget interplay), measured v4 vs v4.1 anchor results.
