#!/usr/bin/env python3
"""Rebuild index.html from tools/template.html with freshly generated QR codes.

    pip install segno
    python3 tools/build_qr.py

Edit CONTACT / PAYLOADS below to change what the QR codes encode, then re-run.
Every QR is baked into the page as a static SVG path, so the published page
never calls an external QR service.
"""
import io, json, os, re, sys

try:
    import segno
except ImportError:
    sys.exit("segno is required:  pip install segno")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- what the QR codes encode -------------------------------------------------
VCARD = "\r\n".join([
    "BEGIN:VCARD", "VERSION:3.0",
    "N:Miao;Qirui;;;", "FN:Qirui Miao",
    "EMAIL;TYPE=INTERNET:qirui.miao@outlook.com",
    "URL:https://www.linkedin.com/in/qirui-miao-b684bb381/",
    "ADR;TYPE=HOME:;;;London;;;United Kingdom",
    "END:VCARD", ""])

PAYLOADS = {
    "card":      VCARD,
    "linkedin":  "https://www.linkedin.com/in/qirui-miao-b684bb381/",
    "instagram": "https://www.instagram.com/jecsrry/",
    "github":    "https://github.com/qiruimiao",
}

TABS = [
    ("card",      "Contact card", "Scan to save my contact",   "Qirui Miao &middot; qirui.miao@outlook.com"),
    ("linkedin",  "LinkedIn",     "Scan to open my LinkedIn",  "in/qirui-miao"),
    ("instagram", "Instagram",    "Scan to open my Instagram", "@jecsrry"),
    ("github",    "GitHub",       "Scan to open my GitHub",    "github.com/qiruimiao"),
]

LINKS = {
    "card":      ("mailto:qirui.miao@outlook.com", "Email me"),
    "linkedin":  ("https://www.linkedin.com/in/qirui-miao-b684bb381/", "Open LinkedIn"),
    "instagram": ("https://www.instagram.com/jecsrry/", "Open Instagram"),
    "github":    ("https://github.com/qiruimiao", "Open GitHub"),
}

ICONS = {
    "card": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="4.5" width="19" height="15" rx="2"/><circle cx="8.6" cy="11" r="2.2"/><path d="M5.2 16.4c.5-1.5 1.8-2.3 3.4-2.3s2.9.8 3.4 2.3M15 10h4M15 13.6h4"/></svg>',
    "linkedin": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4.98 3.5A2.5 2.5 0 1 0 5 8.5a2.5 2.5 0 0 0-.02-5zM3 9.5h4v11H3v-11zm6.5 0h3.8v1.5h.05c.53-.95 1.83-1.95 3.77-1.95 4.03 0 4.78 2.5 4.78 5.76v5.69h-4v-5.05c0-1.2-.02-2.75-1.75-2.75-1.75 0-2.02 1.31-2.02 2.66v5.14h-4v-11z"/></svg>',
    "instagram": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5.2"/><circle cx="12" cy="12" r="4"/><circle cx="17.3" cy="6.7" r="1.15" fill="currentColor" stroke="none"/></svg>',
    "github": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48l-.01-1.7c-2.78.6-3.37-1.34-3.37-1.34-.45-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.61.07-.61 1 .07 1.53 1.03 1.53 1.03.89 1.53 2.34 1.09 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.56-1.11-4.56-4.95 0-1.09.39-1.99 1.03-2.69-.1-.25-.45-1.27.1-2.65 0 0 .84-.27 2.75 1.03a9.5 9.5 0 0 1 5 0c1.91-1.3 2.75-1.03 2.75-1.03.55 1.38.2 2.4.1 2.65.64.7 1.03 1.6 1.03 2.69 0 3.85-2.34 4.7-4.57 4.94.36.31.68.92.68 1.86l-.01 2.75c0 .27.18.58.69.48A10 10 0 0 0 12 2z"/></svg>',
}


def qr_path(text, border=3):
    """Encode `text` and return (module_count, SVG path data) as run-length rects."""
    qr = segno.make(text, error="m")
    rows = list(qr.matrix_iter(border=border))
    n = len(rows)
    parts = []
    for y, row in enumerate(rows):
        x = 0
        while x < n:
            if row[x]:
                run = 0
                while x + run < n and row[x + run]:
                    run += 1
                parts.append("M%d %dh%dv1h-%dz" % (x, y, run, run))
                x += run
            else:
                x += 1
    return n, "".join(parts)


def verify(n, d, expected):
    """Re-expand the path back into a matrix and compare against segno's own."""
    grid = [[0] * n for _ in range(n)]
    consumed = 0
    for m in re.finditer(r"M(\d+) (\d+)h(\d+)v1h-(\d+)z", d):
        x, y, run, back = map(int, m.groups())
        assert run == back
        consumed += m.end() - m.start()
        for i in range(run):
            grid[y][x + i] = 1
    assert consumed == len(d), "path contains unparsed segments"
    ref = [list(r) for r in segno.make(expected, error="m").matrix_iter(border=3)]
    return grid == ref


def main():
    qr = {}
    for key, text in PAYLOADS.items():
        n, d = qr_path(text)
        assert verify(n, d, text), "%s: path does not round-trip" % key
        qr[key] = {"n": n, "d": d}
        print("  %-10s %3d modules  ok" % (key, n))

    tabs, panels = [], []
    for i, (key, label, cap, sub) in enumerate(TABS):
        tabs.append(
            '<button class="tab%s" type="button" role="tab" id="tab-%s" '
            'aria-controls="panel-qr" aria-selected="%s" data-key="%s" '
            "onclick=\"pick('%s')\">%s<span>%s</span></button>"
            % (" is-on" if i == 0 else "", key, "true" if i == 0 else "false",
               key, key, ICONS[key], label))

        href, cta = LINKS[key]
        ext = "" if key == "card" else ' target="_blank" rel="noopener"'
        panels.append(
            '<div class="qrpanel%s" data-key="%s"%s>'
            '<div class="plate"><svg viewBox="0 0 %d %d" shape-rendering="crispEdges" '
            'role="img" aria-label="QR code &mdash; %s"><path d="%s" fill="#0D1214"/></svg></div>'
            '<div class="qrmeta"><p class="cap">%s</p><p class="sub mono">%s</p></div>'
            '<a class="cta" href="%s"%s>%s <span aria-hidden="true">&rarr;</span></a></div>'
            % (" is-on" if i == 0 else "", key, "" if i == 0 else " hidden",
               qr[key]["n"], qr[key]["n"], label, qr[key]["d"], cap, sub, href, ext, cta))

    tpl = io.open(os.path.join(ROOT, "tools", "template.html"), encoding="utf-8").read()
    html = tpl.replace("<!--TABS-->", "\n        ".join(tabs))
    html = html.replace("<!--PANELS-->", "\n        ".join(panels))
    # entity-encode everything non-ASCII so the page is charset-proof
    html = "".join(c if ord(c) < 128 else "&#%d;" % ord(c) for c in html)

    out = os.path.join(ROOT, "index.html")
    io.open(out, "w", encoding="utf-8").write(html)
    print("wrote %s (%d bytes)" % (out, len(html)))


if __name__ == "__main__":
    main()
