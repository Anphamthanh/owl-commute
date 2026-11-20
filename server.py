"""Owl Commute: when do I leave, where do I park, which bus has room.

Live data: GDOT 511 traffic cameras near KSU (read by a vision model), Big Owl Bus GPS + passenger
counts (Passio GO, system 66), and KSU Parking Pulse class-demand curves.
Replay mode serves a recorded snapshot from data/<timestamp>/ so the demo works without live traffic.

Run: .venv/bin/uvicorn server:app --port 8000
"""
import json, os, threading, time, datetime as dt
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, Response
from google import genai
from google.genai import types

ROOT = Path(__file__).parent
DATA = ROOT / "data"
CAMS = json.loads((ROOT / "cams.json").read_text())
DEMAND = json.loads((ROOT / "pulse/demand.json").read_text())
UA = {"User-Agent": "Mozilla/5.0 Chrome/146"}
MODEL = "gemini-3.1-pro-preview"
DEAD_BYTES = 10_000          # GDOT's "STREAM NOT AVAILABLE" placeholder is ~7.5 KB
LIVE_REFRESH = 120           # seconds between live camera reads

PROMPT = """You are a traffic analyst for Kennesaw State University commuters. Look at this live traffic camera frame ({name}).
Return ONLY JSON: {{"camera_ok": bool (false if blank, "stream not available", or frozen),
"time_of_day": "day|dusk|night", "congestion": "free_flow|moderate|heavy|stopped|unknown",
"vehicles_visible": int (rough), "queue_visible": bool,
"incident": "none|crash|stalled_vehicle|emergency_vehicle|debris|construction|unclear",
"pedestrians": int, "weather_visibility": "clear|rain|fog|glare|dark", "confidence": 0-1,
"one_line": "plain-English status a student would read, max 15 words"}}
Calibration rules:
- Cars waiting at a red light or a short line at an intersection is NORMAL: use free_flow or moderate, not heavy.
- heavy = the queue clearly backs up through or past the intersection, or highway lanes are dense and slow end to end.
- stopped = vehicles clearly not moving across most lanes (gridlock, closure).
- Headlight glare, bloom, and light trails at night are not congestion. A few bright blobs on a highway is free_flow.
- emergency_vehicle only if you see flashing red/blue lights; amber beacons are usually maintenance/tow (use construction or unclear).
Do not guess an incident unless clearly visible; say unclear instead. If the image is too dark or blurred to judge, use congestion "unknown" and low confidence."""


def _gemini_key():
    key = os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise SystemExit("Set GOOGLE_API_KEY in the environment (never in a file inside this repo).")
    return key


client = genai.Client(api_key=_gemini_key(), http_options=types.HttpOptions(api_version="v1beta"))
app = FastAPI(title="Owl Commute")

