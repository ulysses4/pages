#!/usr/bin/env python3
"""Python twin of protect.js for machines without node.

Usage: protect.py <source.html> <out.html> <password> [title] [--no-home-link]
Same scheme: AES-256-GCM, key from PBKDF2-SHA256 (600k iterations), same
in-browser unlock wrapper. --no-home-link drops the "Home" anchor (for the
site root, where ../ would leave the site). Nothing secret is written.
"""

import base64
import hashlib
import json
import os
import sys

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def main():
    args = [a for a in sys.argv[1:] if a != "--no-home-link"]
    no_home = "--no-home-link" in sys.argv
    if len(args) < 3:
        sys.exit("usage: protect.py <src> <out> <password> [title] [--no-home-link]")
    src, out, password = args[:3]
    title = args[3] if len(args) > 3 else "Protected page"
    html = open(src, encoding="utf-8").read()
    salt, iv, iters = os.urandom(16), os.urandom(12), 600000
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iters, 32)
    ct = AESGCM(key).encrypt(iv, html.encode(), None)
    b64 = lambda b: base64.b64encode(b).decode()
    payload = json.dumps({"salt": b64(salt), "iv": b64(iv),
                          "iterations": iters, "ct": b64(ct)},
                         separators=(",", ":"))
    home = ('<a href="../">⌂ Home</a>' if not no_home else "")
    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body{{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#fafaf9;font:16px/1.5 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif;color:#1f2a37}}
  form{{background:#fff;border:1px solid #e5e7eb;border-radius:14px;padding:28px 26px;width:min(92vw,360px);box-shadow:0 4px 20px rgba(0,0,0,.05)}}
  h1{{font-size:18px;margin:0 0 4px}} p{{margin:0 0 16px;color:#6b7280;font-size:14px}}
  input{{width:100%;box-sizing:border-box;font-size:17px;padding:11px 12px;border:1px solid #d1d5db;border-radius:10px}}
  button{{margin-top:12px;width:100%;padding:11px;border:0;border-radius:10px;background:#1f2a37;color:#fff;font-size:16px;cursor:pointer}}
  .err{{color:#b91c1c;font-size:14px;margin-top:10px;min-height:20px}}
  a{{color:#6b7280;font-size:13px;display:block;text-align:center;margin-top:14px}}
</style></head><body>
<form id="f" autocomplete="off">
  <h1>{title}</h1><p>Enter the password to open this page.</p>
  <input id="pw" type="password" placeholder="Password" autofocus>
  <button type="submit">Open</button>
  <div class="err" id="err"></div>
  {home}<a href="#" onclick="location.replace(location.pathname+'?r='+Date.now());return false">↻ Refresh</a>
</form>
<script>
const P={payload};
const u8=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
async function unlock(pw){{
  const base=await crypto.subtle.importKey('raw',new TextEncoder().encode(pw),'PBKDF2',false,['deriveKey']);
  const key=await crypto.subtle.deriveKey({{name:'PBKDF2',salt:u8(P.salt),iterations:P.iterations,hash:'SHA-256'}},base,{{name:'AES-GCM',length:256}},false,['decrypt']);
  const pt=await crypto.subtle.decrypt({{name:'AES-GCM',iv:u8(P.iv)}},key,u8(P.ct));
  return new TextDecoder().decode(pt);
}}
document.getElementById('f').addEventListener('submit',async e=>{{
  e.preventDefault();
  const err=document.getElementById('err'); err.textContent='Checking…';
  try{{ const html=await unlock(document.getElementById('pw').value);
       try{{sessionStorage.setItem(location.pathname,document.getElementById('pw').value)}}catch(_){{}}
       document.open(); document.write(html); document.close(); }}
  catch(_){{ err.textContent='Wrong password.'; }}
}});
(async()=>{{ try{{ const s=sessionStorage.getItem(location.pathname); if(s){{ const html=await unlock(s); document.open(); document.write(html); document.close(); }} }}catch(_){{}} }})();
</script></body></html>"""
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w", encoding="utf-8").write(page)
    print(f"wrote {out} ({len(page)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
