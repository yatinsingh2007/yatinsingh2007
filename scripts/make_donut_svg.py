#!/usr/bin/env python3
"""
Generates terminal-donut.svg: an animated spinning 3D ASCII Donut inside a
glowing dark-mode terminal window using pure CSS keyframes.

Each character is now shaded by the donut's *surface luminance* (the same
Lambertian term the classic donut.c computes) and mapped onto a glowing
green -> cyan -> white-hot ramp, so the torus reads as a genuinely lit 3D
object with a bright core instead of a flat green silhouette.

Set THEME=light to emit the light-mode palette (used for the <picture>
prefers-color-scheme variant in the README).
"""
import math
import os

THEME = os.environ.get("THEME", "dark").lower()
_SUFFIX = "" if THEME == "dark" else f"-{THEME}"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", f"terminal-donut{_SUFFIX}.svg")

NUM_FRAMES = 24
WIDTH_CHARS = 44
HEIGHT_CHARS = 22
FONT_SIZE = 11
CHAR_W = FONT_SIZE * 0.6
LINE_H = FONT_SIZE * 1.15

SVG_W = 380
SVG_H = 340
TOP_PAD = 45

TITLE = "yatin@github ~ $ ./donut.c"

# Luminance ramp: darkest (back-lit) -> brightest (facing the light).
# Deep teal climbs through GitHub-green into cyan and finally a white-hot core.
DARK = {
    "bg_a": "#0d1117",
    "bg_b": "#161b22",
    "title": "#8b949e",
    "divider": "#30363d",
    "ramp": ["#0b3d2e", "#0e6b3f", "#1a9850", "#39d353",
             "#4ae08a", "#56d4dd", "#a5f3fc", "#eafcff"],
    "glow": "rgba(57, 211, 83, 0.35)",
    "border": [("0%", "#39d353"), ("50%", "#58a6ff"), ("100%", "#bc8cff")],
}
LIGHT = {
    "bg_a": "#ffffff",
    "bg_b": "#f6f8fa",
    "title": "#57606a",
    "divider": "#d0d7de",
    "ramp": ["#b7e4c7", "#74c69d", "#40916c", "#2d8a56",
             "#1a936f", "#0f8a8a", "#0a7ea4", "#054a63"],
    "glow": "rgba(45, 138, 86, 0.28)",
    "border": [("0%", "#2d8a56"), ("50%", "#0a7ea4"), ("100%", "#8250df")],
}
PAL = DARK if THEME == "dark" else LIGHT

CHARS = ".,-~:;=!*#$@"       # sparse (dim) -> dense (bright)
DOT_COLORS = ["#ff5f56", "#ffbd2e", "#27c93f"]


