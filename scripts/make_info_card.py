#!/usr/bin/env python3
"""
Hand-authored neofetch-style info card: a title bar + colored key/value rows
that fade/slide in on a stagger, like the panel is printing.

Set STATIC=1 to emit a frozen (no-animation) frame, handy for a local
Quick Look preview.
"""
import os

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")
STATIC = os.environ.get("STATIC") == "1"

# Edit this block to change what the card says.
TITLE = "yatinsingh2007@github"
ROWS = [
    ("Education", "BTech CSE (AI) '28 @ Newton School of Tech"),
    ("Role", "SDE Intern @ ByteBlock Technologies"),
    ("Prev", "Full Stack Intern @ AssuredGig"),
    ("Focus", "Agentic AI, Full-Stack & DevOps"),
    ("Stack", "Next.js, TypeScript, Node.js, Go, Python"),
    ("ML / AI", "PyTorch, LangGraph, scikit-learn, RAG"),
    ("Projects", "CreditIQ, ReportLens-AI, ShopSmart, VintiCode"),
]

WIDTH = 540
ROW_H = 26
TOP_PAD = 46
BOTTOM_PAD = 18
HEIGHT = TOP_PAD + len(ROWS) * ROW_H + BOTTOM_PAD

ACCENT = "#39d353"
KEY_COLOR = "#39d353"
VAL_COLOR = "#c9d1d9"
BG = "#0d1117"
BORDER = "#30363d"
DOT_COLORS = ["#ff5f56", "#ffbd2e", "#27c93f"]


def build_svg():
    parts = [
        f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="SFMono-Regular, Consolas, Menlo, monospace">'
    ]

    anim_css = "" if STATIC else '''
      .row { opacity: 0; transform: translateX(-8px); animation: printline 0.4s ease-out forwards; }
      @keyframes printline { to { opacity: 1; transform: translateX(0); } }
    '''
    parts.append(f'''
    <style>
      {anim_css}
      .key {{ fill: {KEY_COLOR}; font-size: 13px; font-weight: bold; }}
      .val {{ fill: {VAL_COLOR}; font-size: 13px; }}
      .title {{ fill: #8b949e; font-size: 12px; }}
    </style>
    <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="10" ry="10"
          fill="{BG}" stroke="{BORDER}" />
    ''')

    # Fake title bar with traffic-light dots
    for i, color in enumerate(DOT_COLORS):
        parts.append(f'<circle cx="{18 + i * 16}" cy="18" r="5" fill="{color}" />')
    parts.append(f'<text x="{WIDTH / 2}" y="22" text-anchor="middle" class="title">{TITLE}</text>')
    parts.append(f'<line x1="0" y1="34" x2="{WIDTH}" y2="34" stroke="{BORDER}" />')

    key_col_w = max(len(k) for k, _ in ROWS) * 8 + 24

    for i, (key, val) in enumerate(ROWS):
        y = TOP_PAD + i * ROW_H
        delay = 0 if STATIC else i * 0.12
        row_class = "row" if not STATIC else ""
        style = "" if STATIC else f' style="animation-delay:{delay:.2f}s"'
        parts.append(f'<g class="{row_class}"{style}>')
        parts.append(f'<text x="20" y="{y}" class="key">{key}</text>')
        parts.append(f'<text x="{20 + key_col_w}" y="{y}" class="val">{val}</text>')
        parts.append('</g>')

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    svg = build_svg()
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"[make_info_card] wrote {OUT_PATH} (static={STATIC})")


if __name__ == "__main__":
    main()
