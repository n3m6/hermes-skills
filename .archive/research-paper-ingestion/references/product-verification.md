# Product Verification — Software Subjects as Benchmark Material

Session-derived recipe (2026-08-09, six-product wave: commandcode,
oh-my-pi, hermes-agent, zcode, kimi-code, kilo-code added to the
coding-agent subject set, 9 → 15).

## Workflow

1. **web_search per product** (`"<name>" <domain> github`) — locate the
   canonical repo and any news. Do all searches in one parallel batch.
2. **GitHub API metadata** for known repos:
   `curl api.github.com/repos/{owner}/{repo}` → full_name, stars,
   created_at, language, license.spdx_id, default_branch, description.
   When the org is unknown, GitHub *search* API:
   `/search/repositories?q=<name>+<domain>&sort=stars&per_page=5` and
   eyeball results — the top hit is often a third-party integration, not
   the product (session: "zcode agent" search surfaced an unrelated
   `simonyos/Z-CODE` and community bridge repos; "commandcode" surfaced
   agent-dotfiles + provider extensions, NOT an official repo — that
   absence is itself the finding: closed product).
3. **README capture** via `raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md`
   — resolve `default_branch` first (never assume `main`).
4. **Closed products → marketing-site capture**: curl with a browser UA,
   strip `<script>/<style>` + tags, unescape, collapse whitespace. The
   site IS the primary source; require converted body ≥ ~2000 chars or
   treat as JS shell. Grep the raw HTML for `github.com/...` to find the
   real repo. Site claims are MARKETING — flag as self-reported on the
   page ("Code 10× faster. Reviews 2× quicker. Bugs 5× fewer." → "not
   verified, self-reported").
5. **Third-party corroboration** for products without repos or with thin
   sites: community extensions/bridges that name the product reveal its
   true nature (session: `pi-commandcode-provider` — "adds Command Code
   as a model provider: DeepSeek V4 Pro, Kimi K2.6, Qwen 3.7 Max" — proved
   Command Code is ALSO a model-subscription gateway, not just an agent;
   `hermes-commandcode-provider` confirmed the subscription name; the rtk
   issue + VentureBeat dated ZCode's launch and vendor).

## Name-collision resolution (do this BEFORE writing pages)

- `simonyos/Z-CODE` (unrelated terminal assistant) ≠ Z.ai's **ZCode**
  (ADE for GLM-5.2, launched July 2026). Resolved via: vendor (Z.ai),
  launch date, VentureBeat article, rtk-ai issue #2898 naming ZCode
  explicitly, and `zai-org/feedback` (feedback repo).
- Benchmarks: EvoCodeBench 2602.10171 ≠ EvoCode-Bench 2605.24110 (both
  valid; cross-link with "do not conflate").
- Rule: when two same-name entities exist, the entity page must state the
  disambiguation explicitly so future sessions don't conflate them.

## Routing-eligibility classification (the benchmark-specific step)

For a fixed-model benchmark (e.g. "all harnesses on deepseek-v4-flash"),
classify each subject by whether it can route an arbitrary model:

- **Vendor-locked** (cannot): claude-code (Anthropic models only), codex
  (OpenAI), copilot-cli (Copilot subscription), antigravity-cli (Google),
  zcode (GLM only), commandcode (subscription-gated — UNVERIFIED, mark
  `[OPEN]`).
- **BYO / endpoint-capable** (can): opencode (multi-provider), cline
  (BYO key), aider, pi + oh-my-pi (15+ providers), hermes (any endpoint),
  kimi-code ("configurable to other compatible providers" — verify exact
  config in docs, `[OPEN]`), kilo-code (500+ models BYOK).
- **First-party eligibility evidence:** the model provider's own docs
  (api-docs.deepseek.com agent-integrations page documented Kilo Code).
- Method: grep the *captured* sources for model-routing lines; never
  classify from memory (the grep of the 9 original pages confirmed the
  split before any claims were made).
- Consequence pattern: "all harnesses, one model" silently becomes
  "the BYO subset, one model" — say this out loud in the deliverable and
  give the vendor-locked set a Phase-2 default-config lane instead.

## Page conventions for products

- Stars: record as "snapshot 2026-08-09" — they drift; re-verify before
  publishing results.
- First-party disclosure: when the wiki's own tooling is the subject
  (hermes-agent page), mark the page as first-party, not independent
  verification.
- Created dates: GitHub created_at for repos; launch news for closed
  products.
- Instrumentation column (runner): from README/docs — headless flags
  (`-p`, `--yolo`, `/sandbox`), SDK/RPC/ACP, approval modes; this feeds
  the benchmark's runner contract.

## Comparison-matrix growth (9 → 15)

- Rewrite the table wholesale (11 rows × 15 cols), not per-cell patches.
- Grep the old count everywhere: page title line ("The nine subjects"),
  intro, cluster analysis ("Three form-factor clusters" → four), verdict,
  sources list (9 → 15 raw files), and the BENCHMARK-SPEC subject table +
  cost model (config count 6 → 10 changed the run total and budget).
- Lint does NOT catch prose-count drift — only broken links/orphans.
