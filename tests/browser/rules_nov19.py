# The owner's answers of November 19, 2026, one check each. python3 tests/browser/rules_nov19.py
#  1. Shrine of Blasphemy first: the Shrine of Order from Power 5 (90 points); imports below 135 switch it on
#  2. Fortitude at a talent's level: both stats max before the shrine, the other stat after too, or skip the talents
#  3. Will o' Wisp: taken with 2+ Wisps, or when the Wisp has no slot (support taken, no wildcard free)
#  5. 100 before the shrine: not pushed past 80 after it by the slider or leftover spending (typed numbers still win)
#  6. mages don't get a Hero's Blade automatically
import pathlib, json
ROOT = pathlib.Path(__file__).resolve().parents[2]; URL = (ROOT / 'index.html').as_uri()
from playwright.sync_api import sync_playwright
bad = []
def check(ok, msg):
    print(('ok   ' if ok else 'FAIL ') + msg)
    if not ok: bad.append(msg)
CLEAN = """()=>{for(const k of Object.keys(S))if(k!=='tab')delete S[k];applyPreset({clean:1});S.noAutoW=true;S.weapon='';S.blasphemy=false;S.sel=[];S.req=[];S.mantras=[]}"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 900}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(2500)
    def wait(): pg.wait_for_timeout(300); pg.wait_for_function("!document.getElementById('results').classList.contains('busy')", timeout=300000); pg.wait_for_timeout(300)
    # 1. Blasphemy
    r = pg.evaluate(CLEAN + "")
    r = pg.evaluate("""()=>{S.blasphemy=false;const off=powerAt(124)>=SHRINE_PWR,pts=SHRINE_PTS;S.blasphemy=true;const on=powerAt(124)>=SHRINE_PWR,p5=SHRINE_PTS,low=powerAt(89)>=SHRINE_PWR;S.blasphemy=false;return {off:!off,on,pts,p5,low}}""")
    check(r['off'] and r['on'] and r['pts'] == 135 and r['p5'] == 90 and not r['low'], f"124 points before: no shrine without Blasphemy, shrine with it (90 points minimum): {r}")
    r = pg.evaluate("""()=>{S.man={pre:{STR:40,AGL:40,CHA:40,MED:1,WND:1,FTD:1,WLL:1},fin:{STR:17,AGL:25,CHA:17,MED:100,WND:100,FTD:50,WLL:20}};S.blasphemy=false;autoBlasphemy();const v=S.blasphemy;S.blasphemy=false;S.man=null;return v}""")
    check(r is True, "an imported build that shrines at 124 points switches the Shrine of Blasphemy on")
    # 2. Fortitude at a talent's level (Concussion: Fortitude 15 + Strength 20)
    pg.evaluate(CLEAN)
    pg.evaluate("""()=>{S.oath='Linkstrider';S.wtype='MED';S.wtarget=100;S.atts={SDW:100};S.mins={};S.preMin={};S.sel=['Battle Tendency','Ether Overdrive','Concussion','Night Terror'];S.req=['Night Terror'];S.prio=50;S.dsplit=50;renderInputs();optimizeAll({noUndo:true,noSpend:true})}""")
    wait()
    r = pg.evaluate("()=>{const b=last.best;return {same:ftdSame(b),pre:b.P.FTD,fin:b.final.FTD,free:b.free,reup:b.reup}}")
    check(not r['same'] and r['free'] >= 0 and not r['reup'], f"Fortitude isn't left at the talent's level before and after: {r}")
    # 3. Will o' Wisp
    r = pg.evaluate(CLEAN + "")
    r = pg.evaluate("""()=>{const t=m=>{S.oath='None';S.mantras=m;S.sel=[];return closure().T.has("Will o' Wisp")};
      return {two:t(['Flame Wisp','Frost Wisp']),one:t(['Flame Wisp']),full:t(['Reinforce','Flame Wisp','Flame Grab','Frost Grab']),fullX:(()=>{S.mantras=['Reinforce','Pressure Blast','Flame Wisp'];return closure().T.has("Will o' Wisp")})()}}""")
    check(r['two'] and not r['one'], f"Will o' Wisp with two Wisps, not with one that has a slot: {r}")
    r2 = pg.evaluate("""()=>{const m=DB.M.filter(x=>x.c==='S'&&x.n!=='Reinforce').map(x=>x.n);S.oath='None';S.mantras=['Reinforce',m[0],'Flame Wisp'];S.sel=[];const C=closure();const su=slotUse(C);return {has:C.T.has("Will o' Wisp"),over:su.over,m:S.mantras}}""")
    check(r2['has'] and r2['over'] == 0, f"Will o' Wisp when the support and wildcard slots are taken, and then the Wisp fits: {r2}")
    # 5. no push past 80 after 100 before the shrine
    pg.evaluate(CLEAN)
    pg.evaluate("""()=>{S.oath='None';S.wtype='MED';S.wtarget=75;S.atts={FLM:80};S.sel=['Scorching Decay'];S.req=['Scorching Decay'];S.prio=0;S.dsplit=50;S.spend=true;renderInputs();optimizeAll({noUndo:true})}""")
    wait()
    r = pg.evaluate("()=>{const b=last.best;return {P:{MED:b.P.MED,FLM:b.P.FLM},fin:{MED:b.final.MED,FLM:b.final.FLM},free:b.free}}")
    check(r['P']['MED'] >= 100 and r['P']['FLM'] >= 100 and r['fin']['MED'] <= 80 and r['fin']['FLM'] <= 80, f"damage slider + leftover spending keep Medium / Flamecharm at 80 or less after 100 before: {r}")
    pg.evaluate("()=>{S.spend=false;S.prio=50}")
    # 6. mages: no automatic Hero's Blade
    pg.evaluate("openAI()"); pg.fill('#aitext', 'flamecharm mage'); pg.click('#ai-go'); pg.wait_for_timeout(500)
    if pg.evaluate("!$('aiqs').hidden"): pg.click('#aiq-go'); pg.wait_for_timeout(300)
    pg.click('#wz-go'); wait()
    r = pg.evaluate("()=>({w:S.weapon,auto:S.weaponAuto,med:last.best.final.MED||0})")
    check(not r['w'] and r['med'] == 0, f"an AI mage gets no Hero's Blade and no weapon points: {r}")
    pg.evaluate("()=>{const p=PRESETS.find(x=>x.n==='Mage');applyPreset(p);renderInputs()}"); pg.wait_for_timeout(300)
    r = pg.evaluate("()=>({w:S.weapon,no:S.noAutoW})")
    check(not r['w'] and r['no'], f"the Mage preset gets no Hero's Blade: {r}")
    check(not errs, 'no page errors ' + str(errs[:2]))
    b.close()
print('FAILED', len(bad)); raise SystemExit(1 if bad else 0)
