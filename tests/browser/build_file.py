# Build file (.txt) export: the owner's deepwoken.co-format example (tests/fixtures/build-file.txt) must import, then
# export back to the same stats and talents through the "Download build file (.txt)" link, and re-import cleanly.
import json, pathlib, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[2]
URL = (ROOT / 'index.html').as_uri()
SAMPLE = (ROOT / 'tests' / 'fixtures' / 'build-file.txt').read_text().strip()
KEYS = ["Strength", "Fortitude", "Agility", "Intelligence", "Willpower", "Charisma", "Heavy Wep.", "Medium Wep.", "Light Wep.",
        "Flamecharm", "Frostdraw", "Thundercall", "Galebreathe", "Shadowcast", "Ironsing", "Bloodrend"]
from playwright.sync_api import sync_playwright
bad = 0
def check(ok, what):
    global bad
    bad += 0 if ok else 1
    print(('ok   ' if ok else 'FAIL ') + what)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(accept_downloads=True); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.route('**/fonts.googleapis.com/**', lambda r: r.abort())
    pg.goto(URL); pg.wait_for_timeout(2500)
    r = pg.evaluate("async t=>{const r=await smartImport(t);return r.ok}", SAMPLE); pg.wait_for_timeout(2500)
    check(r and pg.evaluate("S.oath") == 'Blindseer', 'example imports, oath read from "Oath: Blindseer" in the talents')
    pg.evaluate("showTab('sum')"); pg.wait_for_timeout(400)
    with pg.expect_download() as dl:
        pg.click('section.panel [data-x="txtfile"]')
    d = dl.value; out = pathlib.Path(tempfile.mkdtemp()) / d.suggested_filename; d.save_as(str(out))
    txt = out.read_text(); j = json.loads(txt); s = json.loads(SAMPLE)
    check(d.suggested_filename.endswith('.txt'), 'the link downloads a .txt file: ' + d.suggested_filename)
    check(list(j) == ['preShrine', 'postShrine', 'talents'], 'keys are preShrine, postShrine, talents')
    check(list(j['preShrine']) == KEYS and list(j['postShrine']) == KEYS, 'stat names in deepwoken.co order')
    check(j['preShrine'] == s['preShrine'] and j['postShrine'] == s['postShrine'], 'pre- and post-shrine stats match the example')
    check(sorted(j['talents']) == sorted(s['talents']), f"all {len(s['talents'])} talents match the example")
    r2 = pg.evaluate("async t=>{const r=await smartImport(t);return r.ok}", txt); pg.wait_for_timeout(2000)
    check(r2 and json.loads(pg.evaluate("buildFileText()")) == j, 'the exported file imports back to the same build')
    pg.click('#sharebtn'); pg.wait_for_timeout(300)
    with pg.expect_download() as dl2:
        pg.click('#share [data-x="txtfile"]')
    check(dl2.value.suggested_filename.endswith('.txt'), 'the Share dialog link downloads it too')
    b.close()
print('bad', bad, 'errs', errs)
