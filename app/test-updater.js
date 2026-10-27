// Checks the desktop app's auto-update logic without Electron: node test-updater.js
// (run `python3 src/build.py` first). Serves fake "website" pages from a local server and runs real update checks.
'use strict';
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');
const U = require('./electron/updater');

let fails = 0;
const check = (ok, what) => { if (!ok) fails++; console.log((ok ? 'ok   ' : 'FAIL ') + what); };

const real = fs.readFileSync(fs.existsSync(path.join(__dirname, 'www', 'index.html')) ? path.join(__dirname, 'www', 'index.html') : path.join(__dirname, '..', 'index.html'), 'utf8');
const realVer = U.pageVersion(real);
const bump = (v, n = 1) => { const p = v.split('.').map(Number); p[p.length - 1] += n; return p.join('.'); };
const withVersion = (html, v) => html.replace(/(id="verbtn"[^>]*>)v[\d.]+</, `$1v${v}<`);
const withShell = (html, n) => html.replace(/id="dwshell">\d+</, `id="dwshell">${n}<`);
const newer = withVersion(real, bump(realVer));

// pure helpers
check(!!realVer, 'reads the version from the built page: v' + realVer);
check(U.pageShell(real) === 1, 'built page asks for app version 1');
check(U.compareVersions('0.40', '0.39') === 1 && U.compareVersions('0.9', '0.10') === -1 && U.compareVersions('1.0', '1') === 0, 'version compare is numeric (0.10 > 0.9)');
check(U.validatePage(real) === null, 'the real page passes validation');
check(U.validatePage(real.slice(0, real.length / 2)) !== null, 'a cut-off page is rejected');
check(U.validatePage('<html>404</html>') !== null, 'an error page is rejected');

const pages = { '/newer': newer, '/same': real, '/older': withVersion(real, '0.1'), '/cut': newer.slice(0, newer.length - 5000),
  '/shell': withShell(withVersion(real, bump(realVer, 2)), 2) };
const server = http.createServer((req, res) => {
  const body = pages[req.url];
  if (!body) { res.writeHead(404); return res.end('Not found'); }
  res.writeHead(200, { 'Content-Type': 'text/html' }); res.end(body);
});
const fetchText = url => new Promise((resolve, reject) => {
  http.get(url, res => { let t = ''; res.setEncoding('utf8'); res.on('data', c => t += c); res.on('end', () => resolve({ status: res.statusCode, text: t })); }).on('error', reject);
});

server.listen(0, '127.0.0.1', async () => {
  const base = `http://127.0.0.1:${server.address().port}`;
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'mb-upd-'));
  const bundled = path.join(tmp, 'bundled'), user = path.join(tmp, 'user');
  fs.mkdirSync(bundled); fs.writeFileSync(path.join(bundled, 'index.html'), real);
  const store = U.makeStore(bundled, user);
  const run = url => U.checkForUpdate({ store, fetchText, shellVersion: 1, url: base + url });
  try {
    check(store.activeFile() === store.bundledFile, 'starts on the page that came with the app');
    let r = await run('/same');
    check(r.status === 'current' && !fs.existsSync(store.userFile), 'same version on the website: nothing downloaded');
    r = await run('/older');
    check(r.status === 'current' && !fs.existsSync(store.userFile), 'older page on the website: ignored');
    r = await run('/cut');
    check(r.status === 'error' && /rejected/.test(r.error) && !fs.existsSync(store.userFile), 'cut-off download rejected and not saved');
    r = await run('/missing');
    check(r.status === 'error' && /404/.test(r.error), 'website error (404) reported, nothing changed');
    r = await U.checkForUpdate({ store, fetchText, shellVersion: 1, url: 'http://127.0.0.1:1/' });
    check(r.status === 'error' && /offline/.test(r.error), 'offline reported, nothing changed');
    r = await run('/newer');
    check(r.status === 'updated' && r.version === bump(realVer), `newer page downloaded: v${realVer} -> v${r.version}`);
    check(store.activeFile() === store.userFile && store.activeVersion() === bump(realVer), 'the downloaded page is now the one shown');
    check(!fs.existsSync(store.userFile + '.download'), 'no half-written file left behind');
    r = await run('/newer');
    check(r.status === 'current', 'checking again: already up to date');
    r = await run('/shell');
    check(r.shellUpdate && r.status === 'current' && store.activeVersion() === bump(realVer), 'page that needs a newer app: not installed, person told to download the app');
    // a newer app install (bundled page newer than the download) cleans up the old download
    fs.writeFileSync(path.join(bundled, 'index.html'), withVersion(real, bump(realVer, 3)));
    store.cleanup();
    check(!fs.existsSync(store.userFile) && store.activeFile() === store.bundledFile, 'after installing a newer app, its own page is used and the old download removed');
    // an unreadable download never breaks the app
    fs.mkdirSync(user, { recursive: true }); fs.writeFileSync(store.userFile, 'garbage');
    check(store.activeFile() === store.bundledFile, 'a damaged download is ignored; the built-in page is used');
  } catch (e) { fails++; console.log('FAIL ' + (e.stack || e)); }
  fs.rmSync(tmp, { recursive: true, force: true });
  server.close(() => process.exit(fails ? 1 : 0));
});
