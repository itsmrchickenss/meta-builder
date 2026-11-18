# Clicks every visible button, toggle and dropdown in every tab, like a person poking around, starting from builds that use a
# Medium weapon. Flags: page errors, a click that changes the weapon type or sets the weapon target to 0 when the control
# wasn't a weapon control, a build left over budget, and attunements or stats placed at a level nothing needs (75 Flamecharm).
# python3 tests/browser/monkey.py [seed] [presets]
import pathlib,json,random,sys
ROOT=pathlib.Path(__file__).resolve().parents[2]
URL=(ROOT/'index.html').as_uri()
SEED=int(sys.argv[1]) if len(sys.argv)>1 else 1
NP=int(sys.argv[2]) if len(sys.argv)>2 else 6
ONLY=sys.argv[3] if len(sys.argv)>3 else None
from playwright.sync_api import sync_playwright
bad=[]
def flag(msg):
    print('FAIL '+msg,flush=True);bad.append(msg)
SKIP=('bugsend','file','download','export','print','share','copy','reset','clear all','delete','report')
# a level in final/pre that no talent, mantra, weapon, floor or user value asks for
ODD=r"""(()=>{const b=last&&last.best;if(!b)return [];const R=requirements();const lv={};const addL=(k,v)=>{(lv[k]=lv[k]||new Set()).add(v)};
  for(const it of R.items)for(const a of it.alts){for(const [k,v] of Object.entries(a.min))addL(k,v)}
  for(const a of R.oathAlts||[])for(const [k,v] of Object.entries(a.min))addL(k,v);
  for(const [k,v] of Object.entries(S.atts||{}))addL(k,+v);for(const [k,v] of Object.entries(S.mins||{}))addL(k,+v);for(const [k,v] of Object.entries(S.preMin||{}))addL(k,+v);
  for(const [k,v] of Object.entries(S.want||{}))addL(k,+v);addL(S.wtype,+S.wtarget);
  const out=[];for(const k of ATTS){const f=b.final[k]||0,p=b.P[k]||0;if(f>1&&!(lv[k]&&[...lv[k]].some(v=>v===f))&&!(lv[k]&&[...lv[k]].some(v=>v>f)))out.push(k+' final '+f+' (needs '+[...(lv[k]||[])].join('/')+')');
    if(p>f&&p>1&&!(lv[k]&&[...lv[k]].some(v=>v===p)))out.push(k+' before '+p+' after '+f+' (needs '+[...(lv[k]||[])].join('/')+')')}
  return out})()"""
