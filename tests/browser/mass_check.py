# Mass build check: thousands of random, varied builds run through the real optimizer (optCore), each checked by
#  - the independent checker from full_check.py (points, shrine, requirements, the owner's rules),
#  - efficiency: odd pre-shrine values (not 0, 1, a level something needs, the target, or target + 25 for an attribute), and
#    a much deeper search on the same build that must not find a plan with clearly more points free,
#  - speed (optimizing one build should take seconds, not minutes).
# Usage: python3 tests/browser/mass_check.py SEED COUNT [WORKERS] [OUT.jsonl]
# Archetypes: weapon 100 + attunement 100 (with the 100/100 talent), Strength/Agility 100, Saintsworn heavy weapon with
# Agility/Intelligence/Willpower, casters, hybrid paths, Silentheart, tanks, charisma, presets with tweaks, fully random.
import json, pathlib, sys, time, multiprocessing as mp, re
ROOT = pathlib.Path(__file__).resolve().parents[2]
URL = (ROOT / 'index.html').as_uri()
src = (ROOT / 'tests' / 'browser' / 'full_check.py').read_text()
CHECK = re.search(r'CHECK = r"""(.*?)"""', src, re.S).group(1)

GEN = r"""
window.__rng=function(seed){let s=seed>>>0||1;return ()=>{s=(s*1664525+1013904223)>>>0;return s/4294967296}};
window.__gen=function(seed){const r=__rng(seed*7919+13);const pick=a=>a[Math.floor(r()*a.length)];const chance=p=>r()<p;
  const ATTL=['FLM','ICE','LTN','WND','SDW','IRN','BLD'],ELEM=['FLM','ICE','LTN','WND','SDW'];
  const hundred=DB.T.filter(t=>t.k&&Object.entries(t.req.s||{}).some(([k,v])=>v>=100&&(k==='WPN'||WEP[k]))&&Object.entries(t.req.s||{}).some(([k,v])=>v>=100&&ATT[k]));
  const paths=DB.T.filter(t=>/Path/.test(t.n)&&t.k);
  const popular=[...POP.entries()].sort((a,b)=>b[1]-a[1]).slice(0,200).map(x=>x[0]).filter(n=>TBY.has(n));
  const keyT=[...KEY_T].filter(n=>TBY.has(n));
  const oaths=OATHS.map(o=>o.n);
  const c={oath:'None',wtype:pick(WEPS),wtarget:0,weapon:'',atts:{},pre:{},post:{},want:{},t:[],req:[],m:[],prio:pick([20,50,50,80]),dsplit:pick([0,25,50,75,100]),arch:''};
  const lv=()=>pick([40,60,80,80,100]);
  const arch=window.__ARCH||pick(['w100a100','w100a100','strAgl','saintHeavy','saintHeavy','caster','hybrid','silent','tank','charisma','preset','random','random','random','ai','ai']);c.arch=arch;
  if(arch==='ai'){// a description like the ones players type, read by the AI build maker; the wizard's defaults are applied as on "Start build"
    const w=[];const o=pick(['','','jetstriker','bladeharper','blade harper','silentheart','saintsworn','starkindred','contractor','dawnwalker','visionshaper','soulbreaker','oathless','no oath']);if(o)w.push(o);
    w.push(pick(['','heavy','medium','light','greatsword','katana','mage','caster','umbrite witherblade','railblade','hero blade']));
    for(let i=0;i<pick([0,1,1,2]);i++)w.push(pick(['flamecharm','frostdraw','thundercall','galebreathe','shadowcast','ironsing','bloodrend','flame','ice','lightning','wind','shadow','blood','metal']));
    if(chance(.3))w.push(pick(['black flames','steam path','lava path','glass path','puppet path','sanguine blaze','alloyblood path','the 100 100 talents','100 flame 100 weapon talent']));
    if(chance(.4))w.push(pick(['gank','pvp','boss raid','stealth','armor shredding','support','insanity','tanky','semi tanky','glass cannon','block breaking','charm']));
    for(const st of ['strength','agility','intelligence','willpower','charisma','fortitude'])if(chance(.15))w.push(st+' '+pick([25,40,50,65,75,90,100])+(chance(.25)?pick([' before the shrine',' after']):''));
    const txt=w.filter(Boolean).join(', ');const P=aiParse(txt).p;
    c.ai=txt;c.oath=P.oath==='__auto'?'None':P.oath;c.wtype=P.wtype;c.wtarget=P.wtarget;c.weapon=P.weapon||'';c.atts={...P.atts};c.pre={...P.pre};c.post={...P.post};c.want={...(P.want||{})};c.t=[...P.t];c.req=[...(P.req||[])];c.m=[...(P.m||[])];if(P.dsplit!=null)c.dsplit=P.dsplit;
    if(c.oath==='Silentheart'){c.atts={};c.m=[]}return c}
  if(arch==='w100a100'){const t=pick(hundred);const a=Object.keys(t.req.s).find(k=>ATT[k]);c.wtarget=100;c.atts[a]=100;c.req.push(t.n);if(chance(.5))c.atts[pick(ATTL.filter(x=>x!==a))]=pick([40,80]);c.oath=pick(['None','None',...oaths.filter(o=>o!=='Silentheart')]);c.post.FTD=pick([0,50,50])}
  else if(arch==='strAgl'){const v=pick([[100,100],[100,65],[90,40],[40,100]]);if(chance(.5))c.want={STR:v[0],AGL:v[1]};else c.pre={STR:v[0],AGL:v[1]};c.wtarget=pick([80,90,100]);c.post.FTD=pick([50,50,90]);c.oath=pick(['None','Jetstriker','Starkindred','Contractor'])}
  else if(arch==='saintHeavy'){c.oath='Saintsworn';c.wtype='HVY';c.wtarget=pick([75,80,80,90]);const main=pick(ELEM);for(const e of ELEM)c.atts[e]=15;c.atts[main]=pick([60,80,80,100]);c.want={AGL:pick([25,40,40,65]),INT:pick([25,40,50]),WLL:pick([25,40,50])};c.post.FTD=pick([0,50])}
  else if(arch==='caster'){const a=pick(ATTL);c.atts[a]=100;if(chance(.6))c.atts[pick(ATTL.filter(x=>x!==a))]=pick([40,80,100]);c.wtarget=0;c.dsplit=100;c.want={INT:pick([0,40,90]),WLL:pick([0,40,80]),CHA:pick([0,55,75])};for(const k of Object.keys(c.want))if(!c.want[k])delete c.want[k];c.post.FTD=pick([0,50]);c.oath=pick(['None','None','Visionshaper','Arcwarder','Linkstrider','Blindseer'])}
  else if(arch==='hybrid'){const t=pick(paths);c.req.push(t.n);const al=reqAlts(t.req,false)[0]||{min:{}};for(const [k,v] of Object.entries(al.min))if(ATT[k])c.atts[k]=Math.max(v,pick([v,80,100]));c.wtarget=pick([0,75,90,100]);c.oath=pick(['None','Bladeharper','Soulbreaker','Fadetrimmer','Contractor'])}
  else if(arch==='silent'){c.oath='Silentheart';c.pre={STR:pick([50,75,90]),AGL:pick([50,65,75])};c.post={STR:25,AGL:25,FTD:pick([50,90])};c.wtarget=pick([80,90,95,100])}
  else if(arch==='tank'){c.post.FTD=90;if(chance(.6))c.req.push('Reinforced Armor');c.want={STR:pick([25,40,60]),WLL:pick([0,40,80])};if(!c.want.WLL)delete c.want.WLL;c.wtarget=pick([60,80,90]);if(chance(.5))c.atts[pick(ATTL)]=pick([40,80])}
  else if(arch==='charisma'){c.want={CHA:pick([40,55,75,90]),STR:pick([25,40]),AGL:pick([25,40])};c.wtarget=pick([80,90,100]);c.post.FTD=50;c.oath=pick(['None','Visionshaper','Bladeharper'])}
  else if(arch==='preset'){const p=pick(PRESETS.filter(x=>!x.clean));const v=p.variants?pick(p.variants):p;c.oath=v.oath||p.oath;c.wtype=v.wtype||p.wtype;c.wtarget=v.wtarget!=null?v.wtarget:p.wtarget;c.atts={...(v.atts||p.atts)};c.pre={...v.pre};c.post={...v.post};if(v.ftd)c.post.FTD=pick(v.ftd);c.weapon=p.weapon||'';c.t=[...(p.t||[])];c.req=[...(p.req||[])];
    if(chance(.5)){const k=pick(ATTR);c.want[k]=pick([25,40,60])}}
  else{c.oath=pick(oaths);c.wtarget=pick([0,50,60,75,80,90,100]);const na=pick([0,1,1,2,3]);for(let i=0;i<na;i++)c.atts[pick(ATTL)]=lv();for(const k of ATTR){const x=r();if(x<.2)c.want[k]=pick([25,40,50,65,90,100]);else if(x<.3)c.pre[k]=pick([25,40,75]);else if(x<.4)c.post[k]=pick([25,50])}
    if(chance(.4))c.req.push(pick(r()<.5?hundred:paths).n)}
  // talents: popular / key ones, some required; mantras of the attunements
  const nt=pick([0,0,3,6,12]);for(let i=0;i<nt;i++)c.t.push(pick(r()<.6?popular:keyT));
  if(chance(.3))c.req.push(pick(keyT));
  const mats=Object.keys(c.atts);if(mats.length&&chance(.6)&&c.oath!=='Silentheart'){const ms=DB.M.filter(m=>m.ty==='N'&&m.at.some(a=>mats.includes(a))&&!oathTagOf(m.n));for(let i=0;i<pick([1,2,3]);i++)c.m.push(pick(ms).n)}
  if(c.wtarget>0&&chance(.3)){const ws=DB.W.filter(w=>(w.req.s[c.wtype]||0)>0&&(w.req.s[c.wtype]||0)<=c.wtarget);if(ws.length)c.weapon=pick(ws).n}
  if(c.oath==='Silentheart'){c.atts={};c.m=[]}
  c.t=[...new Set(c.t)];c.req=[...new Set(c.req)];return c};

window.__setup=function(c){
  S.manual=false;S.order=true;S.noReup=true;S.mastery={on:false,pre:{},post:{}};S.oath=c.oath||'None';S.wtype=c.wtype||'MED';S.wtarget=c.wtarget||0;S.weapon=c.weapon&&WBY.has(c.weapon)?c.weapon:'';S.weaponAuto=false;S.noAutoW=!c.weapon;
  S.atts={...(c.atts||{})};S.preMin={...(c.pre||{})};S.mins={...(c.post||{})};S.want={...(c.want||{})};S.pin={};S.sel=[...(c.t||[])].filter(n=>TBY.has(n));S.req=[...(c.req||[])].filter(n=>TBY.has(n)||MBY.has(n));
  S.mantras=[...(c.m||[])].filter(n=>MBY.has(n));S.when={};S.avoid=[];S.caps={};S.keep={};S.prio=c.prio==null?50:c.prio;S.dsplit=c.dsplit==null?50:c.dsplit;S.spend=false;S.traits={};S.allowOver=false;S.gear={outfit:'',slots:{},focus:'bal'};S.enchant='None';
  last=null};
// one build: optimize, then check correctness and efficiency
window.__one=function(seed){const c=__gen(seed);__setup(c);const t0=performance.now();let o;
  try{o=optCore(false,true)}catch(e){return {seed,c,P:['crash: '+String(e&&e.message||e)],W:[],ms:performance.now()-t0}}
  const ms=performance.now()-t0;last=o.res;const out={seed,c,P:[],W:[],ms,free:o.res.best?o.res.best.free:null,dropped:o.dropped||[]};
  const b=o.res.best;if(!b){out.P.push('no plan at all');return out}
  try{const ch=__check();out.P.push(...ch.P);out.W.push(...ch.W)}catch(e){out.P.push('checker crash: '+e.message)}
  if(ms>15000)out.P.push('slow: '+Math.round(ms)+' ms');
  const R=o.res.R;out.preP=Object.fromEntries(ALL.filter(k=>b.P[k]).map(k=>[k,b.P[k]]));out.fin=Object.fromEntries(ALL.filter(k=>b.final[k]).map(k=>[k,b.final[k]]));out.noShrine=!!b.noShrine;
  if(!b.impossible&&b.free>=0){
    // odd pre-shrine values: anything a level, a target, 0 or 1 explains is fine; for the rest see whether snapping it saves points
    const lv=k=>{const t=new Set([0,1,R.pre[k],R.fixed[k]||0,(R.want||{})[k]||0,100,...R.thr[k]]);if(ATTR.includes(k)||WEP[k]){const f=Math.max(R.fixed[k]||0,(R.want||{})[k]||0);if(f>1)t.add(Math.min(100,f+25))}
      for(const it of R.items)for(const a of it.alts)if(a.min[k])t.add(a.min[k]);return t};
    for(const k of ALL){const v=b.P[k];if(v>1&&!lv(k).has(v)){let save=null;for(const x of lv(k)){if(x<R.pre[k]||x>R.max[k])continue;const e=evaluate({...b.P,[k]:x},R,R.oathAlts);if(okMove(e,b)&&e.free>=b.free)save=Math.max(save??-99,e.free-b.free)}
      if(save!=null)out.P.push(`odd pre-shrine ${k} ${v} (${b.sh.out[k]} after the shrine, ${b.final[k]} final): ${save>0?'snapping saves '+save+' points':'a clean value costs the same'}`);else out.W.push(`odd pre-shrine ${k} ${v} needed (filler for Power 8 or a sum requirement)`)}}
    // deeper search on the same build
    const deep=searchStats(R,R.oathAlts,{starts:50,iters:300});
    if(deep&&okMove(deep,b)&&deep.free>=b.free+3)out.P.push(`missed ${deep.free-b.free} points: deeper search found ${JSON.stringify(Object.fromEntries(ALL.filter(k=>deep.P[k]).map(k=>[k,deep.P[k]])))} free ${deep.free} vs ${JSON.stringify(out.preP)} free ${b.free}`)}
  return out};
"""

