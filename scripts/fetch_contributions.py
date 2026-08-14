#!/usr/bin/env python3
"""
Fetch a GitHub user's public contribution calendar with no token/auth.

GitHub serves the exact fragment the profile page uses at:
    https://github.com/users/<username>/contributions

We parse each <td class="ContributionCalendar-day"> for date/level, and
pull the exact per-day count out of the matching <tool-tip> element.
"""
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_USERNAME", "yatinsingh2007")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def fetch_html(username: str) -> str:
    resp = requests.get(
        f"https://github.com/users/{username}/contributions",
        headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.text


def parse_days(html: str):
    soup = BeautifulSoup(html, "html.parser")

    # Map tool-tip "for" id -> count, parsed from its text.
    tooltip_counts = {}
    for tip in soup.select("tool-tip"):
        target_id = tip.get("for")
        if not target_id:
            continue
        text = tip.get_text(strip=True)
        m = re.match(r"([\d,]+)\s+contributions?", text)
        tooltip_counts[target_id] = int(m.group(1).replace(",", "")) if m else 0

    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        date_str = td.get("data-date")
        level_str = td.get("data-level")
        if not date_str or level_str is None:
            continue
        day_id = td.get("id", "")
        count = tooltip_counts.get(day_id, 0)
        days.append({
            "date": date_str,
            "level": int(level_str),
            "count": count,
        })

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days):
    if not days:
        return {}

    total = sum(d["count"] for d in days)
    best_day = max(days, key=lambda d: d["count"])

    # Current streak: walk backward from the most recent day with data.
    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    # Longest streak across the whole window.
    longest_streak = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    # Totals by calendar month (YYYY-MM).
    monthly = {}
    for d in days:
        month_key = d["date"][:7]
        monthly[month_key] = monthly.get(month_key, 0) + d["count"]

    return {
        "total_last_year": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": {"date": best_day["date"], "count": best_day["count"]},
        "monthly_totals": monthly,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def main():
    try:
        html = fetch_html(USERNAME)
        days = parse_days(html)
        if not days:
            raise ValueError("No contribution cells parsed — GitHub markup may have changed.")
        stats = compute_stats(days)
    except Exception as exc:
        print(f"[fetch_contributions] ERROR: {exc}", file=sys.stderr)
        # Don't wipe out a previously-good file if the scrape fails.
        if os.path.exists(OUT_PATH):
            print("[fetch_contributions] Keeping previous data/contributions.json", file=sys.stderr)
            sys.exit(0)
        sys.exit(1)

    payload = {"username": USERNAME, "days": days, "stats": stats}
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"[fetch_contributions] wrote {len(days)} days, "
          f"{stats.get('total_last_year', 0)} contributions -> {OUT_PATH}")


if __name__ == "__main__":
    main()
