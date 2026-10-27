// Auto-update for the desktop app, in two layers that both work without paid code signing:
//  1. Page updates (almost every release): the planner page is downloaded from the website, checked, saved in the
//     app's data folder and used instead of the built-in copy whenever it is newer.
//  2. App updates (rare: when the desktop app code itself changes): every page says which app version it wants
//     (`dwshell`); if that is newer than this app, the person is told and pointed at the download.
// Plain Node (no Electron imports) so it can be tested with `node test-updater.js`.
'use strict';
const fs = require('fs');
const path = require('path');

const PAGE_URL = 'https://itsmrchickenss.github.io/meta-builder/index.html';
const RELEASES_URL = 'https://github.com/itsmrchickenss/meta-builder/releases/latest';
const MIN_PAGE_BYTES = 200 * 1024; // the real page is ~580 KB; anything far smaller is an error page

// "v0.33" from the version badge next to the title
function pageVersion(html) {
  const m = /id="verbtn"[^>]*>v(\d+(?:\.\d+)*)</.exec(html);
  return m ? m[1] : null;
}
// the app version the page asks for (absent on pages from before auto-update = 1)
function pageShell(html) {
  const m = /<script type="text\/plain" id="dwshell">\s*(\d+)\s*<\/script>/.exec(html);
  return m ? Number(m[1]) : 1;
}
// numeric compare of dotted versions: 1 if a > b, -1 if a < b, 0 if equal
function compareVersions(a, b) {
  const pa = String(a).split('.').map(Number), pb = String(b).split('.').map(Number);
  for (let i = 0; i < Math.max(pa.length, pb.length); i++) {
    const x = pa[i] || 0, y = pb[i] || 0;
    if (x !== y) return x > y ? 1 : -1;
  }
  return 0;
}
// a downloaded page is only used if it is clearly a complete Meta Builder page
function validatePage(html) {
  if (typeof html !== 'string') return 'not text';
  if (Buffer.byteLength(html) < MIN_PAGE_BYTES) return 'too small';
  if (!/Meta <span>Builder<\/span>/.test(html)) return 'not the Meta Builder page';
  if (!/<\/html>\s*$/i.test(html)) return 'cut off';
  if (!pageVersion(html)) return 'no version';
  if (!/id="dwdata"/.test(html)) return 'missing game data';
  return null;
}

// Where pages live: the copy bundled with the app, and the downloaded copy in the app's data folder.
function makeStore(bundledDir, userDir) {
  const bundledFile = path.join(bundledDir, 'index.html');
  const userFile = path.join(userDir, 'index.html');
  const versionOf = file => { try { return pageVersion(fs.readFileSync(file, 'utf8')); } catch { return null; } };
  return {
    bundledFile, userFile,
    bundledVersion: () => versionOf(bundledFile),
    downloadedVersion: () => versionOf(userFile),
    // the newer of the two; the bundled copy wins ties and covers a missing or unreadable download
    activeFile() {
      const b = versionOf(bundledFile), u = versionOf(userFile);
      return u && b && compareVersions(u, b) > 0 ? userFile : bundledFile;
    },
    activeVersion() { return versionOf(this.activeFile()); },
    // write to a temp file first so a crash mid-write never leaves a half page
    save(html) {
      fs.mkdirSync(userDir, { recursive: true });
      const tmp = userFile + '.download';
      fs.writeFileSync(tmp, html, 'utf8');
      fs.renameSync(tmp, userFile);
    },
    // a newer app install brings a newer bundled page: the old download is no longer needed
    cleanup() {
      const b = versionOf(bundledFile), u = versionOf(userFile);
      if (u && b && compareVersions(u, b) <= 0) { try { fs.unlinkSync(userFile); } catch {} }
    },
  };
}

// One check. fetchText(url) resolves to {status, text}. shellVersion = this app's own version number for layer 2.
// Returns {status: 'updated' | 'current' | 'error', version, shellUpdate, error}.
async function checkForUpdate({ store, fetchText, shellVersion, url = PAGE_URL }) {
  const current = store.activeVersion();
  let res;
  try { res = await fetchText(url); } catch (e) { return { status: 'error', version: current, error: 'offline or the website could not be reached' }; }
  if (!res || res.status !== 200) return { status: 'error', version: current, error: `the website answered ${res ? res.status : 'nothing'}` };
  const bad = validatePage(res.text);
  if (bad) return { status: 'error', version: current, error: `the downloaded page was rejected (${bad})` };
  const remote = pageVersion(res.text);
  const shellUpdate = pageShell(res.text) > shellVersion;
  if (current && compareVersions(remote, current) <= 0) return { status: 'current', version: current, remote, shellUpdate };
  // a page that needs a newer app is not installed into this one: the person is sent to the download instead
  if (shellUpdate) return { status: 'current', version: current, remote, shellUpdate };
  store.save(res.text);
  return { status: 'updated', version: remote, previous: current, shellUpdate: false };
}

module.exports = { PAGE_URL, RELEASES_URL, pageVersion, pageShell, compareVersions, validatePage, makeStore, checkForUpdate };
