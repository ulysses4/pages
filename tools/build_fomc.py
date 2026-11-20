#!/usr/bin/env python3
"""Build src/fomc/index.html: UST yields with every FOMC meeting marked
(hike/cut/hold) plus the two reaction packs (dots + futures) embedded as
PDFs. Data from ~/GitHub/SOFR (research/ust_yields.csv, fomc_dates.csv,
fomc_data.json ff_base); pre-2024 fed-funds path hardcoded from the
public record. Run by LINUX_FOMC_FUTURES.sh nightly; exit 3 = unchanged.
"""

import base64
import io
import json
import os
import re
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from stamps import stamp

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from PIL import Image

sns.set()
SOFR = "/home/ulysses/GitHub/SOFR/"
OUT = os.path.join(os.path.dirname(__file__), "..", "src", "fomc",
                   "index.html")
HOME = os.path.join(os.path.dirname(__file__), "..", "src", "home",
                    "index.html")
DEEP = sns.color_palette("deep")

# upper-bound changes before fomc_data.json's ff_base coverage begins
FF_PRE = [("2013-01-01", 0.25), ("2015-12-16", 0.50), ("2016-12-14", 0.75),
          ("2017-03-15", 1.00), ("2017-06-14", 1.25), ("2017-12-13", 1.50),
          ("2018-03-21", 1.75), ("2018-06-13", 2.00), ("2018-09-26", 2.25),
          ("2018-12-19", 2.50), ("2019-07-31", 2.25), ("2019-09-18", 2.00),
          ("2019-10-30", 1.75), ("2020-03-03", 1.25), ("2020-03-15", 0.25),
          ("2022-03-16", 0.50), ("2022-05-04", 1.00), ("2022-06-15", 1.75),
          ("2022-07-27", 2.50), ("2022-09-21", 3.25), ("2022-11-02", 4.00),
          ("2022-12-14", 4.50), ("2023-02-01", 4.75), ("2023-03-22", 5.00),
          ("2023-05-03", 5.25), ("2023-07-26", 5.50)]

LOCK_JS = ("try{localStorage.removeItem('pages:pw');"
           "sessionStorage.removeItem('pages:pw')}catch(e){};"
           "location.reload();return false")


def ff_series():
    steps = [(pd.Timestamp(d), u - 0.125) for d, u in FF_PRE]  # midpoints
    base = json.load(open(SOFR + "fomc_data.json"))["ff"]
    for d, (lo, hi) in sorted(base.items()):
        steps.append((pd.Timestamp(d), (lo + hi) / 2))
    s = pd.Series(dict(steps)).sort_index()
    return s[~s.index.duplicated(keep="last")]


def png_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    im = Image.open(buf).convert("RGB")
    out = io.BytesIO()
    im.quantize(colors=256, method=2).save(out, "PNG", optimize=True)
    return base64.b64encode(out.getvalue()).decode()


def chart(y, ff, meets, actions, t0, title):
    yy = y[y.index >= t0]
    fig, ax = plt.subplots(figsize=(11, 5.2))
    for col, c in zip(["2 Yr", "10 Yr", "30 Yr"], (DEEP[0], DEEP[1], DEEP[2])):
        ax.plot(yy.index, yy[col], lw=1.2, color=c, label=col)
    ffp = ff.reindex(ff.index.union(yy.index[-1:])).ffill()
    ffp = ffp[ffp.index >= t0]
    ax.step(ffp.index, ffp.values, where="post", color="0.25", lw=1.0,
            alpha=0.8, label="FF target mid")
    for d in meets:
        if d < t0:
            continue
        a = actions.get(d, 0)
        lvl = ff.asof(d)
        if a > 0:
            ax.scatter([d], [lvl], marker="^", s=46, color="#b22222",
                       zorder=5, edgecolor="white", linewidth=0.5)
        elif a < 0:
            ax.scatter([d], [lvl], marker="v", s=46, color="#2a7a2a",
                       zorder=5, edgecolor="white", linewidth=0.5)
        else:
            ax.scatter([d], [lvl], marker="o", s=14, color="0.45", zorder=5)
    ax.set_title(title, loc="left", fontweight="bold", fontsize=12,
                 color=DEEP[0])
    ax.legend(fontsize=8, ncol=4, loc="upper left")
    ax.set_ylabel("%", fontsize=9)
    ax.margins(x=0.01)
    return fig


