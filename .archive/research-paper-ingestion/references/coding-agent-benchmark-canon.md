# Coding-Agent Benchmark Canon (verified 2026-08-09)

Canon for the harness-wiki (`n3m6/harness-wiki`, local `~/harness-wiki`) —
the user's active project: **building a coding-assistant benchmark**
(targets: opencode, pi, codex-class CLI/IDE agents). All arXiv IDs verified
via the export.arxiv.org API; repos via api.github.com. Ingestion status as of 2026-08-09 (end of day): ALL waves DONE — wave 1
(SWE-bench family), wave 2a, DeepSWE, wave 2b (7 leads), BulkPR-Bench,
tasks 1-7 program (subjects layer, code-level layer, methodology queue),
batch 3 (16 papers), agent-harness survey, 4 new product subjects,
leaderboard snapshots, Awesome-Agent-Engineering mine + Tier 1 (10 papers).
**104 wiki pages** — see wiki index.md for the live catalog; this file is
the verified-ID memory so future waves skip re-verification. Design docs:
**`BENCHMARK-SPEC.md`** (v0.1 draft: 9 subjects, 6 reuse-first task
families, execution grading + judge audits, claw-swe-bench adapter
contract, pilot-first ops, 6 open decisions) and **`WATCHLIST.md`**
(time-sensitive sources) both live in the wiki repo root; the benchmark
itself will be implemented in a separate repo.

## Tier 0 — Harnesses (infrastructure, partly ingested)
- HELM `2211.09110` ✓ (ar5iv) · lm-evaluation-harness (repo
  EleutherAI/lm-evaluation-harness) + Lessons from the Trenches
  `2405.14782` ✓ · OpenCompass `2605.19276` (paper May 2026) · OpenAI Evals
  (repo openai/evals) · Inspect (repo UKGovernmentBEIS/inspect_ai) ·
  BIG-bench `2206.04615` · Chatbot Arena `2403.04132` · Simple Benchmarks
  (Anthropic — web only, NOT on arXiv)

