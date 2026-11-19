# AI build maker: everyday, indirect descriptions (owner, November 19, 2026: "make what people ask sound more human like if they
# ask indirectly for things"). python3 tests/browser/ai_human.py
import pathlib, json
ROOT = pathlib.Path(__file__).resolve().parents[2]
URL = (ROOT / 'index.html').as_uri()
from playwright.sync_api import sync_playwright
bad = []
def check(ok, msg):
    print(('ok   ' if ok else 'FAIL ') + msg)
    if not ok: bad.append(msg)
# description -> test on the parsed plan (r = {o, wt, wv, atts, pre, post, want, prio, ds, caster})
CASES = [
    ("i want to hit really hard with fire and be hard to kill", lambda r: r['atts'].get('FLM') and r['post'].get('FTD') == 50 and r['prio'] == 20),
    ("i dont want any charisma or intelligence", lambda r: 'CHA' not in r['pre'] and 'INT' not in r['pre'] and 'CHA' not in r['want'] and 'INT' not in r['want']),
    ("i don't want charisma, just strength and agility", lambda r: 'CHA' not in r['pre'] and r['pre'].get('STR') and r['pre'].get('AGL')),
    ("flamecharm build, no frost", lambda r: 'ICE' not in r['atts'] and r['atts'].get('FLM')),
    ("mostly spells, i dont really want to m1, with frostdraw", lambda r: r['wv'] == 0 and r['atts'].get('ICE') == 100),
    ("i like dodging around and stabbing people from behind", lambda r: r['pre'].get('AGL', 0) >= 40),
    ("i want lots of health and to heal my friends", lambda r: r['pre'].get('CHA') == 55 and r['post'].get('FTD') == 50),
    ("i want to be fast and use daggers", lambda r: r['wt'] == 'LHT' and r['pre'].get('AGL', 0) >= 45),
    ("a build that burns people and has big sword", lambda r: r['wt'] == 'HVY' and r['atts'].get('FLM')),
    ("something with blood and a scythe that steals life", lambda r: r['wt'] == 'HVY' and r['atts'].get('BLD')),
    ("i'm bad at parrying so i want to be hard to kill", lambda r: r['post'].get('FTD') == 50),
    ("i want max damage on my m1s with a greatsword", lambda r: r['wt'] == 'HVY' and r['prio'] == 20 and r['ds'] == 0),
    ("a wind build that zooms around", lambda r: r['atts'].get('WND') and r['pre'].get('AGL', 0) >= 45),
    ("i want to destroy armor with a heavy weapon", lambda r: r['wt'] == 'HVY' and r['atts'].get('IRN') and r['pre'].get('STR') == 90),
    ("a sneaky assassin that goes invisible", lambda r: r['pre'].get('AGL', 0) >= 40),
    ("give me a support build for my friends", lambda r: r['pre'].get('CHA') == 55),
    ("i hate charisma builds, give me a strength build with a greataxe", lambda r: 'CHA' not in r['pre'] and r['pre'].get('STR') == 75 and r['wt'] == 'HVY'),
    ("i want a really fast light build with wind, nothing tanky", lambda r: 'FTD' not in r['post'] and r['wt'] == 'LHT'),
    ("he has a big hammer and lightning and never dies", lambda r: r['post'].get('FTD') == 50 and r['wt'] == 'HVY' and r['atts'].get('LTN')),
    ("give me the 100/100 frost talent with a heavy weapon please", lambda r: r['atts'].get('ICE') == 80 and r['wv'] == 75),
]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(2000)
    for t, ok in CASES:
        r = pg.evaluate("t=>{const {p,got}=aiParse(t);return {o:p.oath,wt:p.wtype,wv:p.wtarget,atts:p.atts,pre:p.pre,post:p.post,want:p.want,prio:p.prio,ds:p.dsplit,got:got.join(' · ')}}", t)
        try: good = bool(ok(r))
        except Exception as e: good = False
        check(good, f"{t!r}: {json.dumps({k: v for k, v in r.items() if k != 'got'})} | {r['got'][:200]}")
    check(not errs, 'no page errors ' + str(errs[:2]))
    b.close()
print('FAILED', len(bad)); raise SystemExit(1 if bad else 0)
