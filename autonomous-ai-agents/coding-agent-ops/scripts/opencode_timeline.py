#!/usr/bin/env python3
"""Read-only transcript timeline for an opencode session (v2 schema).

Prints the session header, whether the turn is open, the current turn's message
timeline (work-item ids quoted in reasoning, commands, tool status), and the tail
of the newest shell output files (gate verdicts).

Usage:
  opencode_timeline.py [--session ses_...] [--since-seq N] [--db PATH]
                       [--id-pattern REGEX]

Defaults: newest top-level session by time_updated; turn start = last user row.
Never opens the database writable.
"""
import argparse
import datetime
import json
import os
import re
import sqlite3
import sys

DEFAULT_DB = os.path.expanduser("~/.local/share/opencode/opencode.db")


def ts(ms):
    if not ms:
        return "-"
    return datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc).strftime("%H:%M:%S")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", help="ses_... (default: newest top-level)")
    ap.add_argument("--since-seq", type=int, help="start after this seq (default: last user row)")
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--id-pattern", default=r"\b(?:F|W|R)\d{2,3}\b",
                    help="work-item id shape quoted in reasoning")
    a = ap.parse_args()

    con = sqlite3.connect("file:" + a.db + "?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    sid = a.session
    if not sid:
        row = cur.execute("select id from session_v2 where parent_id is null "
                          "order by time_updated desc limit 1").fetchone()
        if not row:
            sys.exit("no sessions in " + a.db)
        sid = row["id"]

    s = cur.execute("select * from session_v2 where id=?", (sid,)).fetchone()
    if not s:
        sys.exit("no such session: " + sid)

    mx = cur.execute("select max(seq) from session_message where session_id=?", (sid,)).fetchone()[0] or 0
    idle = cur.execute("select max(seq) from session_message where session_id=? and type='idle'",
                       (sid,)).fetchone()[0] or 0

    print("session %s %s | %s" % (sid, s["slug"], (s["title"] or "")[:90]))
    print("  %s  agent=%s model=%s" % (s["directory"], s["agent"], s["model"]))
    print("  max seq=%s  last idle seq=%s  turn open=%s" % (mx, idle, idle < mx))
    if s["time_busy"]:
        print("  busy since %s" % ts(s["time_busy"]))
    if s["time_idle"]:
        print("  last idle %s outcome=%s resume_attempts=%s"
              % (ts(s["time_idle"]), s["idle_outcome"], s["resume_attempts"]))

    since = a.since_seq
    if since is None:
        since = (cur.execute("select max(seq) from session_message "
                             "where session_id=? and type='user'", (sid,)).fetchone()[0] or 0) - 1

    pat = re.compile(a.id_pattern)
    print("\n== messages since seq %s ==" % since)
    for r in cur.execute("select seq,type,time_created,data from session_message "
                         "where session_id=? and seq>? order by seq", (sid, since)):
        j = json.loads(r["data"])
        txt, cmds, sts = "", [], []
        for p in j.get("content", []):
            kind = p.get("type")
            if kind == "reasoning":
                txt += p.get("text", "")
            elif kind == "text":
                txt += "\n" + p.get("text", "")
            elif kind == "tool":
                st = p.get("state") or {}
                cmds.append(str((st.get("input") or {}).get("command") or p.get("name")))
                sts.append(st.get("status"))
        ids = ",".join(sorted(set(pat.findall(txt)))) or "-"
        print("%5d %s %-4s ids=%s tools=%s" % (r["seq"], ts(r["time_created"]),
                                               r["type"][:4], ids, ",".join(sts) or "-"))
        first = txt.strip().split("\n")[0][:150]
        if first:
            print("      ", first)
        for c in cmds[:2]:
            print("       $", c.replace("\n", " | ")[:170])

    shell = os.path.expanduser("~/.local/share/opencode/shell")
    if os.path.isdir(shell):
        dirs = sorted((os.path.join(shell, d) for d in os.listdir(shell)),
                      key=os.path.getmtime, reverse=True)
        for d in dirs[:1]:
            outs = sorted((os.path.join(d, f) for f in os.listdir(d) if f.endswith(".out")),
                          key=os.path.getmtime, reverse=True)
            for f in outs[:2]:
                print("\n== %s tail ==" % os.path.basename(f))
                try:
                    lines = open(f, errors="replace").read().splitlines()
                except OSError:
                    continue
                for line in lines[-8:]:
                    print("  ", line[:170])


if __name__ == "__main__":
    main()
