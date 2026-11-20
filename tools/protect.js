#!/usr/bin/env node
// Encrypt a static HTML page so it asks for a password in the browser before rendering.
// Usage: node tools/protect.js <source.html> <out.html> <password> [title]
// AES-256-GCM, key from PBKDF2-SHA256 (600k iterations). Nothing secret is written to the repo.
const fs = require('fs');
const { webcrypto } = require('crypto');
const { subtle } = webcrypto;

async function main() {
  const noHome = process.argv.includes('--no-home-link');
  const args = process.argv.slice(2).filter(a => a !== '--no-home-link');
  const [src, out, password, title = 'Protected page'] = args;
  if (!src || !out || !password) { console.error('usage: protect.js <src> <out> <password> [title] [--no-home-link]'); process.exit(1); }
  const html = fs.readFileSync(src, 'utf8');
  const salt = webcrypto.getRandomValues(new Uint8Array(16));
  const iv = webcrypto.getRandomValues(new Uint8Array(12));
  const iterations = 600000;
  const base = await subtle.importKey('raw', new TextEncoder().encode(password), 'PBKDF2', false, ['deriveKey']);
  const key = await subtle.deriveKey({ name: 'PBKDF2', salt, iterations, hash: 'SHA-256' }, base, { name: 'AES-GCM', length: 256 }, false, ['encrypt']);
  const ct = new Uint8Array(await subtle.encrypt({ name: 'AES-GCM', iv }, key, new TextEncoder().encode(html)));
  const b64 = (u8) => Buffer.from(u8).toString('base64');
  const payload = JSON.stringify({ salt: b64(salt), iv: b64(iv), iterations, ct: b64(ct) });
  const sig = b64(ct).slice(0, 32);   // version fingerprint for the freshness probe

  const page = `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title}</title>
<style>
  body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#0a0a0a;font:16px/1.5 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif;color:#f3f4f6}
  form{background:linear-gradient(160deg,#1f1f1f,#161616);border:1px solid #2a2a2a;border-radius:18px;padding:28px 26px;width:min(92vw,360px);box-shadow:0 12px 30px rgba(0,0,0,.5)}
  h1{font-size:18px;margin:0 0 4px} p{margin:0 0 16px;color:#9ca3af;font-size:14px}
  input{width:100%;box-sizing:border-box;font-size:17px;padding:11px 12px;border:1px solid #2a2a2a;border-radius:10px;background:#0f0f0f;color:#f3f4f6}
  input:focus{outline:none;border-color:#e11d48}
  button{margin-top:12px;width:100%;padding:11px;border:0;border-radius:10px;background:#e11d48;color:#fff;font-size:16px;cursor:pointer}
  .err{color:#f87171;font-size:14px;margin-top:10px;min-height:20px}
  a{color:#9ca3af;font-size:13px;display:block;text-align:center;margin-top:14px;text-decoration:none}
  a:hover{color:#f3f4f6}
</style></head><body>
<form id="f" autocomplete="off">
  <h1>${title}</h1><p>Enter the password to open this page.</p>
  <input id="pw" type="password" placeholder="Password" autofocus>
  <button type="submit">Open</button>
  <div class="err" id="err"></div>
  ${noHome ? '' : '<a href="../">⌂ Home</a>'}<a href="#" onclick="location.replace(location.pathname+'?r='+Date.now());return false">↻ Refresh</a>
</form>
<script>
const P=${payload};
const u8=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
// after rendering, probe the server copy in the background; if this page is a
// stale cache (its fingerprint is absent from the live copy), reload once with
// a cache-buster. 20s guard stops any reload loop.
const FRESH='<scr'+'ipt>(()=>{const C="${sig}";try{if((+sessionStorage.getItem("pages:fr")||0)>Date.now()-20000)return}catch(_){}fetch(location.pathname,{cache:"no-store"}).then(r=>r.ok?r.text():"").then(t=>{if(t&&t.indexOf(C)<0){try{sessionStorage.setItem("pages:fr",String(Date.now()))}catch(_){}location.replace(location.pathname+"?r="+Date.now())}}).catch(()=>{})})()</scr'+'ipt>';
async function unlock(pw){
  const base=await crypto.subtle.importKey('raw',new TextEncoder().encode(pw),'PBKDF2',false,['deriveKey']);
  const key=await crypto.subtle.deriveKey({name:'PBKDF2',salt:u8(P.salt),iterations:P.iterations,hash:'SHA-256'},base,{name:'AES-GCM',length:256},false,['decrypt']);
  const pt=await crypto.subtle.decrypt({name:'AES-GCM',iv:u8(P.iv)},key,u8(P.ct));
  return new TextDecoder().decode(pt);
}
document.getElementById('f').addEventListener('submit',async e=>{
  e.preventDefault();
  const err=document.getElementById('err'); err.textContent='Checking…';
  try{ const html=await unlock(document.getElementById('pw').value);
       try{localStorage.setItem('pages:pw',document.getElementById('pw').value)}catch(_){}
       document.open(); document.write(html+FRESH); document.close(); }
  catch(_){ err.textContent='Wrong password.'; }
});
(async()=>{ try{ const s=localStorage.getItem('pages:pw')||sessionStorage.getItem('pages:pw'); if(s){ const html=await unlock(s); document.open(); document.write(html+FRESH); document.close(); } }catch(_){} })();
</script></body></html>`;
  fs.mkdirSync(require('path').dirname(out), { recursive: true });
  fs.writeFileSync(out, page);
  console.log(`wrote ${out} (${(page.length/1024).toFixed(0)} KB)`);
}
main();
