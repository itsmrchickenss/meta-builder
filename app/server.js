// Meta Builder web server: serves the planner (www/index.html) so it can be hosted anywhere Node.js runs.
// No dependencies. Start with `npm start` (or `node server.js`); set PORT / HOST to change where it listens.
'use strict';
const http = require('http');
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const crypto = require('crypto');

const ROOT = path.join(__dirname, 'www');
// a fresh clone has no www/ copy yet: fall back to the repo's built index.html (what GitHub Pages serves)
const FALLBACK_INDEX = path.join(__dirname, '..', 'index.html');
const indexFile = () => fs.existsSync(path.join(ROOT, 'index.html')) ? path.join(ROOT, 'index.html') : FALLBACK_INDEX;
const PORT = Number(process.env.PORT) || 3000;
const HOST = process.env.HOST || '0.0.0.0';
const VERSION = require('./package.json').version;

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.png': 'image/png', '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
  '.webmanifest': 'application/manifest+json', '.txt': 'text/plain; charset=utf-8', '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
};
const COMPRESSIBLE = /^(text\/|application\/(json|manifest\+json)|image\/svg)/;

// files are read once and kept in memory with their gzip copy and ETag; restart the server after a rebuild
const cache = new Map();
function load(file) {
  let hit = cache.get(file);
  if (hit) return hit;
  const body = fs.readFileSync(file);
  const type = TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream';
  hit = { body, type, etag: '"' + crypto.createHash('sha1').update(body).digest('base64url').slice(0, 20) + '"',
    gz: COMPRESSIBLE.test(type) ? zlib.gzipSync(body, { level: 9 }) : null };
  cache.set(file, hit);
  return hit;
}

function send(res, status, headers, body) { res.writeHead(status, headers); res.end(body); }

const server = http.createServer((req, res) => {
  const base = { 'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'strict-origin-when-cross-origin' };
  if (req.method !== 'GET' && req.method !== 'HEAD') return send(res, 405, { ...base, Allow: 'GET, HEAD' }, 'Method not allowed');
  let url;
  try { url = new URL(req.url, 'http://localhost'); } catch { return send(res, 400, base, 'Bad request'); }
  if (url.pathname === '/healthz') return send(res, 200, { ...base, 'Content-Type': 'text/plain', 'Cache-Control': 'no-store' }, 'ok');
  if (url.pathname === '/version') return send(res, 200, { ...base, 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }, JSON.stringify({ version: VERSION }));

  let rel;
  try { rel = decodeURIComponent(url.pathname); } catch { return send(res, 400, base, 'Bad request'); }
  if (rel.endsWith('/')) rel += 'index.html';
  const file = rel === '/index.html' ? indexFile() : path.normalize(path.join(ROOT, rel));
  if (file !== FALLBACK_INDEX && !file.startsWith(ROOT + path.sep)) return send(res, 404, base, 'Not found');
  let f;
  try { if (!fs.statSync(file).isFile()) throw 0; f = load(file); } catch { return send(res, 404, { ...base, 'Content-Type': 'text/plain' }, 'Not found'); }

  const headers = { ...base, 'Content-Type': f.type, ETag: f.etag, Vary: 'Accept-Encoding',
    // the page changes with every version, so browsers check for a newer copy each time
    'Cache-Control': f.type.startsWith('text/html') ? 'no-cache' : 'public, max-age=3600' };
  if (req.headers['if-none-match'] === f.etag) return send(res, 304, headers);
  const gzip = f.gz && /\bgzip\b/.test(req.headers['accept-encoding'] || '');
  const body = gzip ? f.gz : f.body;
  if (gzip) headers['Content-Encoding'] = 'gzip';
  headers['Content-Length'] = body.length;
  send(res, 200, headers, req.method === 'HEAD' ? undefined : body);
});

if (require.main === module) {
  if (!fs.existsSync(indexFile())) {
    console.error('No built page found. Run `python3 src/build.py` from the repo root first.');
    process.exit(1);
  }
  server.listen(PORT, HOST, () => console.log(`Meta Builder v${VERSION} running at http://${HOST === '0.0.0.0' ? 'localhost' : HOST}:${PORT}/`));
  const stop = () => server.close(() => process.exit(0));
  process.on('SIGTERM', stop);
  process.on('SIGINT', stop);
}
module.exports = server;
