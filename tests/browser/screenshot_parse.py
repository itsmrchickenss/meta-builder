import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
URL=(ROOT/'index.html').as_uri()
from playwright.sync_api import sync_playwright
OCR="""ATTRIBUTES
Strength 25   Fortitude 50
Agility: 40 Intelligence 0
Wil1power 0  Charisma 25
Light Wep. 0  Medium Wep. 90 Heavy Wep. 0
Flamecharm 80 Frostdraw 0 Thundercall 0
Galebreathe 0 Shadowcast 0 Ironsing 0 Bloodrend 0
TALENTS: Exoskeleton, Speed Demon, Showstopper, Ghost
Oath: Bladeharper"""
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':900});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(2500)
    pg.click('#t-imp');pg.wait_for_timeout(300)
    r=pg.evaluate("t=>JSON.stringify(shotFromText(t))",OCR);print('parsed',r)
    print('game fmt',pg.evaluate("JSON.stringify(shotFromText('25 STR; 50 FTD; 25 AGL; 0 INT; 30 WLL; 0 CHA').fin)"))
    print('arrow pre',pg.evaluate("JSON.stringify(shotFromText('Fortitude 100 -> 75\\nWillpower 100 → 75'))"))
    # simulate a read result
    pg.evaluate("t=>{const g=shotFromText(t);SHOT.fin=g.fin;SHOT.pre=g.pre;SHOT.oath=g.oath;SHOT.seen=[...g.talents];renderShot();renderSeen();guessLikely()}",OCR)
    print('likely count',pg.evaluate("SHOT.likely.length"),'picked',pg.evaluate("shotPicked().length"),'cap',pg.evaluate("shotCap()"))
    print('top10',pg.evaluate("SHOT.likely.slice(0,10).map(r=>r.n+' '+r.pct+'%/'+r.co).join(' | ')"))
    pg.fill('#seenin','flash point');pg.click('#seenform button');pg.wait_for_timeout(300);print('seen msg',pg.inner_text('#seenmsg'))
    pg.fill('#seenin','tap dncer');pg.click('#seenform button');pg.wait_for_timeout(300);print('seen msg',pg.inner_text('#seenmsg'))
    # untick first
    pg.locator('#likely input[type=checkbox]').first.uncheck();pg.wait_for_timeout(200);print('after untick',pg.inner_text('#likelycount'))
    pg.evaluate("document.getElementById('tabbar').style.position='static'")
    pg.locator('#tab-imp').screenshot(path=str(pathlib.Path('/tmp')/'mb-shot.png'))
    pg.click('#shotload');pg.wait_for_timeout(1500)
    pg.wait_for_function("!document.getElementById('results').classList.contains('busy')",timeout=180000);pg.wait_for_timeout(500)
    print('loaded',pg.evaluate("JSON.stringify({tab:S.tab,oath:S.oath,sel:S.sel.length,free:last.best.free,fin:ATTR.map(k=>last.best.final[k]).join(','),w:S.wtype+last.best.final[S.wtype],att:S.atts,cap:(()=>{const c=counts(closure());return c.nTal+'/'+c.cap})()})"))
    print('toast',pg.inner_text('#copied')[:200])
    pg2=b.new_page(viewport={'width':390,'height':900});pg2.goto(URL);pg2.wait_for_timeout(2000);pg2.click('#t-imp');pg2.wait_for_timeout(300);print('390 hscroll',pg2.evaluate("document.documentElement.scrollWidth>innerWidth"))
    print('errs',errs);b.close()
