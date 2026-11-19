#!/usr/bin/env bash
# Rebuild every protected site: src/<name>/index.html -> <name>/index.html (encrypted).
# Passwords come from the environment: PW_<NAME> (uppercase), e.g. PW_LONDON=... ./build.sh
set -euo pipefail
cd "$(dirname "$0")"
# protect.py is a node-less twin of protect.js; use whichever runs
PROTECT="node tools/protect.js"
command -v node >/dev/null || PROTECT="python3 tools/protect.py"
for d in src/*/; do
  name=$(basename "$d"); var="PW_${name^^}"; pw="${!var:-}"
  if [ -z "$pw" ]; then echo "skip $name (set $var)"; continue; fi
  title="$(tr '[:lower:]' '[:upper:]' <<< "${name:0:1}")${name:1}"
  if [ "$name" = "home" ]; then
    # the landing page itself: encrypted output goes to the site root
    $PROTECT "$d/index.html" "index.html" "$pw" "Home" --no-home-link
  else
    $PROTECT "$d/index.html" "$name/index.html" "$pw" "$title"
  fi
done