def main():
    srcs = [SOFR + "research/ust_yields.csv", SOFR + "research/fomc_dates.csv",
            SOFR + "fomc_data.json", SOFR + "FOMC_dots_reactions.pdf",
            SOFR + "FOMC_futures_reactions.pdf"]
    dt, changed = stamp("fomc", srcs)
    if not changed and os.path.exists(OUT):
        print(f"fomc: unchanged since {dt:%m/%d %H:%M}; nothing to publish")
        sys.exit(3)
    stamp_s = (f"{dt:%A} {dt.strftime('%I:%M%p').lstrip('0')}, "
               f"{dt:%m/%d/%Y}")

    y = pd.read_csv(SOFR + "research/ust_yields.csv", index_col=0,
                    parse_dates=True)
    meets = pd.to_datetime(
        pd.read_csv(SOFR + "research/fomc_dates.csv", header=None)[0]).tolist()
    ff = ff_series()
    actions = {}
    for d in meets:
        before = ff.asof(d - pd.Timedelta(days=1))
        after = ff.asof(d)   # a change made AT this meeting is dated on d
        if pd.isna(before) or pd.isna(after):
            actions[d] = 0
        else:
            actions[d] = int(bool(after > before)) - int(bool(after < before))
    n_hike = sum(1 for v in actions.values() if v > 0)
    n_cut = sum(1 for v in actions.values() if v < 0)

    img_full = png_b64(chart(y, ff, meets, actions, pd.Timestamp("2013-01-01"),
                       "UST yields and the policy path, 2013-present "
                       "(▲ hike  ▼ cut  · hold)"))
    img_2y = png_b64(chart(y, ff, meets, actions,
                     y.index[-1] - pd.DateOffset(years=2),
                     "Trailing two years (▲ hike  ▼ cut  · hold)"))

    pdfs = []
    for f, label in (("FOMC_futures_reactions.pdf",
                      "Futures reactions pack (per-meeting bars)"),
                     ("FOMC_dots_reactions.pdf",
                      "SEP dots & intraday OIS reactions table")):
        b64 = base64.b64encode(open(SOFR + f, "rb").read()).decode()
        pdfs.append((label, b64))
    rows = "\n".join(
        f'<div class="row"><span>{label}</span>'
        f'<button onclick="openPdf({i})">Open</button></div>'
        for i, (label, _) in enumerate(pdfs))
    blobs = ",".join(f'"{b}"' for _, b in pdfs)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FOMC</title>
<style>
  :root{{--bg:#0a0a0a;--ink:#f3f4f6;--muted:#9ca3af;--line:#2a2a2a;--accent:#e11d48}}
  body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif}}
  main{{max-width:1100px;margin:0 auto;padding:40px 20px 60px}}
  .bar{{display:flex;justify-content:flex-start;gap:18px;margin-bottom:18px}}
  a.home{{color:var(--muted);text-decoration:none;font-size:14px;padding:6px 10px 6px 0}}
  a.home:hover{{color:var(--ink)}}
  h1{{font-size:26px;margin:0 0 2px;letter-spacing:-.01em}}
  .sub{{color:var(--muted);margin:0 0 22px;font-size:14px}}
  figure{{margin:0 0 24px;background:#fff;border-radius:12px;padding:10px}}
  img{{width:100%;height:auto;display:block;border-radius:6px}}
  figcaption{{color:#374151;font-size:13px;padding:8px 4px 2px}}
  .row{{display:flex;align-items:center;justify-content:space-between;padding:15px 18px;background:linear-gradient(160deg,#1f1f1f,#161616);border:1px solid var(--line);border-radius:14px;margin-bottom:12px}}
  .row span{{font-size:17px}}
  button{{font-size:15px;padding:9px 20px;border:0;border-radius:10px;background:var(--accent);color:#fff;cursor:pointer}}
</style>
</head>
<body>
<main>
  <div class="bar"><a class="home" href="../">&#8962; Home</a>
    <a class="home" href="#" onclick="location.replace(location.pathname+'?r='+Date.now());return false" title="Reload latest version">&#8635; Refresh</a>
    <a class="home" href="#" onclick="{LOCK_JS}" title="Forget the password on this device">&#128274; Lock</a></div>
  <h1>FOMC</h1>
  <p class="sub">Market reaction to Fed meetings &middot; {len(meets)} meetings since 2013
    ({n_hike} hikes, {n_cut} cuts) &middot; as of {stamp_s}</p>
  <figure><img src="data:image/png;base64,{img_full}" alt="Yields with FOMC meetings, 2013-present" loading="lazy"></figure>
  <figure><img src="data:image/png;base64,{img_2y}" alt="Yields with FOMC meetings, trailing two years" loading="lazy"></figure>
  {rows}
  <iframe id="viewer" style="width:100%;min-height:72vh;border:1px solid var(--line);border-radius:10px;background:#fff;margin-top:20px;display:none"></iframe>
</main>
<script>
const PDFS = [{blobs}];
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
    print(f"-> {os.path.normpath(OUT)} ({len(html)/1e6:.1f} MB, as of {stamp_s})")

    tile = (f"(updated {dt:%A} at "
            f"{dt.strftime('%I:%M%p').lstrip('0')}, {dt:%m/%d/%Y})")
    h = open(HOME).read()
    h2 = re.sub(r"(<b>FOMC</b><span>)[^<]*(</span>)",
                rf"\g<1>{tile}\g<2>", h)
    if h2 != h:
        open(HOME, "w").write(h2)
        print(f"-> {os.path.normpath(HOME)} (tile stamp refreshed)")


if __name__ == "__main__":
    main()
