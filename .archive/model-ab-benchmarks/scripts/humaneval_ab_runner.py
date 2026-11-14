#!/usr/bin/env python3
"""HumanEval A/B runner for API-hosted LLMs (stdlib only — no pip deps).

Editable at the top: MODELS (any OpenAI-compatible model IDs), N (subset
size), SEED, MAX_TOKENS, BASE, KEY, and the model list to compare.

Usage:
    set -a; . <env-file-with-API-key>; set +a   # e.g. Hermes dot-env
    python3 humaneval_ab_runner.py

Fetch the dataset first (canonical HumanEval JSONL, gz):
    curl -sL -o HumanEval.jsonl.gz \
      https://raw.githubusercontent.com/openai/human-eval/master/data/HumanEval.jsonl.gz

Key design decisions (do not "simplify" these away):
- extract_code() rstrip()s ONLY. Never strip() — it destroys the leading
  indentation of body-only completions -> fake SyntaxError failures.
- Full-function completions get the prompt's pre-`def` header (imports)
  prepended when they contain no imports -> avoids fake NameError: 'List'.
- Body-only completions are stitched under the prompt's truncated
  signature; unindented bodies get a uniform +4 indent.
- Reasoning models (DeepSeek v4 line) count reasoning tokens against
  max_tokens: with a low cap they silently return EMPTY content
  (finish_reason=length, reasoning_tokens==cap). Use >=8192 for codegen.
- Every item stores raw content + assembled candidate + full stderr for
  post-run audit. Audit every failure before reporting numbers.
"""
import json, gzip, os, sys, time, random, re, subprocess, tempfile, threading, concurrent.futures, urllib.request, urllib.error

BASE = "https://api.deepseek.com/v1/chat/completions"
KEY = os.environ.get("DEEPSEEK_API_KEY", "")
MODELS = ["deepseek-v4-flash", "deepseek-v4.1-flash-expires-on-0910"]
N = 40
SEED = 42
MAX_TOKENS = 8192
REQUEST_TIMEOUT = 300
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_LOCK = threading.Lock()

def log(msg):
    with LOG_LOCK:
        print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def load_problems():
    with gzip.open(os.path.join(OUT_DIR, "HumanEval.jsonl.gz"), "rt", encoding="utf-8") as f:
        allp = [json.loads(l) for l in f if l.strip()]
    rng = random.Random(SEED)
    idx = sorted(rng.sample(range(len(allp)), N))
    return [allp[i] for i in idx], idx

def ask(model, messages, temperature):
    body = {"model": model, "messages": messages, "max_tokens": MAX_TOKENS}
    if temperature is not None:
        body["temperature"] = temperature
    data = json.dumps(body).encode()
    req = urllib.request.Request(BASE, data=data, headers={
        "Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as r:
            resp = json.load(r)
        return {"ok": True, "resp": resp, "latency": time.time() - t0}
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"HTTP {e.code}: {e.read()[:300].decode(errors='replace')}", "latency": time.time() - t0}
    except Exception as e:
        return {"ok": False, "error": repr(e), "latency": time.time() - t0}

def extract_code(text):
    """Preserve leading indentation. Strip only trailing whitespace.
    If fenced, take the LAST fenced block's interior."""
    t = text.rstrip()
    m = list(re.finditer(r"```[ \t]*[a-zA-Z]*\n(.*?)```", t, re.DOTALL))
    if m:
        return m[-1].group(1).lstrip("\n").rstrip()
    return t.lstrip("\n").rstrip()

def prompt_header(prompt):
    """Everything in the prompt before the first function definition (imports)."""
    i = prompt.find("def ")
    return prompt[:i] if i >= 0 else ""

def assemble(prompt, completion, entry_point):
    code = extract_code(completion)
    if not code.strip():
        return None, "empty completion content"
    first_line = next((l for l in code.split("\n") if l.strip()), "")
    has_any_def = bool(re.search(r"^\s*def\s+", code, re.M))
    if has_any_def:
        # full-function (or import+function) response
        if not re.search(r"^\s*(from|import)\s", code, re.M):
            hdr = prompt_header(prompt)
            if hdr.strip():
                code = hdr.rstrip("\n") + "\n" + code
    else:
        # body-only continuation of the truncated signature in prompt
        if first_line and not first_line[0] in (" ", "\t"):
            code = "    " + code  # uniform indent keeps relative structure
        code = prompt.rstrip() + "\n" + code
    if not re.search(r"def\s+" + re.escape(entry_point) + r"\s*\(", code):
        return code, "entry-point def missing from assembled candidate"
    return code, None

def grade(problem, candidate):
    test = problem["test"]
    src = candidate + "\n\n" + test
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, dir=OUT_DIR) as f:
        f.write(src)
        path = f.name
    try:
        r = subprocess.run([sys.executable, path], capture_output=True, timeout=30)
        return r.returncode == 0, (r.stderr or b"").decode(errors="replace")[-800:]
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT (30s)"
    finally:
        os.unlink(path)

