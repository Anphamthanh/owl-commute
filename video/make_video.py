"""Assemble the 4-minute demo video from app screenshots, deck slides, and narration.

Narration is synthesized with macOS `say` (voice Samantha) from the text below, which follows pitch/SCRIPT.md.
If the author records his own voice instead, replace the per-scene .aiff files in video/clips/ and rerun.

Usage: python3 video/make_video.py        (needs ffmpeg, ffprobe, say)
Output: video/owl-commute-demo.mp4, 1280x720, H.264 + AAC
"""
import subprocess, json
from pathlib import Path

HERE = Path(__file__).parent
IMG, CLIPS = HERE / "img", HERE / "clips"
CLIPS.mkdir(exist_ok=True)
VOICE = "Samantha"
PAD = 0.7  # seconds of silence after each scene

SCENES = [
    ("slide-1.png",
     "Owl Commute. When do I leave, where do I park, which bus has room? A hackathon project by An Pham, "
     "a computer science graduate student at Kennesaw State."),
    ("slide-2.png",
     "Every K S U commuter knows this problem. Last year, one thousand four hundred twenty five students signed a petition "
     "about parking and buses. The Sentinel quoted a senior who has to show up an hour early to find a spot. "
     "The Big Owl Bus between campuses gets filled past capacity, and people get left at the stop. "
     "So we all leave early and guess. Owl Commute replaces the guess."),
    ("app-live-top.png",
     "This is the live app. I enter my campus, my class time, and my normal drive, and it answers one question: "
     "when do I leave? Every minute in that answer is explained. My drive. Parking search time, from K S U's own "
     "Parking Pulse demand chart for that hour. The walk from the deck. And road delay, only when the cameras confirm it. "
     "Each line says where it came from, and the estimates are labeled as estimates."),
    ("app-buses.png",
     "This panel is live too. The Big Owl Bus system publishes the G P S position and the passenger count of every bus, "
     "and nobody uses it. Last night the Kennesaw to Marietta bus showed twenty nine of twenty nine seats, completely full, "
     "at eight fifty one P M. If you were walking to that stop, you would want to know. The leave by card tells you which "
     "bus has seats."),
    ("app-map.png",
     "On the map, buses show seats left, and every camera is colored by what the vision model saw in its latest frame. "
     "Click a camera and you jump to its picture."),
    ("app-cams.png",
     "These are the public G DOT traffic cameras around campus: Chastain Road, Frey Road, I 75. "
     "A vision language model reads every frame every two minutes and writes one plain sentence a student can read. "
     "It is not just counting cars. Last night it caught police lights at Frey and Campus Loop and said: avoid the area."),
    ("app-replay-cams.png",
     "Here is replay mode, playing back this morning's rush at seven twenty nine. The model read the I 75 South camera past "
     "Roswell Road as heavy traffic in the main lanes, with the express lanes flowing well. I checked that frame by eye, "
     "and that is exactly what it shows."),
    ("app-replay-top.png",
     "At that moment, a student with an eight thirty class in Marietta gets: leave by seven forty. Twenty five minutes of "
     "driving, ten minutes for that confirmed I 75 backup, a short parking search, and the walk. "
     "The ten minutes were added only because two frames two minutes apart agreed. One frame can be wrong."),
    ("slide-6.png",
     "We measured it instead of assuming. On twenty rush hour frames checked by eye this morning, the model agreed "
     "twenty out of twenty on whether a road was slow. Its incident calls in fog and darkness did not hold up: "
     "zero of eight were clearly visible. So the next version turns an incident call into a warning, not minutes. "
     "The app never adds delay from a single frame, from a dead camera, or from a camera that only matters later in the day."),
    ("slide-7.png",
     "All of this is public data K S U already has. Cameras, buses, class demand. The model costs about twelve dollars a "
     "day for both campuses on a rush hour schedule, measured from five hundred ninety five real reads this morning. "
     "Users cost nothing extra, because each camera is read once no matter how many students ask."),
    ("slide-1.png",
     "Owl Commute puts it in one answer: leave by this time, park here, take that bus. Thank you."),
]


def run(*cmd):
    subprocess.run(cmd, check=True, capture_output=True)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(json.loads(out)["format"]["duration"])


def main():
    parts, total = [], 0.0
    for i, (img, text) in enumerate(SCENES, 1):
        aiff, clip = CLIPS / f"scene{i:02d}.aiff", CLIPS / f"scene{i:02d}.mp4"
        if not aiff.exists():
            run("say", "-v", VOICE, "-r", "175", "-o", str(aiff), text)
        d = duration(aiff) + PAD
        run("ffmpeg", "-y", "-loop", "1", "-framerate", "24", "-i", str(IMG / img), "-i", str(aiff),
            "-t", f"{d:.2f}", "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0x0e1116,format=yuv420p",
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
