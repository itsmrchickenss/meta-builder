// Meta Builder desktop app (Electron). It shows the same page as the website from www/, served on a private
// app:// address so saved builds, presets and themes (localStorage) persist between launches.
'use strict';
const { app, BrowserWindow, protocol, net, shell, Menu } = require('electron');
const path = require('path');
const { pathToFileURL } = require('url');

const HOST = 'meta-builder';
const START = `app://${HOST}/index.html`;
const WWW = path.join(__dirname, '..', 'www');
const isMac = process.platform === 'darwin';

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

function buildMenu() {
  const template = [
    ...(isMac ? [{ role: 'appMenu' }] : []),
    { role: 'fileMenu' },
    { role: 'editMenu' },
    { label: 'View', submenu: [{ role: 'reload' }, { type: 'separator' }, { role: 'resetZoom' }, { role: 'zoomIn' }, { role: 'zoomOut' }, { type: 'separator' }, { role: 'togglefullscreen' }] },
    { role: 'windowMenu' },
    { role: 'help', submenu: [
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
    const file = path.normalize(path.join(WWW, rel));
    if (!file.startsWith(WWW + path.sep)) return new Response('Not found', { status: 404 });
    return net.fetch(pathToFileURL(file).toString());
  });
  buildMenu();
  createWindow();
  app.on('activate', () => { if (!BrowserWindow.getAllWindows().length) createWindow(); });
});

app.on('window-all-closed', () => { if (!isMac) app.quit(); });
