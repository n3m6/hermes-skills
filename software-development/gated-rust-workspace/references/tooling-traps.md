# Traps that cost a build round-trip

Rust/cargo/clippy and file-editing failures that surface only at `cargo build`, `cargo test`,
`cargo clippy -- -D warnings`, or the next edit. Expect the real bugs here; treat that pass as part
of the deliverable, not an interruption.

## Borrow checker and accessors

- **A context hands its stores out one at a time.** Reading one store and mutating another in the
  same expression is `E0502` — both borrow the context. Collect the rule's inputs into an owned `Vec`
  first, then write in a second loop; where the same reading is needed by a phase *and* by a loader or
  a test, have the rule RETURN the owned values (not record them) so it keeps one implementation while
  every caller keeps its own borrows.
- **Check for an existing accessor before adding one — `pub fn` is not the whole API.** A tree mixing
  `pub fn` and `pub const fn` defeats a `pub fn`-only grep, and the duplicate surfaces as `E0592` on a
  method that already existed. Grep the bare name inside the impl block; where a layer has its own
  helper duplicating a core accessor, delete the helper and call the accessor.
- **A marker type sharing a name with a data struct shadows it** (`State;` beside `State { .. }`); the
  compiler error points at a use site, not the collision. Name identity markers `*Key` (`StateKey`,
  `ProvinceKey`, `GroupKey`) and leave the data struct unprefixed.

## `clippy -- -D warnings` failures on code that reads correctly

- **Workspace lints can deny the clock and `println!` in every target.** Expect
  `clippy::disallowed_types` on `std::time::Instant`, `disallowed_methods` on `now()`, and
  `print_stdout` on a diagnostic `println!`. The escape is a *scoped* `#[allow(..)]` on the one item
  that needs it plus a comment saying why (a test asserting a wall-clock budget is the legitimate
  case) — never a crate-wide allow. To observe a long run, put the values in the `assert!` message
  (`"{observed:?}"` on a `#[derive(Debug)]` observation struct) instead of printing them. The other
  legitimate case is the **tool test that regenerates a stored artifact**: it must report what it
  wrote, so give it a scoped allow *and* `#[ignore]` it — regeneration stays an act somebody asks for
  while the gate stays read-only.
- **A workspace `clippy::print_stdout = "warn"` breaks a CLI**, whose entire job is printing. Opt out
  at the top of the **binary** only (`#![allow(clippy::print_stdout)]`, one comment saying the output
  is the deliverable) so the library stays held to the lint.
- **A same-width `try_from` is `clippy::useless_conversion`, and `.iter().next()` on a slice-like is
  `clippy::iter_next_slice`.** `u32::try_from(a - b + 1)` where the fields are already `u32`, and
  `i64::try_from(v.to_ppm())` where the getter already returns `i64`, each fail a `-D warnings` gate on
  code that reads perfectly well; write the expression directly and use `.first()`. Both cost a full
  build round-trip to discover, so sweep for them in one pass when a gate reports one.
- **A wrapped doc-comment line must not begin with `- `.** A workspace gating on
  `clippy -- -D warnings` fails `doc_lazy_continuation` when a reflowed sentence starts its
  continuation line with a hyphen ("... minus stability - and the rival's presence ..."), because
  Markdown reads it as a list item. Reflow the sentence; indenting it is how the prose starts lying
  about its own structure.
- **`clippy::type_complexity` fires on a 4-tuple**, which a book of armed/disarmed state reaches
  quickly. Name a `type` alias with a doc comment rather than `#[allow]`ing the lint; the alias is
  also where the reading of the fields gets written down.
- **An edition-2024 workspace makes the write-time lint lie about `let` chains.**
  `let chains are only allowed in Rust 2024` from a file-writing tool's linter is a false positive
  (the lint runs with a default edition); the workspace's own `cargo clippy` is the authority. Do not
  restructure correct code for it.

## Toolchain portability

- **Integer arithmetic only, and round up by hand.** Write `(gap + rate - 1) / rate`; `div_ceil` is
  not available on every toolchain, and a helper using `TryFrom` cannot be a `const fn`.

## A test whose message is part of the contract

- **`#[should_panic(expected = "..")]` strings must move with the message** they match; editing an
  error message otherwise turns a test into a failure.

## Editing files (cargo fmt and the file tools)

- **`cargo fmt` moves the text you were about to patch.** A string quoted before a format either
  stops matching or starts matching twice. Re-read the region after formatting, and include enough
  surrounding context to be unique.
- **Never overwrite a file you have not read this task** — `write_file` refuses, and forcing it
  through is how unrelated edits are lost. Read it, then `patch`. The same care covers a *sibling
  agent* sharing the tree: a whole-file rewrite clobbers an edit you never saw, so prefer small
  `patch` hunks, re-read before a rewrite, and use `git status` to tell your files from theirs before
  reporting which ones you touched.
- **`read_file` returns lines prefixed `N|`.** Writing that back corrupts the file; whole-file edits
  go through a generator script instead.
