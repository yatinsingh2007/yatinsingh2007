#!/usr/bin/env python3
"""
Convert scripts/prepped.png into a monochrome ASCII-art SVG that "types"
itself in: each row wipes left-to-right (with a small cursor block riding
the edge), staggered top to bottom. Plays once via CSS keyframes, no loop.
"""
import os

from PIL import Image

RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense); leading space = blank
GRID_COLS = 100
GRID_ROWS = 53
FONT_SIZE = 7
CHAR_W = FONT_SIZE * 0.6   # monospace advance approximation
LINE_H = FONT_SIZE * 1.05
COLOR = "#c9d1d9"          # single light-gray fill -- monochrome on purpose

IN_PATH = os.path.join(os.path.dirname(__file__), "prepped.png")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "avi-ascii.svg")


def image_to_ascii_rows(img: Image.Image):
    img = img.convert("L").resize((GRID_COLS, GRID_ROWS))
    pixels = img.load()
    ramp_len = len(RAMP)

    rows = []
    for y in range(GRID_ROWS):
        chars = []
        for x in range(GRID_COLS):
            brightness = pixels[x, y]  # 0=black .. 255=white
            idx = int((255 - brightness) / 255 * (ramp_len - 1))
            chars.append(RAMP[idx])
        rows.append("".join(chars).rstrip() or " ")
    return rows


def escape_xml(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;"))


def build_svg(rows):
    width = GRID_COLS * CHAR_W + 10
    height = GRID_ROWS * LINE_H + 10

    parts = [
        f'<svg viewBox="0 0 {width:.0f} {height:.0f}" width="{width:.0f}" height="{height:.0f}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="SFMono-Regular, Consolas, Menlo, monospace">'
    ]
    parts.append(f'''
    <style>
      text {{ font-size: {FONT_SIZE}px; fill: {COLOR}; white-space: pre; }}
      .rowclip-rect {{
        animation: wipe 0.35s steps(30, end) forwards;
        transform-box: fill-box;
      }}
      @keyframes wipe {{
        from {{ transform: scaleX(0); }}
        to   {{ transform: scaleX(1); }}
      }}
      .cursor {{
        fill: {COLOR};
        opacity: 0;
        animation: cursor-move 0.35s steps(30, end) forwards;
      }}
      @keyframes cursor-move {{
        0%   {{ opacity: 1; transform: translateX(0); }}
        99%  {{ opacity: 1; }}
        100% {{ opacity: 0; transform: translateX(var(--rowpx)); }}
      }}
    </style>
    ''')

    for i, row_text in enumerate(rows):
        y = 8 + i * LINE_H
        row_px = len(row_text) * CHAR_W
        delay = i * 0.03
        clip_id = f"clip{i}"
        safe_text = escape_xml(row_text)

        parts.append(f'<clipPath id="{clip_id}">')
        parts.append(
            f'  <rect class="rowclip-rect" x="0" y="{y - FONT_SIZE:.1f}" '
            f'width="{row_px:.1f}" height="{LINE_H:.1f}" '
            f'style="transform-origin: left center; animation-delay:{delay:.2f}s" />'
        )
        parts.append('</clipPath>')

        parts.append(f'<g class="rowclip" style="animation-delay:{delay:.2f}s">')
        parts.append(f'  <g clip-path="url(#{clip_id})">')
        parts.append(f'    <text x="5" y="{y:.1f}" xml:space="preserve">{safe_text}</text>')
        parts.append('  </g>')
        parts.append(
            f'  <rect class="cursor" x="0" y="{y - FONT_SIZE:.1f}" width="{CHAR_W:.1f}" '
            f'height="{LINE_H:.1f}" style="--rowpx:{row_px:.1f}px; animation-delay:{delay:.2f}s" />'
        )
        parts.append('</g>')

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    if not os.path.exists(IN_PATH):
        print(f"[make_ascii_svg] {IN_PATH} not found -- run prep_photo.py first.")
        return
    img = Image.open(IN_PATH)
    rows = image_to_ascii_rows(img)
    svg = build_svg(rows)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"[make_ascii_svg] wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
