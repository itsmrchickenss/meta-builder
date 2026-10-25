import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
URL=(ROOT/'index.html').as_uri()
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':900});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(2500)
    def wait():pg.wait_for_function("!document.getElementById('results').classList.contains('busy')",timeout=180000);pg.wait_for_timeout(400)
    print('tab label',pg.inner_text('#t-bug'),'| ai card',pg.inner_text('.aicard span'))
    print('bug key set',pg.evaluate("BUG_KEY.length>10"))
    pg.evaluate("applyTemplate(TEMPLATES[5])");wait()
    print('cap',pg.evaluate("(()=>{const c=counts(closure());return c.nTal+'/'+c.cap})()"))
    n=pg.evaluate("DB.T.find(t=>t.k&&!closure().T.has(t.n)&&!hasStats(reqAlts(t.req,false))&&!t.req.t.length&&t.r!=='Q'&&t.r!=='O'&&!(t.req.x||[]).length).n")
    pg.evaluate("n=>{const el=document.createElement('button');el.dataset.tadd=encodeURIComponent(n);document.body.appendChild(el);el.click();el.remove()}",n);pg.wait_for_timeout(400)
    print('warning:',pg.inner_text('#copied'))
    pg.locator('#copied input[data-allowover]').click();pg.wait_for_timeout(800)
    print('after tick:',pg.inner_text('#copied')[:120],'| sel has',pg.evaluate(f"S.sel.includes({n!r})"),'| cap',pg.evaluate("(()=>{const c=counts(closure());return c.nTal+'/'+c.cap})()"))
    pg.click('#t-req');pg.wait_for_timeout(300);print('capline:',pg.inner_text('#capline'))
    pg.evaluate("optimizeAll()");pg.wait_for_timeout(300);wait();print('after optimize kept over:',pg.evaluate("(()=>{const c=counts(closure());return c.nTal+'/'+c.cap})()"))
    pg.locator('#capline input[data-allowover]').click();pg.wait_for_timeout(300);pg.evaluate("optimizeAll()");pg.wait_for_timeout(300);wait()
    print('unticked + optimize:',pg.evaluate("(()=>{const c=counts(closure());return c.nTal+'/'+c.cap})()"),pg.evaluate("S.allowOver"))
    print('errs',errs);b.close()
