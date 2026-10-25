import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
URL=(ROOT/'index.html').as_uri()
from playwright.sync_api import sync_playwright
import json
fx=open(ROOT/'tests'/'fixtures'/'dwco-build.json').read()
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':900});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(2500)
    def wait():pg.wait_for_function("!document.getElementById('results').classList.contains('busy')",timeout=60000);pg.wait_for_timeout(600)
    for i in range(1,pg.evaluate("PRESETS.length")):
        pg.evaluate(f"openWizard(PRESETS[{i}])");pg.wait_for_timeout(200)
        vis=pg.evaluate("[!document.getElementById('wz-core').closest('label').hidden,document.getElementById('wz-pop').checked]")
        pg.click('#wz-go');pg.wait_for_timeout(300);wait()
        print(pg.evaluate(f"PRESETS[{i}].n").ljust(20),'FTD pre/final',pg.evaluate("last.best.P.FTD+' / '+last.best.final.FTD"),'talents',pg.evaluate("S.sel.length"),'atts',pg.evaluate("JSON.stringify(S.atts)"),'free',pg.evaluate("last.best.free"),'core/pop',vis)
    # clean slate resets talents, required, gear
    pg.evaluate("S.req=['Ghost'];S.sel=['Exoskeleton'];S.gear.outfit='Flame Worshipper Armor';run()");wait()
    pg.evaluate("openWizard(PRESETS[0])");wait()
    print('clean slate',pg.evaluate("JSON.stringify({req:S.req,sel:S.sel,m:S.mantras,outfit:S.gear.outfit})"))
    # import panel on Stats tab
    pg.click('#t-imp');print('import panel visible',pg.is_visible('#importpanel'))
    pg.fill('#imp1',fx);pg.click('#imp1form button');pg.wait_for_timeout(1500);wait()
    print('json import',pg.evaluate("JSON.stringify({o:S.oath,w:S.weapon,a:S.atts,sel:S.sel.length,m:S.mantras.length,outfit:S.gear.outfit})"),'|',pg.inner_text('#imp1msg'),pg.inner_text('#copied')[:120])
    pg.fill('#imp1','https://deepwoken.co/builder?id=U9Sjyncd');pg.click('#imp1form button');pg.wait_for_timeout(2500)
    print('dwco link msg:',pg.inner_text('#imp1msg')[:200],'| help open',pg.evaluate("document.getElementById('dwcohelp').open"))
    print('bookmarklet ok', pg.evaluate("$('bmlink').href.startsWith('javascript:')"), 'snippet parses', pg.evaluate("(()=>{try{new Function(DWCO_SNIP);return true}catch(e){return String(e)}})()"))
    print('errs',errs);b.close()
