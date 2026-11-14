# Delegation bundle for one plan phase (fill the placeholders)

Pass this as the child's `context`. Keep the clause order: it is the order the child needs the facts.

```
Repo: <abs path> (branch <branch>; remote `<remote>` - push with `<exact push command>`). HEAD is now
<sha> (Phases 0-<N-1> done).

THE PLAN YOU ARE EXECUTING: <absolute plan path> - read '<the planning section>' and the whole
'Phase <N> - <title>' section before starting. Execute <T-a> through <T-b> IN ORDER. Do only
Phase <N>.

LOAD THE PROJECT SKILL FIRST and follow it: skill_view(name='<skill>').

Baseline you must verify at your start (the gate prints all of these): <fingerprint / hash / hash /
version constants>. If they do not match, STOP and report rather than changing anything.

THE TASKS (the plan has each one's file, line anchors, code and test - read them there):
1. <id> - <what changes, one sentence, with file:line>, and the test that must fail first.
2. ...

HARD RULES: run `<gate command>` and get <the success line> before each commit; never claim the
repo's state without running it. Write the failing test first, see it fail, implement minimally, see
it pass, commit with the plan's exact message, push. ONE COMMIT PER TASK - never batch. Commit each
task as it finishes, before starting the next, and if you approach the middle of your tool budget,
commit what is complete and report rather than leaving work uncommitted. NEVER force-push and never
amend a commit that is already on the remote: amend before the push, otherwise make a follow-up commit
(the owner pulls this branch himself).
<phase hash rule: EITHER "this is presentation only, so the fingerprints stay byte-identical - say so
in every commit message" OR "this moves persisted state: bump <the constant>, re-record, and update
<the docs that carry measured numbers> and the register item from the tool's own output, never from
memory">. Do not read files with cat/sed/grep in the shell: use read_file, search_files, patch,
write_file or python in execute_code, and never write read_file's 'N|' prefixes back into a file. Do
not refactor outside these tasks. Do not implement a task the plan marks as awaiting the owner's
ruling.

Report back concisely: the commit SHAs, the gate's measured numbers after the last task, which values
moved and why, the tests you added with pass counts, and anything you did NOT do and why.
```

## Notes that save a round trip

- **Name the phase and forbid the rest.** Children read the whole plan; without the boundary they
  start the next phase, and then two phases' commits interleave in `git log`.
- **Spell out the push remote.** "Push to origin" and "push to the ssh alias" differ in repos that use
  a host alias; a child that guesses leaves the work local and reports success.
- **Say which documents carry measured numbers.** After a state-moving change the child must re-read
  them from the tool's output; the list is project-specific and a child will miss one.
- **Give the report format.** Commits + measured numbers + tests + what was not done. A report without
  the numbers cannot be verified, only trusted.
- **One sentence on what the phase is for.** A child that knows the phase exists to prove the world
  did not move makes better choices than one following steps blindly.
