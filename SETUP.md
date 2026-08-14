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

## 3. Generate the ASCII portrait (optional but recommended)
```bash
python scripts/prep_photo.py path/to/your-photo.jpg   # -> scripts/prepped.png
python scripts/make_ascii_svg.py                       # -> avi-ascii.svg
```
If you skip this step, drop any other `avi-ascii.svg` in the repo root, or edit `README.md`
to remove that `<td>` — the layout still works with just the heatmap + info card.

## 4. Generate the info card
Edit the `ROWS` list in `scripts/make_info_card.py` (it's already pre-filled with your
ByteBlock / Next.js / PyTorch / CreditIQ / Netherlands details), then:
```bash
python scripts/make_info_card.py    # -> info-card.svg
```

## 5. Generate the live heatmap once, locally, to confirm it works
```bash
python scripts/fetch_contributions.py    # -> data/contributions.json (already tested — works)
python scripts/render_heatmap_svg.py     # -> contrib-heatmap.svg
```

## 6. Push
```bash
git add .
git commit -m "init: animated terminal profile README"
git push
```

## 7. Confirm the daily automation
Go to the repo's **Actions** tab → "Update profile art" → **Run workflow** (this is the
`workflow_dispatch` trigger) to fire it once by hand. Check that it commits a fresh
`contrib-heatmap.svg` and `data/contributions.json`. After that it runs automatically
every day at ~06:17 UTC via the cron in `.github/workflows/update-profile-art.yml`.

## Notes specific to this build
- `scripts/requirements.txt` = full deps (portrait + heatmap), for local use.
- `scripts/requirements-ci.txt` = just `requests` + `beautifulsoup4`, used by the
  GitHub Action so the daily job stays fast and doesn't need OpenCV/rembg.
- The scraper (`fetch_contributions.py`) was verified live against
  `https://github.com/users/yatinsingh2007/contributions` — it pulled real data
  (803 contributions in the last year, 13-day longest streak at time of writing) with
  no token needed.
- All three SVGs are self-contained animated CSS/SMIL — no `<script>`, no external CSS,
  so they render and animate directly on your GitHub profile page.
