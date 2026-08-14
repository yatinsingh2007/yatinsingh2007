# Setup — yatinsingh2007's animated profile README

## 1. Create the magic repo
GitHub renders `README.md` from a repo whose name matches your username, at the top of your profile.

```bash
gh repo create yatinsingh2007 --public --clone
cd yatinsingh2007
```

Copy everything from this package into that folder (`scripts/`, `.github/`, `README.md`), preserving the structure.

## 2. Local toolchain (only needed once, or when you change your photo)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements.txt
```

## 3. One-shot build (recommended)
`scripts/build_all.sh` regenerates every animated SVG in **both** dark and light
variants (dark files have no suffix, light files end in `-light.svg`; the README
serves the right one per viewer theme via `<picture>`).

```bash
# rebuild from an existing scripts/prepped.png
scripts/build_all.sh

# or, prep a fresh photo first (background removal + auto-crop + contrast),
# then rebuild everything:
scripts/build_all.sh path/to/your-photo.jpg
```

`prep_photo.py` removes the background (rembg), auto-crops to the subject so the
ASCII fills the frame, and boosts local contrast. The result feeds both the
standalone typing portrait (`avi-ascii.svg`) and the neofetch card's logo panel.

### Individual generators (if you'd rather run them one at a time)
```bash
python scripts/prep_photo.py path/to/your-photo.jpg   # -> scripts/prepped.png
python scripts/make_ascii_svg.py                       # -> avi-ascii.svg   (typing portrait)
python scripts/make_info_card.py                       # -> info-card.svg   (neofetch + logo)
python scripts/make_donut_svg.py                       # -> terminal-donut.svg
python scripts/fetch_contributions.py                  # -> data/contributions.json
python scripts/render_heatmap_svg.py                   # -> contrib-heatmap.svg
```
Prefix any of them with `THEME=light` for the light variant. Edit the `ROWS`
list in `make_info_card.py` to change what the card says. If no `prepped.png`
exists, the portrait/logo are simply skipped and the layout still works.

## 6. Push
```bash
git add .
git commit -m "init: animated terminal profile README"
git push
```

## 7. Automation status
The only automated piece is the **contribution snake** (`.github/workflows/snake.yml`),
which rebuilds `github-contribution-grid-snake*.svg` on the `output` branch daily.
The donut, info-card, heatmap, and portrait SVGs are generated **locally** with
`scripts/build_all.sh` and committed. To keep the heatmap fresh automatically you'd
add a workflow step that runs `fetch_contributions.py` + `render_heatmap_svg.py`
(both themes) and commits the result — not wired up yet.

## Notes specific to this build
- `scripts/requirements.txt` = full deps (portrait + heatmap), for local use.
- `scripts/requirements-ci.txt` = just `requests` + `beautifulsoup4`, used by the
  snake Action so it stays fast and doesn't need OpenCV/rembg.
- The scraper (`fetch_contributions.py`) was verified live against
  `https://github.com/users/yatinsingh2007/contributions` — it pulled real data
  (803 contributions in the last year, 13-day longest streak at time of writing) with
  no token needed.
- All three SVGs are self-contained animated CSS/SMIL — no `<script>`, no external CSS,
  so they render and animate directly on your GitHub profile page.
