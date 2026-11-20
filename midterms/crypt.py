#!/usr/bin/env python3
"""Encrypt/decrypt midterms data for the GitHub Pages site.

  MIDTERMS_PW=... python3 crypt.py encrypt [stem]   # <stem>.json -> <stem>.enc.json (default stem: data)
  MIDTERMS_PW=... python3 crypt.py decrypt [stem]

Format matches the page's WebCrypto code: PBKDF2-SHA256 (200k iters) -> AES-256-GCM.
data.json is gitignored; only data.enc.json is committed.
"""
import os, sys, json, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

HERE = os.path.dirname(os.path.abspath(__file__))
STEM = sys.argv[2] if len(sys.argv) > 2 else "data"
PLAIN = os.path.join(HERE, STEM + ".json")
ENC = os.path.join(HERE, STEM + ".enc.json")
ITER = 200_000

def key(pw: bytes, salt: bytes) -> bytes:
    return PBKDF2HMAC(hashes.SHA256(), 32, salt, ITER).derive(pw)

def main():
    pw = os.environ.get("MIDTERMS_PW", "").encode()
    if not pw:
        sys.exit("set MIDTERMS_PW")
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "encrypt":
        salt, iv = os.urandom(16), os.urandom(12)
        ct = AESGCM(key(pw, salt)).encrypt(iv, open(PLAIN, "rb").read(), None)
        b64 = lambda b: base64.b64encode(b).decode()
        json.dump({"v": 1, "iter": ITER, "salt": b64(salt), "iv": b64(iv), "ct": b64(ct)}, open(ENC, "w"))
        print("wrote", os.path.basename(ENC))
    elif mode == "decrypt":
        e = json.load(open(ENC))
        d = lambda s: base64.b64decode(s)
        pt = AESGCM(key(pw, d(e["salt"]))).decrypt(d(e["iv"]), d(e["ct"]), None)
        open(PLAIN, "wb").write(pt)
        print("wrote", os.path.basename(PLAIN))
    else:
        sys.exit("usage: crypt.py encrypt|decrypt")

if __name__ == "__main__":
    main()
