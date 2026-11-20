"""Pre-read recorded snapshots so replay is instant and never calls the model during the demo.

Usage: GOOGLE_API_KEY=... .venv/bin/python precompute_rush.py [START] [END]
Defaults to Fri Nov 20, 2026, 06:15 to 08:10 (every snapshot in the window, including the one before
the first replay frame, because two-frame confirmation looks one snapshot back).
Writes data/<ts>/reads.json and a summary of flagged frames to rush_summary.txt.
"""
import os, sys, json, collections, time
os.environ["NO_LIVE"] = "1"
import server

start = sys.argv[1] if len(sys.argv) > 1 else "20261120-061500"
end = sys.argv[2] if len(sys.argv) > 2 else "20261120-081000"
snaps = [s for s in server.all_snapshots() if start <= s <= end]
tally, lines, t0 = collections.Counter(), [], time.time()
for ts in snaps:
    reads = server.replay_reads(ts)
    for cid, r in reads.items():
        if r.get("camera_ok"):
            tally[r.get("congestion")] += 1
            if r.get("congestion") in ("heavy", "stopped") or r.get("incident") not in ("none", "unclear", None):
                lines.append(f"{ts} {cid} {r.get('congestion')} {r.get('incident')} conf={r.get('confidence')} | {r.get('one_line')}")
    print(ts, "done", flush=True)
summary = (f"{len(snaps)} snapshots {start}..{end}, {server.STATS['model_calls']} model calls, "
           f"{server.STATS['prompt_tokens']} prompt + {server.STATS['output_tokens']} output tokens, {time.time() - t0:.0f}s\n"
           f"congestion tally (camera_ok frames): {dict(tally)}\n\nflagged frames (heavy, stopped, or incident):\n" + "\n".join(lines) + "\n")
open("rush_summary.txt", "w").write(summary)
print(summary)
