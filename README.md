# pages

Static sites hosted on GitHub Pages. The landing page (`index.html`) links to each site; each site lives in its own folder and is AES-encrypted so it asks for a password in the browser before rendering.

- Plain sources live in `src/<name>/index.html` (git-ignored — never committed).
- `PW_LONDON=... ./build.sh` encrypts every site in `src/` into `<name>/index.html`.
- Add a site: drop `src/<name>/index.html`, add a card to `index.html`, run the build with `PW_<NAME>` set, commit.
