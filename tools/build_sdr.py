#!/usr/bin/env python3
"""Build src/sdr/index.html: today's SDR inflation-tables PDF embedded as
base64 inside the page, so after the site gate decrypts it the report opens
with NO separate PDF password. Run by LINUX_SDR_OCULUS.sh (5-min weekday
cadence, hash-guarded on the source PDF), then encrypted via protect.js.
"""

import base64
import os
from datetime import datetime

SRC = "/home/ulysses/GitHub/SDR/daily/US_inflation_tables_today.pdf"
OUT = os.path.join(os.path.dirname(__file__), "..", "src", "sdr",
                   "index.html")
HOME = os.path.join(os.path.dirname(__file__), "..", "src", "home",
                    "index.html")

LOCK_JS = ("try{localStorage.removeItem('pages:pw');"
           "sessionStorage.removeItem('pages:pw')}catch(e){};"
           "location.reload();return false")


def main():
    dt = datetime.fromtimestamp(os.path.getmtime(SRC))
    stamp = (f"{dt:%A} {dt.strftime('%I:%M%p').lstrip('0')}, "
             f"{dt:%m/%d/%Y}")
    b64 = base64.b64encode(open(SRC, "rb").read()).decode()
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SDR</title>
<style>
  :root{{--bg:#0a0a0a;--ink:#f3f4f6;--muted:#9ca3af;--line:#2a2a2a;--accent:#e11d48}}
  body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif}}
  main{{max-width:1100px;margin:0 auto;padding:40px 20px 60px;display:flex;flex-direction:column;min-height:calc(100vh - 100px)}}
  .bar{{display:flex;justify-content:flex-start;gap:18px;margin-bottom:18px}}
  a.home{{color:var(--muted);text-decoration:none;font-size:14px;padding:6px 10px 6px 0}}
  a.home:hover{{color:var(--ink)}}
  h1{{font-size:26px;margin:0 0 2px;letter-spacing:-.01em}}
  .sub{{color:var(--muted);margin:0 0 22px;font-size:14px}}
  button{{align-self:flex-start;font-size:17px;padding:13px 22px;border:0;border-radius:12px;background:var(--accent);color:#fff;cursor:pointer}}
  iframe{{flex:1;width:100%;min-height:70vh;border:1px solid var(--line);border-radius:10px;background:#fff;margin-top:22px}}
</style>
</head>
<body>
<main>
  <div class="bar"><a class="home" href="../">&#8962; Home</a>
    <a class="home" href="#" onclick="location.replace(location.pathname+'?r='+Date.now());return false" title="Reload latest version">&#8635; Refresh</a>
    <a class="home" href="#" onclick="{LOCK_JS}" title="Forget the password on this device">&#128274; Lock</a></div>
  <h1>SDR</h1>
  <p class="sub">Today&#8217;s US inflation swap tables &middot; as of {stamp}</p>
  <button id="open">Open report (PDF)</button>
  <div id="holder"></div>
</main>
<script>
const PDF = "{b64}";
const blob = new Blob([Uint8Array.from(atob(PDF), c => c.charCodeAt(0))],
                      {{type: "application/pdf"}});
const url = URL.createObjectURL(blob);
document.getElementById("open").onclick = () => location.href = url;
// desktop browsers render it inline below; iOS uses the button
if (!/iPhone|iPad/.test(navigator.userAgent)) {{
  const f = document.createElement("iframe");
  f.src = url;
  document.getElementById("holder").appendChild(f);
}}
</script>
</body>
</html>"""
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write(html)
    print(f"-> {os.path.normpath(OUT)} ({len(html)/1e3:.0f} KB, as of {stamp})")

    # mirror the stamp onto the landing page's SDR tile (PDP-tile format;
    # caller re-encrypts the home page alongside this one)
    import re
    tile = (f"(updated {dt:%A} at "
            f"{dt.strftime('%I:%M%p').lstrip('0')}, {dt:%m/%d/%Y})")
    h = open(HOME).read()
    h2 = re.sub(r"(<b>SDR</b><span>)[^<]*(</span>)",
                rf"\g<1>{tile}\g<2>", h)
    if h2 != h:
        open(HOME, "w").write(h2)
        print(f"-> {os.path.normpath(HOME)} (tile stamp refreshed)")


if __name__ == "__main__":
    main()