def render_donut_frame(A, B):
    """Return (char_rows, color_rows): the ASCII glyphs and, per glyph, an
    index into PAL['ramp'] derived from that point's surface luminance."""
    z = [0.0] * (WIDTH_CHARS * HEIGHT_CHARS)
    b = [' '] * (WIDTH_CHARS * HEIGHT_CHARS)
    c = [-1] * (WIDTH_CHARS * HEIGHT_CHARS)

    cosA, sinA = math.cos(A), math.sin(A)
    cosB, sinB = math.cos(B), math.sin(B)

    R1 = 1
    R2 = 2
    K2 = 5
    K1 = WIDTH_CHARS * K2 * 3 / (8 * (R1 + R2))

    n_ramp = len(PAL["ramp"])

    theta = 0.0
    while theta < 2 * math.pi:
        costheta = math.cos(theta)
        sintheta = math.sin(theta)

        phi = 0.0
        while phi < 2 * math.pi:
            cosphi = math.cos(phi)
            sinphi = math.sin(phi)

            circleX = R2 + R1 * costheta
            circleY = R1 * sintheta

            x = circleX * (cosB * cosphi + sinA * sinB * sinphi) - circleY * cosA * sinB
            y = circleX * (sinB * cosphi - sinA * cosB * sinphi) + circleY * cosA * cosB
            z_val = K2 + cosA * circleX * sinphi + circleY * sinA
            ooz = 1 / z_val

            xp = int(WIDTH_CHARS / 2 + K1 * ooz * x)
            yp = int(HEIGHT_CHARS / 2 - K1 * ooz * y * 0.55)

            L = (cosphi * costheta * sinB - cosA * costheta * sinphi -
                 sinA * sintheta + cosB * (cosA * sintheta - costheta * sinA * sinphi))

            if 0 <= xp < WIDTH_CHARS and 0 <= yp < HEIGHT_CHARS:
                idx = xp + yp * WIDTH_CHARS
                if ooz > z[idx]:
                    z[idx] = ooz
                    luminance_idx = int(L * 8)
                    if luminance_idx > 0:
                        b[idx] = CHARS[min(luminance_idx, len(CHARS) - 1)]
                    else:
                        luminance_idx = 0
                        b[idx] = "."
                    # Map 0..11 glyph brightness onto the colour ramp.
                    c[idx] = min(n_ramp - 1, luminance_idx * n_ramp // len(CHARS))

            phi += 0.07
        theta += 0.07

    char_rows, color_rows = [], []
    for j in range(HEIGHT_CHARS):
        s = j * WIDTH_CHARS
        char_rows.append("".join(b[s:s + WIDTH_CHARS]))
        color_rows.append(c[s:s + WIDTH_CHARS])
    return char_rows, color_rows


def escape_xml(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


def row_to_tspans(chars, colors):
    """Group a row into <tspan> runs of a single ramp colour. Spaces inherit
    the current run so blank gaps don't shatter it into tiny elements."""
    ramp = PAL["ramp"]
    spans = []
    buf = []
    cur = None
    for ch, col in zip(chars, colors):
        if ch == " ":
            buf.append(ch)
            continue
        col = col if col >= 0 else 0
        if buf and col != cur and cur is not None:
            spans.append((cur, "".join(buf)))
            buf = []
        cur = col
        buf.append(ch)
    if buf:
        spans.append((cur if cur is not None else 0, "".join(buf)))
    return "".join(
        f'<tspan fill="{ramp[col]}">{escape_xml(text)}</tspan>'
        for col, text in spans
    )


def build_svg():
    frames_data = []
    for i in range(NUM_FRAMES):
        A = i * (2 * math.pi / NUM_FRAMES)
        B = i * (math.pi / NUM_FRAMES)
        frames_data.append(render_donut_frame(A, B))

    cycle_dur = 2.4  # seconds for full 360 loop
    pct_visible = 100.0 / NUM_FRAMES

    parts = [
        f'<svg viewBox="0 0 {SVG_W} {SVG_H}" width="{SVG_W}" height="{SVG_H}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="SFMono-Regular, Consolas, Menlo, monospace">'
    ]

    border_stops = "".join(
        f'<stop offset="{off}" stop-color="{col}" />' for off, col in PAL["border"]
    )

    parts.append(f'''
    <style>
      .title {{ fill: {PAL["title"]}; font-size: 12px; font-weight: 600; }}
      .donut-text {{ font-size: {FONT_SIZE}px; white-space: pre; font-weight: bold; }}
      .frame {{ opacity: 0; animation: anim-frame {cycle_dur:.2f}s infinite; }}
      @keyframes anim-frame {{
        0% {{ opacity: 1; }}
        {pct_visible:.2f}% {{ opacity: 1; }}
        {pct_visible + 0.01:.2f}% {{ opacity: 0; }}
        100% {{ opacity: 0; }}
      }}
      .dot {{ animation: pulse 2s infinite ease-in-out; }}
      @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
      .glow {{ filter: drop-shadow(0px 0px 8px {PAL["glow"]}); }}
      .donut-group {{ filter: url(#bloom); }}
    </style>
    <defs>
      <linearGradient id="donutBg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="{PAL["bg_a"]}" />
        <stop offset="100%" stop-color="{PAL["bg_b"]}" />
      </linearGradient>
      <linearGradient id="donutBorder" x1="0%" y1="0%" x2="100%" y2="0%">
        {border_stops}
      </linearGradient>
      <radialGradient id="coreGlow" cx="50%" cy="52%" r="42%">
        <stop offset="0%" stop-color="{PAL["glow"]}" />
        <stop offset="100%" stop-color="{PAL["glow"].replace('0.35', '0').replace('0.28', '0')}" />
      </radialGradient>
      <filter id="bloom" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur in="SourceGraphic" stdDeviation="0.6" result="soft" />
        <feMerge>
          <feMergeNode in="soft" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
    </defs>

    <rect x="1" y="1" width="{SVG_W - 2}" height="{SVG_H - 2}" rx="12" ry="12"
          fill="url(#donutBg)" stroke="url(#donutBorder)" stroke-width="1.5" class="glow" />
    <ellipse cx="{SVG_W / 2}" cy="{TOP_PAD + HEIGHT_CHARS * LINE_H / 2}" rx="150" ry="110"
             fill="url(#coreGlow)" />
    ''')

    # Title bar
    for i, color in enumerate(DOT_COLORS):
        parts.append(f'<circle class="dot" cx="{18 + i * 16}" cy="18" r="5" fill="{color}" />')
    parts.append(f'<text x="{SVG_W / 2}" y="22" text-anchor="middle" class="title">{escape_xml(TITLE)}</text>')
    parts.append(f'<line x1="0" y1="34" x2="{SVG_W}" y2="34" stroke="{PAL["divider"]}" stroke-width="1" />')

    # Render each frame
    for f_idx, (char_rows, color_rows) in enumerate(frames_data):
        delay = f_idx * (cycle_dur / NUM_FRAMES)
        parts.append(f'<g class="frame donut-group" style="animation-delay: {delay:.3f}s;">')
        for r_idx, (chars, colors) in enumerate(zip(char_rows, color_rows)):
            y_pos = TOP_PAD + r_idx * LINE_H
            spans = row_to_tspans(chars, colors)
            if not spans:
                continue
            parts.append(
                f'  <text x="24" y="{y_pos:.1f}" class="donut-text" xml:space="preserve">{spans}</text>'
            )
        parts.append('</g>')

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    svg = build_svg()
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"[make_donut_svg] wrote {OUT_PATH} (theme={THEME})")


if __name__ == "__main__":
    main()
