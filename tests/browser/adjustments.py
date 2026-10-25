import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
URL=(ROOT/'index.html').as_uri()
from playwright.sync_api import sync_playwright
ST="(()=>{const b=last.best;return 'free '+b.free+' | fin '+ATTR.map(k=>k+b.final[k]).join(' ')+' | W '+S.wtype+b.final[S.wtype]+' '+(S.weapon||'')+' | atts '+JSON.stringify(S.atts)+' | oath '+S.oath+' | sel '+S.sel.length})()"
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':900});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(2500)
    def wait():pg.wait_for_function("!document.getElementById('results').classList.contains('busy')",timeout=180000);pg.wait_for_timeout(500)
    print('panel hidden before AI:',pg.evaluate("$('adjpanel').hidden"))
    pg.evaluate("openAI()");pg.fill('#aitext','flamecharm medium weapon pvp build');pg.click('#ai-go');pg.wait_for_timeout(400);pg.click('#wz-go');pg.wait_for_timeout(500);wait();pg.wait_for_timeout(800)
    print('panel shown after AI:',not pg.evaluate("$('adjpanel').hidden"));print('start  ',pg.evaluate(ST))
    for t in ["more agility","intelligence to 30","lower charisma by 10","swap flamecharm for frostdraw","add thundercall 40","heavy weapon 90","oath Blindseer","add Speed Demon and Ghost","remove Ghost","tankier","banana"]:
        pg.fill('#adjtext',t);pg.click('#adjgo');pg.wait_for_timeout(300);wait();pg.wait_for_timeout(300)
        print(f'{t!r:34}',pg.inner_text('#adjmsg')[:150].replace('\n',' '));print(' '*36,pg.evaluate(ST))
    pg.evaluate("document.getElementById('tabbar').style.position='static'");pg.locator('#adjpanel').screenshot(path=str(pathlib.Path('/tmp')/'mb-shot.png'))
    print('errs',errs);b.close()