with sync_playwright() as p:
    br=p.chromium.launch();rng=random.Random(SEED)
    for width in (1280,390):
        pg=br.new_page(viewport={'width':width,'height':900});errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('dialog',lambda d:d.dismiss())
        pg.goto(URL);pg.wait_for_timeout(2500)
        def idle():
            try:pg.wait_for_function("!document.getElementById('results').classList.contains('busy')&&!document.querySelector('#optpop:not([hidden])')",timeout=90000)
            except Exception:flag(f'{width}px: still busy after 90 s')
            pg.wait_for_timeout(250)
        med=pg.evaluate("PRESETS.map((p,i)=>[i,p.n,p.wtype,p.wtarget]).filter(x=>x[2]==='MED'&&x[3]>0)")
        rng.shuffle(med)
        if ONLY:med=[m for m in med if ONLY in m[1]]
        for i,name,_,_ in med[:NP]:
            pg.evaluate(f"openWizard(PRESETS[{i}])");pg.wait_for_timeout(200);pg.click('#wz-go');idle()
            for tab in ('build','req','sum','arm','build'):
                pg.evaluate(f"document.querySelector('[role=tab][data-tab={tab}]').click()");pg.wait_for_timeout(300)
                n=pg.evaluate(f"""(()=>{{const root=document.getElementById('tab-{tab}')||document.body;const els=[...root.querySelectorAll('button,select,input[type=checkbox],input[type=radio],input[type=number],summary')].filter(e=>e.offsetParent&&!e.disabled);
                  els.forEach((e,j)=>e.setAttribute('data-mk',j));return els.length}})()""")
                order=list(range(n));rng.shuffle(order)
                for j in order[:60]:
                    info=pg.evaluate(f"""(()=>{{const e=document.querySelector('[data-mk="{j}"]');if(!e||!e.offsetParent)return null;
                      const lab=(e.textContent||e.getAttribute('aria-label')||e.id||e.name||'').trim().replace(/\\s+/g,' ').slice(0,50);
                      return {{tag:e.tagName,type:e.type||'',id:e.id,lab,w:!!e.closest('#wtype,#wquick,#wz-wbtns,#wpicked,#wsearch-res,.wres')||/weapon|wep|heavy|medium|light|\\bw(type|target|q|pick|use|clear)\\b/i.test(e.outerHTML.slice(0,200))}}}})()""")
                    if not info:continue
                    if any(s in (info['lab']+' '+info['id']).lower() for s in SKIP):continue
                    before=pg.evaluate("[S.wtype,+S.wtarget,S.manual]")
                    loc=pg.locator(f'[data-mk="{j}"]')
                    try:
                        if info['tag']=='SELECT':
                            opts=pg.evaluate(f"[...document.querySelector('[data-mk=\"{j}\"]').options].map(o=>o.value)")
                            if opts:loc.select_option(rng.choice(opts),timeout=2000)
                        elif info['type']=='number':
                            v=pg.evaluate(f"+document.querySelector('[data-mk=\"{j}\"]').value||0");loc.fill(str(max(0,min(100,v+rng.choice([-5,5,10])))),timeout=2000);loc.press('Tab')
                        else:loc.click(timeout=2000)
                    except Exception:continue
                    pg.wait_for_timeout(120);idle()
                    after=pg.evaluate("[S.wtype,+S.wtarget,S.manual]")
                    if not info['w'] and not before[2] and (after[0]!=before[0] or (before[1]>0 and after[1]==0)):
                        flag(f"{width}px {name} [{tab}] clicking {info['tag']} '{info['lab']}' ({info['id']}) changed weapon {before[0]} {before[1]} -> {after[0]} {after[1]}")
                    if errs:flag(f"{width}px {name} [{tab}] after '{info['lab']}': {errs[:2]}");errs.clear()
                    # close anything that popped up
                    pg.keyboard.press('Escape');pg.evaluate("document.querySelectorAll('.modal:not([hidden]),dialog[open]').forEach(m=>{const c=m.querySelector('[data-close],.close,.x');if(c)c.click()})")
                    if pg.evaluate(f"!document.getElementById('tab-{tab}')||document.getElementById('tab-{tab}').hidden"):
                        pg.evaluate(f"document.querySelector('[role=tab][data-tab={tab}]').click()");pg.wait_for_timeout(200)
                        pg.evaluate(f"""(()=>{{const root=document.getElementById('tab-{tab}');[...root.querySelectorAll('button,select,input[type=checkbox],input[type=radio],input[type=number],summary')].filter(e=>e.offsetParent&&!e.disabled&&!e.hasAttribute('data-mk')).forEach((e,k)=>e.setAttribute('data-mk','n'+k))}})()""")
            pg.evaluate("optimizeAll&&optimizeAll()");idle()
            odd=pg.evaluate(ODD);free=pg.evaluate("last&&last.best?last.best.free:null")
            if odd and not pg.evaluate("S.manual"):flag(f"{width}px {name}: odd levels after Optimize: {odd} | state "+pg.evaluate("JSON.stringify({oath:S.oath,atts:S.atts,mins:S.mins,preMin:S.preMin,want:S.want,pin:S.pin,caps:S.caps,mantras:S.mantras,req:S.req,P:Object.fromEntries(Object.entries(last.best.P).filter(([k,v])=>v)),fin:Object.fromEntries(Object.entries(last.best.final).filter(([k,v])=>v))})"))
            if free is not None and free<0 and not pg.evaluate("S.allowOver"):flag(f"{width}px {name}: over budget ({free})")
            print(f'{width}px {name}: done',flush=True)
    br.close()
print(f'{len(bad)} problems')
sys.exit(1 if bad else 0)
