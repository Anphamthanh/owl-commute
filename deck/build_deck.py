"""Build the Owl Commute pitch deck (deck/Owl Commute.pptx) with python-pptx.

Every number on a slide comes from FACTS below. Fill the Friday-morning values (accuracy, rush frame, call count)
there and rerun: python3 deck/build_deck.py
Values marked TBD render in red so an unfilled placeholder cannot slip into the submitted deck unnoticed.
"""
import json
from pathlib import Path
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

HERE = Path(__file__).parent
IMG = HERE / "img"
FACTS = json.loads((HERE / "facts.json").read_text())

BG, PANEL, TEXT, MUTE, GOLD, RED, GREEN = (RGBColor(0x0e, 0x11, 0x16), RGBColor(0x16, 0x1b, 0x22), RGBColor(0xe6, 0xed, 0xf3),
                                           RGBColor(0x8b, 0x94, 0x9e), RGBColor(0xfd, 0xbb, 0x30), RGBColor(0xf8, 0x51, 0x49),
                                           RGBColor(0x3f, 0xb9, 0x50))
prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def fact(key):
    v = FACTS.get(key)
    return (str(v), False) if v not in (None, "", "TBD") else ("TBD", True)


def slide(title, subtitle=None):
    s = prs.slides.add_slide(BLANK)
    bg = s.background.fill
    bg.solid()
    bg.fore_color.rgb = BG
    tb = s.shapes.add_textbox(Inches(0.6), Inches(0.35), Inches(12.1), Inches(0.9))
    p = tb.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = title
    r.font.size, r.font.bold, r.font.color.rgb, r.font.name = Pt(34), True, GOLD, "Calibri"
    if subtitle:
        p2 = tb.text_frame.add_paragraph()
        r2 = p2.add_run()
        r2.text = subtitle
        r2.font.size, r2.font.color.rgb, r2.font.name = Pt(16), MUTE, "Calibri"
    return s


def bullets(s, items, left=0.6, top=1.5, width=6.3, height=5.4, size=18):
    """items: str, or (str, 'tbd') to render red, or (str, 'src') for a small gray source line."""
    tb = s.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    first = True
    for it in items:
        text, kind = (it, None) if isinstance(it, str) else it
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        r = p.add_run()
        r.text = ("" if kind == "src" else "• ") + text
        r.font.name = "Calibri"
        if kind == "src":
            r.font.size, r.font.color.rgb, r.font.italic = Pt(11), MUTE, True
        elif kind == "tbd":
            r.font.size, r.font.color.rgb, r.font.bold = Pt(size), RED, True
        else:
            r.font.size, r.font.color.rgb = Pt(size), TEXT
        p.space_after = Pt(6)
    return tb


def picture(s, name, left=7.1, top=1.5, width=5.8):
    p = IMG / name
    if p.exists():
        s.shapes.add_picture(str(p), Inches(left), Inches(top), width=Inches(width))
    else:
        tb = s.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(1))
        r = tb.text_frame.paragraphs[0].add_run()
        r.text, r.font.color.rgb, r.font.size = f"[missing image: {name}]", RED, Pt(16)


def note(s, text):
    s.notes_slide.notes_text_frame.text = text


# 1. Title
s = prs.slides.add_slide(BLANK)
s.background.fill.solid()
s.background.fill.fore_color.rgb = BG
tb = s.shapes.add_textbox(Inches(0.8), Inches(2.3), Inches(11.7), Inches(3))
p = tb.text_frame.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
r = p.add_run()
r.text = "Owl Commute"
r.font.size, r.font.bold, r.font.color.rgb, r.font.name = Pt(60), True, GOLD, "Calibri"
for line, size, col in [("When do I leave, where do I park, which bus has room?", 26, TEXT),
                        (FACTS["team_line"], 18, MUTE), ("KSU AI Club Hackathon 2026, AI Club track", 16, MUTE)]:
    p = tb.text_frame.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text, r.font.size, r.font.color.rgb, r.font.name = line, Pt(size), col, "Calibri"
note(s, "0:00. One line: every commuter guesses when to leave. We replace the guess with one sourced answer.")

# 2. Problem
s = slide("The problem: KSU commuters leave early and guess", "Parking, bus crowding, and the I-75 trip between campuses")
bullets(s, [
    "1,425 students signed a petition demanding action on parking, buses, and overcrowding",
    ("Change.org, \"KSU students demand action on parking, buses, and campus overcrowding\"", "src"),
    "\"I have to show up at least an hour before my class or I won't get a parking spot.\"",
    ("The Sentinel, Aug 28, 2025, \"A race to space\" (senior Grace Cauldill)", "src"),
    "\"The Big Owl buses are routinely filled beyond safe capacity, leaving students stranded.\"",
    ("Same petition; KSU added buses and about 600 spaces for Fall 2026 (KSU News, 2026)", "src"),
    "KSU advising: \"give yourself at least an hour to get to the other campus, as slowdowns on 75 are common.\"",
    ("campus.kennesaw.edu, academic advising registration resources", "src"),
    "KSU is a commuter campus: this touches most of the student body, every class day",
], width=12)
note(s, "0:00 to 1:00. Read the senior's quote. These are not our numbers; they are the students' own words and a petition count.")

