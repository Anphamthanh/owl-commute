# Owl Commute

**When do I leave, where do I park, which bus has room?**

A one-page web app for Kennesaw State University commuters, built for the KSU AI Club Hackathon 2026
(theme: use AI to solve problems on campus). You enter your campus, class time, and normal drive time.
It answers with a "Leave by" time, and every minute in that answer says where it came from.

## What it does

- **Leave by**: your drive, plus parking search time from KSU's own Parking Pulse class-demand chart for that
  hour, plus the walk from the deck, plus road delay from live traffic cameras.
- **Road delay from a vision model**: 16 public GDOT 511 traffic cameras around both campuses are read every
  2 minutes by Gemini 3.1 Pro. Each read returns congestion, incident, confidence, and one plain sentence a
  student can read ("Emergency vehicles at Frey Rd and Campus Loop Rd. Avoid area if possible.").
- **Live bus seats**: the Big Owl Bus system publishes GPS and the passenger count of every bus. The app shows
  seats left per bus on the map and tells you whether the Kennesaw to Marietta bus has room.
- **Replay mode**: plays back recorded mornings so the demo works even when the roads are quiet.

## Safeguards (the model can be wrong)

- A camera adds delay only when two consecutive frames, two minutes apart, agree.
- Cameras only count when you are leaving within 90 minutes; tonight's traffic says nothing about 9 AM tomorrow.
- Only the worst camera on each road counts, so overlapping cameras do not stack the same jam.
- Dead cameras (GDOT's "stream not available" placeholder) are detected by file size and never sent to the model.
- Reads with confidence below 0.6 are ignored. Parking and walk minutes are labeled "estimate" on the card.
- Accuracy is measured, not assumed: `/label` lets a person label frames by eye, and `/api/label/score` reports
  how often the model agreed. The number and the sample size go on the slide together.

## Run it

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
export GOOGLE_API_KEY=...            # environment only; the code never reads a key from a file
.venv/bin/uvicorn server:app --port 8000
open http://localhost:8000
```

- `record.sh` records camera frames and the bus feed into `data/<timestamp>/` (every 2 minutes at rush hour).
- `GOOGLE_API_KEY=... .venv/bin/python precompute_rush.py START END` pre-reads a window of snapshots so replay
  never calls the model during a demo. Only pre-read snapshots appear in the Replay menu.
- `python3 pulse/extract_demand.py` rebuilds `pulse/demand.json` from KSU's chart images.
- `python3 pitch/cost.py CALLS PROMPT_TOKENS OUTPUT_TOKENS` computes the model cost per day from measured tokens.
- `python3 deck/build_deck.py` rebuilds the pitch deck from `deck/facts.json`.

## Data sources (all public, no login)

| Source | What | How |
|---|---|---|
| GDOT 511 Georgia | Still frames from traffic cameras near both campuses | `https://511ga.org/map/Cctv/<id>`; list from `/List/GetData/Cameras` |
| Passio GO (Big Owl Bus, system 66) | Live bus GPS, route, passengers on board, capacity | `POST passio3.com/www/mapGetData.php?getBuses=2` with `json={"s0":"66","sA":1}` |
| KSU Parking Pulse | Hourly class-demand bar charts (Mon/Wed, Tue/Thu, per campus) | Bar heights measured in pixels from the chart images (`pulse/extract_demand.py`) |

## Limitations

- Parking search, walk, and delay minutes are estimates from a simple formula, not measurements.
- There is no public live parking deck occupancy. The Parking Pulse demand curve is a stand-in.
- KSU publishes no Friday or weekend chart; the app uses the Mon/Wed chart and labels it as an assumption.
- Some Marietta-side cameras were offline during the hackathon week.
- Night, fog, and glare lower the model's confidence; it reports "unknown" rather than guessing.
- The bus feed is undocumented and could change without notice.

## Layout

```
server.py            FastAPI app: live loop, replay, leave-by advice, labeling endpoints
static/index.html    the app (Leaflet map, leave-by card, bus seats, camera grid)
static/label.html    label frames by eye to score the model
cams.json            the 16 cameras (GDOT ids, names, campus, corridor, coordinates)
pulse/               KSU Parking Pulse chart images, extraction script, demand.json
record.sh            frame and bus recorder
precompute_rush.py   pre-read a window of snapshots for replay
pitch/               video script, pitch notes, cost calculator
deck/                pitch deck builder, facts.json, screenshots
```
