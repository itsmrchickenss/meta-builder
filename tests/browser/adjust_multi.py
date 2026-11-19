# Adjustments with two or more changes in one line: every change must go through (owner, November 19, 2026: "sometimes when
# I ask for 2 things only one thing goes through"). python3 tests/browser/adjust_multi.py
import pathlib, json
ROOT = pathlib.Path(__file__).resolve().parents[2]
URL = (ROOT / 'index.html').as_uri()
from playwright.sync_api import sync_playwright
bad = []
def check(ok, msg):
    print(('ok   ' if ok else 'FAIL ') + msg)
    if not ok: bad.append(msg)
# request -> words that must each appear in what was done
CASES = [
    ('more agility and strength', ['more Agility', 'more Strength']),
    ('more str & agl', ['more Strength', 'more Agility']),
    ('higher int and will', ['more Intelligence', 'more Willpower']),
    ('more strength, agility and willpower', ['more Strength', 'more Agility', 'more Willpower']),
    ('less charisma and intelligence', ['less Charisma', 'less Intelligence']),
    ('raise flame and frost by 10', ['Flamecharm raised', 'Frostdraw raised']),
    ('lower strength and agility by 5', ['Strength lowered', 'Agility lowered']),
    ('set agility and willpower to 40', ['Agility set to 40', 'Willpower set to 40']),
    ('strength 40 and agility 60', ['Strength set to 40', 'Agility set to 60']),
    ('flame 90, frost 50', ['Flamecharm set to 90', 'Frostdraw set to 50']),
    ('less flame, more frost', ['less Flamecharm', 'more Frostdraw']),
    ('less flame and frost', ['less Flamecharm', 'less Frostdraw']),
    ('add speed demon and ghost', ['added Speed Demon', 'added Ghost']),
    ('remove azure flames and flame within', ['removed Azure Flames', 'removed Flame Within']),
    ('remove speed demon, ghost and risky moves', ['removed Speed Demon', 'removed Ghost', 'removed Risky Moves']),
    ('get rid of ghost and speed demon please', ['removed Ghost', 'removed Speed Demon']),
    ('avoid azure flames and flame within', ['avoided Azure Flames', 'avoided Flame Within']),
    ('add ghost and remove speed demon', ['added Ghost', 'removed Speed Demon']),
    ('add thundercall and remove frostdraw', ['Thundercall added', 'Frostdraw removed']),
    ('drop frost and add shadow', ['Frostdraw removed', 'Shadowcast added']),
    ('take out frost, make agility 50 and add ghost', ['Frostdraw removed', 'Agility set to 50', 'added Ghost']),
    ('swap frost for thunder and more agility', ['swapped for Thundercall', 'more Agility']),
    ('heavy weapon and tankier', ['Heavy weapon', 'tankier']),
    ("i'd like a bit more health and a heavier weapon", ['tankier', 'Heavy weapon']),
    ('could you lower charisma and bump up intelligence', ['less Charisma', 'more Intelligence']),
    ('increase strength by 10 and decrease agility by 10', ['Strength raised', 'Agility lowered']),
    ('can you make it tankier and add ghost', ['tankier', 'added Ghost']),
]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 900}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(2500)
    def wait(): pg.wait_for_function("!document.getElementById('results').classList.contains('busy')", timeout=180000); pg.wait_for_timeout(400)
    pg.evaluate("openAI()"); pg.fill('#aitext', 'medium flamecharm frostdraw build'); pg.click('#ai-go'); pg.wait_for_timeout(500)
    if pg.evaluate("!$('aiqs').hidden"): pg.click('#aiq-go'); pg.wait_for_timeout(300)
    pg.click('#wz-go'); pg.wait_for_timeout(300); wait()
    snap = pg.evaluate("JSON.stringify(S)")
    for t, need in CASES:
        d = pg.evaluate("([j,t])=>{const tab=S.tab;for(const k of Object.keys(S))delete S[k];Object.assign(S,JSON.parse(j));S.tab=tab;return applyAdjust(t)}", [snap, t])
        miss = [w for w in need if not any(w in x for x in d)]
        check(not miss, f"{t!r}: {d}" + (f" (missing {miss})" if miss else ''))
    # end to end: both changes are in the build after it re-optimizes
    pg.evaluate("j=>{const tab=S.tab;for(const k of Object.keys(S))delete S[k];Object.assign(S,JSON.parse(j));S.tab=tab;renderInputs()}", snap)
    pg.fill('#adjtext', 'more agility and strength'); pg.click('#adjgo'); pg.wait_for_timeout(300); wait()
    st = pg.evaluate("({AGL:S.mins.AGL||0,STR:S.mins.STR||0,fa:last.best.final.AGL,fs:last.best.final.STR,free:last.best.free})")
    check(st['AGL'] > 0 and st['STR'] > 0 and st['fa'] >= st['AGL'] and st['fs'] >= st['STR'] and st['free'] >= 0, f"more agility and strength, after optimizing: {st}")
    pg.fill('#adjtext', 'remove speed demon and add ghost'); pg.click('#adjgo'); pg.wait_for_timeout(300); wait()
    st = pg.evaluate("({sel:S.sel.includes('Ghost'),sd:S.sel.includes('Speed Demon')})")
    check(st['sel'] and not st['sd'], f"remove Speed Demon and add Ghost, after optimizing: {st}")
    check(not errs, 'no page errors ' + str(errs[:2]))
    b.close()
print('FAILED', len(bad)); raise SystemExit(1 if bad else 0)
