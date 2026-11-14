# CI triage for starpath

`silentsea-xyz/starpath` is private: `api.github.com` answers 404 for it without a token, and
the deploy key only carries git access. Reading runs needs an authenticated `gh`.

## One-time setup

```bash
# official release tarball into ~/.local/bin (no sudo); arch amd64 on the lab host
V=$(curl -sS https://api.github.com/repos/cli/cli/releases/latest \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["tag_name"].lstrip("v"))')
curl -sSL -o /tmp/gh.tgz \
  "https://github.com/cli/cli/releases/download/v${V}/gh_${V}_linux_amd64.tar.gz"
tar xzf /tmp/gh.tgz -C /tmp
install -m 755 "/tmp/gh_${V}_linux_amd64/bin/gh" ~/.local/bin/gh
export PATH=$HOME/.local/bin:$PATH

# device flow: print the one-time code and the URL for the user, press Enter, then poll.
# Run it with pty=true, background=true; the user enters the code in their own browser.
gh auth login --hostname github.com --git-protocol ssh --skip-ssh-key --web
```

`gh auth status` must show the account before any run query. Git pushes keep using the
`github-starpath` SSH alias — do not re-point remotes at HTTPS.

## Read a run

```bash
gh run list --limit 8
gh run view <run-id> --json status,conclusion,jobs \
  --jq '"run: \(.status)/\(.conclusion)", (.jobs[]|"  \(.status)/\(.conclusion) \(.name) id=\(.databaseId)")'
gh api /repos/silentsea-xyz/starpath/actions/jobs/<job-id> \
  --jq '"\(.name) \(.status)/\(.conclusion)", (.steps[]|"  \(.number) \(.status)/\(.conclusion) \(.name)")'
```

Step-level conclusions are what tell you where a job died; the run-level `conclusion` stays
`null` until every job finishes, and `gh run view`'s job list can lag behind the jobs API.

## Triggers, and what each run costs

`.github/workflows/ci.yml` is the repo's only workflow file, and it fires on `push` to `main`,
`pull_request`, and `workflow_dispatch` (one `full_proof_matrix` boolean input). Check the `on:`
block rather than assuming: a `schedule:` cron re-runs the entire pipeline daily from the
default branch, and removing it from the file does nothing until the change lands on `main`.

Minutes are billed **per job, rounded up to the minute**, at 1x on ubuntu — so wall-clock run
length understates cost, and a run that fails after 12 minutes still bills every job it started
(10 jobs in the full pipeline: ~125 job-minutes when it completes).

```bash
gh api "repos/silentsea-xyz/starpath/actions/runs?per_page=100" --paginate \
  --jq '.workflow_runs[]|"\(.id)\t\(.created_at)\t\(.event)\t\(.conclusion)"' > /tmp/runs.tsv
python3 - /tmp/runs.tsv <<'PY'
import sys, json, math, subprocess, datetime, collections
agg, n = collections.Counter(), collections.Counter()
f = "%Y-%m-%dT%H:%M:%SZ"
for line in open(sys.argv[1]):
    rid, created, event, _ = line.rstrip("\n").split("\t")
    out = subprocess.run(["gh", "api", f"repos/silentsea-xyz/starpath/actions/runs/{rid}/jobs",
                          "--jq", "[.jobs[]|[.started_at,.completed_at]]"],
                         capture_output=True, text=True).stdout
    try:
        jobs = json.loads(out)           # strict=False if a step name carries a control char
    except Exception:
        continue                         # expired job data: skip it, do not estimate
    m = sum(max(1, math.ceil((datetime.datetime.strptime(b, f) - datetime.datetime.strptime(a, f)).total_seconds() / 60))
            for a, b in jobs if a and b)
    agg[event] += m; n[event] += 1
for e, m in agg.most_common():
    print(f"{e:14} {n[e]:3} runs  {m:5} job-min")
PY
```

`.../actions/runs?event=schedule` isolates one trigger, but `created=>=<iso-date>` does not
reliably window the list — paginate and compare timestamps yourself. The remaining balance is
**not** readable with the token this repo's `gh` carries (`repo`, `gist`, `read:org`);
`/users/<login>/settings/billing/actions` needs the `user` scope, so quote run-derived numbers
and say the balance is unknown rather than guessing it.

## Suspending CI without spending (and restoring it)

When minutes are exhausted and the pipeline has to stop, edit the file — do **not** reach for
`gh workflow disable`. The disabled state attaches to the workflow id and survives restoring the
file on `main`, so a later "re-enable" by file alone silently runs nothing.

GitHub rejects a workflow with no `on` and no `jobs` ("The workflow must contain at least one
job and an 'on' trigger" — an empty file is an *invalid workflow file* annotation on every
push, not a silent no-op). So the shape is: a valid stub that cannot fire automatically, with
the real pipeline commented out beneath it.

