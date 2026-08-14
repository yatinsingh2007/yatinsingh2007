#!/usr/bin/env python3
"""
Generates terminal-donut.svg: an animated spinning 3D ASCII Donut inside a
glowing dark-mode terminal window using pure CSS keyframes.
"""
import math
import os

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "terminal-donut.svg")
OUT_PATH_AVI = os.path.join(os.path.dirname(__file__), "..", "avi-ascii.svg")

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
KEY_COLOR = "#58a6ff"
DONUT_COLOR = "#39d353"
BG = "#0d1117"
BORDER = "#30363d"
DOT_COLORS = ["#ff5f56", "#ffbd2e", "#27c93f"]


def render_donut_frame(A, B):
    z = [0.0] * (WIDTH_CHARS * HEIGHT_CHARS)
    b = [' '] * (WIDTH_CHARS * HEIGHT_CHARS)

    cosA, sinA = math.cos(A), math.sin(A)
    cosB, sinB = math.cos(B), math.sin(B)

    R1 = 1
    R2 = 2
    K2 = 5
    K1 = WIDTH_CHARS * K2 * 3 / (8 * (R1 + R2))

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
                    chars = ".,-~:;=!*#$@"
                    b[idx] = chars[luminance_idx] if luminance_idx > 0 else "."

            phi += 0.07
        theta += 0.07

    rows = []
    for j in range(HEIGHT_CHARS):
        row = "".join(b[j * WIDTH_CHARS : (j + 1) * WIDTH_CHARS])
        rows.append(row)
    return rows


def escape_xml(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


def build_svg():
    frames_data = []
    for i in range(NUM_FRAMES):
        A = i * (2 * math.pi / NUM_FRAMES)
        B = i * (math.pi / NUM_FRAMES)
        rows = render_donut_frame(A, B)
        frames_data.append(rows)

    cycle_dur = 2.4  # seconds for full 360 loop
    pct_visible = 100.0 / NUM_FRAMES

    parts = [
        f'<svg viewBox="0 0 {SVG_W} {SVG_H}" width="{SVG_W}" height="{SVG_H}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="SFMono-Regular, Consolas, Menlo, monospace">'
    ]

    parts.append(f'''
    <style>
      .title {{ fill: #8b949e; font-size: 12px; font-weight: 600; }}
      .donut-text {{ font-size: {FONT_SIZE}px; fill: {DONUT_COLOR}; white-space: pre; font-weight: bold; }}
      .frame {{ opacity: 0; animation: anim-frame {cycle_dur:.2f}s infinite; }}
      @keyframes anim-frame {{
        0% {{ opacity: 1; }}
        {pct_visible:.2f}% {{ opacity: 1; }}
        {pct_visible + 0.01:.2f}% {{ opacity: 0; }}
        100% {{ opacity: 0; }}
      }}
      .dot {{ animation: pulse 2s infinite ease-in-out; }}
      @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
      .glow {{ filter: drop-shadow(0px 0px 8px rgba(57, 211, 83, 0.3)); }}
    </style>
    <defs>
      <linearGradient id="donutBg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#0d1117" />
        <stop offset="100%" stop-color="#161b22" />
      </linearGradient>
      <linearGradient id="donutBorder" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#39d353" />
        <stop offset="50%" stop-color="#58a6ff" />
        <stop offset="100%" stop-color="#bc8cff" />
      </linearGradient>
    </defs>

    <rect x="1" y="1" width="{SVG_W - 2}" height="{SVG_H - 2}" rx="12" ry="12"
          fill="url(#donutBg)" stroke="url(#donutBorder)" stroke-width="1.5" class="glow" />
    ''')

    # Title bar
    for i, color in enumerate(DOT_COLORS):
        parts.append(f'<circle class="dot" cx="{18 + i * 16}" cy="18" r="5" fill="{color}" />')
    parts.append(f'<text x="{SVG_W / 2}" y="22" text-anchor="middle" class="title">{TITLE}</text>')
    parts.append(f'<line x1="0" y1="34" x2="{SVG_W}" y2="34" stroke="#30363d" stroke-width="1" />')

    # Render each frame
    for f_idx, rows in enumerate(frames_data):
        delay = f_idx * (cycle_dur / NUM_FRAMES)
        parts.append(f'<g class="frame" style="animation-delay: {delay:.3f}s;">')
        for r_idx, row_str in enumerate(rows):
            y_pos = TOP_PAD + r_idx * LINE_H
            safe_str = escape_xml(row_str)
            parts.append(f'  <text x="24" y="{y_pos:.1f}" class="donut-text" xml:space="preserve">{safe_str}</text>')
        parts.append('</g>')

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    svg = build_svg()
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    with open(OUT_PATH_AVI, "w") as f:
        f.write(svg)
    print(f"[make_donut_svg] wrote {OUT_PATH} and {OUT_PATH_AVI}")


if __name__ == "__main__":
    main()
