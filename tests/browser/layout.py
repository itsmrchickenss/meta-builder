import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
URL=(ROOT/'index.html').as_uri()
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch();errs=[]
    for w in (1280,390):
        pg=b.new_page(viewport={'width':w,'height':1000});pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto(URL);pg.wait_for_timeout(2500)
        for t in ['build','req','sum','arm']:
            pg.click('#t-'+t);pg.wait_for_timeout(400);print(w,t,'hscroll' if pg.evaluate("document.documentElement.scrollWidth>innerWidth") else 'ok')
        pg.click('#t-build');pg.wait_for_timeout(300);pg.locator('#statspanel').screenshot(path=str(pathlib.Path('/tmp')/'mb-shot.png'))
        pg.click('[data-mode=man]');pg.wait_for_timeout(600);print('manual rows',pg.locator('#bstats tr').count());pg.click('[data-mode=opt]');pg.wait_for_timeout(600)
        # old saved tab 'opt' maps to Stats
        pg.evaluate("showTab('opt')");print('opt->',pg.evaluate("S.tab"))
    print('errs',errs);b.close()
