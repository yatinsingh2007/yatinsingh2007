#!/usr/bin/env python3
"""
Hand-authored neofetch-style info card: a title bar + colored key/value rows
that fade/slide in on a stagger, with neon glowing borders, traffic lights,
and a blinking cursor.
"""
import os

THEME = os.environ.get("THEME", "dark").lower()
_SUFFIX = "" if THEME == "dark" else f"-{THEME}"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", f"info-card{_SUFFIX}.svg")
STATIC = os.environ.get("STATIC") == "1"

# Optional ASCII "logo" panel (real neofetch shows art beside the info). Only
# rendered when a prepped portrait exists; otherwise the card degrades to the
# original text-only layout.
PREPPED = os.path.join(os.path.dirname(__file__), "prepped.png")
LOGO_COLS = 30
LOGO_FONT = 7
LCHAR_W = LOGO_FONT * 0.6
LLINE_H = LOGO_FONT * 1.05
LOGO_ROWS = None
try:
    from PIL import Image
    from make_ascii_svg import image_to_ascii_rows
    if os.path.exists(PREPPED):
        LOGO_ROWS = image_to_ascii_rows(Image.open(PREPPED), LOGO_COLS)
except Exception as e:  # pragma: no cover - Pillow/helper unavailable
    print(f"[make_info_card] logo panel skipped: {e}")

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

ROW_H = 28
TOP_PAD = 50
BOTTOM_PAD = 24

# When a logo panel is present, reserve a left column for it and push the
# info rows to the right; otherwise keep the original single-column card.
LOGO_X = 24
LOGO_TOP = 52
if LOGO_ROWS:
    _logo_w = LOGO_COLS * LCHAR_W
    INFO_X = LOGO_X + _logo_w + 26
    _logo_h = len(LOGO_ROWS) * LLINE_H
else:
    INFO_X = 22
    _logo_h = 0

_info_h = TOP_PAD + (len(ROWS) + 1) * ROW_H + BOTTOM_PAD
HEIGHT = max(_info_h, LOGO_TOP + _logo_h + BOTTOM_PAD)
WIDTH = 760 if LOGO_ROWS else 580

DARK = {
    "key": "#58a6ff", "val": "#c9d1d9", "title": "#8b949e",
    "bg_a": "#0d1117", "bg_b": "#161b22", "divider": "#30363d",
    "glow": "rgba(88, 166, 255, 0.25)",
}
LIGHT = {
    "key": "#0969da", "val": "#24292f", "title": "#57606a",
    "bg_a": "#ffffff", "bg_b": "#f6f8fa", "divider": "#d0d7de",
    "glow": "rgba(9, 105, 218, 0.18)",
}
PAL = DARK if THEME == "dark" else LIGHT

KEY_COLOR = PAL["key"]
VAL_COLOR = PAL["val"]
BG = PAL["bg_a"]
BORDER = PAL["divider"]
ACCENT_BORDER = PAL["key"]
DOT_COLORS = ["#ff5f56", "#ffbd2e", "#27c93f"]


def escape_xml(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


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
      .blink { animation: blinker 1s infinite; fill: ''' + KEY_COLOR + '''; }
      @keyframes blinker { 50% { opacity: 0; } }
      .glow-border { filter: drop-shadow(0px 0px 6px ''' + PAL["glow"] + '''); }
      .logo-row { opacity: 0; animation: fadein 0.4s ease-out forwards; }
      @keyframes fadein { to { opacity: 1; } }
    '''
    parts.append(f'''
    <style>
      {anim_css}
      .key {{ fill: {KEY_COLOR}; font-size: 13px; font-weight: 600; letter-spacing: 0.3px; }}
      .val {{ fill: {VAL_COLOR}; font-size: 13px; }}
      .title {{ fill: {PAL["title"]}; font-size: 12px; font-weight: 600; letter-spacing: 0.5px; }}
    </style>
    <defs>
      <linearGradient id="cardBg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="{PAL["bg_a"]}" />
        <stop offset="100%" stop-color="{PAL["bg_b"]}" />
      </linearGradient>
      <linearGradient id="borderGrad" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#58a6ff" />
        <stop offset="50%" stop-color="#bc8cff" />
        <stop offset="100%" stop-color="#39d353" />
      </linearGradient>
      <linearGradient id="logoGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#58a6ff" />
        <stop offset="55%" stop-color="#bc8cff" />
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
    parts.append(f'<text x="{WIDTH / 2}" y="24" text-anchor="middle" class="title">{escape_xml(TITLE)}</text>')
    parts.append(f'<line x1="0" y1="38" x2="{WIDTH}" y2="38" stroke="{PAL["divider"]}" stroke-width="1" />')

    # Left ASCII "logo" panel (real neofetch layout), tinted with a gradient.
    if LOGO_ROWS:
        parts.append(
            f'<style>.logo-text {{ font-size: {LOGO_FONT}px; fill: url(#logoGrad); '
            f'white-space: pre; font-weight: bold; }}</style>'
        )
        for li, row_text in enumerate(LOGO_ROWS):
            ly = LOGO_TOP + li * LLINE_H + LOGO_FONT
            delay = 0 if STATIC else 0.05 + li * 0.03
            g_open = ('<g class="logo-row"'
                      + ('' if STATIC else f' style="animation-delay:{delay:.2f}s"') + '>')
            parts.append(g_open)
            parts.append(
                f'<text x="{LOGO_X}" y="{ly:.1f}" class="logo-text" xml:space="preserve">'
                f'{escape_xml(row_text)}</text>')
            parts.append('</g>')
        # thin divider between logo and info
        div_x = INFO_X - 13
        parts.append(
            f'<line x1="{div_x}" y1="46" x2="{div_x}" y2="{HEIGHT - 16}" '
            f'stroke="{PAL["divider"]}" stroke-width="1" opacity="0.6" />')

    key_col_w = max(len(k) for k, _ in ROWS) * 8 + 18

    for i, (key, val) in enumerate(ROWS):
        y = TOP_PAD + i * ROW_H
        delay = 0 if STATIC else 0.1 + i * 0.1
        row_class = "row" if not STATIC else ""
        style = "" if STATIC else f' style="animation-delay:{delay:.2f}s"'
        parts.append(f'<g class="{row_class}"{style}>')
        parts.append(f'<text x="{INFO_X}" y="{y}" class="key">{escape_xml(key)}</text>')
        parts.append(f'<text x="{INFO_X + key_col_w}" y="{y}" class="val">{escape_xml(val)}</text>')
        parts.append('</g>')

    # Add cursor prompt line at bottom
    last_y = TOP_PAD + len(ROWS) * ROW_H
    cursor_delay = 0.1 + len(ROWS) * 0.1
    parts.append(f'''
    <g class="row" style="animation-delay:{cursor_delay:.2f}s">
      <text x="{INFO_X}" y="{last_y}" class="key">❯</text>
      <rect x="{INFO_X + 16}" y="{last_y - 11}" width="8" height="13" class="blink" rx="1.5" />
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
