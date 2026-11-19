# The owner's featured builds (src/data/featured.txt) rebuilt by the optimizer and auto-pick, compared with the real builds
# (owner, November 19, 2026: "create more builds and compare them to some of the sample builds i gave you").
#  - stats: given the same final stats, oath, weapon, talents and mantras, the optimizer must fit them with at least as many
#    points left as the real build (within 1), without odd before-shrine values. Builds whose own before-shrine total is under
#    135 (Power 8) aren't compared: they use the shrine below Power 8, which the game doesn't allow.
#  - auto-pick: given the same before-shrine and final stats and no talents, auto-pick must choose at least 70% of the real
#    build's talents overall, and never a weapon-class talent (Spear, Club, Rifle…) the build's weapon can't use.
# python3 tests/browser/samples_compare.py
import pathlib, json, re
ROOT = pathlib.Path(__file__).resolve().parents[2]; URL = (ROOT / 'index.html').as_uri()
from playwright.sync_api import sync_playwright
rows = [l.rstrip('\n').split('|') for l in open(ROOT / 'src/data/featured.txt') if l.strip() and not l.startswith('#')]
st = lambda x: {m[0]: int(m[1]) for m in re.findall(r'([A-Z]{3})(\d+)', x)}
WEPS = ['HVY', 'MED', 'LHT']; ATTS = ['FLM', 'ICE', 'LTN', 'WND', 'SDW', 'IRN', 'BLD']
bad = []
def check(ok, msg):
    print(('ok   ' if ok else 'FAIL ') + msg)
    if not ok: bad.append(msg)
SETUP = """c=>{for(const k of Object.keys(S))if(k!=='tab')delete S[k];applyPreset({clean:1});
  S.oath=OATHS.some(o=>o.n===c.oath)?c.oath:'None';S.wtype=c.wt||'MED';S.wtarget=c.wv;S.weapon=WBY.has(c.weapon)?c.weapon:'';S.noAutoW=!S.weapon;
  S.atts={...c.atts};S.mins={...c.mins};S.preMin=c.usePre?Object.fromEntries(Object.entries(c.pre).filter(([k,v])=>ATTR.includes(k)&&v>1)):{};
  S.sel=c.tal.filter(n=>TBY.has(n));S.mantras=c.man.filter(n=>MBY.has(n));S.req=[];renderInputs();optimizeAll({noUndo:true,noSpend:true});return 1}"""
THEIRS = """c=>{const R=requirements();const P={};for(const k of ALL)P[k]=c.pre[k]||0;const e=evaluate(P,R,R.oathAlts);return e&&!e.impossible?e.free:null}"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 900}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(2500)
    def wait(): pg.wait_for_timeout(300); pg.wait_for_function("!document.getElementById('results').classList.contains('busy')", timeout=300000); pg.wait_for_timeout(300)
    hit = tot = 0
    for r in rows:
        name, oath, wt, weapon = r[3], r[4], r[5], r[7]; pre, fin = st(r[9]), st(r[10])
        tal = [t for t in r[11].split(';') if t]
        cfg = {'oath': oath, 'wt': wt, 'wv': fin.get(wt, 0), 'weapon': weapon, 'atts': {k: v for k, v in fin.items() if k in ATTS},
               'mins': {k: v for k, v in fin.items() if k not in ATTS + WEPS}, 'tal': tal, 'man': [m for m in r[12].split(';') if m], 'pre': pre, 'usePre': False}
        if sum(pre.values()) >= 135:
            pg.evaluate(SETUP, cfg); wait()
            theirs = pg.evaluate(THEIRS, cfg)
            o = pg.evaluate("""c=>{const b=last.best;const C=closure();return {free:b.free,kept:c.tal.filter(n=>TBY.has(n)&&C.T.has(n)).length,asked:c.tal.filter(n=>TBY.has(n)).length,odd:ALL.filter(k=>oddPre(k,last.R,b)),
              capOnly:c.tal.filter(n=>TBY.has(n)&&!C.T.has(n)).every(n=>{const keep=S.sel.slice();S.sel=[...S.sel,n];const C2=closure();const cn=counts(C2);S.sel=keep;return cn.nTal>cn.cap})}}""", cfg)
            if theirs is not None and theirs >= 0:
                # a talent left out only because adding it (with the mantra it needs) would pass the talent cap is the cap rule, not a miss
                check(o['free'] >= theirs - 1 and (o['kept'] == o['asked'] or o['capOnly']) and not o['odd'], f"{name[:34]}: ours {o['free']} points left with {o['kept']}/{o['asked']} talents, theirs {theirs}; odd {o['odd']}")
        cfg = {**cfg, 'tal': [], 'usePre': True}
        pg.evaluate(SETUP, cfg); wait(); pg.evaluate("autoPick()"); wait()
        a = pg.evaluate("""t=>{const C=closure();const th=t.filter(n=>{const x=TBY.get(n);return x&&x.k});
          return {hit:th.filter(n=>C.T.has(n)).length,n:th.length,wrongClass:[...C.T.keys()].filter(n=>{const x=TBY.get(n);return x&&x.req&&x.req.w&&!wClassOk(x)})}}""", tal)
        hit += a['hit']; tot += a['n']
        check(not a['wrongClass'], f"{name[:34]}: auto-pick {a['hit']}/{a['n']} of the real talents; weapon-class talents the weapon can't use: {a['wrongClass']}")
    check(hit >= 0.7 * tot, f"auto-pick overall: {hit}/{tot} = {round(100 * hit / max(1, tot))}% of the real builds' talents (at least 70%)")
    check(not errs, 'no page errors ' + str(errs[:2]))
    b.close()
print('FAILED', len(bad)); raise SystemExit(1 if bad else 0)
