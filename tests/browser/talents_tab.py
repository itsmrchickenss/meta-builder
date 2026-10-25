import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
URL=(ROOT/'index.html').as_uri()
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':900});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(2500)
    pg.evaluate("applyTemplate(TEMPLATES[0])");pg.wait_for_function("!document.getElementById('results').classList.contains('busy')",timeout=120000);pg.wait_for_timeout(500)
    pg.click('#t-req');pg.wait_for_timeout(500)
    rows=lambda:pg.evaluate("[document.querySelectorAll('#reqbrowse .brow, #reqbrowse > div').length, document.getElementById('reqbrcount').textContent, [...document.querySelectorAll('#reqbrowse b, #reqbrowse .nm')].slice(0,5).map(x=>x.textContent.slice(0,25)).join(' | ')]")
    print('bf buttons',pg.evaluate("[...document.querySelectorAll('#reqbf button')].map(b=>b.textContent+':'+b.getAttribute('aria-pressed'))"))
    print('start',rows())
    for i in range(pg.locator('#reqbf button').count()):
        pg.locator('#reqbf button').nth(i).click();pg.wait_for_timeout(400);print(' bf',pg.locator('#reqbf button').nth(i).inner_text(),pg.evaluate("S.bfilter"),rows())
    pg.locator('#reqbf button').nth(0).click();pg.wait_for_timeout(300)
    for q in ['steam','speed','WLL','ragdoll','ghost']:
        pg.fill('#reqbq',q);pg.wait_for_timeout(400);print(' browse q',q,rows())
    pg.fill('#reqbq','');pg.wait_for_timeout(300)
    for q in ['speed','insanity','charm']:
        pg.fill('#reqin',q);pg.wait_for_timeout(400);print(' reqin q',q,rows(),pg.evaluate("document.getElementById('reqbq').value"))
    print('picked filter:');pg.locator('#tfilter button',has_text='Picked').click();pg.wait_for_timeout(300);print(pg.evaluate("document.querySelectorAll('#tchips .chip').length"))
    print('errs',errs);b.close()
