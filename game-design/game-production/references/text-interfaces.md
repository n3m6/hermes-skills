# Text interfaces: CLI, TUI and REPL

Scope: a game or tool whose primary surface is a terminal, before or alongside a
visual client. Use with `references/look-and-feel-best-practices.md`; the
hierarchy, readability and feedback rules are the same ones, expressed in
characters instead of pixels.

## Why the text phase matters

A text interface is the wireframe and the content model for the visual product.
Typographic hierarchy, surface order, wording and refusal text all transfer. Get
them right while they are cheap; a visual client built on a bad text screen
inherits the bad information architecture and merely adds chrome.

## Procedure

1. **Define the screen grammar before styling.** List the surfaces (briefing,
dossier, queue, map, ledger). Give each one primary read, secondary context and
tertiary detail. Fix the section order and the footer per surface. A screen with
no primary read is a log.
2. **Build a style layer at the print boundary.** Renderers keep returning plain
facts; the printer decides how loud each fact is. Define tokens: dim (metadata,
ages, counts), default (facts), bold (section headers and the one decision), one
accent (actionable), one danger (interrupts and losses). Respect `NO_COLOR`,
`TERM=dumb` and non-TTY output, and keep the unstyled strings for tests.
3. **Make the prompt a status line.** Show the turn/date, pause or speed state,
and queued actions: `1945-01 · paused · 2 queued >`. Show the advance key only
when it is meaningful. A bare `>` forces the player to remember the loop state.
4. **Print a receipt after every command.** One line, fixed grammar:
`queued: <verb> <target> — <cost>, <duration>`, `ran 3 months; stopped: <reason>`,
`refused: <condition that would clear it>`. The screen is context; the receipt is
acknowledgement. Without it the player cannot tell their order from the world's
noise.
5. **Design the empty states and the silence.** "Nothing needs you this month" is
a designed line, not a missing block. Never print an empty table. Distinguish
unknown from known-zero in words and glyphs, not only in colour.
6. **Dedupe and use progressive disclosure.** One fact in one place. A context
footer lists the five commands that matter on this surface; `help` carries the
rest. A footer that lists every command everywhere is a menu, not an instrument.
7. **Put numbers in a table.** Label, value, delta, threshold — fixed columns,
same order on every surface. A run-on sentence with four numbers is parsed, not
scanned. A number without its direction and threshold is incomplete.
8. **Keep one motif.** A document header rule with date and surface, a `SOURCE`
line for believed facts, a `FILED` age and a `CONFIDENCE` band. Apply it to every
screen. One motif used everywhere reads as a designed product; a different
header per screen reads as a debug log.
9. **Onboard in the first screenful.** Put the actionable list above authored
prose; one line per item, detail behind a command. The first hour is the
tutorial, and the first decision should arrive before the first wall of text.
10. **Test at the real terminal.** 80×24, monochrome, no Unicode, piped output,
non-TTY, slow link. Snapshot the canonical screens — briefing, dossier, queue,
map, refusal, empty state — as plain text and as ANSI-stripped text. The golden
snapshot is the CLI's "gold standard" asset.

## Glyph and colour vocabulary

Reserve one meaning per glyph and provide ASCII fallbacks:

| Glyph | Meaning | ASCII |
|---|---|---|
| `•` | bullet | `-` |
| `·` | inline separator only | `|` |
| `!` | interrupt | `!` |
| `?` | unknown | `?` |
| `~` | believed | `~` |
| `=` | verified | `=` |
| `▸` | action / next | `>` |

Colour roles: dim metadata, default facts, bold headers and the decision, accent
for actionable, danger for interrupts and losses. Never colour alone — a glyph
and a word must carry the same meaning in monochrome.

## Pitfalls

- **All-caps headers with no weight or colour layer.** Every line reads equally;
the eye cannot triage. Hierarchy is the first job, not the last.
- **One glyph doing two jobs** (bullet and separator, for example). It weakens
the signal and makes the screen ambiguous.
- **A bare prompt with no state.** The player has to remember the date, pause
state and queued orders; the interface should not outsource memory.
- **Reprinting the whole static screen after every command.** It floods
scrollback and feels like input lag. Prefer a receipt plus the changed block;
keep full redraws for explicit screen changes.
- **Duplicated facts.** The same number in two sections costs a line and dilutes
the hierarchy. One fact, one home.
- **Repeated labels instead of a section header.** `governments:` on every line
is a log, not a list; use one header and indented entries.
- **ANSI without a non-TTY / `NO_COLOR` path.** Piped output, logs and tests get
corrupted. Style only when the terminal supports it.
- **Testing only in a wide, coloured terminal.** It hides 80-column wraps,
Unicode fallbacks and monochrome ambiguity.
- **Footer sprawl.** A dozen commands on every surface is a menu; a
context-sensitive five is an instrument.

## Checklist

- Does each screen have one obvious primary read?
- Is the actionable item above the prose and above the books?
- Does the prompt show turn, pause state and queued work?
- Does every command produce a one-line receipt?
- Are unknown, known-zero and believed distinct without colour?
- Is each fact printed once, in one home?
- Are numbers aligned with their delta and threshold?
- Does the footer match the surface?
- Does the screen survive 80×24, monochrome, no Unicode and a pipe?
