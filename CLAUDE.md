# Instructions for Claude sessions on this repo

Read `NOTES.md` first: it has the links, file layout, data formats, game formulas and past decisions.

- Edit `src/template.html` and the files in `src/data/`, never `index.html` directly.
- After a change: `python3 src/build.py`, then `node tests/core-test.js` (all presets must say `ok`), then check the page in a headless browser (Chromium via Playwright) at desktop and 390px width with no horizontal scroll and no console errors.
- To update the Claude artifact, publish `dist/meta-builder.html` to https://claude.ai/artifact/BoupUctZcdQwYCUpkDoyFn.
- The private `itsmrchickenss/Projects` repo has an older copy in `deepwoken-shrine-planner/index.html`. Update it too if the owner asks.
- Keep share links backward compatible (`decodeBuild`), and keep game data credited to deepwoken.co.
- Commit messages end with the `Co-Authored-By` and `Claude-Session` trailer lines.