```yaml
name: CI
on:
  workflow_dispatch: # manual only; nothing runs on push or pull_request
jobs:
  disabled:
    name: CI disabled
    runs-on: ubuntu-24.04
    steps:
      - run: 'echo "CI is disabled."'   # note the quotes: `run: echo "a: b"` is a YAML error
```

Prefix every original line with `# `, then check with `actionlint <file>` (install the static
release binary into `~/.local/bin`; it flags a missing `on`/`jobs` section, which PyYAML does
not), `python3 -c 'import yaml;print(yaml.safe_load(open(f))[True])'` to prove only
`workflow_dispatch` remains, and `git diff --stat`. Put the restore command in the file header
— `git checkout <previous-sha> -- .github/workflows/ci.yml` — and commit/push it.

Verify rather than assume: after the push, `gh run list --limit 3` must still show the *previous*
run as newest. A push whose commit carries only `workflow_dispatch` starts nothing — that is the
proof the suspension took effect, and it costs no minutes to obtain.

Two leftovers to check before calling it done: an open PR's merge ref can still carry the
pre-suspension workflow (`gh api repos/<owner>/<repo>/git/refs/pull/<n>/merge --jq .object.sha`,
then read `ci.yml` at that sha), and the `Copilot` / `Dependabot Updates` dynamic workflows keep
running on their own triggers (a handful of job-minutes each) regardless of what `ci.yml` says.

## Live status: the jobs API, not the log

Job logs are published **when the job finishes**. For an in-progress job the log endpoint
returns a two-line XML body (`<Error><Code>BlobNotFound</Code>…`), and `gh run view --job <id>
--log-failed` refuses with *"run is still in progress; logs will be available when it is
complete"*. For live status use the jobs API — status, step numbers, and elapsed time:

```bash
gh api /repos/silentsea-xyz/starpath/actions/runs/<run-id>/jobs \
  --jq '.jobs[]|"  \(.status)/\(.conclusion) \(.name) id=\(.id)"'
```

## Judge a duration against history before calling it a hang

"This job has been running 30 minutes" is usually a 30-minute job. The jobs API carries
`started_at`/`completed_at` per job, so build the lane's normal range from the last several
runs before saying anything about slowness:

```bash
for R in $(gh run list --limit 8 --json databaseId --jq '.[].databaseId'); do
  gh api /repos/silentsea-xyz/starpath/actions/runs/$R/jobs \
    --jq ".jobs[]|select(.name==\"<Job name>\")|\"$R \(.started_at) \(.completed_at) \(.status)/\(.conclusion)\""
done
```

## Where the wall time goes — gap analysis over a finished job's log

Before proposing anything about a slow lane, price it: fetch a completed run's job log, strip
the `\t<step>\t<timestamp>Z ` prefix, then diff consecutive timestamps and print the gaps. The
largest gaps are the time, and the lines around them name the phase.

```bash
curl -sS -H "Authorization: Bearer $(gh auth token)" -L -o /tmp/job.log \
  "https://api.github.com/repos/silentsea-xyz/starpath/actions/jobs/<job-id>/logs"
python3 - <<'PY'
import re, datetime
rec = []
for l in open('/tmp/job.log', errors='replace'):
    m = re.match(r'^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d+Z)\s?(.*)$', l.rstrip('\n'))
    if m:
        rec.append((datetime.datetime.fromisoformat(m.group(1).replace('Z','+00:00')), m.group(2)))
print("wall", round((rec[-1][0]-rec[0][0]).total_seconds()/60, 1), "min over", len(rec), "stamped lines")
for (ta, ca), (tb, cb) in zip(rec, rec[1:]):
    if (tb-ta).total_seconds() > 20:
        print(f"{(tb-ta).total_seconds():7.1f}s | {ca[:130]}\n          -> {cb[:130]}")
PY
```

A silent window (no lines at all between two phase markers) is where a CPU-bound phase is
hiding; check the harness source for the deadline it runs under before assuming a stall.

