# Meta Builder app

The same planner as the website, packaged two ways. Everything is JavaScript (Node.js), so the desktop app and a future hosted site share one code base.

| | What it is | How to run it |
|---|---|---|
| **Desktop app** | Electron app for Mac and Windows | Download from the repo's [Releases](https://github.com/itsmrchickenss/meta-builder/releases/latest) |
| **Web server** | `server.js`, no dependencies | `npm start` (or Docker), then open http://localhost:3000 |

The page itself is built from `src/` by `python3 src/build.py`, which also writes `app/www/index.html` and sets this app's version from `src/data/versions.txt` (v0.32 → 0.32.0).

## Desktop app

**Download:** every push to `main` builds the app on GitHub (Actions → "Desktop app") and publishes a release named after the version:

- **Mac:** `Meta-Builder-<version>-mac-universal.dmg` (Apple Silicon and Intel). The app isn't notarized by Apple, so the first time, right-click the app → Open → Open (or System Settings → Privacy & Security → Open Anyway).
- **Windows:** `Meta-Builder-<version>-Setup.exe` installs it; `Meta-Builder-<version>-Portable.exe` runs without installing. The app isn't code-signed, so the first time Windows may show "Windows protected your PC": click More info → Run anyway.

**Updates:** the app keeps itself up to date. When it opens (and every few hours) it fetches the latest planner page from the website, checks it, and asks whether to reload now or use it next time. If a release changes the app itself, it says so and opens the download page. Turn this off with Help → Update Automatically; Check for Updates is in the app menu (Mac) or Help menu (Windows).

Builds, presets and themes are saved inside the app. Links to deepwoken.co, the wiki and share links open in your normal browser. Share links point to the website.

**Build it yourself** (on the computer you're building for):

```bash
python3 src/build.py          # from the repo root
cd app
npm install
npm run desktop               # try it
npm run dist:mac              # or dist:win → files land in app/release/
```

## Web server

```bash
python3 src/build.py          # from the repo root (a fresh clone already has a built index.html)
cd app
npm start                     # http://localhost:3000  (PORT and HOST change where it listens)
npm test                      # checks the server
```

It serves the page with gzip and ETags, plus `/healthz` (returns `ok`) and `/version` for hosting platforms.

**Host it later**, any of these work:

- **Docker** (any VPS, Fly.io, Railway, Render…): from the repo root, `docker build -f app/Dockerfile -t meta-builder .` then `docker run -p 3000:3000 meta-builder`.
- **Plain Node** (Render, Railway, a VPS): root directory `app`, start command `npm start`, health check path `/healthz`.
- Put it behind HTTPS (most hosts do this for you). Share links automatically use whatever address the site is served from.

## Notes

- The bug/suggestion form sends through Web3Forms, which is registered to the GitHub Pages address. From the desktop app or a new domain it may be refused until that domain is added in Web3Forms; the app's Help menu links to GitHub Issues instead.
- Reading builds from screenshots downloads its text reader (Tesseract.js) from the internet the first time, the same as the website.
