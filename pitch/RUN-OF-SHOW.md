# Owl Commute: 5-minute presentation (Fri Nov 20, 2026, ETC Q 104)

Tracks entered: **AI Club** and **Nudox**. Say both in the first 15 seconds.

## 1. What is on the laptop

Two windows, nothing else open:

| Window | File or address | Used for |
|---|---|---|
| **Preview** | `~/Downloads/Owl Commute - present.pdf` (5 pages: title, problem, accuracy, feasibility, tools) | The talking parts |
| **Browser** | http://localhost:8000, two tabs | The demo |

Browser tabs:
- **Tab 1, Live:** campus Marietta, class time about 60 minutes ahead, drive 25, Check my commute clicked.
- **Tab 2, Replay:** Mode Replay, snapshot Fri 7:29 AM, campus Marietta, class 08:30, Check my commute clicked.

Keys you will press, in order: `Cmd+Ctrl+F` once (Preview full screen), then `→` for the next page, `Cmd+Tab` to swap
Preview and the browser, `Cmd+1` and `Cmd+2` for the two browser tabs. Nothing else.

## 2. Before they call your name

1. Mirror the display (not extend). Browser zoom 125%.
2. Preview on page 1, full screen (`Cmd+Ctrl+F`).
3. Browser on Tab 1 (Live). Re-click Check my commute so the card is fresh.
4. Glance at the bus panel: note which buses say FULL.
5. Glance at the top camera card: you will read it aloud.
6. Glance at the card: does it have a "Traffic on ..." line? Either way is fine; Replay carries the delay example.
7. `Cmd+Tab` to Preview so you start on page 1.

## 3. The talk, step by step

**0:00  PREVIEW page 1 (title)**
Hi, I'm An Pham, a computer science master's student. My project is Owl Commute, and I'm entering it in two tracks: the AI Club track and the Nudox track.

**0:15  press `→`  PREVIEW page 2 (the problem)**
Every commuter in this room knows the problem. Last year 1,425 students signed a petition about parking and buses. The Sentinel quoted a senior who shows up an hour early just to find a spot. The bus between campuses fills up and leaves people at the stop. So we all leave early and guess. Owl Commute replaces the guess.

**1:00  `Cmd+Tab`  BROWSER, Tab 1 (Live)**
Look at the bus panel right now: (point) these buses say FULL, live, at (read the time).

One question: when do I leave? I typed my campus, my class time, and my normal drive. It says leave by (read the time), and every minute is explained. My drive. Finding parking, from KSU's own demand chart for that hour. The walk from the deck. And road delay, but only when the cameras confirm it. The estimates say estimate. Nothing here is a black box.

**1:50  scroll down to the camera grid**
These are the public GDOT traffic cameras around both campuses, sixteen of them. An AI reads every picture every two minutes and writes one sentence a student can read. (Read the top card aloud.) It's not counting cars; it's telling you what's happening. (Scroll up, click one camera marker on the map.) Click a camera on the map and you jump to its picture.

**2:45  `Cmd+2`  BROWSER, Tab 2 (Replay, Fri 7:29 AM)**
Right now the roads are easy, so let me play back this morning's rush. 7:29 AM. The model read the I-75 South camera as heavy traffic in the main lanes with the express lanes flowing. I checked that frame by eye; that is exactly what it shows. The card added ten minutes, and only because two frames, two minutes apart, agreed. One frame can be wrong, so one frame is never enough.

**3:30  `Cmd+Tab`, then `→`  PREVIEW page 3 (accuracy and safeguards)**
Because the AI can be wrong, I measured it instead of assuming. Twenty rush-hour frames checked by eye this morning: twenty of twenty on whether a road was slow. Its crash calls in fog were wrong, zero of eight, so the next version turns those into a warning instead of minutes. The limits are on this slide and in the repo.

**4:05  press `→`  PREVIEW page 4 (feasibility)**
How KSU could run this: every input is public. Camera frames from GDOT, live seat counts from the Big Owl Bus system, KSU's own Parking Pulse chart. The model costs about twelve dollars a day for both campuses, measured from 595 real reads. Users cost nothing extra, because each camera is read once no matter how many students ask. It's one small server. The missing piece is live deck counters; when KSU adds them, the parking estimate becomes a measurement.

