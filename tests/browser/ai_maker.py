import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
URL=(ROOT/'index.html').as_uri()
from playwright.sync_api import sync_playwright
ST="(()=>({oath:S.oath,atts:S.atts,w:S.weapon,wt:S.wtype+' '+S.wtarget,req:S.req,m:S.mantras,outfit:S.gear.outfit,slots:Object.keys(S.gear.slots).length,free:last.best.free,cap:(()=>{const c=counts(closure());return c.nTal+'/'+c.cap})()}))()"
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':900});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(2500)
    def ai(txt):
        pg.evaluate("openAI()");pg.fill('#aitext',txt);pg.click('#ai-go');pg.wait_for_timeout(400)
        d=pg.inner_text('#wizform p.hint');pg.click('#wz-go');pg.wait_for_timeout(500)
        pg.wait_for_function("!document.getElementById('results').classList.contains('busy')",timeout=90000);pg.wait_for_timeout(800)
        print('\n>>',txt);print('  read:',d[:600]);print('  ',pg.evaluate(ST))
    ai("saintsworn bossraid flamecharm build, flame worshipper outfit, vaporborne, require Fire Blade")
    ai("gank build")
    ai("silentheart hero blade")
    ai("hero blade frost build")
    ai("bossraid with thundercall")
    ai("charisma mage")
    print('errs',errs);b.close()
