# Instructions for Claude sessions on this repo

Read `NOTES.md` first: it has the links, file layout, data formats, game formulas and past decisions.

- Edit `src/template.html` and the files in `src/data/`, never `index.html` directly.
- After a change: `python3 src/build.py`, then `node tests/core-test.js` (all presets must say `ok`), then check the page in a headless browser (Chromium via Playwright) at desktop and 390px width with no horizontal scroll and no console errors (`python3 tests/browser/layout.py`, plus the other `tests/browser/` scripts that touch what changed).
- Follow the owner's rules in NOTES.md ("Owner's rules and preferences"): shrine at Power 8+, never raise an attribute again after the shrine, stats-only presets, no elemental armor, 500 HP / 50% physical armor, don't bypass deepwoken.co's block, and so on.
- Every update the owner asks for is a new version (+0.01; pre-release v0.x, the owner sets v1.0 at release): add a `## vX | YYYY-MM-DD` entry with `- change` lines at the top of `src/data/versions.txt`. The build puts the newest version on the badge next to the title, and clicking the badge shows that history. Write the lines for players, in plain words. Commit and push every version.
- If formulas or game data change, regenerate the workbook: `node tools/formulas/dump.js && python3 tools/formulas/build.py`, recalc it, commit `docs/Meta Builder formulas.xlsx`.
- To update the Claude artifact, publish `dist/meta-builder.html` to https://claude.ai/artifact/BoupUctZcdQwYCUpkDoyFn.
- Refresh the handoff page automatically every 10 versions (v0.30, v0.40, v0.50…), and otherwise only when the owner asks: `python3 tools/handoff.py`, then publish `dist/handoff.html` to https://claude.ai/artifact/YBSQSo98nCQC84rkSZVZE3.
- The private `itsmrchickenss/Projects` repo has an older copy in `deepwoken-shrine-planner/index.html`. Update it too if the owner asks.
- Keep share links backward compatible (`decodeBuild`), and keep game data credited to deepwoken.co.
- Commit messages end with the `Co-Authored-By` and `Claude-Session` trailer lines.