def main():
    problems, idx = load_problems()
    log(f"Loaded {len(problems)} problems (orig indices {idx[0]}..{idx[-1]})")
    temps = {}
    for m in MODELS:
        r = ask(m, [{"role": "user", "content": "Say OK"}], 0.2)
        temps[m] = 0.2 if r["ok"] else None
        log(f"smoke {m}: temp={temps[m]}")
    sys_prompt = "You are an expert Python programmer. Complete the function exactly as specified by its docstring."
    user_tmpl = "{prompt}\n\nComplete the Python function above. Output ONLY valid Python code: either the rest of the function body or the full function. No markdown fences, no explanations, no tests."
    results = {}
    for m in MODELS:
        results[m] = []
        log(f"start {m} ({len(problems)} problems, temp={temps[m]})")
        def work(p):
            messages = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_tmpl.format(prompt=p["prompt"])},
            ]
            r = ask(m, messages, temps[m])
            if not r["ok"]:
                return {"task_id": p["task_id"], "ok": False, "error": r["error"], "latency": r["latency"]}
            msg = r["resp"]["choices"][0]["message"]
            content = msg.get("content") or ""
            candidate, asm_err = assemble(p["prompt"], content, p["entry_point"])
            if asm_err:
                passed, err, cand = False, asm_err, candidate
            else:
                passed, err = grade(p, candidate)
                cand = candidate
            usage = r["resp"].get("usage", {})
            return {
                "task_id": p["task_id"], "ok": True, "passed": passed,
                "error": err if not passed else None, "latency": r["latency"],
                "content": content, "candidate": cand,
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "reasoning_tokens": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                "finish_reason": r["resp"]["choices"][0].get("finish_reason"),
            }
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
            for i, res in enumerate(ex.map(work, problems), 1):
                results[m].append(res)
                if i % 10 == 0:
                    log(f"  {m}: {i}/{len(problems)} done")
        log(f"done {m}")
    out = {"meta": {"models": MODELS, "n": N, "seed": SEED, "sampled_indices": idx,
                    "timestamp": time.time(), "temperatures": temps}, "results": results}
    with open(os.path.join(OUT_DIR, "results.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("\n================ SUMMARY ================")
    for m in MODELS:
        rs = results[m]
        done = [x for x in rs if x.get("ok")]
        passed = [x for x in done if x.get("passed")]
        lat = [x["latency"] for x in done]
        ptok = sum(x["prompt_tokens"] or 0 for x in done)
        ctok = sum(x["completion_tokens"] or 0 for x in done)
        rtok = sum(x["reasoning_tokens"] or 0 for x in done)
        print(f"\n{m}:")
        print(f"  pass@1: {len(passed)}/{len(problems)} = {len(passed)/len(problems):.2%}")
        print(f"  api errors: {len(rs)-len(done)}  mean latency: {sum(lat)/len(lat):.1f}s  "
              f"prompt_tok: {ptok}  completion_tok: {ctok}  (reasoning: {rtok})")
    log("ALL DONE")

if __name__ == "__main__":
    main()
