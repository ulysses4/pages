#!/usr/bin/env bash
# Rebuild every protected site: src/<name>/index.html -> <name>/index.html (encrypted).
# Passwords come from the environment: PW_<NAME> (uppercase), e.g. PW_LONDON=... ./build.sh
set -euo pipefail
cd "$(dirname "$0")"
for d in src/*/; do
  name=$(basename "$d"); var="PW_${name^^}"; pw="${!var:-}"
  if [ -z "$pw" ]; then echo "skip $name (set $var)"; continue; fi
  title=$(sed -n 's:.*<title>\(.*\)</title>.*:\1:p' "$d/index.html" | head -1)
  node tools/protect.js "$d/index.html" "$name/index.html" "$pw" "${title:-$name}"
done
