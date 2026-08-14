#!/usr/bin/env python3
"""
Draw the contribution calendar as rounded boxes, GitHub-green ramp,
revealed with a one-shot diagonal slide-down, then kept alive by a slow
diagonal "shimmer" wave that sweeps across the lit cells forever.

Set THEME=light for the light-mode palette (used by the README's
<picture> prefers-color-scheme variant).
"""
import json
import os

THEME = os.environ.get("THEME", "dark").lower()
_SUFFIX = "" if THEME == "dark" else f"-{THEME}"

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", f"contrib-heatmap{_SUFFIX}.svg")

DARK = {
    "palette": ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"],
    "lbl": "#8b949e",
    "footer": "#c9d1d9",
}
LIGHT = {
    "palette": ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"],
    "lbl": "#57606a",
    "footer": "#24292f",
}
THEME_PAL = DARK if THEME == "dark" else LIGHT
PALETTE = THEME_PAL["palette"]

BOX = 10
GAP = 3
CELL = BOX + GAP
LEFT_PAD = 28      # room for day-of-week labels
TOP_PAD = 30        # room for month labels
BOTTOM_PAD = 46     # room for legend + stats footer
RIGHT_PAD = 10

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DOW_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}  # sparse, like GitHub's own graph


def load_data():
    with open(DATA_PATH) as f:
        return json.load(f)


def weeks_from_days(days):
    """Bucket days into GitHub-style weeks (columns), each starting Sunday."""
    from datetime import datetime
    parsed = [dict(d, dt=datetime.strptime(d["date"], "%Y-%m-%d")) for d in days]
    parsed.sort(key=lambda d: d["dt"])

    weeks = []
    current_week = [None] * 7
    if not parsed:
        return weeks

    first_dow = (parsed[0]["dt"].weekday() + 1) % 7  # Sunday=0
    for i in range(first_dow):
        current_week[i] = None

    for d in parsed:
        dow = (d["dt"].weekday() + 1) % 7
        current_week[dow] = d
        if dow == 6:
            weeks.append(current_week)
            current_week = [None] * 7

    if any(c is not None for c in current_week):
        weeks.append(current_week)

    return weeks


def month_label_positions(weeks):
    labels = []
    last_month = None
    for w_idx, week in enumerate(weeks):
        for day in week:
            if day is None:
                continue
            month = day["dt"].month
            if month != last_month:
                labels.append((w_idx, MONTH_NAMES[month - 1]))
                last_month = month
            break
    return labels


def build_svg(data):
    days = data["days"]
    stats = data.get("stats", {})
    weeks = weeks_from_days(days)
    n_weeks = len(weeks)

    width = LEFT_PAD + n_weeks * CELL + RIGHT_PAD
    height = TOP_PAD + 7 * CELL + BOTTOM_PAD

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="-apple-system, Segoe UI, Helvetica, sans-serif">'
    )
    parts.append(f'''
    <style>
      .cell {{
        opacity: 0;
        transform-box: fill-box;
        transform-origin: center;
        animation: reveal 0.5s ease-out forwards;
      }}
      @keyframes reveal {{
        0%   {{ opacity: 0; transform: translate(-6px, -6px) scale(0.4); }}
        100% {{ opacity: 1; transform: translate(0, 0) scale(1); }}
      }}
      /* Lit cells keep breathing: a diagonal brightness wave sweeps across
         forever, phase-shifted per cell so it reads as a travelling ripple. */
      .live {{
        animation: reveal 0.5s ease-out forwards, shimmer 3.6s ease-in-out infinite;
      }}
      @keyframes shimmer {{
        0%, 100% {{ filter: brightness(1); }}
        50%      {{ filter: brightness(1.55) drop-shadow(0 0 2px currentColor); }}
      }}
      .lbl {{ fill: {THEME_PAL["lbl"]}; font-size: 10px; }}
      .footer {{ fill: {THEME_PAL["footer"]}; font-size: 11px; }}
    </style>
    <rect width="100%" height="100%" fill="transparent" />
    ''')

    # Month labels
    for w_idx, label in month_label_positions(weeks):
        x = LEFT_PAD + w_idx * CELL
        parts.append(f'<text x="{x}" y="{TOP_PAD - 10}" class="lbl">{label}</text>')

    # Day-of-week labels
    for dow, label in DOW_LABELS.items():
        y = TOP_PAD + dow * CELL + BOX
        parts.append(f'<text x="0" y="{y}" class="lbl">{label}</text>')

    # Cells, staggered diagonally by (week + day-of-week)
    for w_idx, week in enumerate(weeks):
        for dow, day in enumerate(week):
            if day is None:
                continue
            x = LEFT_PAD + w_idx * CELL
            y = TOP_PAD + dow * CELL
            level = max(0, min(day["level"], len(PALETTE) - 1))
            color = PALETTE[level]
            delay = (w_idx + dow) * 0.006
            title = f'{day["count"]} contributions on {day["date"]}'
            if level > 0:
                # Second delay = shimmer phase; negative offset makes the wave travel.
                phase = -((w_idx + dow) * 0.10)
                style = (f'animation-delay:{delay:.3f}s, {phase:.2f}s; color:{color}')
                cls = "cell live"
            else:
                style = f'animation-delay:{delay:.3f}s'
                cls = "cell"
            parts.append(
                f'<rect class="{cls}" x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="2" ry="2" '
                f'fill="{color}" style="{style}"><title>{title}</title></rect>'
            )

    # Legend: Less -> More
    legend_y = TOP_PAD + 7 * CELL + 20
    legend_x = LEFT_PAD
    parts.append(f'<text x="{legend_x}" y="{legend_y + 8}" class="lbl">Less</text>')
    lx = legend_x + 32
    for color in PALETTE:
        parts.append(f'<rect x="{lx}" y="{legend_y}" width="{BOX}" height="{BOX}" rx="2" ry="2" fill="{color}" />')
        lx += CELL
    parts.append(f'<text x="{lx + 4}" y="{legend_y + 8}" class="lbl">More</text>')

    # Stats footer
    total = stats.get("total_last_year", sum(d["count"] for d in days))
    streak = stats.get("longest_streak", 0)
    footer = f'{total:,} contributions in the last year  ·  longest streak {streak} days'
    parts.append(f'<text x="{width - RIGHT_PAD}" y="{legend_y + 8}" text-anchor="end" class="footer">{footer}</text>')

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    data = load_data()
    svg = build_svg(data)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"[render_heatmap_svg] wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