## Tier 1 — Agentic coding benchmarks
Wave 1 DONE: SWE-bench `2310.06770` ✓ · SWE-bench Verified (OpenAI blog,
Cloudflare → r.jina.ai) ✓ · SWE-bench Multimodal `2410.03859` ✓ · SWE-agent
`2405.15793` ✓ (PDF fallback) · SWE-Bench Illusion `2506.12286` ✓ ·
Ability-or-memory `2512.10218` ✓
Wave 2a DONE: AgentBench `2308.03688` ✓ (native) · DevBench/DevEval
`2403.08604` ✓ (native) · InterCode `2306.14898` ✓ (PDF — no HTML/ar5iv) ·
RepoBench `2306.03091` ✓ (ar5iv) · LiveCodeBench `2403.07974` ✓ (native)
Also DONE: **DeepSWE `2607.07946`** ✓ (native; Datacurve, Jul 2026) —
authored-never-merged tasks, functional verifiers (1.4% vs 32.4% judge
disagreement vs SWE-Bench Pro), shallow-clone containers; the third
contamination strategy (see wiki entities/deepswe.md)
Wave 2b DONE (seven leads surfaced by DeepSWE's related-work, all
verified + ingested): **SWE-Bench Pro `2509.16941`** ✓ (native; Scale AI,
Sep 2025; 1865 tasks, public/commercial/held-out splits) · **SWE-bench Live
`2505.23419`** ✓ (native; "SWE-bench Goes Live!", Microsoft) · **SWE-rebench
`2505.20411`** ✓ (native; Nebius; V2 `2602.23866` Feb 2026) · **APEX-SWE
`2601.08806`** ✓ (PDF — no native/ar5iv; Mercor+Cognition) · **Multi-SWE-bench
`2504.02605`** ✓ (native; ByteDance) · **SWE-smith `2504.21798`** ✓ (native;
Stanford/Princeton) · **FrontierSWE — NO arXiv paper** ✓ (captured
frontierswe.com, Epoch AI, as raw article; ultra-long-horizon, partial credit)
Batch 3 DONE (16 papers, the 2026 "beyond single-issue" wave): **Hybrid-gym
`2602.16819`** (training) · **ProjDevBench `2602.01655`** · **SWE-EVO
`2512.18470`** · **OmniCode `2602.02262`** · **Claw-SWE-Bench `2606.12344`**
(harness adapter protocol — key for product-level eval) · **SWE-PolyBench
`2504.08703`** · **Beyond Isolated Tasks `2604.03035`** · **FeatureBench
`2602.10975`** (ICLR 2026) · **REAP `2604.01527`** (Meta, production-usage
curation) · **PerfOpt Reliability `2607.01211`** (validity) · **SWE Atlas
`2605.08366`** · **SWE-NFI `2607.27409`** · **RoadmapBench `2605.15846`** ·
**EvoCode-Bench `2605.24110`** · **SlopCodeBench `2603.24755`** ·
**SaaSBench `2605.17526`**
DONE (task 7, methodology queue): Terminal-Bench `2601.11868` (+ TB 2.0
`2607.14004`, Long-Horizon `2607.08964`, repo harbor-framework/terminal-bench)
· MLE-bench `2410.07095` · Commit0 `2412.01769` · AppWorld `2407.18901` ·
SWT-Bench `2406.12952` · GAIA `2311.12983` · OSWorld `2404.07972` ·
WebArena `2307.13854` · R2E-Gym `2504.07164` · OpenHands `2407.16741` ·
AutoCodeRover `2404.05427` · Agentless `2407.01489` (validity!) · UTBoost
`2506.09289` (validity!) · METR long tasks → **arXiv `2503.14499`** ✓ (the
metr.org blog URL 404'd — check arXiv FIRST before scraping a METR blog) ·
DeepCode `2512.07921` · Proactivity `2605.06717` · Scaling TTC `2604.16529`
· TestGen-LLM `2402.09171` · BulkPR-Bench `2608.02685` (queue-level PR
governance)
Still pending: CORE-Bench `2409.11363` · Terminal-Bench 2.0 `2607.14004` /
Long-Horizon `2607.08964` (IDs verified, not yet ingested) · awesome-ae
Tier 2 (15 IDs — full list in wiki `queries/awesome-ae-lead-inventory.md`)

## Harness layer (2026-08-09 additions)
- **Agent System and Harness Design Survey `2606.20683`** ✓ (Guo et al.,
  incl. Zheng/Han of Claw-SWE-Bench group; 4 paradigms prompt→workflow→
  context→harness engineering; 7-component harness anatomy; Table 7 =
  same-model/different-harness SWE-bench Verified rates: vendor scaffolds
  beat open harnesses — Opus 4/4.5 80.9% vs mini-SWE-agent 76.8%; GPT-5
  80.0% vs 72.8%; 20-pt swings on Claude 3.5 Sonnet). Companion repo:
  ggjy/Awesome-Agent-Engineering (mined, see below).
- **Harness Engineering for Agentic AI Coding Tools `2602.14690`** ✓
  (8 configuration mechanisms across Claude Code/Copilot/Cursor/Gemini/
  Codex — the run-manifest checklist for the product benchmark)
- **MCP vs RAG vs NLWeb vs HTML `2511.23281`** ✓ (controlled interface
  comparison — harness-standardization evidence)
- **Efficient Benchmarking of AI Agents `2603.23749`** ✓ (8 benchmarks ×
  33 scaffolds × 70+ models: subsets preserve RANKINGS not absolutes;
  scaffold-driven distribution shift)

## Tier-1 mine + validity (2026-08-09)
- **ELT-Bench-Verified `2603.29399`** ✓ (underestimation failure mode)
- **Reproducible/Explainable/Effective Evals of Agentic AI for SE
  `2604.01437`** ✓ (18-paper audit of eval reporting)
- **IDE-Bench `2601.20886`** ✓ (IDE-native tool surface, Dockerized)
- **SWE Context Bench `2602.08316`** ✓ (context learning/reuse)
- **EvoCodeBench `2602.10171`** ✓ (self-evolution, human baseline — NOT
  the same as EvoCode-Bench `2605.24110`)
- **ABC-Bench `2601.11077`** ✓ (backend/deployment tasks) ·
  **AgencyBench `2601.11044`** ✓ (1M-token contexts, usage-derived)

## Leaderboard snapshots (dated raws + entity pages, WATCHLIST-tracked)
swebench.com/verified — Claude 4.5 Opus 76.8% top bash-only; 79.2% top
agent (data rows Feb 2026, lags capture) · tbench.ai TB@2.1 — Claude Code
(Fable 5) 83.8% top; product-level leaderboard, the closest thing to the
product-eval lane · frontierswe.com — re-verified 2026-08-09 UNCHANGED
since 2026-07 (Claude Fable 5, avg rank 2.47, 89% dominance)

## Awesome-Agent-Engineering mine (ggjy, 62★)
275 entries parsed, 270 arXiv IDs, 13 already in wiki. Inventory:
`queries/awesome-ae-lead-inventory.md`. Tier 1 (10) ingested; Tier 2 (15)
queued; ~150 Tier-3 computer-use/safety/domain logged out-of-scope.
Re-mine monthly (WATCHLIST).

## Tier 2 — Code-level benchmarks (task material)
HumanEval `2107.03374` · MBPP `2108.07732` · EvalPlus/HumanEval+
`2305.01210` · BigCodeBench `2406.15877` · APPS `2105.09938` ·
AlphaCode/CodeContests `2203.07814` · MultiPL-E `2208.08227` · CRUXEval
`2401.03065` · CoderEval `2302.00288` · CodeXGLUE `2102.04664` ·
TestGen-LLM `2402.09171` (LiveCodeBench + RepoBench now ingested, wave 2a)

## Tier 3 — Measurement & contamination
METR long tasks (metr.org blog, verified 200) · Scaling TTC for Agentic
Coding `2604.16529` · Agentic Coding Needs Proactivity `2605.06717` ·
DeepCode: Open Agentic Coding `2512.07921` · Verbal Process Supervision
`2503.18494` · Reflection-Driven Control for Code Agents `2512.21354` ·
Rethinking Benchmark Contamination `2311.04899` · Proving Test Set
Contamination `2310.17623` · Careful Exam GSM8K arithmetic `2405.00332` ·
GPT-3 Few-Shot `2005.14165` · Scaling Laws `2001.08361` · Frontier Models
Dangerous Capabilities `2403.13793`

## Agent entities (subjects for the benchmark)
Nine products documented + compared (`comparisons/coding-agent-products.md`):
opencode → **anomalyco/opencode** (rename of sst/opencode; 195k★, branch
`dev` — not `main`) · **codex** openai/codex (105k★) · **aider**
Aider-AI/aider (48k★) · **cline** cline/cline (66k★) · **pi** →
**earendil-works/pi** (86k★, created 2025-08-09, Earendil Inc.; identity
RESOLVED 2026-08-09 — terminal agent, pi.dev, Rust, extensions/packages,
RPC/SDK/print modes) · **claude-code** anthropics/claude-code (141k★,
Feb 2025, the de-facto benchmark reference) · **cursor** getcursor/cursor
(33k★, Mar 2023; repo README is an empty landing page — use cursor.com/docs
via r.jina.ai) · **antigravity-cli** google-antigravity/antigravity-cli
(1.9k★, May 2026, Google; shared engine with Antigravity 2.0 GUI) ·
**copilot-cli** github/copilot-cli (11k★, Jan 2023; approval-gated,
MCP-powered). OpenHands/OpenHands (83k★) also documented as platform/harness.

## Known-wrong IDs (do NOT reuse — all resolved to unrelated papers)
`2405.18290` OpenCompass (astronomy) · `2210.14233` GSM8K-exam (astronomy)
· `2501.17192` Simple Benchmarks (astronomy) · `2505.00688` frontier evals
(arch) · `2208.08272` MultiPL-E (chem) · `2303.11374` LiveCodeBench
(astro) · `2306.05789` CoderEval (physics) · `2310.16632` CruxEval (trust
study) · `2408.01432` Terminal-Bench (CV) · `2406.02876` Commit0 (NMT) ·
`2408.16509` CORE-Bench (CFD) · `2311.14808` InterCode (NLG) ·
`2404.01089` SWE-bench M (try-on) · `2406.01304` R2E (CodeR paper, wrong
paper) · **`2403.07772` user-supplied "DevBench" (statistics; correct =
`2403.08604`, artifact is DevEval not DevBench)**

## Capture notes
- SWE-agent: native HTML + ar5iv both fail → `arxiv.org/pdf/2405.15793` +
  pypdf in throwaway venv ✓
- InterCode + APEX-SWE: native HTML stub / missing, ar5iv missing → PDF
  fallback ✓ (APEX-SWE `2601.08806` had NO usable HTML at all)
- OpenAI blog: curl 403 + browser Cloudflare → `https://r.jina.ai/<url>` ✓
- Pre-2023 papers (HELM, MMLU): no native HTML → ar5iv ✓
- 2024+ papers mostly have native HTML (AgentBench, DevBench, LiveCodeBench,
  DeepSWE, SWE-Bench Pro/Live/rebench, Multi-SWE-bench, SWE-smith all
  native) — stub-check the full document before accepting (see SKILL.md
  Step 1); ar5iv sometimes fatals (InterCode had no usable HTML anywhere)
- Web-only benchmark (no arXiv): FrontierSWE → captured frontierswe.com
  (Epoch AI) directly as `raw/articles/`; leaderboard numbers are a dated
  snapshot, frame them as such on the page

## Unverified leads (still to chase — NOT on the verified list)
BeetleBox (chakraborty_blaze_2025) · SWE-bench+ (Aleithan et al. 2024,
post-cutoff issues) · LessLeak-Bench (Zhou et al. 2025) · from search
snippets: SWE-Atlas-QnA, FrontierCode 1.1 — the 2026-generation benchmarks
behind composite coding agent leaderboards (Artificial Analysis Coding
Agent Index). Also: Multi-LCB `2606.20517` + LiveCodeBench Pro `2506.11928`
(verified, not yet ingested) · CORE-Bench saturation study `2606.26158` ·
R2E-Gym `2504.07164` (R2E original itself not found on arXiv)
