# Formatted Google Docs

`docs create --body` inserts plain text only. When the deliverable needs
headings, bullets, inline links and a chosen typeface, create the Doc in its
target folder with the Drive API, then format it with Docs `batchUpdate`.

## Create in the target folder

`docs create` has no `--parent`. Create the Doc directly instead of creating it
in the root and moving it:

```python
drive.files().create(
    body={
        "name": title,
        "mimeType": "application/vnd.google-apps.document",
        "parents": [folder_id],
    },
    fields="id,webViewLink",
).execute()
```

The returned id is editable with the Docs API exactly like a normally created
Doc.

## Insert once, then style by offsets

1. Parse the source into paragraphs and record `(start, end, kind)` for each
   block, plus inline spans for bold and links. Strip the markup while recording
   the offsets.
2. Join every paragraph with a trailing newline and insert the whole string once
   at index 1.
3. Document indices are 1-based: `doc_index = 1 + offset`. Style requests do not
   change text length, so offsets computed from the inserted string remain valid
   for the entire batch.
4. Send paragraph and text style requests in `batchUpdate` chunks of about 40.

Minimal request shapes:

```python
{"updateParagraphStyle": {
    "range": {"startIndex": s, "endIndex": e},
    "paragraphStyle": {
        "namedStyleType": "HEADING_1",
        "spaceAbove": {"magnitude": 18, "unit": "PT"},
        "spaceBelow": {"magnitude": 6, "unit": "PT"},
        "lineSpacing": 115,
    },
    "fields": "namedStyleType,spaceAbove,spaceBelow,lineSpacing",
}}
{"updateTextStyle": {
    "range": {"startIndex": s, "endIndex": e},
    "textStyle": {
        "weightedFontFamily": {"fontFamily": "Georgia"},
        "fontSize": {"magnitude": 10.5, "unit": "PT"},
        "foregroundColor": {"color": {"rgbColor": {
            "red": 0.10, "green": 0.13, "blue": 0.17,
        }}},
    },
    "fields": "weightedFontFamily,fontSize,foregroundColor",
}}
{"updateTextStyle": {
    "range": {"startIndex": s, "endIndex": e},
    "textStyle": {"link": {"url": url}, "underline": True},
    "fields": "link,underline",
}}
```

## Pitfalls

- **`fontFamily` is not a `TextStyle` field.** The API rejects the whole batch
  with `Unknown name "fontFamily"`. Use
  `weightedFontFamily: {"fontFamily": "..."}` and include `weightedFontFamily`
  in the `fields` mask.
- **`fields` masks are mandatory in practice.** A request without one errors or
  applies nothing. List every property you set.
- **Do not insert the title after styling.** Any insertion shifts every later
  index; build the complete text, including the title paragraph, before the one
  insert.
- **One insert, many styles.** Interleaving inserts and style requests makes
  offsets stale. Insert all text, then style it.
- **`lineSpacing` is a percentage** (115 = 1.15), not a multiplier.
- **`foregroundColor` components are floats 0–1**, not 0–255.
- **A batch of style requests is all-or-nothing.** One bad property name rejects
  the chunk; split large batches so a failure is cheap to isolate.

## Code blocks and inline code

- A fenced code block must be inserted as **one paragraph** with `\v` (vertical
tab) between lines, not `\n`. `\n` starts a new paragraph, so paragraph shading
and spacing apply line by line and the block looks broken.
- Style the block with `weightedFontFamily: {"fontFamily": "Roboto Mono"}` at
8–8.5 pt and a light `paragraphStyle.shading.backgroundColor`; include `shading`
in the `fields` mask.
- Inline code: strip the backticks while recording a span, then apply the mono
font at about 9 pt. Do not use bold for code.
- Keep code lines at or under ~78 characters at 8.5 pt; a terminal capture made
at 78 columns then fits without wrapping.
- `\v` counts as one character, so compute spans on the joined string exactly
as for prose.
- Put the document title in the body as a `TITLE` paragraph. The Drive file name
is metadata; it is not printed or exported as document text.

## Verify

Read the Doc back and assert:

- the title and heading count by `paragraphStyle.namedStyleType`;
- the number of linked runs (`textRun.textStyle.link`);
- the first and last lines actually read as intended.

For layout, export a PDF and render the first pages. **A box around a link in a
PDF preview is a link annotation drawn by the viewer**, not document formatting;
Google Docs shows an ordinary blue underline.
