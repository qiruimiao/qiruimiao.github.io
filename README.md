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

## CV

`assets/Qirui_Miao_CV.pdf` is a **public-web version** of the master CV, exported
from `01_MASTER_CV/Qirui_Miao_Master_CV_V2_EN.docx` with two things removed:

- the mobile number (the site deliberately keeps it off the open web)
- an internal tailoring note that had leaked into the skills section

Keep the local master CV as the version you actually send to employers. When the
master changes, re-export a public copy the same way rather than editing this PDF.

## Portrait

No photo is used, by choice: UK CV convention is to omit one. The mechanism below
stays available in case that changes.


Drop a square photo at `assets/portrait.jpg` (400x400 is plenty) and re-run the
build script; it gets embedded as a data URI so the page stays a single file.

## Editing

Open `index.html` and edit it directly, then commit and push — GitHub Pages
redeploys automatically within a minute or so.

To regenerate the QR codes after changing a URL or the vCard, see
`tools/build_qr.py`.