# Every model call is counted so the cost per day on a slide comes from real numbers, not a guess.
STATS = {"model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "started": dt.datetime.now().isoformat(timespec="seconds")}
_stats_lock = threading.Lock()


def read_frame(cam, png: bytes) -> dict:
    """One vision-model read of one frame. Dead cameras are detected by size, no model call."""
    if len(png) < DEAD_BYTES:
        return {"camera_ok": False, "congestion": "unknown", "incident": "unclear", "confidence": 1.0,
                "one_line": "Camera offline.", "vehicles_visible": 0, "pedestrians": 0, "queue_visible": False}
    try:
        r = client.models.generate_content(
            model=MODEL,
            contents=[types.Part.from_bytes(data=png, mime_type="image/png"), PROMPT.format(name=cam["name"])],
            config=types.GenerateContentConfig(response_mime_type="application/json"))
        u = getattr(r, "usage_metadata", None)
        with _stats_lock:
            STATS["model_calls"] += 1
            STATS["prompt_tokens"] += getattr(u, "prompt_token_count", 0) or 0
            STATS["output_tokens"] += getattr(u, "candidates_token_count", 0) or 0
        out = json.loads(r.text)
        out["tokens"] = [getattr(u, "prompt_token_count", 0) or 0, getattr(u, "candidates_token_count", 0) or 0]
        return out
    except Exception as e:
        return {"camera_ok": False, "congestion": "unknown", "incident": "unclear", "confidence": 0,
                "one_line": f"Read failed ({type(e).__name__}).", "vehicles_visible": 0, "pedestrians": 0,
                "queue_visible": False}


def read_all(frames: dict) -> dict:
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {c["id"]: ex.submit(read_frame, c, frames[c["id"]]) for c in CAMS if c["id"] in frames}
        return {cid: f.result() for cid, f in futs.items()}


# ---------- live state ----------
LIVE = {"frames": {}, "reads": {}, "prev": {}, "ts": None}
_bus_cache = {"t": 0, "data": None}


def live_loop():
    while True:
        try:
            frames = {}
            with httpx.Client(headers=UA, timeout=20) as h:
                for c in CAMS:
                    try:
                        frames[c["id"]] = h.get(f"https://511ga.org/map/Cctv/{c['id']}").content
                    except Exception:
                        pass
            reads = read_all(frames)
            LIVE.update(prev=LIVE["reads"], frames=frames, reads=reads, ts=dt.datetime.now().isoformat(timespec="seconds"))
        except Exception as e:
            print("live loop error", e)
        time.sleep(LIVE_REFRESH)


def live_buses():
    if time.time() - _bus_cache["t"] > 15 or _bus_cache["data"] is None:
        r = httpx.post("https://passio3.com/www/mapGetData.php?getBuses=2&deviceId=1",
                       data={"json": '{"s0":"66","sA":1}'}, headers=UA, timeout=15)
        _bus_cache.update(t=time.time(), data=r.json())
    return _bus_cache["data"]


# ---------- replay state ----------
def snapshot_dir(ts: str) -> Path:
    d = DATA / ts
    if not d.is_dir():
        raise HTTPException(404, f"no snapshot {ts}")
    return d


def all_snapshots() -> list:
    """Every recorded snapshot, read or not. Used by the pre-read job and for finding the previous frame."""
    return sorted(p.name for p in DATA.iterdir() if p.is_dir() and (p / "buses.json").exists())


def replay_reads(ts: str, allow_model: bool = True) -> dict:
    """Reads for a recorded snapshot, cached to reads.json so the model runs once per snapshot.

    The web app passes allow_model=False: replay must never call the model mid-demo, so a snapshot
    that was not pre-read returns {} (its cameras show as 'not read') instead of stalling the page.
    """
    d = snapshot_dir(ts)
    cache = d / "reads.json"
    if cache.exists():
        return json.loads(cache.read_text())
    if not allow_model:
        return {}
    frames = {c["id"]: (d / f"cam_{c['id']}.png").read_bytes() for c in CAMS if (d / f"cam_{c['id']}.png").exists()}
    reads = read_all(frames)
    cache.write_text(json.dumps(reads, indent=1))
    return reads


# ---------- shared logic ----------
def bus_summary(raw: dict) -> list:
    out = []
    for lst in (raw or {}).get("buses", {}).values():
        for b in lst:
            if b.get("outOfService"):
                continue
            cap = b.get("totalCap") or 0
            pax = b.get("paxLoad") or 0
            out.append({"bus": b.get("busName"), "route": (b.get("route") or "").replace("KM  ", "").strip(),
                        "lat": float(b["latitude"]), "lon": float(b["longitude"]), "pax": pax, "cap": cap,
                        "load": round(pax / cap, 2) if cap else None, "seen": b.get("createdTime"),
                        "color": b.get("color")})
    return sorted(out, key=lambda x: (x["route"], x["bus"]))


PENALTY = {"free_flow": 0, "moderate": 2, "heavy": 10, "stopped": 18, "unknown": 0}


def advice(campus: str, class_time: str, drive_min: int, day: str, reads: dict, buses: list, now: dt.datetime, prev: dict = None):
    """Transparent 'leave by' math. Every minute added is explained with its source."""
    h, m = map(int, class_time.split(":"))
    cls = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if cls < now:  # class time already passed today: plan for the next class day
        cls += dt.timedelta(days=1)
    reasons, extra, notes, by_corridor = [], 0, [], {}
    # Live road conditions only matter if you are leaving soon; tonight's cameras say nothing about tomorrow 9 AM.
    rough_leave = cls - dt.timedelta(minutes=drive_min + 30)
    roads_apply = (rough_leave - now) <= dt.timedelta(minutes=90)
    if not roads_apply:
        recheck = (rough_leave - dt.timedelta(minutes=60))
        notes.append(f"Traffic cameras are checked once you are within 90 minutes of leaving. Check back around {recheck.strftime('%-I:%M %p')}.")
    for c in CAMS:
        if not roads_apply or c["campus"] != campus or c["id"] not in reads:
            continue
        r, pr = reads[c["id"]], (prev or {}).get(c["id"])
        if not r.get("camera_ok") or r.get("confidence", 0) < 0.6:
            continue
        p = PENALTY.get(r.get("congestion"), 0)
        bad_inc = r.get("incident") in ("crash", "stalled_vehicle", "emergency_vehicle", "debris")
        if bad_inc:
            p += 8
        if not p:
            continue
        # Require two consecutive frames (~2 min apart) to agree before adding delay.
        confirmed = pr is not None and (PENALTY.get(pr.get("congestion"), 0) > 0 or (bad_inc and pr.get("incident") == r.get("incident")))
        if not confirmed:
            notes.append(f"Watching {c['corridor']} ({c['name']}): {r.get('one_line')} It counts only if the next picture agrees.")
            continue
        worst = by_corridor.get(c["corridor"])
        if worst is None or p > worst["minutes"]:  # cameras overlap: count only the worst camera per road
            by_corridor[c["corridor"]] = {"minutes": p, "why": f"Traffic on {c['corridor']}: {r.get('one_line')}",
                                          "source": f"Traffic camera at {c['name']}, same reading on 2 pictures in a row"}
    for r in by_corridor.values():
        reasons.append(r)
        extra += r["minutes"]
    extra = min(extra, 30)  # cameras overlap on the same corridor; cap so one jam isn't counted 5 times
    # Demand curve for the day the class is on (not today, if the class rolled over to tomorrow).
    day = day or cls.strftime("%a")
    # KSU publishes Mon/Wed and Tue/Thu charts only. Fri, Sat and Sun use the Mon/Wed chart: an assumption, labeled as such.
    assumed = day not in ("Mon", "Tue", "Wed", "Thu")
    key = ("TR" if day in ("Tue", "Thu") else "MW") + "-" + campus.lower()
    hour = max(8, min(19, h))  # you hunt for parking in the hour your class starts
    demand = DEMAND[key][str(hour)]
    park = round(5 + 20 * demand)  # estimate: 5 min at an empty deck, up to 25 min at the day's peak
    label = "after 7 PM" if h > 19 else "before 8 AM" if h < 8 else f"{hour % 12 or 12} {'PM' if hour >= 12 else 'AM'}"
    busy = "the busiest hour of the day" if demand >= 0.95 else f"{int(demand * 100)}% as busy as the busiest hour"
    src = "Estimate from KSU's Parking Pulse chart" + (f" (KSU publishes no {day} chart, so the Mon/Wed chart is used)" if assumed else "")
    reasons.append({"minutes": park, "why": f"Finding parking: {label} is {busy} at {campus}", "source": src})
    walk = 7
    reasons.append({"minutes": walk, "why": "Walk from the deck to class", "source": "Estimate"})
    total = drive_min + extra + park + walk
    leave = cls - dt.timedelta(minutes=total)
    km = [b for b in buses if "Marietta" in b["route"] and "Kennesaw" in b["route"]]
    return {"class_time": cls.strftime("%-I:%M %p"), "class_day": day, "leave_by": leave.strftime("%-I:%M %p"),
            "minutes_until_leave": round((leave - now).total_seconds() / 60),
            "breakdown": [{"minutes": drive_min, "why": "Drive to campus", "source": "The time you entered"}] + reasons,
            "total_minutes": total, "demand": demand, "notes": notes,
            "km_buses": [{"bus": b["bus"], "seats_left": b["cap"] - b["pax"], "full": b["pax"] >= b["cap"]} for b in km]}


# ---------- API ----------
@app.get("/")
def index():
    return FileResponse(ROOT / "static/index.html")


@app.get("/api/snapshots")
def snapshots():
    """Only snapshots that were pre-read (reads.json exists) are offered for replay, so replay never calls the model."""
    return [s for s in all_snapshots() if (DATA / s / "reads.json").exists()]


@app.get("/api/stats")
def stats():
    return {**STATS, "model": MODEL, "cams": len(CAMS), "live_refresh_s": LIVE_REFRESH}


@app.get("/api/state")
def state(mode: str = "live", ts: str = None):
    if mode == "replay":
        d = snapshot_dir(ts)
        reads = replay_reads(ts, allow_model=False)
        snaps = all_snapshots()
        i = snaps.index(ts)
        prev = replay_reads(snaps[i - 1], allow_model=False) if i > 0 else {}
        buses = bus_summary(json.loads((d / "buses.json").read_text()))
        when = dt.datetime.strptime(ts, "%Y%m%d-%H%M%S").isoformat()
    else:
        reads, prev, buses, when = LIVE["reads"], LIVE["prev"], bus_summary(live_buses()), LIVE["ts"] or dt.datetime.now().isoformat(timespec="seconds")
    cams = [{**c, "read": reads.get(c["id"])} for c in CAMS]
    return {"mode": mode, "ts": ts, "as_of": when, "cams": cams, "buses": buses, "prev": prev}


@app.get("/api/cam/{cid}.png")
def cam_png(cid: str, mode: str = "live", ts: str = None):
    if mode == "replay":
        p = snapshot_dir(ts) / f"cam_{cid}.png"
        if not p.exists():
            raise HTTPException(404)
        return Response(p.read_bytes(), media_type="image/png")
    png = LIVE["frames"].get(cid)
    if png is None:
        png = httpx.get(f"https://511ga.org/map/Cctv/{cid}", headers=UA, timeout=20).content
    return Response(png, media_type="image/png", headers={"Cache-Control": "no-store"})


@app.get("/api/advice")
def get_advice(campus: str = "Kennesaw", class_time: str = "09:30", drive_min: int = Query(25, ge=0, le=180),
               day: str = None, mode: str = "live", ts: str = None):
    st = state(mode, ts)
    now = dt.datetime.fromisoformat(st["as_of"])
    reads = {c["id"]: c["read"] for c in st["cams"] if c["read"]}
    return advice(campus, class_time, drive_min, day, reads, st["buses"], now, st["prev"])


# ---------- accuracy labeling (a human labels frames by eye, then we score the model against them) ----------
LABELS = DATA / "labels.json"
_label_lock = threading.Lock()


@app.get("/label")
def label_page():
    return FileResponse(ROOT / "static/label.html")


@app.get("/api/label/frames")
def label_frames(start: str = "20261120-061500", end: str = "20261120-081000", n: int = 30, seed: int = 1):
    """Every flagged frame (heavy, stopped, or incident) in the window, plus a random sample of the rest, up to n."""
    import random
    flagged, rest, done = [], [], set()
    if LABELS.exists():
        done = {(x["ts"], x["cid"]) for x in json.loads(LABELS.read_text())}
    names = {c["id"]: c["name"] for c in CAMS}
    for ts in all_snapshots():
        if not (start <= ts <= end) or not (DATA / ts / "reads.json").exists():
            continue
        for cid, r in json.loads((DATA / ts / "reads.json").read_text()).items():
            if not r.get("camera_ok") or (ts, cid) in done:
                continue
            item = {"ts": ts, "cid": cid, "name": names.get(cid, cid), "read": r}
            (flagged if r.get("congestion") in ("heavy", "stopped") or r.get("incident") not in ("none", "unclear", None) else rest).append(item)
    random.Random(seed).shuffle(rest)
    return flagged + rest[: max(0, n - len(flagged))]


@app.post("/api/label")
def label_save(item: dict):
    with _label_lock:
        labels = json.loads(LABELS.read_text()) if LABELS.exists() else []
        labels = [x for x in labels if not (x["ts"] == item["ts"] and x["cid"] == item["cid"])]
        labels.append({"ts": item["ts"], "cid": item["cid"], "congestion": item["congestion"], "incident": bool(item["incident"]),
                       "at": dt.datetime.now().isoformat(timespec="seconds")})
        LABELS.write_text(json.dumps(labels, indent=1))
    return {"n": len(labels)}


@app.get("/api/label/score")
def label_score():
    """How often the model agreed with the human labels. This is the accuracy number for the deck."""
    labels = json.loads(LABELS.read_text()) if LABELS.exists() else []
    n = exact = binned = inc = unknown = 0
    slow = {"heavy", "stopped"}
    for x in labels:
        r = json.loads((DATA / x["ts"] / "reads.json").read_text()).get(x["cid"], {})
        model_inc = r.get("incident") in ("crash", "stalled_vehicle", "emergency_vehicle", "debris")
        inc += model_inc == x["incident"]
        if x["congestion"] == "unknown":
            unknown += 1
            continue
        n += 1
        exact += r.get("congestion") == x["congestion"]
        binned += (r.get("congestion") in slow) == (x["congestion"] in slow)
    total = len(labels)
    pct = lambda a, b: round(100 * a / b) if b else 0
    return {"n": n, "unknown": unknown, "total": total, "cong_exact": exact, "cong_exact_pct": pct(exact, n),
            "cong_bin": binned, "cong_bin_pct": pct(binned, n), "inc": inc, "inc_pct": pct(inc, total)}


if os.environ.get("NO_LIVE") != "1":
    threading.Thread(target=live_loop, daemon=True).start()