**The epoch-pipeline lane, measured** (stable across runs): ~1.5 min setup + tee-node build +
`forge build`/`forge create` + three bootstraps, then ~12.5 min for the first accepted epoch
and ~17 min for the second (the phase-2 driver, withdrawal path), then a ~0.03 min restart
check. So ~96% of a ~31 min job is two GKR epoch proofs; the harness itself documents ~12 min
per epoch on an 8-core development host, and the standard runner is 4 vCPU, which is the whole
difference. Setup, compilation and deployment are noise by comparison — do not spend effort
caching those. The only levers that actually move it are: fewer/cheaper proofs per epoch
(weakens what the lane establishes — the user's call), a larger runner, or moving the lane off
the per-push critical path.

## Inner deadlines must leave room to fail cleanly inside the job timeout

Add up the deadlines a job's phases can each burn before it reports: the epoch-pipeline harness
gives every driver a 30-minute accept deadline and the job's `timeout-minutes` is 60, so two
expired drivers exactly exhaust the job — a genuine hang ends as *"job timed out"* with no
failure detail, after an hour of runner. When you add or review a lane, check that one clean
inner timeout still fits inside the job budget, and keep the accept deadline around twice the
observed worst-case phase, not ten times it.

## Verify the lane exercised its matrix, not just that it exited 0

The heavy acceptance lanes seal an evidence manifest as a job artifact. Read the row count: a
lane that passed while sealing `rows: []` proves nothing about the matrix it claims to cover.
Download the artifact and count before reporting a lane as genuinely green.

```bash
gh api /repos/silentsea-xyz/starpath/actions/runs/<run-id>/artifacts \
  --jq '.artifacts[]|"\(.name) \(.size_in_bytes) \(.id)"'
gh api /repos/silentsea-xyz/starpath/actions/artifacts/<artifact-id>/zip > /tmp/ev.zip
python3 -c "import zipfile,json;z=zipfile.ZipFile('/tmp/ev.zip');n=[f for f in z.namelist() if f.endswith('.json')];print(n);print(json.loads(z.read([f for f in n if 'manifest' in f][0]))['rows'].__len__())"
```

## Caches: what makes one actually save the run, and how to verify it

A `actions/cache` entry only helps if a hit *skips* the network step it replaces. Four
properties, each load-bearing:

- **Exact key, no `restore-keys`**, so a tree built for another pinned version can never be
  activated; to invalidate, edit the version in the key.
- **Gate the installer *and* its retry on a cache miss.** `steps.<install>.outcome` is
  `skipped` on a hit, so a retry step conditioned only on `outcome != 'success'` fires on every
  hit and goes straight back to the network — the cache silently does nothing.
- **Restore the PATH the skipped action would have set** (`echo "$HOME/.foundry/bin" >>
  "$GITHUB_PATH"`). Without it the cached binaries exist and are invisible.
- **Let the version gate be the cache guard**: assert every binary the lane uses resolves and
  that the tool reports the pinned version, so a partial or stale entry fails at the guard
  instead of three steps later.

Verify from the run, not from intent: the step outcomes tell you hit vs miss (`Put the cached
… on PATH` skipped + `Install …` run ⇒ miss; the reverse ⇒ hit), and the entry itself is
visible in the repo:

```bash
gh api /repos/silentsea-xyz/starpath/actions/caches --paginate \
  --jq '.actions_caches[]|select(.key|test("foundry"))|"\(.key) \(.size_in_bytes) created \(.created_at)"'
```

Cache entries are **compressed**: a `~/.foundry` tree that `du` reports as ~296 MB is saved as
~104 MiB, i.e. about the size of the release tarball it replaces. Size the tradeoff from
`size_in_bytes`, never from the on-disk tree.

## Rerunning: infra flakes, and what a push does to an in-flight run

A job that dies in a toolchain-install step, before any repository code runs, is infrastructure
(see the acceptance-gate rule in the `starpath` skill). Re-run just the failures:

```bash
gh run rerun <run-id> --failed     # keeps the green jobs; new attempt, same commit
```

`concurrency.cancel-in-progress` is conditioned on the event being a pull request, so a push to
`main` does **not** cancel a run already in flight: a rerun of the old commit keeps verifying
while the new commit's run starts.

## Artifacts carry the missing evidence

Many lanes upload a private evidence bundle on failure (child-process logs, playwright traces,
readiness snapshots). Download and inspect it before theorising:

```bash
gh api /repos/silentsea-xyz/starpath/actions/runs/<run-id>/artifacts \
  --jq '.artifacts[]|"\(.name) \(.size_in_bytes) \(.id)"'
gh api /repos/silentsea-xyz/starpath/actions/artifacts/<artifact-id>/zip > /tmp/ev.zip
python3 - <<'PY'   # `unzip` is not always installed; zipfile always is
import zipfile
z = zipfile.ZipFile('/tmp/ev.zip')
print('\n'.join(z.namelist()[:50]))
print(z.read('failure.json').decode())
PY
```

## Chronic-red workflow

A pipeline that has been red for weeks has several independent failures, not one. Find when
each job first broke instead of chasing the newest log:

1. `gh api "/repos/silentsea-xyz/starpath/actions/workflows/ci.yml/runs?per_page=100"` and keep
   `id`, `head_sha`, `created_at`, `conclusion` for every run.
2. The newest `success` is the last known-good commit; everything newer is suspect.
3. Loop the runs oldest-first from that success and print each run's failing job names. The
   first appearance of each job name is the commit window that broke it — one API call per run.
4. Then diff/read the sources those jobs exercise, and treat `skipped` jobs as unknown, not as
   passing.

## When a failure is opaque, instrument the gate

The retained log is part of the test's contract. If a lane records only a status code, or a
stuck child logs nothing, the fix is to make the failing fact visible in the next run — a
readiness body in the error message, the lane's verbose flag in the child env — then read the
answer, then fix the cause. Instrumentation is a legitimate change; say plainly that it is a
diagnostic and that the pass criteria are unchanged.
