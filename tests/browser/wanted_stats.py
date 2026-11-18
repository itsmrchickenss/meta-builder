# Wanted stats (before or after the shrine, the optimizer picks) and the AI build maker's oath question.
# python3 tests/browser/wanted_stats.py
import pathlib,json
ROOT=pathlib.Path(__file__).resolve().parents[2]
URL=(ROOT/'index.html').as_uri()
from playwright.sync_api import sync_playwright
bad=[]
def check(ok,msg):
    print(('ok   ' if ok else 'FAIL ')+msg)
    if not ok:bad.append(msg)
with sync_playwright() as p:
    b=p.chromium.launch();errs=[]
    pg=b.new_page(viewport={'width':1280,'height':900});pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(2500)
    def wait():pg.wait_for_function("!document.getElementById('results').classList.contains('busy')",timeout=60000);pg.wait_for_timeout(500)
    # oath named in any spelling: no oath question
    for t,o in [('blade harper ironsing medium','Bladeharper'),('jet striker light','Jetstriker'),('silent heart heavy','Silentheart'),('contractor bloodrend','Contractor'),('soul-breaker flame','Soulbreaker')]:
        r=pg.evaluate("t=>{const p=aiParse(t).p;return [p.oath,aiQuestions(p)]}",t)
        check(r[0]==o and 'oath' not in r[1],f'"{t}" -> {r[0]}, questions {r[1]}')
    check('oath' in pg.evaluate("aiQuestions(aiParse('flame mage').p)"),'no oath named: still asks')
    # typed numbers become wanted stats unless the words say before / after
    r=pg.evaluate("aiParse('jetstriker medium, strength 40, agility 65, int 30 before the shrine, willpower 20 after, fort 50').p")
    check(r['want']=={'STR':40,'AGL':65} and r['pre'].get('INT')==30 and r['post'].get('WLL')==20 and r['post'].get('FTD')==50,f"AI reads wanted / before / after: want {r['want']} pre {r['pre']} post {r['post']}")
    # AI build maker -> wizard: the Wanted row is filled, Start build keeps it, the note says where each went
    pg.evaluate("openAI()");pg.fill('#aitext','jetstriker medium semi tanky, strength 40, agility 65, charisma 40');pg.click('#ai-go');pg.wait_for_timeout(600)
    if pg.evaluate("!!document.getElementById('wiz').open")==False and pg.evaluate("!$('aiqs').hidden"):pg.click('#aiq-go');pg.wait_for_timeout(400)
    row=pg.evaluate("Object.fromEntries(ATTR.map(a=>[a,+$('wz-want-'+a).value]).filter(x=>x[1]))")
    check(row=={'STR':40,'AGL':65,'CHA':40},f'wizard Wanted row {row}')
    pg.click('#wz-go');pg.wait_for_timeout(300);wait()
    st=pg.evaluate("JSON.stringify({want:S.want,at:last.best.wantAt,free:last.best.free})")
    check(json.loads(st)['want']=={'STR':40,'AGL':65,'CHA':40} and len(json.loads(st)['at'])==3 and json.loads(st)['free']>=0,'build keeps wanted stats '+st)
    check('Wanted stats:' in pg.inner_text('#note'),'results note says where each wanted stat went')
    # share link round trip
    rt=pg.evaluate("JSON.stringify(decodeBuild(encodeBuild()).want)")
    check(json.loads(rt)=={'STR':40,'AGL':65,'CHA':40},'share link keeps wanted stats '+rt)
    check(pg.evaluate("JSON.stringify(decodeBuild(encodeBuild.call(null)).want)")!=None,'decode ok')
    # an old share code (no wanted stats) decodes to none
    pg.evaluate("S.want={};run()");wait()
    check(pg.evaluate("JSON.stringify(decodeBuild(encodeBuild()).want)")=='{}','no wanted stats: none after decode')
    # Stats tab: the Wanted (either) row edits S.want
    pg.evaluate("document.getElementById('floorsbox').open=true");pg.fill('#wn-STR','50');pg.dispatch_event('#wn-STR','input');pg.dispatch_event('#wn-STR','change');pg.wait_for_timeout(300);wait()
    check(pg.evaluate("S.want.STR")==50,'Stats tab Wanted row sets the wanted value')
    pg.close()
    pg=b.new_page(viewport={'width':390,'height':900});pg.on('pageerror',lambda e:errs.append(str(e)));pg.goto(URL);pg.wait_for_timeout(2500)
    pg.evaluate("openWizard(PRESETS.find(p=>p.n==='High Strength'))");pg.wait_for_timeout(200)
    check(pg.evaluate("document.documentElement.scrollWidth<=window.innerWidth+1"),'390px wizard with the Wanted row: no sideways scroll')
    check(not errs,'no page errors '+str(errs[:3]))
    b.close()
print('FAILED',len(bad))
raise SystemExit(1 if bad else 0)