# 3. What it does
s = slide("What it does: one answer, every minute explained", "Leave by a time. Each line says where it came from.")
bullets(s, [
    "You enter campus, class time, and your normal drive",
    "It returns Leave by, built from four parts:",
    "   your drive, parking search time (KSU Parking Pulse demand for that hour),",
    "   walk from deck to class, and road delay from live cameras",
    "Road delay is added only when two camera frames two minutes apart agree",
    "Which Kennesaw to Marietta bus has seats right now",
    "Replay mode plays back any recorded morning for the demo",
], width=6.2)
picture(s, FACTS.get("leaveby_image", "leaveby-placeholder.png"), width=6.0)
note(s, "1:00 to 2:00. Point at the breakdown. Say the word estimate where the card says estimate.")

# 4. Live bus seats
s = slide("Live bus seats: the feed nobody uses", "Big Owl Bus publishes GPS and passenger count for every bus")
bullets(s, [
    "Passio GO exposes paxLoad and totalCap per bus, no login",
    "Thu Nov 19, 8:51 PM: Kennesaw to Marietta bus #2603 showed 29 of 29, FULL",
    "The app shows seats left per bus on the map and in the leave-by card",
    "Alerting is the obvious next step: \"your bus is full, next one has 26 seats\"",
    ("Source: passio3.com mapGetData.php, system 66, read live during the demo", "src"),
], width=6.2)
picture(s, "bus-seats.png", width=6.0)
note(s, "No other team will have live crowding. Say it plainly.")

# 5. AI at the core
s = slide("AI at the core: a vision model reads the road", "16 GDOT 511 cameras around both campuses, one read every 2 minutes")
bullets(s, [
    "Gemini 3.1 Pro reads each frame and returns congestion, incident, confidence, and one plain sentence",
    "Thu night it caught police lights at Frey Rd and Campus Loop: \"Avoid area if possible\"",
    (f"Fri Nov 20 rush frame: {FACTS.get('rush_caption', 'TBD')}", "tbd" if fact("rush_caption")[1] else None),
    "The sentence is what a student reads; the structured fields drive the leave-by math",
    "A car counter cannot tell a red-light queue from a jam, or see emergency lights. A vision language model can",
], width=6.2)
picture(s, "cam-frey-police.png", left=7.1, top=1.5, width=5.8)
picture(s, FACTS.get("rush_image", "rush-frame.png"), left=7.1, top=4.4, width=5.8)
note(s, "2:00 to 4:00 is the demo. This slide backs it up if the live feed fails.")

# 6. Accuracy and safeguards
acc, acc_tbd = fact("accuracy_line")
s = slide("Accuracy and safeguards: the model can be wrong, so we check it", "Measured, not assumed")
bullets(s, [
    (acc, "tbd" if acc_tbd else None),
    ("Labeled by eye on Fri Nov 20 morning frames, then scored against the model's reads (data/labels.json)", "src"),
    "Two-frame confirmation: no delay is added from a single frame",
    "90-minute rule: cameras only count when you are leaving within 90 minutes",
    "Worst camera per road only, so overlapping cameras do not stack the same jam",
    "Dead cameras detected by file size and skipped (3 Marietta cameras were offline this week)",
    "Gemini 3 Flash called a glare-smeared empty I-75 frame \"free flow, 0.9 confidence\"; Pro said \"unclear\". We use Pro",
    "Confidence below 0.6 is ignored",
], width=12, size=17)
note(s, "Give the number, then the N. Say what was not measured: afternoons, rain, Marietta.")

# 7. Feasibility
cost, cost_tbd = fact("cost_line")
s = slide("Feasibility: KSU could run this next semester", "All inputs are public today")
bullets(s, [
    "Data: GDOT 511 camera frames, Passio GO bus feed, KSU Parking Pulse charts. No scraping behind logins, no student data",
    (cost, "tbd" if cost_tbd else None),
    ("Tokens per call measured from the app's own counter; price from Google's published list price", "src"),
    "Rush-hour schedule (6:30 to 10:30 AM and 3:30 to 6:30 PM) cuts the bill to about a third of all-day reading",
    "To adopt: one small server, a data agreement with Passio, and deck counters for live parking",
    "Users cost nothing extra: each camera is read once per cycle no matter how many students ask",
], width=12, size=17)
note(s, "Cost is from measured tokens times list price. If asked about Flash: cheaper, but it failed the glare test.")

# 8. Limitations
s = slide("Limitations: what this is not", "Said on the card, said here")
bullets(s, [
    "Parking search, walk, and delay minutes are estimates from a simple formula, not measurements",
    "No live parking deck occupancy exists publicly; Parking Pulse class demand is a stand-in",
    "Fri, Sat, Sun have no Parking Pulse chart; the app uses the Mon/Wed chart and labels it as an assumption",
    "Some Marietta cameras are offline; coverage there is thinner",
    "Night, fog, and glare lower the model's confidence; it says unknown rather than guessing",
    "Accuracy was measured on one morning, by one labeler",
], width=12)
note(s, "Judges trust a team that names its limits before they do.")

# 9. Tools and data sources
s = slide("Tools and data sources")
bullets(s, [
    "Vision model: Gemini 3.1 Pro (google-genai SDK), structured JSON output",
    "Backend: FastAPI, httpx. Frontend: one HTML page, Leaflet map, OpenStreetMap tiles",
    "Cameras: GDOT 511 Georgia, https://511ga.org (camera list and still frames)",
    "Buses: Passio GO (Big Owl Bus system 66), live GPS and passenger counts",
    "Parking demand: KSU Parking Pulse charts, bar heights measured in pixels",
    "Evidence: The Sentinel (KSU), Change.org petition, KSU News, KSU advising pages",
    "Code: " + FACTS.get("repo_url", "TBD"),
], width=12)
note(s, "Q and A prep is in pitch/SCRIPT.md.")

out = HERE / "Owl Commute.pptx"
prs.save(out)
print("saved", out, "slides:", len(prs.slides))
