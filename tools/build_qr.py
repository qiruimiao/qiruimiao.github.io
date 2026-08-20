#!/usr/bin/env python3
"""Rebuild index.html from tools/template.html with freshly generated QR codes.

    pip install segno
    python3 tools/build_qr.py

Edit CONTACT / PAYLOADS below to change what the QR codes encode, then re-run.
Every QR is baked into the page as a static SVG path, so the published page
never calls an external QR service.
"""
import base64, io, json, os, re, sys

try:
    import segno
except ImportError:
    sys.exit("segno is required:  pip install segno")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- what the QR codes encode -------------------------------------------------
# WhatsApp: the "add me" invite link from WhatsApp > Settings > QR icon > share.
# It can be reset from inside WhatsApp; if you reset it, paste the new one here
# and re-run this script.
WHATSAPP = "https://wa.me/qr/JVVGJ6DVEJS3P1"

PAYLOADS = {
    "whatsapp":  WHATSAPP,
    "linkedin":  "https://www.linkedin.com/in/qirui-miao-b684bb381/",
    "instagram": "https://www.instagram.com/jecsrry/",
    "github":    "https://github.com/qiruimiao",
}

TABS = [
    ("whatsapp",  "WhatsApp",  "Scan to add me on WhatsApp", "wa.me/qr/JVVGJ6DVEJS3P1"),
    ("linkedin",  "LinkedIn",  "Scan to open my LinkedIn",   "in/qirui-miao"),
    ("instagram", "Instagram", "Scan to open my Instagram",  "@jecsrry"),
    ("github",    "GitHub",    "Scan to open my GitHub",     "github.com/qiruimiao"),
]

LINKS = {
    "whatsapp":  (WHATSAPP, "Open WhatsApp"),
    "linkedin":  ("https://www.linkedin.com/in/qirui-miao-b684bb381/", "Open LinkedIn"),
    "instagram": ("https://www.instagram.com/jecsrry/", "Open Instagram"),
    "github":    ("https://github.com/qiruimiao", "Open GitHub"),
}

ICONS = {
    "whatsapp": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.16-.17.2-.35.22-.64.08-.3-.15-1.26-.46-2.4-1.48-.88-.79-1.48-1.76-1.65-2.06-.17-.3-.02-.46.13-.6.13-.14.3-.35.45-.52.15-.18.2-.3.3-.5.1-.2.05-.37-.03-.52-.07-.15-.67-1.61-.91-2.21-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.8.37-.27.3-1.04 1.02-1.04 2.48 0 1.46 1.07 2.87 1.22 3.07.15.2 2.1 3.2 5.08 4.49.71.3 1.26.49 1.69.62.71.23 1.36.2 1.87.12.57-.09 1.76-.72 2-1.41.25-.7.25-1.29.18-1.42-.08-.12-.28-.2-.57-.34m-5.42 7.4h-.01a9.87 9.87 0 0 1-5.03-1.38l-.36-.21-3.74.98 1-3.65-.24-.37a9.86 9.86 0 0 1-1.51-5.26c0-5.45 4.44-9.89 9.89-9.89 2.64 0 5.12 1.03 6.99 2.9a9.83 9.83 0 0 1 2.89 6.99c0 5.45-4.44 9.89-9.88 9.89m8.41-18.3A11.82 11.82 0 0 0 12.05 0C5.5 0 .16 5.34.16 11.89c0 2.1.55 4.14 1.59 5.95L.06 24l6.3-1.65a11.88 11.88 0 0 0 5.69 1.45c6.55 0 11.89-5.34 11.89-11.89a11.82 11.82 0 0 0-3.48-8.42Z"/></svg>',
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



def portrait_tag():
    """Embed assets/portrait.{jpg,jpeg,png,webp} as a data URI, if present.

    Embedding rather than linking keeps index.html a single self-contained file,
    so the same page works on GitHub Pages, saved locally, and offline.
    Keep the source image small (400x400 is plenty) -- base64 adds ~33%.
    """
    for ext, mime in (("jpg", "image/jpeg"), ("jpeg", "image/jpeg"),
                      ("png", "image/png"), ("webp", "image/webp")):
        path = os.path.join(ROOT, "assets", "portrait." + ext)
        if os.path.exists(path):
            with open(path, "rb") as fh:
                raw = fh.read()
            b64 = base64.b64encode(raw).decode("ascii")
            print("  portrait   %s (%.0f KB embedded)" % (os.path.basename(path), len(b64) / 1024))
            return ('<img class="portrait" src="data:%s;base64,%s" '
                    'alt="Qirui Miao" width="92" height="92">' % (mime, b64))
    print("  portrait   none found (drop one in assets/portrait.jpg to add it)")
    return ""


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
    html = html.replace("<!--PORTRAIT-->", portrait_tag())
    # entity-encode everything non-ASCII so the page is charset-proof
    html = "".join(c if ord(c) < 128 else "&#%d;" % ord(c) for c in html)

    out = os.path.join(ROOT, "index.html")
    io.open(out, "w", encoding="utf-8").write(html)
    print("wrote %s (%d bytes)" % (out, len(html)))


if __name__ == "__main__":
    main()
