#!/usr/bin/env python3
"""
Hand-authored neofetch-style info card: a title bar + colored key/value rows
that fade/slide in on a stagger, with neon glowing borders, traffic lights,
and a blinking cursor.
"""
import os

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")
STATIC = os.environ.get("STATIC") == "1"

# Edit this block to change what the card says.
TITLE = "⚡ yatinsingh2007@github ~ $ neofetch"
ROWS = [
    ("⚡ Education", "BTech CSE (AI) '28 @ Newton School of Tech"),
    ("💼 Experience", "SDE Intern @ ByteBlock | Ex-Full Stack Intern @ AssuredGig"),
    ("🚀 Focus Area", "Agentic AI Systems, Full-Stack & Scalable Cloud DevOps"),
    ("💻 Tech Stack", "Next.js 14, TypeScript, Node.js, Go, Python, Tailwind"),
    ("🧠 AI / ML", "PyTorch, LangGraph, scikit-learn, RAG, LLM Agents"),
    ("⭐ Highlights", "CreditIQ (92% acc. RAG), ReportLens-AI, ShopSmart"),
    ("📫 Status", "Open for SDE / AI Internships & Global Collaborations"),
]

WIDTH = 580
ROW_H = 28
TOP_PAD = 50
BOTTOM_PAD = 24
HEIGHT = TOP_PAD + len(ROWS) * ROW_H + BOTTOM_PAD

KEY_COLOR = "#58a6ff"
VAL_COLOR = "#c9d1d9"
BG = "#0d1117"
BORDER = "#30363d"
ACCENT_BORDER = "#58a6ff"
DOT_COLORS = ["#ff5f56", "#ffbd2e", "#27c93f"]


def build_svg():
    parts = [
        f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="SFMono-Regular, Consolas, Menlo, monospace">'
    ]

    anim_css = "" if STATIC else '''
      .row { opacity: 0; transform: translateX(-10px); animation: printline 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
      @keyframes printline { to { opacity: 1; transform: translateX(0); } }
      .dot { animation: pulse 2s infinite ease-in-out; }
      @keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.6; transform: scale(0.92); } }
      .blink { animation: blinker 1s infinite; fill: #58a6ff; }
      @keyframes blinker { 50% { opacity: 0; } }
      .glow-border { filter: drop-shadow(0px 0px 6px rgba(88, 166, 255, 0.25)); }
    '''
    parts.append(f'''
    <style>
      {anim_css}
      .key {{ fill: {KEY_COLOR}; font-size: 13px; font-weight: 600; letter-spacing: 0.3px; }}
      .val {{ fill: {VAL_COLOR}; font-size: 13px; }}
      .title {{ fill: #8b949e; font-size: 12px; font-weight: 600; letter-spacing: 0.5px; }}
    </style>
    <defs>
      <linearGradient id="cardBg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#0d1117" />
        <stop offset="100%" stop-color="#161b22" />
      </linearGradient>
      <linearGradient id="borderGrad" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#58a6ff" />
        <stop offset="50%" stop-color="#bc8cff" />
        <stop offset="100%" stop-color="#39d353" />
      </linearGradient>
    </defs>
    
    <rect x="1" y="1" width="{WIDTH - 2}" height="{HEIGHT - 2}" rx="12" ry="12"
          fill="url(#cardBg)" stroke="url(#borderGrad)" stroke-width="1.5" class="glow-border" />
    ''')

    # Fake title bar with traffic-light dots
    for i, color in enumerate(DOT_COLORS):
        delay = i * 0.3
        parts.append(f'<circle class="dot" cx="{20 + i * 18}" cy="20" r="5.5" fill="{color}" style="animation-delay:{delay:.1f}s" />')
    parts.append(f'<text x="{WIDTH / 2}" y="24" text-anchor="middle" class="title">{TITLE}</text>')
    parts.append(f'<line x1="0" y1="38" x2="{WIDTH}" y2="38" stroke="#30363d" stroke-width="1" />')

    key_col_w = max(len(k) for k, _ in ROWS) * 8 + 18

    for i, (key, val) in enumerate(ROWS):
        y = TOP_PAD + i * ROW_H
        delay = 0 if STATIC else 0.1 + i * 0.1
        row_class = "row" if not STATIC else ""
        style = "" if STATIC else f' style="animation-delay:{delay:.2f}s"'
        parts.append(f'<g class="{row_class}"{style}>')
        parts.append(f'<text x="22" y="{y}" class="key">{key}</text>')
        parts.append(f'<text x="{22 + key_col_w}" y="{y}" class="val">{val}</text>')
        parts.append('</g>')

    # Add cursor prompt line at bottom
    last_y = TOP_PAD + len(ROWS) * ROW_H
    cursor_delay = 0.1 + len(ROWS) * 0.1
    parts.append(f'''
    <g class="row" style="animation-delay:{cursor_delay:.2f}s">
      <text x="22" y="{last_y}" class="key">❯</text>
      <rect x="38" y="{last_y - 11}" width="8" height="13" class="blink" rx="1.5" />
    </g>
    ''')

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    svg = build_svg()
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"[make_info_card] wrote {OUT_PATH} (static={STATIC})")


if __name__ == "__main__":
    main()