**4:40  press `→`  PREVIEW page 5 (tools and code)**
For the Nudox track: the code is public, twenty small commits, one change each, and the README says where to start.

Owl Commute: leave by this time, park here, take that bus. Thank you.

**Stop on page 5. Wait for questions.** `Cmd+Tab` back to the browser only if a question needs the app.

## 4. If something goes wrong

| Problem | Do this |
|---|---|
| Live card has no camera line | Normal at quiet times. Say "the roads are easy right now" and let Tab 2 carry the delay example. |
| No bus says FULL | Say "earlier tonight three buses were full: 2603, 2616, 2604." |
| Wi-Fi drops | Replay works offline (map tiles go gray). Do the whole demo from Tab 2. |
| Page won't load | Terminal: `cd ~/projects/ksu/hackathon && .venv/bin/uvicorn server:app --port 8000` (key must be in the environment). |
| Projector shows nothing after Cmd+Tab | The display is set to extend, not mirror. System Settings, Displays, Mirror. |
| Cut to 3 minutes | Skip the map click, and shorten page 3 to one sentence: "twenty of twenty on slow versus not slow, and the slide says where it was wrong." |
| Asked to see a failure | Tab 2: snapshot Fri 7:39 AM, Kennesaw, class 08:30, Check. The Frey Rd "crash" in fog. Say "this is the one I flagged on the slide." |

## 5. Questions and answers

- **Why not Google Maps?** Maps gives drive time. It doesn't know parking search time at KSU, which bus has seats, or why a road is slow. Owl Commute adds those three and shows its reasons.
- **How accurate is the AI?** Twenty frames from one morning, checked by eye: 20 of 20 on slow vs not slow, 18 of 20 on the exact level, 0 of 8 incident calls verifiable in fog. Not tested: afternoons, rain, the Marietta-side cameras (three were offline all week).
- **Why a language model instead of a car counter?** A counter can't tell a red-light queue from a jam, can't see emergency lights, and can't write the sentence. The cost is that it can be wrong, which is why two frames must agree and low-confidence reads are ignored.
- **Privacy?** Public traffic cameras at 450 by 253 pixels; no plates or faces readable; no student data stored.
- **Does it scale?** Each camera is read once per cycle no matter how many students ask. Users are free; a camera read costs $0.0043.
- **What does it cost KSU?** About $12 a day on the rush-hour schedule, about $40 all day, from measured tokens and Google's list price.
- **What's next?** Push alerts ("your bus is full, next one in 9 minutes"), incident calls as warnings, live deck counts, fix the offline Marietta cameras.
- **The GitHub link?** It was public the whole time and opens now; the code also went to the organizers as a zip.
- **Did you build it alone?** Yes, solo, this week, with AI coding tools. The design, the data sources, the safeguards, and the accuracy check are mine.

## 6. Facts and where they come from

| Fact | Source |
|---|---|
| 1,425 signatures | Change.org, "KSU Students Demand Action on Parking, Buses, and Campus Overcrowding!", started Aug 28, 2025; count checked today |
| "I have to show up at least an hour before my class or I won't get a parking spot." | The Sentinel, Aug 28, 2025, "A race to space" |
| "The Big Owl buses are routinely filled beyond safe capacity, leaving students stranded." | Same petition page |
| "give yourself at least an hour to get to the other campus" | KSU academic advising registration page |
| 16 cameras, read every 2 minutes | cams.json; GDOT 511 still frames |
| Live seats on 11 to 16 buses | Passio GO feed, Big Owl Bus system 66 |
| Parking demand by hour | KSU Parking Pulse charts, bar heights measured in pixels |
| 20 of 20, 18 of 20, 0 of 8 | pitch/spot-check.md, Fri Nov 20 morning frames |
| $0.0043 per read, $12/day, 595 reads | pitch/cost.py; Gemini 3.1 Pro list price |
| 20 commits | git log on Anphamthanh/owl-commute |
