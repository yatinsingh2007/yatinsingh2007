#!/usr/bin/env bash
# Regenerate every animated SVG in both dark and light variants.
#
# Usage:
#   scripts/build_all.sh                 # rebuild from the current prepped.png
#   scripts/build_all.sh path/to/you.jpg # run background removal first, then rebuild
#
# Run from the repo root with the venv's python on PATH (or edit PY below).
set -euo pipefail
cd "$(dirname "$0")/.."

PY="${PY:-./.venv/bin/python}"

if [[ "${1:-}" != "" ]]; then
  echo "==> prepping photo: $1"
  "$PY" scripts/prep_photo.py "$1"
fi

for theme in dark light; do
  echo "==> building theme: $theme"
  THEME="$theme" "$PY" scripts/make_donut_svg.py
  THEME="$theme" "$PY" scripts/render_heatmap_svg.py
  THEME="$theme" "$PY" scripts/make_info_card.py   # picks up prepped.png as the logo
  THEME="$theme" "$PY" scripts/make_ascii_svg.py   # no-op if prepped.png is missing
done

echo "==> done. Dark files have no suffix; light files end in -light.svg"
