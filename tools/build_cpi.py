#!/usr/bin/env python3
"""Build src/cpi/index.html: the five CPI tables that publish to Oculus
(1/2/3/4/13.pdf), embedded base64 so they open with no PDF password behind
the site gate. Run by LINUX_OCULUS.sh weekday mornings (hash-guarded),
then encrypted via protect.js. Also restamps the landing CPI tile.
"""

import base64
import os
import re
from datetime import datetime

CPI = "/home/ulysses/GitHub/CPI/"
OUT = os.path.join(os.path.dirname(__file__), "..", "src", "cpi",
                   "index.html")
HOME = os.path.join(os.path.dirname(__file__), "..", "src", "home",
                    "index.html")

TABLES = [
    ("Core_cond.pdf", "Core — conditional"),
    ("Core_full.pdf", "Core — full"),
    ("Core_goods_services.pdf", "Core goods vs services"),
    ("Food.pdf", "Food"),
    ("Core_ex_housing.pdf", "Core ex-housing"),
]

LOCK_JS = ("try{localStorage.removeItem('pages:pw');"
           "sessionStorage.removeItem('pages:pw')}catch(e){};"
           "location.reload();return false")


def main():
    dt = datetime.fromtimestamp(max(os.path.getmtime(CPI + f)
                                    for f, _ in TABLES))
    stamp = (f"{dt:%A} {dt.strftime('%I:%M%p').lstrip('0')}, "
             f"{dt:%m/%d/%Y}")
    rows, blobs = [], []
    for i, (f, label) in enumerate(TABLES):
        b64 = base64.b64encode(open(CPI + f, "rb").read()).decode()
        blobs.append(f'"{b64}"')
        rows.append(
            f'<div class="row"><span>{label}</span>'
            f'<button onclick="openPdf({i})">Open</button></div>')
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CPI</title>
<style>
  :root{{--bg:#0a0a0a;--ink:#f3f4f6;--muted:#9ca3af;--line:#2a2a2a;--accent:#e11d48}}
  body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif}}
  main{{max-width:760px;margin:0 auto;padding:40px 20px 60px}}
  .bar{{display:flex;justify-content:flex-start;gap:18px;margin-bottom:18px}}
  a.home{{color:var(--muted);text-decoration:none;font-size:14px;padding:6px 10px 6px 0}}
  a.home:hover{{color:var(--ink)}}
  h1{{font-size:26px;margin:0 0 2px;letter-spacing:-.01em}}
  .sub{{color:var(--muted);margin:0 0 22px;font-size:14px}}
  .row{{display:flex;align-items:center;justify-content:space-between;padding:15px 18px;background:linear-gradient(160deg,#1f1f1f,#161616);border:1px solid var(--line);border-radius:14px;margin-bottom:12px}}
  .row span{{font-size:17px}}
  button{{font-size:15px;padding:9px 20px;border:0;border-radius:10px;background:var(--accent);color:#fff;cursor:pointer}}
  iframe{{width:100%;min-height:72vh;border:1px solid var(--line);border-radius:10px;background:#fff;margin-top:20px;display:none}}
</style>
</head>
<body>
<main>
  <div class="bar"><a class="home" href="../">&#8962; Home</a>
    <a class="home" href="#" onclick="location.replace(location.pathname+'?r='+Date.now());return false" title="Reload latest version">&#8635; Refresh</a>
    <a class="home" href="#" onclick="{LOCK_JS}" title="Forget the password on this device">&#128274; Lock</a></div>
  <h1>CPI</h1>
  <p class="sub">US CPI tables &middot; as of {stamp}</p>
  {chr(10).join(rows)}
  <iframe id="viewer"></iframe>
</main>
<script>
const PDFS = [{",".join(blobs)}];
const urls = {{}};
function openPdf(i) {{
  if (!urls[i]) {{
    const blob = new Blob([Uint8Array.from(atob(PDFS[i]), c => c.charCodeAt(0))],
                          {{type: "application/pdf"}});
    urls[i] = URL.createObjectURL(blob);
  }}
  if (/iPhone|iPad/.test(navigator.userAgent)) location.href = urls[i];
  else {{
    const f = document.getElementById("viewer");
    f.style.display = "block"; f.src = urls[i];
    f.scrollIntoView({{behavior: "smooth"}});
  }}
}}
</script>
</body>
</html>"""
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write(html)
    print(f"-> {os.path.normpath(OUT)} ({len(html)/1e3:.0f} KB, as of {stamp})")

    tile = (f"(updated {dt:%A} at "
            f"{dt.strftime('%I:%M%p').lstrip('0')}, {dt:%m/%d/%Y})")
    h = open(HOME).read()
    h2 = re.sub(r"(<b>CPI</b><span>)[^<]*(</span>)",
                rf"\g<1>{tile}\g<2>", h)
    if h2 != h:
        open(HOME, "w").write(h2)
        print(f"-> {os.path.normpath(HOME)} (tile stamp refreshed)")


if __name__ == "__main__":
    main()
