#!/usr/bin/env python3
"""Build the Fedspeak page from a Markdown digest and encrypt it.

Usage: PW_FEDSPEAK=... python3 tools/build_fedspeak.py digest.md

Writes src/fedspeak/index.html (plain, git-ignored), fedspeak/index.html
(encrypted via protect.js) and fedspeak/stamp.json. The stamp is public and
holds only the update time, so the landing tile can show it without this
build having to re-encrypt the home page.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SRC = os.path.join(ROOT, "src", "fedspeak", "index.html")
OUT = os.path.join(ROOT, "fedspeak", "index.html")
STAMP = os.path.join(ROOT, "fedspeak", "stamp.json")
TITLE = "Dot Plot Detective"
TZ = ZoneInfo("America/New_York")

LOCK_JS = ("try{localStorage.removeItem('pages:pw');"
           "sessionStorage.removeItem('pages:pw')}catch(e){};"
           "location.reload();return false")

UNSAFE = re.compile(r"<\s*(script|iframe|object|embed|style|link|meta|form)\b"
                    r"|\son\w+\s*=|javascript:", re.I)


def to_html(md_text):
    try:
        import markdown
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet",
                        "markdown"], check=True)
        import markdown
    return markdown.markdown(md_text, extensions=["tables", "sane_lists"])


def page(body, stamp_s):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<style>
  :root{{--bg:#0a0a0a;--ink:#f3f4f6;--muted:#9ca3af;--line:#2a2a2a;--accent:#e11d48}}
  body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif}}
  main{{max-width:860px;margin:0 auto;padding:40px 16px 60px}}
  .bar{{display:flex;justify-content:flex-start;gap:18px;margin-bottom:18px}}
  a.home{{color:var(--muted);text-decoration:none;font-size:14px;padding:6px 10px 6px 0}}
  a.home:hover{{color:var(--ink)}}
  h1{{font-size:26px;margin:0 0 2px;letter-spacing:-.01em}}
  .sub{{color:var(--muted);margin:0 0 22px;font-size:14px}}
  article h1{{font-size:21px;margin:26px 0 8px}}
  article h2{{font-size:18px;margin:34px 0 10px;padding-top:18px;border-top:1px solid var(--line);color:var(--accent);letter-spacing:.02em}}
  article h3{{font-size:16px;margin:24px 0 8px}}
  article a{{color:#fda4af}}
  article li{{margin:6px 0}}
  article hr{{border:0;border-top:1px solid var(--line);margin:28px 0}}
  article code{{background:#1f1f1f;padding:1px 5px;border-radius:5px;font-size:14px}}
  .tbl{{overflow-x:auto;margin:14px 0}}
  table{{border-collapse:collapse;font-size:14px;min-width:640px}}
  th,td{{border:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}}
  th{{background:#161616;color:var(--muted);font-weight:600}}
</style>
</head>
<body>
<main>
  <div class="bar"><a class="home" href="../">&#8962; Home</a>
    <a class="home" href="#" onclick="location.replace(location.pathname+'?r='+Date.now());return false" title="Reload latest version">&#8635; Refresh</a>
    <a class="home" href="#" onclick="{LOCK_JS}" title="Forget the password on this device">&#128274; Lock</a></div>
  <h1>{TITLE}</h1>
  <p class="sub">Fedspeak since the last FOMC &middot; as of {stamp_s}</p>
  <article>
{body}
  </article>
</main>
</body>
</html>"""


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: build_fedspeak.py <digest.md>")
    pw = os.environ.get("PW_FEDSPEAK") or os.environ.get("PW_SITE")
    if not pw:
        sys.exit("fedspeak: set PW_FEDSPEAK (the site password); nothing published")
    body = to_html(open(sys.argv[1], encoding="utf-8").read())
    if UNSAFE.search(body):
        sys.exit("fedspeak: digest contains active HTML; refusing to publish")
    body = body.replace("<table>", '<div class="tbl"><table>').replace(
        "</table>", "</table></div>")
    body = body.replace('<a href="http', '<a target="_blank" rel="noopener" href="http')

    now = datetime.now(TZ)
    clock = now.strftime("%I:%M%p").lstrip("0")
    stamp_s = f"{now:%A} {clock}, {now:%m/%d/%Y}"
    os.makedirs(os.path.dirname(SRC), exist_ok=True)
    with open(SRC, "w", encoding="utf-8") as f:
        f.write(page(body, stamp_s))
    subprocess.run(["node", os.path.join(ROOT, "tools", "protect.js"),
                    SRC, OUT, pw, TITLE], check=True)
    with open(STAMP, "w") as f:
        json.dump({"updated": now.isoformat(timespec="seconds"),
                   "tile": f"(updated {now:%A} at {clock}, {now:%m/%d/%Y})"}, f)
        f.write("\n")
    print(f"fedspeak: published, as of {stamp_s}")


if __name__ == "__main__":
    main()
