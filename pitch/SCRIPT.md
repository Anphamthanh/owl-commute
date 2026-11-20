# Owl Commute: video script (4 min max) and 5-minute pitch

Record Fri Nov 20 at 8:30 AM, screen capture of http://localhost:8000 with An narrating (QuickTime or Cmd+Shift+5,
microphone on). Keep the browser at 1440 wide. Have Replay mode ready on a 7:45 to 8:05 AM snapshot before recording.
Time targets are for the video; the live pitch adds 1 minute of "how it works and what's next" at the end.

## 0:00 to 0:20  The problem (talk over slide 2 or the app's header)
"Every KSU commuter knows this one. Last year 1,425 students signed a petition about parking and buses. The Sentinel
quoted a senior saying she has to show up an hour early to find a spot. The Big Owl Bus between campuses gets filled
past capacity, and people get left at the stop. We all leave early and guess. Owl Commute replaces the guess."

## 0:20 to 0:50  The answer: Leave by (live)
Type campus Kennesaw, class 9:30, normal drive 25, click Check my commute.
"One question: when do I leave? It says leave by [read the time], and every minute is explained. My drive. Parking search
time from KSU's own Parking Pulse demand chart for this hour. Walk from the deck. And road delay, only when the cameras
confirm it. Nothing here is a black box: each line says where it came from."

## 0:50 to 1:20  Live bus seats
Scroll to the Big Owl Bus panel. Point at any bus near full.
"This is live. The Big Owl Bus system publishes GPS and the passenger count on every bus, and nobody uses it.
Last night the Kennesaw to Marietta bus showed 29 of 29, full, at 8:51 PM. If you were walking to that stop, you'd
want to know. The leave-by card tells you which bus has seats."

## 1:20 to 2:10  AI at the core: what the cameras see
Scroll to the camera grid, hover a card on the map, click a camera marker to jump to its frame.
"These are the GDOT traffic cameras around campus, Chastain Road, Frey Road, I-75. A vision model reads every frame
every two minutes and writes one plain sentence a student can read. [Read one card aloud.] It is not just counting cars:
last night it caught police lights at Frey and Campus Loop and said avoid the area."

## 2:10 to 3:10  Replay of this morning's rush
Switch Mode to Replay, pick a 7:45 to 8:05 AM snapshot, set class 8:30, click Check.
"Here is this morning at [time]. [Read what the cameras said.] The leave-by card adds [N] minutes for [road], and only
because two frames two minutes apart agreed. One frame can be wrong: a line of cars at a red light is not a traffic jam."

## 3:10 to 3:45  Safeguards and honesty
Show the breakdown lines labeled "estimate" and the "Watching camera" note.
"We measured it. On [N] rush-hour frames I labeled by eye this morning, the model agreed [X]% on whether the road was
slow. Where it is unsure it says so, and it never adds delay from one frame, from a dead camera, or from a camera that
only matters later in the day. Parking and walking minutes are estimates and the card says so."

## 3:45 to 4:00  Close
"All of this is public data KSU already has. Cameras, buses, class demand. Owl Commute just puts it in one answer:
leave by this time, park here, take that bus. Thank you."

## Live pitch add-on (4:00 to 5:00): how it works and what's next
- Stack: FastAPI, one HTML page, Leaflet map, Gemini 3.1 Pro reading GDOT camera frames, Passio GO bus feed, Parking
  Pulse curves measured in pixels from KSU's charts.
- Cost: [calls per day] model calls at the rush-hour schedule, [$ per day] (measured tokens per call, Google list price).
- What KSU would need: host one small server, a data agreement with Passio for the bus feed, and deck counters for
  live parking (we don't have live deck occupancy today; the demand curve is a stand-in).
- Next: push alerts ("your bus is full, next one in 9 min"), per-deck guidance once counters exist, Marietta cameras
  that are currently offline.

## Likely judge questions
- Why not Google Maps? Maps gives drive time. It does not know parking search time at KSU, which bus has seats, or why
  a road is slow. Owl Commute adds those three and shows its reasons.
- How accurate is the vision model? Give the measured number and what it was measured on (N frames, labeled by eye,
  one morning). Say what was not measured: afternoons, rain, Marietta.
- Why not an object detector instead of an LLM? A detector counts cars. We also need "is this a queue or a red light,"
  "are those emergency lights," and a sentence a student can read. A vision language model does all three; the price is
  that it can be wrong, so we confirm on two frames.
- Privacy? Public traffic cameras at 450 by 253 pixels, no plates or faces readable, no student data stored.
- Does it scale to every student? The model reads each camera once per cycle no matter how many users ask. Users cost
  nothing extra; cameras do.
