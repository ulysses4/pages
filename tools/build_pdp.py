#!/usr/bin/env python3
"""Build src/pdp/index.html: the six PDP/PDT charts from ~/GitHub/PDP
embedded as base64 data-URIs, so the images live INSIDE the encrypted page
(the PDP repo is private; nothing is hotlinked). Run by LINUX_PDP.sh every
Thursday after the charts regenerate, then encrypted via tools/protect.js.
"""

import base64
import io
import os
from datetime import datetime

from PIL import Image

PDP = "/home/ulysses/GitHub/PDP/"
OUT = os.path.join(os.path.dirname(__file__), "..", "src", "pdp",
                   "index.html")
HOME = os.path.join(os.path.dirname(__file__), "..", "src", "home",
                    "index.html")

SECTIONS = [
    ("Positions", [("PDP_graph.png", "Positions"),
                   ("PDP_graph_seas.png", "Positions — seasonal"),
                   ("PDP_table.png", "Positions table")]),
    ("Transactions", [("PDT_graph.png", "Transactions"),
                      ("PDT_graph_seas.png", "Transactions — seasonal"),
                      ("PDT_table.png", "Transactions table")]),
]

LOCK_JS = ("try{localStorage.removeItem('pages:pw');"
           "sessionStorage.removeItem('pages:pw')}catch(e){};"
           "location.reload();return false")


def main():
    stamp = max(os.path.getmtime(PDP + f) for _, fs in SECTIONS
                for f, _ in fs)
    dt = datetime.fromtimestamp(stamp)
    asof = (f"(updated {dt:%A} at "
            f"{dt.strftime('%I:%M%p').lstrip('0')}, {dt:%m/%d/%Y})")
    body = []
    for head, files in SECTIONS:
        body.append(f'<h2>{head}</h2>')
        for f, label in files:
            # charts are flat-color line art: palette PNG / lossless WebP
            # shrink them 70-90% with no visible change (JPEG does neither)
            im = Image.open(PDP + f).convert("RGB")
            p1, p2 = io.BytesIO(), io.BytesIO()
            im.quantize(colors=256, method=2).save(p1, "PNG", optimize=True)
            im.save(p2, "WEBP", lossless=True, method=6)
            raw, mime = ((p1.getvalue(), "png")
                         if p1.tell() <= p2.tell()
                         else (p2.getvalue(), "webp"))
            b64 = base64.b64encode(raw).decode()
            body.append(
                f'<figure><img src="data:image/{mime};base64,{b64}" '
                f'alt="{label}" loading="lazy">'
                f'<figcaption>{label}</figcaption></figure>')
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PDP</title>
<style>
  :root{{--bg:#0a0a0a;--ink:#f3f4f6;--muted:#9ca3af;--line:#2a2a2a}}
  body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif}}
  main{{max-width:1100px;margin:0 auto;padding:40px 20px 60px}}
  .bar{{display:flex;justify-content:flex-start;gap:18px;margin-bottom:18px}}
  a.home{{color:var(--muted);text-decoration:none;font-size:14px;padding:6px 10px 6px 0}}
  a.home:hover{{color:var(--ink)}}
  h1{{font-size:26px;margin:0 0 2px;letter-spacing:-.01em}}
  .sub{{color:var(--muted);margin:0 0 26px;font-size:14px}}
  h2{{font-size:19px;margin:34px 0 10px;border-bottom:1px solid var(--line);padding-bottom:6px}}
  figure{{margin:0 0 26px;background:#fff;border-radius:12px;padding:10px}}
  img{{width:100%;height:auto;display:block;border-radius:6px}}
  figcaption{{color:#374151;font-size:13px;padding:8px 4px 2px}}
</style>
</head>
<body>
<main>
  <div class="bar"><a class="home" href="../">&#8962; Home</a>
    <a class="home" href="#" onclick="location.replace(location.pathname+'?r='+Date.now());return false" title="Reload latest version">&#8635; Refresh</a>
    <a class="home" href="#" onclick="{LOCK_JS}" title="Forget the password on this device">&#128274; Lock</a></div>
  <h1>PDP</h1>
  <p class="sub">{asof}</p>
  {chr(10).join(body)}
</main>
</body>
</html>"""
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write(html)
    print(f"-> {os.path.normpath(OUT)} ({len(html)/1e6:.1f} MB, {asof})")

    # mirror the stamp onto the landing page's PDP tile (caller re-encrypts
    # the home page whenever this file changes)
    import re
    h = open(HOME).read()
    h2 = re.sub(r"(<b>PDP</b><span>)[^<]*(</span>)",
                rf"\g<1>{asof}\g<2>", h)
    if h2 != h:
        open(HOME, "w").write(h2)
        print(f"-> {os.path.normpath(HOME)} (tile stamp refreshed)")


if __name__ == "__main__":
    main()
