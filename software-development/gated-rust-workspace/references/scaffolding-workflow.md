# Scaffolding workflow that works

Depth for the SKILL.md section of the same name: how to create a multi-crate workspace's files without
dozens of hand-written tool calls, and the generation traps that cost a build round-trip.

Hand-writing dozens of files one tool call at a time is slow and loses structure. Instead:

1. Write one Python script into the scratch dir (`~/.hermes/cache/scratch/<proj>_<step>.py`) that writes
   every file of a step: `pathlib.Path`, a `w(rel, content)` helper with `textwrap.dedent`, and a
   `patch(rel, old, new, label)` helper for edits.
2. **Run it, then patch what it generated.** A `patch`/`write_file` against a path a not-yet-run script
   will create fails with `Failed to read file`. Generate first, then edit the real files.
3. **Every replacement verifies its match count** and prints `FAIL <label> <count>` rather than silently
   doing nothing: `if t.count(old) != 1: print("  FAIL", label, t.count(old)); return`. A pattern whose
   leading whitespace is shorter than the target line matches as a substring of a deeper-indented line,
   so one replacement lands in the wrong place. When a line is not unique, include the preceding line in
   `old`.
   **Never find a nested JSON object's end by searching for a brace**: `t.index("    }")` matches
   *inside* `"      }"`, so the inserted field lands inside the inner object and the file stops parsing —
   surfacing as a parse panic in a test written long after the script ran. Anchor on the last field name
   of the object you are extending, or round-trip the file through `json`, and `json.load` it right after
   the edit, printing the fields you meant to change, before running anything else.
4. Scripts that only touch the filesystem are stdlib-only — run them with system `python3`. Only scripts
   importing Hermes skill helpers need the Hermes venv interpreter, which is a different requirement for
   a different reason.
5. Expect the real bugs to surface at `cargo build` and `cargo test`; treat that pass as part of the
   deliverable, not as an interruption. The traps in `references/tooling-traps.md` all came from it.
