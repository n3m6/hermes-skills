# Diffing a peer's fork of a dependency we vendor

Use when a claim about a peer or competitor rests on "their implementation does X", or
when an obligation says our corrections to vendored code are not upstreamed and a
peer's fork is public evidence either way. It is a **source comparison**; the record must
say so, because nothing here proxies for a run.

## 1. Get both trees and prove the shared base

```bash
git clone --quiet https://github.com/<peer>/<fork>.git /tmp/peer
git clone --quiet https://github.com/<upstream>/<repo>.git /tmp/upstream
cd /tmp/peer && git log -1 --format='%H %ad %s' --date=short && git branch -a
```

A fork usually carries upstream's whole history, so its base is upstream's own HEAD (or
`git merge-base`). Compare that against the revision our `VENDOR.md` / `.rev` file pins.
When they match, the comparison is clean and that is worth stating outright; when they do
not, the base difference is itself part of the finding.

## 2. Find the extra capability first

Paths over the API are enough to map the delta:

```bash
curl -s "https://api.github.com/repos/<peer>/<fork>/git/trees/main?recursive=1" \
  | grep -o '"path": "[^"]*<term>[^"]*"'
```

Look for the things upstream does not have — a new gate, a raw deserializer, an unmerged
branch (`git branch -a`, then `git diff --stat main origin/<branch>`). An unmerged branch
is the most useful find: it is a peer's in-progress answer to one of our open items, and
it costs one `git show` to read.

## 3. Diff with the noise stripped

Vendored copies differ in import paths, module names and provenance headers, and none of
that is a finding. Strip it, then diff:

```bash
diff <(grep -v '^use \|^// \|Vendor edit' ours/file.rs) <(grep -v '^use \|^// ' theirs/file.rs)
```

Then enforce byte-identity on the part that actually matters — round constants, MDS
matrices, generator values — with a plain `diff` on that file alone. Two teams arriving
at the same constants from the same source independently is the strongest corroboration
available short of a differential run; one blank line of difference is not a finding.

## 4. Attribute every change to a commit

```bash
git log --oneline <base>..origin/main -- path/to/file
git show <sha>          # the change, its message, its author date
```

Commit messages carry the intent a diff cannot ("Update generators", "Observe FRI
parameters"). Capture the mechanism as well as the value: a peer that edits a constant in
the vendored tree and a project that assigns it from a caller reach the same number with
different blast radius on the vendored copy — that difference is what decides whether the
correction can live outside the vendored tree.

## 5. Read what their code says about itself

Doc comments state the boundary the diff cannot: which input classes are supported, what
is deliberately not production, what shape is fixed at build time. Quote the mechanism,
not the incident.

## 6. What the record needs

- The shared base commit, so the reader can tell how clean the comparison was.
- Each corroborated fix, with its commit id and the value or element sequence that
  matches.
- Each divergence, classified: defect here / defect there / capability they declined.
- Toolchain and licence deltas (a peer on a much newer toolchain, a renamed module path,
  a different licence) — those decide whether their tree can be adopted or only read.
- One clause stating this was a source comparison and neither implementation was run
  against the other's artifact.

## Pitfalls

- **A fork that refuses a feature has not corrected anything.** A retained panic, a
  `TODO`, or an unmerged branch means the class of input that reveals the bug is rejected
  before it is reached. Classify it as a declined capability — and note that their
  implementation then cannot corroborate anything about that class, including for us.
- **Their module path is usually their own**, so adopting their tree is an import
  rewrite. A `replace` directive that keeps upstream's path is friendlier to eventual
  upstreaming than a rebase onto the peer's fork.
- **Licence travels with vendored code.** Check the peer's licence and our own before
  proposing a transplant; a different licence is a decision for the owner, not a detail.
