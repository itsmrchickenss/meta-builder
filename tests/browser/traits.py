import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
URL=(ROOT/'index.html').as_uri()
from playwright.sync_api import sync_playwright
fx=open(ROOT/'tests'/'fixtures'/'dwco-build.json').read()
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':900});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(2000)
    def wait():pg.wait_for_function("!document.getElementById('results').classList.contains('busy')",timeout=120000);pg.wait_for_timeout(400)
    pg.evaluate("applyTemplate(TEMPLATES[0])");wait()
    pg.evaluate("S.traits={};renderTraits();run()");wait()
    base=pg.evaluate("[Math.round(last.best.dm.hit*10)/10, Math.round(gearStats(S.gear,last.best.final).hp)]")
    for _ in range(6): pg.click('#traits [data-trait="PRO:1"]')
    for _ in range(6): pg.click('#traits [data-trait="VIT:1"]')
    pg.wait_for_timeout(500);wait()
    print('panel:',pg.inner_text('#traitleft'),'| plus disabled when full:',pg.evaluate("document.querySelector('#traits [data-trait=\"ERU:1\"]').disabled"))
    after=pg.evaluate("[Math.round(last.best.dm.hit*10)/10, Math.round(gearStats(S.gear,last.best.final).hp), last.best.dm.pen]")
    print('weapon hit / hp before',base,'after PRO6 VIT6',after)
    print('effects:',pg.inner_text('#traits').replace('\n',' | ')[:300])
    link=pg.evaluate("buildLink()");pg.evaluate("S.traits={};renderTraits()")
    pg.evaluate("l=>{Object.assign(S,decodeBuild(l));renderInputs()}",link);print('share link round trip',pg.evaluate("JSON.stringify(S.traits)"))
    gt=pg.evaluate("buildGameText()");print('game text has traits:','== TRAITS ==' in gt, gt.split('== TRAITS ==')[-1].strip()[:40] if '== TRAITS ==' in gt else '')
    pg.evaluate("S.traits={};renderTraits()");pg.evaluate("t=>applyDwb(dwbFromGameText(t))",gt);wait();print('game text import',pg.evaluate("JSON.stringify(S.traits)"))
    pg.evaluate("S.traits={};renderTraits()");pg.evaluate("t=>applyDwb(dwbFromCoJson(JSON.parse(t)))",fx);wait();print('deepwoken.co import',pg.evaluate("JSON.stringify(S.traits)"))
    pg.evaluate("openWizard(PRESETS[0])");wait();print('clean slate',pg.evaluate("JSON.stringify(S.traits)"))
    for n in ['Bossraid Mage','Chime']:
        pg.evaluate(f"openWizard(PRESETS.find(p=>p.n==={n!r}))");pg.wait_for_timeout(200);pg.click('#wz-go');pg.wait_for_timeout(300);wait();print(n,'suggested',pg.evaluate("JSON.stringify(S.traits)"))
    pg.evaluate("document.getElementById('tabbar').style.position='static'");pg.locator('#traitpanel').screenshot(path=str(pathlib.Path('/tmp')/'mb-shot.png'))
    print('errs',errs);b.close()
