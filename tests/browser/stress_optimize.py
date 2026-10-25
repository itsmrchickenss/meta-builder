import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
URL=(ROOT/'index.html').as_uri()
from playwright.sync_api import sync_playwright
import sys
N=int(sys.argv[1]) if len(sys.argv)>1 else 12
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':900});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(2500)
    def wait():pg.wait_for_function("!document.getElementById('results').classList.contains('busy')",timeout=180000);pg.wait_for_timeout(300)
    bad=0
    for i in range(N):
        pg.evaluate(f"""(()=>{{let seed={i}*7919+13;const rnd=()=>{{seed=(seed*16807)%2147483647;return seed/2147483647}};
          const P=PRESETS[1+Math.floor(rnd()*(PRESETS.length-1))];S.manual=false;S.oath=P.oath;S.wtype=P.wtype;S.wtarget=P.wtarget;S.weapon=P.weapon||'';S.atts={{...P.atts}};S.preMin={{...P.pre}};S.mins={{...P.post}};S.pin={{}};S.req=[...(P.req||[])];S.avoid=[];S.caps={{}};S.mantras=[];S.when={{}};
          const pool=DB.T.filter(t=>t.k&&t.r!=='Q'&&t.r!=='O'&&!t.req.q&&!t.n.startsWith('Oath:')&&hasStats(reqAlts(t.req,false)));S.sel=[];for(let j=0;j<{12}+Math.floor(rnd()*25);j++){{const t=pool[Math.floor(rnd()*pool.length)];if(!S.sel.includes(t.n))S.sel.push(t.n)}}
          window.__p=P.n;run()}})()""".replace('{12}','12'))
        wait();before=pg.evaluate("last.best.free")
        pg.evaluate("optimizeAll()");pg.wait_for_timeout(200);wait()
        r=pg.evaluate("(()=>{const b=last.best,c=counts(closure());return {p:window.__p,free:b.free,imp:b.impossible,sel:S.sel.length,cap:c.nTal+'/'+c.cap}})()")
        ok=r['free']>=0 and not r['imp']
        if not ok: bad+=1
        print('ok ' if ok else 'BAD', i, r['p'], 'before',before,'after',r['free'],'sel',r['sel'],r['cap'], '' if ok else pg.inner_text('#copied')[:200])
    print('bad',bad,'errs',errs);b.close()
