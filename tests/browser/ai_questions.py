import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
URL=(ROOT/'index.html').as_uri()
from playwright.sync_api import sync_playwright
ST="(()=>({oath:S.oath,atts:S.atts,wt:S.wtype+' '+S.wtarget,ftd:S.mins.FTD||0,free:last.best.free}))()"
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':900});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(2500)
    def wait():pg.wait_for_function("!document.getElementById('results').classList.contains('busy')",timeout=120000);pg.wait_for_timeout(600)
    def start(txt):
        pg.evaluate("openAI()");pg.fill('#aitext',txt);pg.click('#ai-go');pg.wait_for_timeout(400)
        return pg.evaluate("[...document.querySelectorAll('#aiqbody legend')].map(l=>l.textContent)") if pg.is_visible('#aiqs') else []
    def finish():
        pg.click('#wz-go');pg.wait_for_timeout(400);wait();return pg.evaluate(ST)
    # 1: three attunements with a steam path -> attunement question offers "just what the path needs"
    q=start('thundercall flamecharm frostdraw steam path');print('Q1 questions',q)
    print('  att options',pg.evaluate("[...document.querySelectorAll('.aiqopt')].slice(0,6).map(l=>l.textContent.trim())"))
    pg.check('input[name=aiq-att][value=path]');pg.check('input[name=aiq-wep][value="heavy weapon"]');pg.select_option('#aiq-oath','Dawnwalker');pg.check('input[name=aiq-dur][value="semi tanky"]')
    pg.click('#aiq-go');pg.wait_for_timeout(400);print('  read:',pg.inner_text('#wizform p.hint')[:300]);print('  ',finish())
    # 2: two attunements, choose 80/80
    q=start('flamecharm frostdraw pvp build');print('Q2 questions',q)
    pg.check('input[name=aiq-att][value=both]');pg.click('#aiq-go');pg.wait_for_timeout(400);print('  ',finish())
    # 3: "other" with typed numbers and a different main
    q=start('shadowcast ironsing bloodrend build');pg.select_option('#aiq-main','IRN');pg.wait_for_timeout(200)
    print('Q3 options after main=Ironsing',pg.evaluate("[...document.querySelectorAll('.aiqopt')].slice(0,4).map(l=>l.textContent.trim())"))
    pg.check('input[name=aiq-att][value=other]');pg.fill('[data-aiqatt=SDW]','25');pg.fill('[data-aiqatt=IRN]','90');pg.fill('[data-aiqatt=BLD]','35')
    pg.click('#aiq-go');pg.wait_for_timeout(400);print('  ',finish())
    # 4: skip uses defaults
    q=start('frostdraw thundercall mage');pg.click('#aiq-skip');pg.wait_for_timeout(400);print('Q4 skip',finish())
    # 5: fully specified -> no questions
    q=start('saintsworn bossraid heavy weapon semi tanky flamecharm');print('Q5 questions',q,'wizard open',pg.evaluate("document.getElementById('wiz').open"))
    print('errs',errs);b.close()
