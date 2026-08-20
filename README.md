# qiruimiao.github.io

Personal site for Qirui Miao — a single self-contained HTML page.

- **Live:** https://qiruimiao.github.io
- **Source:** `index.html` (no build step, no dependencies)

The QR codes are pre-generated static SVG paths embedded directly in the page,
so nothing is fetched from an external QR service. The only network request the
page makes is to Google Fonts; saved locally and opened offline, it still renders
and the QR codes still scan.

## Two view modes

- `https://qiruimiao.github.io`        - full profile (default; what a recruiter sees)
- `https://qiruimiao.github.io/#card`  - business-card view for networking

The toggle at the top switches between them and updates the URL, so either
state can be bookmarked or shared.

## Portrait

Drop a square photo at `assets/portrait.jpg` (400x400 is plenty) and re-run the
build script; it gets embedded as a data URI so the page stays a single file.

## Editing

Open `index.html` and edit it directly, then commit and push — GitHub Pages
redeploys automatically within a minute or so.

To regenerate the QR codes after changing a URL or the vCard, see
`tools/build_qr.py`.
