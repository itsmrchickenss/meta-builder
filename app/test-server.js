// Checks the web server: node test-server.js (run `python3 src/build.py` first so www/index.html exists)
'use strict';
const http = require('http');
const zlib = require('zlib');
const server = require('./server');
let fails = 0;
const check = (ok, what) => { if (!ok) fails++; console.log((ok ? 'ok   ' : 'FAIL ') + what); };
const get = (port, path, headers = {}) => new Promise((resolve, reject) => {
  http.get({ host: '127.0.0.1', port, path, headers }, res => {
    const chunks = []; res.on('data', c => chunks.push(c)); res.on('end', () => resolve({ res, body: Buffer.concat(chunks) }));
  }).on('error', reject);
});
server.listen(0, '127.0.0.1', async () => {
  const port = server.address().port;
  try {
    const home = await get(port, '/');
    check(home.res.statusCode === 200 && /text\/html/.test(home.res.headers['content-type']), 'GET / returns the page');
    check(/Meta <span>Builder<\/span>/.test(home.body.toString()), 'page has the Meta Builder title');
    check(home.res.headers['cache-control'] === 'no-cache', 'page is re-checked each visit (no-cache)');
    const gz = await get(port, '/', { 'accept-encoding': 'gzip' });
    check(gz.res.headers['content-encoding'] === 'gzip' && zlib.gunzipSync(gz.body).equals(home.body), 'gzip works and matches');
    check(gz.body.length < home.body.length / 2, `gzip shrinks the page (${home.body.length} -> ${gz.body.length} bytes)`);
    const again = await get(port, '/', { 'if-none-match': home.res.headers.etag });
    check(again.res.statusCode === 304, 'ETag gives 304 Not Modified');
    check((await get(port, '/index.html')).res.statusCode === 200, 'GET /index.html');
    check((await get(port, '/healthz')).body.toString() === 'ok', '/healthz says ok');
    const v = JSON.parse((await get(port, '/version')).body.toString());
    check(v.version === require('./package.json').version, '/version is ' + v.version);
    check((await get(port, '/nope.js')).res.statusCode === 404, 'missing file is 404');
    check((await get(port, '/../package.json')).res.statusCode === 404, 'cannot read outside www (../)');
    check((await get(port, '/%2e%2e/server.js')).res.statusCode === 404, 'cannot read outside www (%2e%2e)');
  } catch (e) { fails++; console.log('FAIL ' + e.message); }
  server.close(() => process.exit(fails ? 1 : 0));
});
