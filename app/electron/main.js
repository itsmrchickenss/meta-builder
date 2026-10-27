// Meta Builder desktop app (Electron). It shows the same page as the website from www/, served on a private
// app:// address so saved builds, presets and themes (localStorage) persist between launches.
'use strict';
const { app, BrowserWindow, protocol, net, shell, Menu, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const { pathToFileURL } = require('url');
const updater = require('./updater');

const HOST = 'meta-builder';
const START = `app://${HOST}/index.html`;
const WWW = path.join(__dirname, '..', 'www');
const isMac = process.platform === 'darwin';
// bump "shellVersion" in package.json whenever this desktop code changes in a way pages depend on
const SHELL_VERSION = Number(require('../package.json').shellVersion) || 1;
const CHECK_EVERY_MS = 6 * 60 * 60 * 1000;

let store = null, activeFile = null, settings = { autoUpdate: true };
const settingsFile = () => path.join(app.getPath('userData'), 'settings.json');
function loadSettings() { try { settings = { ...settings, ...JSON.parse(fs.readFileSync(settingsFile(), 'utf8')) }; } catch {} }
function saveSettings() { try { fs.writeFileSync(settingsFile(), JSON.stringify(settings, null, 2)); } catch {} }

// a standard, secure scheme behaves like https: storage, clipboard and fetch all work
protocol.registerSchemesAsPrivileged([
  { scheme: 'app', privileges: { standard: true, secure: true, supportFetchAPI: true, corsEnabled: true, stream: true } },
]);

// one window per app: a second launch focuses the first
if (!app.requestSingleInstanceLock()) app.quit();

let win = null;
const openOutside = url => { if (/^https?:\/\//i.test(url)) shell.openExternal(url); };

function createWindow() {
  win = new BrowserWindow({
    width: 1320, height: 900, minWidth: 380, minHeight: 500,
    backgroundColor: '#0c1418', title: 'Meta Builder', autoHideMenuBar: true, show: false,
    icon: path.join(__dirname, '..', 'build', 'icon.png'),
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: true, spellcheck: false },
  });
  win.once('ready-to-show', () => win.show());
  // links to deepwoken.co, the wiki or the website open in the normal browser, never inside the app
  win.webContents.setWindowOpenHandler(({ url }) => { openOutside(url); return { action: 'deny' }; });
  win.webContents.on('will-navigate', (e, url) => {
    if (!url.startsWith(`app://${HOST}/`)) { e.preventDefault(); openOutside(url); }
  });
  win.on('closed', () => { win = null; });
  win.loadURL(START);
}

// ---- updates ----
async function fetchText(url) {
  const ctl = new AbortController(); const t = setTimeout(() => ctl.abort(), 20000);
  try { const res = await net.fetch(url, { cache: 'no-store', signal: ctl.signal }); return { status: res.status, text: res.status === 200 ? await res.text() : '' }; }
  finally { clearTimeout(t); }
}
let checking = false, shellNoticeShown = false;
async function checkForUpdates(manual) {
  if (checking) return; checking = true;
  try {
    const r = await updater.checkForUpdate({ store, fetchText, shellVersion: SHELL_VERSION });
    if (r.shellUpdate && (manual || !shellNoticeShown)) {
      shellNoticeShown = true;
      const { response } = await dialog.showMessageBox(win, { type: 'info', buttons: ['Download', 'Later'], defaultId: 0, cancelId: 1,
        message: `A new version of the Meta Builder app is available (v${r.remote}).`,
        detail: 'This update changes the app itself, so it needs a new download. Your saved builds, presets and theme are kept.' });
      if (response === 0) shell.openExternal(updater.RELEASES_URL);
    } else if (r.status === 'updated') {
      activeFile = store.activeFile();
      const { response } = await dialog.showMessageBox(win, { type: 'info', buttons: ['Reload now', 'Later'], defaultId: 0, cancelId: 1,
        message: `Meta Builder v${r.version} is ready.`,
        detail: 'Reload to use it now (your current build is saved), or it will be used the next time you open the app. Click the version next to the title to see what changed.' });
      if (response === 0 && win) win.reload();
    } else if (manual) {
      await dialog.showMessageBox(win, r.status === 'current'
        ? { type: 'info', message: `You have the latest version (v${r.version}).` }
        : { type: 'warning', message: 'Couldn\'t check for updates.', detail: `${r.error[0].toUpperCase() + r.error.slice(1)}. Try again later.` });
    }
  } finally { checking = false; }
}

function buildMenu() {
  const template = [
    ...(isMac ? [{ label: app.name, submenu: [{ role: 'about' }, { label: 'Check for Updates…', click: () => checkForUpdates(true) }, { type: 'separator' }, { role: 'services' }, { type: 'separator' }, { role: 'hide' }, { role: 'hideOthers' }, { role: 'unhide' }, { type: 'separator' }, { role: 'quit' }] }] : []),
    { role: 'fileMenu' },
    { role: 'editMenu' },
    { label: 'View', submenu: [{ role: 'reload' }, { type: 'separator' }, { role: 'resetZoom' }, { role: 'zoomIn' }, { role: 'zoomOut' }, { type: 'separator' }, { role: 'togglefullscreen' }] },
    { role: 'windowMenu' },
    { role: 'help', submenu: [
      ...(isMac ? [] : [{ label: 'Check for Updates…', click: () => checkForUpdates(true) }]),
      { label: 'Update Automatically', type: 'checkbox', checked: settings.autoUpdate !== false,
        click: item => { settings.autoUpdate = item.checked; saveSettings(); if (item.checked) checkForUpdates(false); } },
      { label: 'About this version', click: () => dialog.showMessageBox(win, { type: 'info', message: `Meta Builder v${store.activeVersion() || '?'}`,
        detail: `App ${app.getVersion()} (app version ${SHELL_VERSION}). ${activeFile === store.userFile ? 'Using the page downloaded by auto-update.' : 'Using the page that came with the app.'}` }) },
      { type: 'separator' },
      { label: 'Meta Builder website', click: () => shell.openExternal('https://itsmrchickenss.github.io/meta-builder/') },
      { label: 'Report a bug or idea (GitHub)', click: () => shell.openExternal('https://github.com/itsmrchickenss/meta-builder/issues') },
      { label: 'Game data: deepwoken.co', click: () => shell.openExternal('https://deepwoken.co/') },
    ] },
  ];
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

app.on('second-instance', () => { if (win) { if (win.isMinimized()) win.restore(); win.focus(); } });

app.whenReady().then(() => {
  protocol.handle('app', req => {
    const u = new URL(req.url);
    if (u.host !== HOST) return new Response('Not found', { status: 404 });
    let rel = decodeURIComponent(u.pathname);
    if (!rel || rel === '/') rel = '/index.html';
    if (rel === '/index.html') return net.fetch(pathToFileURL(activeFile).toString(), { cache: 'no-store' });
    const file = path.normalize(path.join(WWW, rel));
    if (!file.startsWith(WWW + path.sep)) return new Response('Not found', { status: 404 });
    return net.fetch(pathToFileURL(file).toString());
  });
  loadSettings();
  store = updater.makeStore(WWW, path.join(app.getPath('userData'), 'www'));
  store.cleanup();
  activeFile = store.activeFile();
  buildMenu();
  createWindow();
  // check shortly after opening, then every 6 hours while the app stays open (if Update Automatically is on)
  setTimeout(() => { if (settings.autoUpdate !== false) checkForUpdates(false); }, 8000);
  setInterval(() => { if (settings.autoUpdate !== false) checkForUpdates(false); }, CHECK_EVERY_MS);
  app.on('activate', () => { if (!BrowserWindow.getAllWindows().length) createWindow(); });
});

app.on('window-all-closed', () => { if (!isMac) app.quit(); });
