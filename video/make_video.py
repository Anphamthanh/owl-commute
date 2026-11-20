"""Assemble the demo video (4 min max) from app screenshots, deck slides, and narration.

Narration: OpenAI text to speech (gpt-4o-mini-tts) when OPENAI_API_KEY is set, otherwise macOS `say` as a fallback.
The text follows pitch/SCRIPT.md. To use a human recording instead, drop scene01.wav ... scene11.wav into video/clips/.

Usage: OPENAI_API_KEY=... python3 video/make_video.py        (needs ffmpeg, ffprobe; the openai package for TTS)
Output: video/owl-commute-demo.mp4, 1280x720, H.264 + AAC
"""
import os, subprocess, json
from pathlib import Path

HERE = Path(__file__).parent
IMG, CLIPS = HERE / "img", HERE / "clips"
CLIPS.mkdir(exist_ok=True)
PAD = 0.6  # seconds of silence after each scene
TTS_MODEL, TTS_VOICE = "gpt-4o-mini-tts", "ash"
TTS_STYLE = ("You are a graduate student presenting your own hackathon demo to judges. Speak naturally and warmly at a "
             "relaxed, confident pace, like you are showing a friend something you built. Not a news anchor, not a narrator.")

SCENES = [
    ("slide-1.png",
     "Hi, I'm An Pham. This is Owl Commute: when do I leave, where do I park, and which bus has room?"),
    ("slide-2.png",
     "Every KSU commuter knows this problem. Last year, 1,425 students signed a petition about parking and buses. "
     "The Sentinel quoted a senior who has to show up an hour early just to find a spot. The Big Owl Bus between campuses "
     "gets filled past capacity, and people get left at the stop. So we all leave early and guess. Owl Commute replaces the guess."),
    ("app-live-top.png",
     "Here's the live app. I enter my campus, my class time, and my normal drive, and it answers one question: when do I leave? "
     "And every minute in that answer is explained. My drive. Parking search time, from KSU's own Parking Pulse demand chart for that hour. "
     "The walk from the deck. And road delay, but only when the cameras confirm it. Each line says where it came from, "
     "and the estimates are labeled as estimates."),
    ("app-buses.png",
     "This panel is live too. The Big Owl Bus system publishes the GPS position and the passenger count of every bus, "
     "and nobody uses it. Last night, the Kennesaw to Marietta bus showed 29 of 29 seats, completely full, at 8:51 PM. "
     "If you were walking to that stop, you'd want to know. The leave-by card tells you which bus actually has seats."),
    ("app-map.png",
     "On the map, each bus shows its seats left, and every camera is colored by what the vision model saw in its latest frame. "
     "Click a camera, and you jump straight to its picture."),
    ("app-cams.png",
     "These are the public GDOT traffic cameras around campus: Chastain Road, Frey Road, I-75. A vision language model reads "
     "every frame every two minutes and writes one plain sentence a student can actually read. It's not just counting cars. "
     "Last night it caught police lights at Frey and Campus Loop and said: avoid the area."),
    ("app-replay-cams.png",
     "This is replay mode, playing back this morning's rush at 7:29. The model read the I-75 South camera past Roswell Road as "
     "heavy traffic in the main lanes, with the express lanes flowing well. I checked that frame by eye, and that's exactly what it shows."),
    ("app-replay-top.png",
     "At that moment, a student with an 8:30 class in Marietta gets: leave by 7:40. Twenty-five minutes of driving, ten minutes "
     "for that confirmed I-75 backup, a short parking search, and the walk. Those ten minutes were added only because two frames, "
     "two minutes apart, agreed. One frame can be wrong."),
    ("slide-6.png",
     "We measured it instead of assuming. On twenty rush-hour frames checked by eye this morning, the model agreed twenty out of twenty "
     "on whether a road was slow. But its incident calls in fog and darkness did not hold up: zero of eight were clearly visible. "
     "So the next version turns an incident call into a warning instead of minutes. And the app never adds delay from a single frame, "
     "from a dead camera, or from a camera that only matters later in the day."),
    ("slide-7.png",
     "All of this is public data KSU already has: cameras, buses, class demand. The model costs about twelve dollars a day for both "
     "campuses on a rush-hour schedule, measured from 595 real reads this morning. And users cost nothing extra, because each camera "
     "is read once, no matter how many students ask."),
    ("slide-1.png",
     "Owl Commute puts it all in one answer: leave by this time, park here, take that bus. Thanks for watching."),
]


def run(*cmd):
    subprocess.run(cmd, check=True, capture_output=True)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(json.loads(out)["format"]["duration"])


def synthesize(text, wav: Path):
    if os.environ.get("OPENAI_API_KEY"):
        from openai import OpenAI
        with OpenAI().audio.speech.with_streaming_response.create(
                model=TTS_MODEL, voice=TTS_VOICE, input=text, instructions=TTS_STYLE, response_format="wav") as r:
            r.stream_to_file(wav)
    else:
        aiff = wav.with_suffix(".aiff")
        run("say", "-v", "Samantha", "-r", "175", "-o", str(aiff), text)
        run("ffmpeg", "-y", "-i", str(aiff), str(wav))


def main():
    parts, total = [], 0.0
    for i, (img, text) in enumerate(SCENES, 1):
        wav, clip = CLIPS / f"scene{i:02d}.wav", CLIPS / f"scene{i:02d}.mp4"
        if not wav.exists():
            synthesize(text, wav)
        d = duration(wav) + PAD
        run("ffmpeg", "-y", "-loop", "1", "-framerate", "24", "-i", str(IMG / img), "-i", str(wav), "-t", f"{d:.2f}",
            "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0x0e1116,format=yuv420p",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
            "-shortest", str(clip))
        parts.append(clip)
        total += d
        print(f"scene {i:2d} {img:22s} {d:5.1f}s  (running {total:5.1f}s)")
    lst = CLIPS / "list.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    out = HERE / "owl-commute-demo.mp4"
    run("ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out))
    print(f"wrote {out} total {duration(out):.1f}s (limit 240s)")


if __name__ == "__main__":
    main()
