# AI build maker: "the 100/100 talents" and "black flames" require every talent that goes with them, and the optimizer places
# the stats cleanly (owner's November 18, 2026 report: Umbrite Witherblade Bladeharper black flames Flamecharm Shadowcast).
# python3 tests/browser/ai_hundred.py
import pathlib, json
ROOT = pathlib.Path(__file__).resolve().parents[2]
URL = (ROOT / 'index.html').as_uri()
from playwright.sync_api import sync_playwright
bad = []
def check(ok, msg):
    print(('ok   ' if ok else 'FAIL ') + msg)
    if not ok: bad.append(msg)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 900}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(2500)
    def wait(): pg.wait_for_function("!document.getElementById('results').classList.contains('busy')", timeout=120000); pg.wait_for_timeout(400)
    parse = lambda t: pg.evaluate("t=>{const p=aiParse(t).p;return {oath:p.oath,w:p.weapon,wt:p.wtype,wv:p.wtarget,atts:p.atts,req:p.req,q:aiQuestions(p)}}", t)
    r = parse('umbrite witherblade bladeharper black flames flamecharm shadowcast with the 100 100 talents')
    need = {'Scorching Decay', 'Night Terror', 'Wraith Path: Twisted Puppets', 'Burning Puppets', 'Burning Sacrifice', 'Explosive Rage', 'Moths to a Flame'}
    check(r['oath'] == 'Bladeharper' and r['w'] == 'Umbrite Witherblade' and r['wt'] == 'MED' and r['wv'] == 100, f"oath / weapon / Medium 100: {r['oath']} {r['w']} {r['wt']} {r['wv']}")
    check(r['atts'].get('FLM') == 100 and r['atts'].get('SDW') == 100, f"Flamecharm and Shadowcast 100: {r['atts']}")
    check(need <= set(r['req']), f"required: {sorted(set(r['req']))}")
    check('att' not in r['q'] and 'oath' not in r['q'], f"no attunement or oath question: {r['q']}")
    r = parse('medium flamecharm build with the 100 flame 100 weapon talent')
    check(r['req'] == ['Scorching Decay'] and r['wv'] == 100 and r['atts'].get('FLM') == 100, f"100 flame 100 weapon -> Scorching Decay only: {r['req']} {r['wv']} {r['atts']}")
    r = parse('heavy frostdraw 100/100 talent'); check('Frozen Anchor' in r['req'], f"100/100 with Frostdraw -> Frozen Anchor: {r['req']}")
    r = parse('bladeharper shadowcast black flame build'); check('Wraith Path: Twisted Puppets' in r['req'], f"black flame -> Twisted Puppets path: {r['req']}")
    r = parse('jetstriker light 100 100 talents'); check(not r['req'], f"100/100 with no attunement named: nothing required, a note instead: {r['req']}")
    # whole flow: AI build maker -> wizard -> build; every required talent in, plan within budget, no odd pre-shrine values
    pg.evaluate("openAI()"); pg.fill('#aitext', 'umbrite witherblade bladeharper black flames flamecharm shadowcast with the 100 100 talents, semi tanky')
    pg.click('#ai-go'); pg.wait_for_timeout(600)
    if pg.evaluate("!$('aiqs').hidden"): pg.click('#aiq-go'); pg.wait_for_timeout(400)
    pg.click('#wz-go'); pg.wait_for_timeout(300); wait()
    st = pg.evaluate("""(()=>{const b=last.best,C=closure();return {free:b.free,impossible:b.impossible,P:Object.fromEntries(ALL.filter(k=>b.P[k]).map(k=>[k,b.P[k]])),
      fin:Object.fromEntries(ALL.filter(k=>b.final[k]).map(k=>[k,b.final[k]])),req:S.req,missing:S.req.filter(n=>!C.T.has(n)&&!C.M.has(n)),odd:ALL.filter(k=>oddPre(k,last.R,b))}})()""")
    check(st['free'] >= 0 and not st['impossible'], f"fits: {st['free']} points left, before {st['P']}, final {st['fin']}")
    check(not st['missing'], f"required talents all in: missing {st['missing']}")
    check(not st['odd'], f"no odd pre-shrine values: {st['odd']}")
    # (with semi tanky on top the budget can't keep all three at 100 after the shrine: they reach 100 before it, where the
    # 100/100 talents are taken, and the starting-point step says what it lowered)
    pk = lambda k: max(st['P'].get(k, 0), st['fin'].get(k, 0))
    check(pk('MED') >= 100 and pk('FLM') >= 100 and pk('SDW') >= 100, f"Medium, Flamecharm and Shadowcast reach 100 (before or after the shrine): {pk('MED')} {pk('FLM')} {pk('SDW')}")
    check(not errs, 'no page errors ' + str(errs[:2]))
    b.close()
print('FAILED', len(bad)); raise SystemExit(1 if bad else 0)