def worker(args):
    wid, seeds, out_path = args
    from playwright.sync_api import sync_playwright
    res = []
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        pg.route('**/fonts.googleapis.com/**', lambda r: r.abort()); pg.route('**/fonts.gstatic.com/**', lambda r: r.abort())
        pg.goto(URL); pg.wait_for_timeout(2500); pg.evaluate(CHECK); pg.evaluate(GEN)
        with open(out_path, 'a') as f:
            for i, sd in enumerate(seeds):
                try: r = pg.evaluate(f"__one({sd})")
                except Exception as e:
                    r = {'seed': sd, 'P': ['harness: ' + str(e)[:200]], 'W': []}
                    pg.goto(URL); pg.wait_for_timeout(2500); pg.evaluate(CHECK); pg.evaluate(GEN)
                if errs: r['P'] = r.get('P', []) + ['page error: ' + e for e in errs]; errs.clear()
                f.write(json.dumps(r) + '\n'); f.flush()
                if r['P']: print(f'[w{wid}] seed {sd} ({r.get("c",{}).get("arch")}): ' + ' | '.join(r['P'])[:500], flush=True)
                if (i + 1) % 50 == 0: print(f'[w{wid}] {i+1}/{len(seeds)}', flush=True)
        b.close()

if __name__ == '__main__':
    seed = int(sys.argv[1]); n = int(sys.argv[2]); w = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    out = sys.argv[4] if len(sys.argv) > 4 else f'/tmp/mass_{seed}.jsonl'
    open(out, 'w').close()
    seeds = [seed * 100000 + i for i in range(n)]
    parts = [(i, seeds[i::w], out) for i in range(w)]
    t0 = time.time()
    with mp.Pool(w) as pool: pool.map(worker, parts)
    rows = [json.loads(l) for l in open(out)]
    bad = [r for r in rows if r['P']]
    print(f'{len(rows)} builds in {time.time()-t0:.0f}s, {len(bad)} with problems')
    from collections import Counter
    kinds = Counter(re.sub(r'[0-9]+', 'N', p.split(':')[0])[:60] for r in rows for p in r['P'])
    for k, v in kinds.most_common(30): print(f'{v:5d}  {k}')
