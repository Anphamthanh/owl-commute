"""Turn KSU's Parking Pulse chart images into numbers.

KSU publishes four bar charts (Mon/Wed and Tue/Thu, for each campus) of hourly class demand with no y axis,
so the only honest reading is relative: each bar divided by the tallest bar of its chart. Bar heights are
measured in pixels (saturated columns above the baseline), not estimated by a model.

Usage: python3 pulse/extract_demand.py   (reads pulse/*.jpg, writes pulse/demand.json)
Source: https://campus.kennesaw.edu/offices-services/parking/parking-information/parking-pulse.php
"""
import colorsys, json
from pathlib import Path
from PIL import Image

HERE = Path(__file__).parent
CHARTS = {"MW-kennesaw": "monday-and-wednesday-kennesaw.jpg", "TR-kennesaw": "tuesday-and-thursday-kennesaw.jpg",
          "MW-marietta": "monday-and-wednesday-marietta.jpg", "TR-marietta": "tuesday-and-thursday-marietta.jpg"}
HOURS = list(range(8, 20))  # the charts run 8 a.m. to 7 p.m.
SAT = 0.4                   # bars are saturated colors; background and gridlines are not


def bar_heights(path: Path) -> list:
    im = Image.open(path).convert("RGB")
    w, h = im.size

    def saturated(x, y):
        r, g, b = (v / 255 for v in im.getpixel((x, y)))
        return colorsys.rgb_to_hsv(r, g, b)[1] > SAT

    base = next(y for y in range(h - 1, 0, -1) if sum(saturated(x, y) for x in range(0, w, 4)) > w / 12)
    cols = [saturated(x, base - 3) for x in range(w)]
    bars, x = [], 0
    while x < w:
        if cols[x]:
            start = x
            while x < w and cols[x]:
                x += 1
            if x - start > 30:
                bars.append((start, x))
        x += 1
    heights = []
    for start, end in bars:
        c, y = (start + end) // 2, 0
        while y < base and not saturated(c, y):
            y += 1
        heights.append(base - y)
    return heights


def main():
    out = {}
    for key, name in CHARTS.items():
        hs = bar_heights(HERE / name)
        if len(hs) != len(HOURS):
            raise SystemExit(f"{name}: found {len(hs)} bars, expected {len(HOURS)}")
        top = max(hs)
        out[key] = {str(hr): round(v / top, 2) for hr, v in zip(HOURS, hs)}
    (HERE / "demand.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
