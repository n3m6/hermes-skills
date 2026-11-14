#!/usr/bin/env python3
"""Create a styled native Google Doc from a markdown-ish text file, optionally in a Drive folder.

Run it with the Hermes venv interpreter (it has google-api-python-client + google-auth):

  /home/faraz/.hermes/hermes-agent/venv/bin/python gdocs_report.py \
      --title "Victoria 3 - Competitive Analysis" \
      --body-file report.md \
      --folder-id <drive folder id>

Body format: a line starting `# ` becomes HEADING_1, `## ` becomes HEADING_2,
everything else is a plain paragraph. Prints one JSON object with the doc id, URL,
char count, heading count and the owner addresses.

Why this is a script: `documents().create` has no parent parameter, so the doc must
be created and then moved; heading styles are NOT applied by insertText, they are a
second batchUpdate over paragraph ranges recorded while the body is built. Both are
easy to get subtly wrong by hand, and the readback check is what proves the write
landed (a 1-2 character difference from Google's own newline handling is normal).
"""

import argparse
import json
import os


def build(text):
    """Strip heading markers, returning (body, [(start, end, style), ...]) 0-based."""
    lines, heads, pos = [], [], 0
    for raw in text.split("\n"):
        line, style = raw, None
        if raw.startswith("## "):
            style, line = "HEADING_2", raw[3:]
        elif raw.startswith("# "):
            style, line = "HEADING_1", raw[2:]
        if style:
            heads.append((pos, pos + len(line) + 1, style))  # span includes the newline
        lines.append(line)
        pos += len(line) + 1
    body = "\n".join(lines)
    if not body.endswith("\n"):
        body += "\n"
    return body, heads


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--body-file", required=True)
    ap.add_argument("--folder-id", default=None)
    ap.add_argument("--token", default=os.path.expanduser("~/.hermes/google_token.json"))
    ap.add_argument("--dry-run", action="store_true",
                    help="parse and report sizes without touching the API")
    a = ap.parse_args()

    text = open(a.body_file, encoding="utf-8").read().rstrip("\n")
    body, heads = build(text)
    if a.dry_run:
        print(json.dumps({"chars": len(body), "headings": len(heads)}, indent=2))
        return

    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build as gbuild

    creds = Credentials.from_authorized_user_file(a.token)
    docs = gbuild("docs", "v1", credentials=creds)
    drive = gbuild("drive", "v3", credentials=creds)

    did = docs.documents().create(body={"title": a.title}).execute()["documentId"]
    docs.documents().batchUpdate(documentId=did, body={"requests": [
        {"insertText": {"location": {"index": 1}, "text": body}}]}).execute()

    if heads:
        docs.documents().batchUpdate(documentId=did, body={"requests": [
            {"updateParagraphStyle": {
                "range": {"startIndex": 1 + s, "endIndex": 1 + e},
                "paragraphStyle": {"namedStyleType": style},
                "fields": "namedStyleType"}} for s, e, style in heads]}).execute()

    if a.folder_id:
        # create-then-move: this is the only way to file a Doc in a folder
        drive.files().update(fileId=did, addParents=a.folder_id, removeParents="root",
                             fields="id,parents").execute()

    # read back: a successful call is not a successful document
    doc = docs.documents().get(documentId=did).execute()
    chars, styles = 0, {}
    for el in doc["body"]["content"]:
        p = el.get("paragraph")
        if not p:
            continue
        chars += sum(len(r.get("textRun", {}).get("content", "")) for r in p["elements"])
        st = p.get("paragraphStyle", {}).get("namedStyleType", "NORMAL_TEXT")
        styles[st] = styles.get(st, 0) + 1

    meta = drive.files().get(fileId=did, fields="id,name,webViewLink,owners(emailAddress)").execute()
    print(json.dumps({
        "id": did,
        "name": meta["name"],
        "url": meta["webViewLink"],
        "chars": chars,
        "headings": len(heads),
        "styles": styles,
        "owners": [o["emailAddress"] for o in meta.get("owners", [])],
        "verified": abs(chars - len(body)) <= 2,
    }, indent=2))


if __name__ == "__main__":
    main()
