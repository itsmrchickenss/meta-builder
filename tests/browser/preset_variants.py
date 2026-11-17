# Every preset's variation menu: picking a variation fills the wizard (stats, Fortitude, attunements, weapon level,
# damage focus, oath), "Start build" loads it within budget, and edits after picking one are kept.
# python3 tests/browser/preset_variants.py
import pathlib,json
ROOT=pathlib.Path(__file__).resolve().parents[2]
URL=(ROOT/'index.html').as_uri()
from playwright.sync_api import sync_playwright
bad=[]
def check(ok,msg):
    print(('ok   ' if ok else 'FAIL ')+msg)
    if not ok:bad.append(msg)
with sync_playwright() as p:
    b=p.chromium.launch();errs=[]
    for width in (1280,390):
        pg=b.new_page(viewport={'width':width,'height':900});pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto(URL);pg.wait_for_timeout(2500)
        def wait():pg.wait_for_function("!document.getElementById('results').classList.contains('busy')",timeout=60000);pg.wait_for_timeout(500)
        n=pg.evaluate("PRESETS.length")
        check(pg.evaluate("PRESETS.filter(p=>!p.clean).every(p=>p.variants&&p.variants.length>=2)"),f'{width}px: every preset but Clean Slate has 2+ variations')
        for i in range(1,n):
            name=pg.evaluate(f"PRESETS[{i}].n");nv=pg.evaluate(f"PRESETS[{i}].variants.length")
            for j in range(nv):
                pg.evaluate(f"openWizard(PRESETS[{i}])");pg.wait_for_timeout(150)
                pg.select_option('#wz-var',str(j));pg.wait_for_timeout(100)
                want=pg.evaluate(f"""(()=>{{const p=PRESETS[{i}],x=p.variants[{j}];const ftd=$('wz-ftd')?+$('wz-ftd').value:null;const post={{...x.post}};if(ftd)post.FTD=ftd;
                  const got={{}};for(const a of ATTR){{got[a]=[+$('wz-pre-'+a).value,+$('wz-post-'+a).value]}}
                  const okS=ATTR.every(a=>got[a][0]===snap5(x.pre[a]||0)&&got[a][1]===snap5(post[a]||0));
                  const rows=[...document.querySelectorAll('#wz-atts .wzatt')].map(r=>[r.querySelectorAll('select')[0].value,+r.querySelectorAll('select')[1].value]).filter(r=>r[0]);
                  const wantA=Object.entries(x.atts||p.atts);const okA=!x.atts||(rows.length===wantA.length&&wantA.every(([k,v])=>rows.some(r=>r[0]===k&&r[1]===v)));
                  const okW=x.wtarget==null||+$('wz-wv').value===x.wtarget;
                  const okO=x.oath?$('wz-oath').value===x.oath:true;
                  const btn=$('wz-wbtns');const okB=!btn||(getComputedStyle(btn).display==='none')===!(+$('wz-wv').value>0);
                  return {{okS,okA,okW,okO,okB}}}})()""")
                check(all(want.values()),f'{width}px {name} / variation {j+1}: form filled {json.dumps(want) if not all(want.values()) else ""}')
                if width==1280:
                    pg.click('#wz-go');pg.wait_for_timeout(300);wait()
                    free=pg.evaluate("last.best.free");check(free>=0,f'{width}px {name} / variation {j+1}: loads within budget (free {free})')
                else:
                    pg.evaluate("closeWizard()")
        # edits after picking a variation are kept: pick variation 2 of High Strength, change Charisma before, start
        hs=pg.evaluate("PRESETS.findIndex(p=>p.n==='High Strength')")
        pg.evaluate(f"openWizard(PRESETS[{hs}])");pg.select_option('#wz-var','1');pg.select_option('#wz-pre-CHA','25')
        if width==1280:
            pg.click('#wz-go');pg.wait_for_timeout(300);wait()
            check(pg.evaluate("S.preMin.CHA===25&&S.preMin.AGL===65&&S.preMin.STR===100"),f'{width}px own edits on top of a variation are kept ({pg.evaluate("JSON.stringify(S.preMin)")})')
        else:
            check(pg.evaluate("document.documentElement.scrollWidth<=window.innerWidth+1"),f'{width}px wizard with variations: no sideways scroll')
            pg.evaluate("closeWizard()")
        pg.close()
    check(not errs,'no page errors '+str(errs[:3]))
    b.close()
print('FAILED',len(bad) if bad else 0)
raise SystemExit(1 if bad else 0)
