#!/usr/bin/env python3
"""
Convert scripts/prepped.png into a monochrome ASCII-art portrait that "types"
itself in inside a glowing terminal window: each row wipes left-to-right (with
a small cursor block riding the edge), staggered top to bottom. Plays once via
CSS keyframes, no loop.

Exposes image_to_ascii_rows() so the neofetch info-card can reuse the same
converter for its small logo panel.

Set THEME=light for the light-mode variant used by the README <picture> swap.
"""
import os

from PIL import Image

RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense); leading space = blank

THEME = os.environ.get("THEME", "dark").lower()
_SUFFIX = "" if THEME == "dark" else f"-{THEME}"

GRID_COLS = 88
FONT_SIZE = 7
CHAR_W = FONT_SIZE * 0.6    # monospace advance approximation
LINE_H = FONT_SIZE * 1.05

TITLE = "yatin@github ~ $ render avatar.jpg"

DARK = {
    "ink": "#c9d1d9", "title": "#8b949e",
    "bg_a": "#0d1117", "bg_b": "#161b22", "divider": "#30363d",
    "glow": "rgba(88, 166, 255, 0.28)",
    "border": [("0%", "#58a6ff"), ("50%", "#bc8cff"), ("100%", "#39d353")],
}
LIGHT = {
    "ink": "#24292f", "title": "#57606a",
    "bg_a": "#ffffff", "bg_b": "#f6f8fa", "divider": "#d0d7de",
    "glow": "rgba(9, 105, 218, 0.18)",
    "border": [("0%", "#0969da"), ("50%", "#8250df"), ("100%", "#2d8a56")],
}
PAL = DARK if THEME == "dark" else LIGHT

DOT_COLORS = ["#ff5f56", "#ffbd2e", "#27c93f"]

IN_PATH = os.path.join(os.path.dirname(__file__), "prepped.png")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", f"avi-ascii{_SUFFIX}.svg")


def rows_for_aspect(img: Image.Image, cols: int) -> int:
    """Pick a row count that keeps the portrait un-squished, correcting for the
    fact that monospace character cells are taller than they are wide."""
    w, h = img.size
    return max(1, round(cols * (h / w) * (CHAR_W / LINE_H)))


def image_to_ascii_rows(img: Image.Image, cols: int, rows: int | None = None):
    if rows is None:
        rows = rows_for_aspect(img, cols)
    img = img.convert("L").resize((cols, rows))
    pixels = img.load()
    ramp_len = len(RAMP)

    out = []
    for y in range(rows):
        chars = []
        for x in range(cols):
            brightness = pixels[x, y]           # 0=black .. 255=white
            idx = int((255 - brightness) / 255 * (ramp_len - 1))
            chars.append(RAMP[idx])
        out.append("".join(chars).rstrip() or " ")
    return out


def escape_xml(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;"))


def build_svg(rows):
    grid_w = GRID_COLS * CHAR_W
    grid_h = len(rows) * LINE_H
    pad_x = 22
    top_pad = 42
    bottom_pad = 16
    width = grid_w + pad_x * 2
    height = top_pad + grid_h + bottom_pad

    border_stops = "".join(
        f'<stop offset="{off}" stop-color="{col}" />' for off, col in PAL["border"]
    )

    parts = [
        f'<svg viewBox="0 0 {width:.0f} {height:.0f}" width="{width:.0f}" height="{height:.0f}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="SFMono-Regular, Consolas, Menlo, monospace">'
    ]
    parts.append(f'''
    <style>
      text {{ font-size: {FONT_SIZE}px; fill: {PAL["ink"]}; white-space: pre; }}
      .title {{ font-size: 12px; fill: {PAL["title"]}; font-weight: 600; }}
      .rowclip-rect {{
        animation: wipe 0.35s steps(30, end) forwards;
        transform-box: fill-box;
      }}
      @keyframes wipe {{
        from {{ transform: scaleX(0); }}
        to   {{ transform: scaleX(1); }}
      }}
      .cursor {{
        fill: {PAL["ink"]};
        opacity: 0;
        animation: cursor-move 0.35s steps(30, end) forwards;
      }}
      @keyframes cursor-move {{
        0%   {{ opacity: 1; transform: translateX(0); }}
        99%  {{ opacity: 1; }}
        100% {{ opacity: 0; transform: translateX(var(--rowpx)); }}
      }}
      .dot {{ animation: pulse 2s infinite ease-in-out; }}
      @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
      .glow {{ filter: drop-shadow(0px 0px 8px {PAL["glow"]}); }}
    </style>
    <defs>
      <linearGradient id="aviBg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="{PAL["bg_a"]}" />
        <stop offset="100%" stop-color="{PAL["bg_b"]}" />
      </linearGradient>
      <linearGradient id="aviBorder" x1="0%" y1="0%" x2="100%" y2="0%">
        {border_stops}
      </linearGradient>
    </defs>
    <rect x="1" y="1" width="{width - 2:.0f}" height="{height - 2:.0f}" rx="12" ry="12"
          fill="url(#aviBg)" stroke="url(#aviBorder)" stroke-width="1.5" class="glow" />
    ''')

    # Title bar
    for i, color in enumerate(DOT_COLORS):
        parts.append(f'<circle class="dot" cx="{18 + i * 16}" cy="18" r="5" fill="{color}" />')
    parts.append(f'<text x="{width / 2}" y="22" text-anchor="middle" class="title">{escape_xml(TITLE)}</text>')
    parts.append(f'<line x1="0" y1="32" x2="{width}" y2="32" stroke="{PAL["divider"]}" stroke-width="1" />')

    for i, row_text in enumerate(rows):
        y = top_pad + i * LINE_H
        row_px = len(row_text) * CHAR_W
        delay = i * 0.03
        clip_id = f"clip{i}"
        safe_text = escape_xml(row_text)

        parts.append(f'<clipPath id="{clip_id}">')
        parts.append(
            f'  <rect class="rowclip-rect" x="{pad_x}" y="{y - FONT_SIZE:.1f}" '
            f'width="{row_px:.1f}" height="{LINE_H:.1f}" '
            f'style="transform-origin: {pad_x}px center; animation-delay:{delay:.2f}s" />'
        )
        parts.append('</clipPath>')

        parts.append('<g>')
        parts.append(f'  <g clip-path="url(#{clip_id})">')
        parts.append(f'    <text x="{pad_x}" y="{y:.1f}" xml:space="preserve">{safe_text}</text>')
        parts.append('  </g>')
        parts.append(
            f'  <rect class="cursor" x="{pad_x}" y="{y - FONT_SIZE:.1f}" width="{CHAR_W:.1f}" '
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
    rows = image_to_ascii_rows(img, GRID_COLS)
    svg = build_svg(rows)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"[make_ascii_svg] wrote {OUT_PATH} (theme={THEME}, {GRID_COLS}x{len(rows)})")


if __name__ == "__main__":
    main()
