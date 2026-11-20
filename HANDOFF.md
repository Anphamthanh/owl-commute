# Owl Commute: handoff notes (updated Thu Nov 19, 2026, 9:40 PM)

## Event facts (from the organizers' Discord, opening slides, and the submission form, read Nov 19)
- Brief: "Use AI to solve problems on campus." KSU AI Club Hackathon 2026, Mon Nov 16 to Fri Nov 20.
- Submission: one Google Form for all tracks, due Fri Nov 20, 12:00 PM. A separate announcement says do not change
  the PowerPoint or video after 10:00 AM, and an edit after the deadline disqualifies the team. **Treat 10:00 AM as
  the hard lock.** An submits the form himself.
- Form fields: team name, each member's full name and school email, contact email, tracks entered, whether the
  project was built with itcan.do, and three links: (1) PowerPoint as .pptx or PDF on Google Drive or OneDrive shared
  "Anyone with the link can edit" (judges read edit history), (2) demo video, 4 minutes max, "Anyone with the link can
  view", (3) GitHub repo viewable by anyone. Only page 1 of 6 of the form has been read.
- Judges pick presenters from the submissions. Presentations Fri 5:30 to 8:30 PM, ETC Q 104, Marietta campus, in
  person, 5 minutes per team, laptop on the projector. Video required even with a live demo.
- Tracks: AI Club ($800 first, $200 second, main target). itcan.do ($800, must use itcan.do). Nudox ($900, most
  organized codebase, judged from the repo and commit history, requires the Nudox tool and an account screenshot).
  IEEE CS is games only, do not enter.
- AI Club rubric /100: campus impact 25 (real data), use of AI 25 (AI is the core), feasibility 20, creativity 15, pitch 15.
- Suggested timing: 0 to 1 problem, 1 to 2 solution, 2 to 4 demo, 4 to 5 how it works and next.
- The organizers' own example is a parking app counting spots from camera footage, so lead with leave-by and live bus
  crowding; parking is one input.

## Facts the KSU OneDrive test showed (Nov 19, 9:25 PM)
- KSU's tenant **refuses anonymous edit links** (CreateAnonymousLink isEditLink=true returns "Operation is not valid").
  Anonymous view links and organization edit links work. So the "Anyone with the link can edit" deck link must come
  from Google Drive (An's Google account), or we submit a OneDrive view link and say why.

## State of the code (all verified by running)
- server.py reads GOOGLE_API_KEY from the environment only. Model calls are counted at /api/stats.
- Replay never calls the model: /api/snapshots lists only pre-read snapshots, and a strict test (live loop off,
  replay of every snapshot plus advice plus labeling) left model_calls at 0.
- advice(): class day rolls to tomorrow when the time has passed and the demand curve follows the class day; Fri/Sat/Sun
  use the Mon/Wed chart and the card says "no Fri chart published, Mon/Wed chart assumed".
- Labeling: /label page, /api/label/frames (every flagged frame plus a random fill to 30), /api/label (save),
  /api/label/score (exact, slow-vs-not, incident agreement).
- Git: local repo on main with small commits. No GitHub remote yet (needs An's OK and a name).

## Friday schedule (MacBook)
- record.sh runs until 6:30 PM (every 2 min 6:30 to 10:30 AM and 3:30 to 6:30 PM, else every 15 min). caffeinate keeps
  the MacBook awake until 10:30 AM. iCloud sync copies data/ to iCloud Drive/owl-commute every 10 min until 10:45 AM.
- 8:15 AM: run_precompute_at_815.sh pre-reads 6:15 to 8:10 AM snapshots, writes rush_summary.txt and precompute.log.
- 8:20 AM: An labels about 30 frames at http://localhost:8000/label (server must be running). Score goes on slide 6.
- 8:30 AM: record the video from pitch/SCRIPT.md.
- 9:15 AM: fill deck/facts.json (accuracy_line, cost_line from pitch/cost.py, rush image and caption, repo_url),
  rebuild the deck, upload, set sharing, test the links in a private window.
- 9:45 AM: hand An the three links and the unfinished list. 10:00 AM hard lock.

## Rules
- Never submit the form, post in Discord, or message anyone on An's behalf.
- No invented numbers. Every figure is measured here or cited. Never claim live parking deck occupancy.
- Never print or commit API keys. American English. No em dashes or double dashes anywhere.
- No Co-Authored-By or "Generated with" lines in commit messages.
- Ask An before anything public or hard to undo (creating the GitHub repo, uploading).

## Friday 8:40 AM status
- Pre-read done: 46 snapshots (6:15 to 8:10 AM), 595 model calls, 406 s. rush_summary.txt lists 48 flagged frames.
- Spot check (pitch/spot-check.md): congestion slow vs not slow 20/20, exact 18/20; incident calls 0/8 verifiable in fog
  or dark. Labeled by the assistant, so stated that way on slide 6. The Frey Rd "crash" 7:37 to 7:50 AM is unverifiable.
- Deck rebuilt with Friday numbers: deck/Owl Commute.pptx (copy in ~/Downloads). Cost line measured on 595 reads.
- Fallback video built: video/owl-commute-demo.mp4, 3:09, real screenshots, synthetic narration (macOS Samantha) from
  video/make_video.py. Copy in ~/Downloads. If An records his own voice, drop per-scene .aiff files into video/clips and rerun.
- Nudox: account, key, index, README section, session log all done Thu night. Screenshot in ~/Downloads.
- Still needed from An: upload deck to Google Drive (Anyone with the link: Editor), upload video (Anyone with the link: view),
  fill the form. Hard lock 10:00 AM.
