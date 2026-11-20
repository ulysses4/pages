# pages

Static sites hosted on GitHub Pages. The landing page (`index.html`) links to each site; each site lives in its own folder and is AES-encrypted so it asks for a password in the browser before rendering.

- Plain sources live in `src/<name>/index.html` (git-ignored — never committed).
- `PW_LONDON=... ./build.sh` encrypts every site in `src/` into `<name>/index.html`.
- Add a site: drop `src/<name>/index.html`, add a card to the landing source (`src/home/index.html`), run the build with `PW_<NAME>` set, commit. The landing page itself is encrypted (`src/home` -> root `index.html`, built with `--no-home-link`).

## Tile convention (landing page)

Every tile follows the same format:

- `<b>` = the short site name (e.g. `PDP`, `SDR`, `London`).
- `<span>` (second line) = the update stamp, exactly: `(updated <Weekday> at <h:MM>AM/PM, <MM/DD/YYYY>)` — e.g. `(updated Thursday at 8:15PM, 11/19/2026)`. For auto-updating sites, the site's `tools/build_<name>.py` regex-replaces the span (`<b>NAME</b><span>...</span>`) in `src/home/index.html` from the source data's mtime, and the cron that rebuilds the site also re-encrypts the home page. Static sites may use a short description instead.
- An inline SVG icon in `.top`, red/grey palette (`#e11d48`/`#9ca3af`).

Every page's top bar carries, left-aligned: `⌂ Home · ↻ Refresh · 🔒 Lock` (Lock clears the shared `pages:pw` from localStorage; copy the bar from an existing source — it is not auto-injected).

## Fedspeak (cloud-built)

`fedspeak/` is rebuilt by a cloud scheduled task from the private `ulysses4/Fedspeak` repo, not by the local cron: its `build.py --publish` encrypts the page into `fedspeak/index.html` with `tools/protect.js` and writes `fedspeak/stamp.json` (public, update time only). That build never touches the home page, so the tile's stamp comes from `stamp.json` rather than from `src/home/index.html`.
