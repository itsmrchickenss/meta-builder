# Full check: many builds (presets x attunements x talent paths x stat changes, AI build maker descriptions, popular
# deepwoken.co reference builds), each optimized and auto-picked at several stages, then the Summary and Armor tabs and
# import/export. Every state is checked by an independent checker (window.__check) that recomputes points, the shrine,
# requirements and the owner's rules from the raw data instead of trusting the optimizer's own numbers.
# Usage: python3 tests/browser/full_check.py [seed] [scale]   (scale 1 = about 300 builds)
import json, pathlib, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[2]
URL = (ROOT / 'index.html').as_uri()
SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 1
SCALE = float(sys.argv[2]) if len(sys.argv) > 2 else 1
FROM = int(sys.argv[3]) if len(sys.argv) > 3 else None
SECTIONS = FROM is None or FROM < 0  # FROM -1: skip the random builds, run every other section
TO = int(sys.argv[4]) if len(sys.argv) > 4 else None
from playwright.sync_api import sync_playwright

CHECK = r"""
window.__check=function(){
  const P=[],W=[];const b=last&&last.best;if(!b)return {P:['no result'],W};
  if(b.impossible)P.push('impossible build');
  const pre=b.P,fin=b.final;const sum=o=>ALL.reduce((s,k)=>s+(o[k]||0),0);
  for(const k of ALL){for(const [nm,o] of [['pre',pre],['final',fin]]){const v=o[k];if(!Number.isFinite(v)||v<0||v>100)P.push(`${nm} ${k} out of range: ${v}`)}}
  const preSum=sum(pre);if(preSum>BUDGET&&!(b.noShrine&&b.manual))P.push('pre-shrine points over the budget: '+preSum);
  const mastery=S.mastery&&S.mastery.on;
  const useShrine=S.order!==false&&!b.noShrine;
  if(useShrine&&powerAt(preSum)<SHRINE_PWR)P.push('shrine used below Power 8 (pre '+preSum+')');
  if(S.order!==false&&!useShrine&&powerAt(preSum)>=SHRINE_PWR&&!mastery)W.push('shrine skipped at Power '+powerAt(preSum));
  const sh=useShrine?shrine(pre):{out:{...pre},refund:0};
  if(useShrine&&!mastery)for(const k of ATTR)if(pre[k]>0&&sh.out[k]<pre[k]-25)P.push(`shrine took more than 25 from ${k}: ${pre[k]} -> ${sh.out[k]}`);
  if(!mastery){let adds=0;for(const k of ALL){if(fin[k]<sh.out[k])P.push(`final ${k} ${fin[k]} below the shrine result ${sh.out[k]}`);adds+=fin[k]-sh.out[k]}
    const nAtt=ATTS.filter(k=>fin[k]>0).length;const used=preSum-sh.refund+adds-Math.max(0,nAtt-1);
    if(used!==b.used)P.push(`points used: checker ${used}, builder ${b.used}`);
    if(BUDGET-used<0)(S.manual?W:P).push('over the 330 budget by '+(used-BUDGET));
    if(b.free!==BUDGET-used&&!b.capOver&&!b.reup)P.push(`free points shown ${b.free}, should be ${BUDGET-used}`)}
  // the owner's rule: pre-shrine is the peak for attributes
  if(useShrine&&!S.manual)for(const k of ATTR)if(pre[k]>1&&!(S.pin&&k in S.pin)&&fin[k]>sh.out[k])P.push(`${k} raised again after the shrine: ${pre[k]} -> ${sh.out[k]} -> ${fin[k]}`);
  if(useShrine&&!S.manual&&pre.FTD>1&&pre.FTD===fin.FTD&&!(S.pin&&'FTD' in S.pin))P.push('Fortitude the same before and after: '+pre.FTD);
  const caps=capsOf();for(const [k,v] of Object.entries(caps))if(fin[k]>v)P.push(`${k} over its limit ${v}: ${fin[k]}`);
  for(const [k,v] of Object.entries(S.atts||{}))if(fin[k]<Math.min(+v||0,k in caps?caps[k]:100))P.push(`attunement ${k} ${fin[k]} under its target ${v}`);
  if(S.wtarget&&fin[S.wtype]<Math.min(S.wtarget,S.wtype in caps?caps[S.wtype]:100))P.push(`weapon ${S.wtype} ${fin[S.wtype]} under its target ${S.wtarget}`);
  for(const [k,v] of Object.entries(S.mins||{}))if(v&&fin[k]<Math.min(v,k in caps?caps[k]:100))P.push(`${k} ${fin[k]} under its after-shrine floor ${v}`);
  for(const [k,v] of Object.entries(S.pin||{}))if(pre[k]!==v)P.push(`pinned ${k} ${v} but pre is ${pre[k]}`);
  const C=closure();const blocked=new Set((last.R&&last.R.capBlocked)||[]);
  const met=(req,isW,o)=>{const al=reqAlts(req,isW);return !hasStats(al)||al.some(a=>altCost(a,o)===0)};
  for(const n of C.T.keys()){const t=TBY.get(n);const okPre=met(t.req,false,pre),okFin=met(t.req,false,fin);
    if(!okPre&&!okFin&&!blocked.has(n))(S.manual?W:P).push('talent requirement not met: '+n+' ('+fmtReq(t.req)+')');
    else if(!okFin&&S.when[n]==='post')P.push('talent set to after the shrine but only the pre-shrine stats meet it: '+n);
    for(const x of t.req.t||[])if(x.startsWith('Oath:')&&x!=='Oath: '+S.oath)P.push('talent of another oath: '+n);
    for(const x of t.req.x||[])if(C.T.has(x)&&n<x)P.push('mutually exclusive talents both taken: '+n+' / '+x)}
  for(const n of C.M.keys()){const m=MBY.get(n);if(!met(m.req,false,pre)&&!met(m.req,false,fin))P.push('mantra requirement not met: '+n);
    if(S.oath==='Silentheart'&&m.at.some(a=>ATT[a])&&!oathTagOf(n))P.push('Silentheart with an attunement mantra: '+n)}
  if(S.weapon&&!blocked.has(S.weapon)){const w=WBY.get(S.weapon);if(w&&!met(w.req,true,fin))P.push('weapon requirement not met: '+S.weapon+' ('+fmtReq(w.req)+')')}
  if(S.oath&&S.oath!=='None'){const al=oathAltsOf(findO(S.oath));if(al&&!al.some(a=>altCost(a,fin)===0))P.push('oath requirement not met: '+S.oath)}
  const cn=counts(C);if(cn.nTal>cn.cap&&!S.allowOver)P.push(`over the talent cap: ${cn.nTal}/${cn.cap}`);
  for(const n of S.req||[])if(!C.T.has(n)&&!C.M.has(n)&&(TBY.has(n)||MBY.has(n)))P.push('required talent missing: '+n);
  for(const n of S.sel)if((S.avoid||[]).includes(n)&&!(S.req||[]).includes(n))P.push('avoided talent picked: '+n);
  if(!Number.isFinite(b.damage)||!Number.isFinite(b.score))P.push('damage or score not a number');
  return {P,W};
};
window.__snap=()=>({oath:S.oath,w:S.wtype+' '+S.wtarget,weapon:S.weapon,atts:S.atts,sel:S.sel.length,req:S.req.length,m:S.mantras.length,free:last&&last.best?last.best.free:null,cap:(()=>{const c=counts(closure());return c.nTal+'/'+c.cap})()});
window.__badText=el=>{const t=(document.getElementById(el)||{innerText:''}).innerText;const m=t.match(/\bNaN\b|\bundefined\b|\bInfinity\b|\[object Object\]|\bnull\b/);return m?m[0]+' in: '+t.slice(Math.max(0,m.index-60),m.index+40).replace(/\s+/g,' '):''};
"""

problems, warns, counts = [], [], {'builds': 0, 'checks': 0}
def rec(tag, res, extra=None):
    counts['checks'] += 1
    for x in res['P']:
        problems.append(f'{tag}: {x}'); print('PROBLEM', f'{tag}: {x}'[:400], flush=True)
    for x in res['W']: warns.append(f'{tag}: {x}')

with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(accept_downloads=True, viewport={'width': 1280, 'height': 900}); pg = ctx.new_page()
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
    pg.on('console', lambda m: errs.append('console: ' + m.text[:300]) if m.type == 'error' and 'fonts.g' not in m.text and 'ERR_FAILED' not in m.text else None)
    pg.route('**/fonts.googleapis.com/**', lambda r: r.abort()); pg.route('**/fonts.gstatic.com/**', lambda r: r.abort())
    pg.goto(URL); pg.wait_for_timeout(2500); pg.evaluate(CHECK)
    def wait():
        pg.wait_for_function("!document.getElementById('results').classList.contains('busy')", timeout=240000); pg.wait_for_timeout(150)
    def check(tag): rec(tag, pg.evaluate("__check()"))
    def opt(tag):
        pg.evaluate("optimizeAll()"); pg.wait_for_timeout(50); wait(); check(tag + ' optimize')
    def autopick(tag):
        pg.evaluate("autoPick()"); wait(); check(tag + ' auto-pick')

    # ---------- summary / armor / import-export checks on the current build ----------
    def tabs(tag):
        pg.evaluate("showTab('sum')"); pg.wait_for_timeout(250)
        for el in ['dmg', 'winfo', 'steps', 'recs', 'mviewout', 'wcmpout']:
            t = pg.evaluate(f"__badText('{el}')")
            if t: problems.append(f'{tag}: Summary #{el} shows {t}')
        if not pg.evaluate("(document.getElementById('dmg')||{}).innerText||''").strip(): problems.append(f'{tag}: Summary damage is empty')
        # compare weapons: pick a few weapons of this type
        r = pg.evaluate("""(()=>{const s=document.getElementById('wcmp');if(!s)return 'no compare select';const opts=[...s.options].filter(o=>o.value).slice(0,3);if(!opts.length)return 'compare has no weapons';
            for(const o of opts){s.value=o.value;s.dispatchEvent(new Event('change',{bubbles:true}))}return ''})()""")
        pg.wait_for_timeout(150)
        if r and r != 'compare has no weapons': problems.append(f'{tag}: {r}')
        t = pg.evaluate("__badText('wcmpout')")
        if t: problems.append(f'{tag}: weapon compare shows {t}')
        # recommended talents: Take the first one, it must still be a valid build
        took = pg.evaluate("""(()=>{const bt=document.querySelector('#recs [data-tadd]');if(!bt)return null;const n=decodeURIComponent(bt.dataset.tadd);if(!roomFor(n))return null;bt.click();return n})()""")
        if took:
            wait(); res = pg.evaluate("__check()"); rec(tag + f' after Take {took}', {'P': [x for x in res['P'] if 'over the 330' not in x and 'free points shown' not in x], 'W': []})
            if took not in pg.evaluate("S.sel"): problems.append(f'{tag}: Take {took} did not add it')
        # armor
        pg.evaluate("showTab('arm')"); pg.wait_for_timeout(200)
        pg.click('#gearopt'); pg.wait_for_timeout(400)
        g = pg.evaluate("""(()=>{const f=last.best.final;const st=gearStats(S.gear,f);const els=[];const tr=[];
            for(const [l,s] of Object.entries(S.gear.slots||{})){if(!s)continue;if((s.p||[]).includes('E'))els.push(s.n);if(GEAR_NEVER.has(s.n))tr.push(s.n)}
            const maxhp=gearStats(optimizeGear(f,{a:0,minhp:0,minpp:0}),f).hp;const maxpp=gearStats(optimizeGear(f,{a:3,minhp:0,minpp:0}),f).pp;
            let both=false;for(const o of [{a:0,minhp:500,minpp:50},{a:1,minhp:500,minpp:50},{a:2,minhp:500,minpp:50},{a:3,minhp:500,minpp:0},{a:0,minhp:0,minpp:50}]){const x=gearStats(optimizeGear(f,o),f);if(x.hp>=500&&x.pp>=50)both=true}
            return {both,hp:Math.round(st.hp),pp:Math.round(st.pp),bad:st.bad,els,tr,maxhp:Math.round(maxhp),maxpp:Math.round(maxpp),outfit:S.gear.outfit,minhp:S.gear.minhp??500,minpp:S.gear.minpp??50}})()""")
        if g['els']: problems.append(f'{tag}: armor optimizer used elemental pips on {g["els"]}')
        if g['tr']: problems.append(f'{tag}: armor optimizer equipped {g["tr"]}')
        if g['bad']: problems.append(f'{tag}: armor optimizer equipped gear the stats can\'t wear: {g["bad"]}')
        if g['both'] and (g['hp'] < 500 or g['pp'] < 50): problems.append(f'{tag}: Optimize equipment gave {g["hp"]} HP / {g["pp"]}% physical although 500 HP + 50% is reachable')
        elif not g['both'] and (g['hp'] < 500 or g['pp'] < 50): warns.append(f'{tag}: 500 HP + 50% physical not reachable with these stats (got {g["hp"]} HP / {g["pp"]}%)')
        for el in ['ehp', 'gslots', 'goutinfo']:
            t = pg.evaluate(f"__badText('{el}')")
            if t: problems.append(f'{tag}: Armor #{el} shows {t}')
        pg.evaluate("showTab('build')")
        return g

    def roundtrip(tag):
        before = pg.evaluate("JSON.stringify({o:S.oath,w:S.wtype,t:S.wtarget,a:S.atts,s:[...S.sel].sort(),m:[...S.mantras].sort(),r:[...S.req].sort(),p:S.weapon})")
        plan_before = pg.evaluate("JSON.stringify({P:last.best.P,f:last.best.final,free:last.best.free})")
        code = pg.evaluate("encodeBuild()")
        game = pg.evaluate("buildGameText()"); file = pg.evaluate("buildFileText()")
        # share link
        pg.evaluate("c=>{Object.assign(S,decodeBuild(c));renderInputs();run()}", code); pg.wait_for_timeout(100)
        after = pg.evaluate("JSON.stringify({o:S.oath,w:S.wtype,t:S.wtarget,a:S.atts,s:[...S.sel].sort(),m:[...S.mantras].sort(),r:[...S.req].sort(),p:S.weapon})")
        if after != before: problems.append(f'{tag}: share code round trip changed the build')
        plan_after = pg.evaluate("JSON.stringify({P:last.best.P,f:last.best.final,free:last.best.free})")
        if plan_after != plan_before: problems.append(f'{tag}: share link opened with a different plan: {plan_before} -> {plan_after}')
        res = pg.evaluate("__check()")
        if json.loads(plan_before)['free'] < 0: res['P'] = [x for x in res['P'] if 'over the 330' not in x]
        rec(tag + ' share import', res)
        # Deepwoken text and build file: import back, stats and talents must survive
        for kind, txt in [('Deepwoken text', game), ('build file', file)]:
            if not txt: problems.append(f'{tag}: {kind} export is empty'); continue
            ok = pg.evaluate("async t=>{const r=await smartImport(t);return !!(r&&r.ok)}", txt); pg.wait_for_timeout(300); wait()
            if not ok: problems.append(f'{tag}: {kind} export does not import back'); continue
            got = pg.evaluate("JSON.stringify({s:[...S.sel,...S.req].filter(n=>TBY.has(n)).sort()})")
            src = json.loads(before); want = sorted(set([n for n in src['s'] + src['r']]))
            have = set(json.loads(got)['s']); miss = [n for n in want if n not in have and pg.evaluate("n=>!!TBY.get(n)&&TBY.get(n).k", n)]
            if miss: problems.append(f'{tag}: {kind} round trip lost talents {miss[:6]}')
            if pg.evaluate("S.oath") != src['o'] and src['o'] not in ('None', '__auto'): problems.append(f'{tag}: {kind} round trip changed the oath {src["o"]} -> {pg.evaluate("S.oath")}')
            check(tag + f' {kind} import')
            pg.evaluate("S.manual=false;renderShrines()")
        # put the original build back
        pg.evaluate("c=>{Object.assign(S,decodeBuild(c));renderInputs();run()}", code); pg.wait_for_timeout(100)

    # ---------- build generator ----------
    ATT_SETS = [{}, {'FLM': 80}, {'ICE': 80, 'FLM': 40}, {'LTN': 80, 'WND': 40}, {'SDW': 100}, {'IRN': 80, 'BLD': 80}, {'BLD': 80, 'FLM': 40},
                {'ICE': 80, 'LTN': 40, 'FLM': 40}, {'WND': 60}, {'FLM': 80, 'ICE': 30, 'LTN': 80}]
    PATHS = [[], ['Flashboil'], ['Eruption Path: Lava Serpent'], ['Glass Path: Crystallization'], ['Composite Path: Alloyblood'],
             ['Exotherm Path: Sanguine Blaze'], ['Wraith Path: Twisted Puppets'], ['Gilded Path: Scrapsinger']]
    presets = pg.evaluate("PRESETS.map(p=>p.n)")
    n_builds = int(120 * SCALE)
    def setup(i):
        return pg.evaluate("""([i,seed,ATT,PATH])=>{let s=(i+1)*7919+seed*104729;const rnd=()=>{s=(s*16807)%2147483647;return s/2147483647};const pick=a=>a[Math.floor(rnd()*a.length)];
          const P=PRESETS[1+Math.floor(rnd()*(PRESETS.length-1))];S.manual=false;S.allowOver=false;S.order=true;S.mastery={on:false,pre:{},post:{}};
          S.oath=P.oath;S.wtype=pick(['LHT','MED','HVY']);if(rnd()<.5)S.wtype=P.wtype;S.wtarget=pick([0,40,60,75,90,P.wtarget]);S.atts={...(rnd()<.4?P.atts:pick(ATT))};
          if(S.oath==='Silentheart')S.atts={};
          const ws=DB.W.filter(w=>w.ty&&WDMG.has(w.n)&&(w.req.s[S.wtype]||0)>0&&!w.req.t.length);S.weapon=rnd()<.5&&ws.length?pick(ws).n:'';
          S.preMin={...P.pre};S.mins={...P.post};for(const a of ATTR)if(rnd()<.15){const v=pick([10,25,40,50,60,75]);if(rnd()<.5)S.preMin[a]=v;else S.mins[a]=v}
          S.pin={};S.req=[...(P.req||[])];S.avoid=[];S.caps={};S.mantras=[];S.when={};S.prio=pick([20,50,80]);S.dsplit=pick([0,50,100]);
          const path=pick(PATH);S.sel=[...path];
          const pool=DB.T.filter(t=>t.k&&t.r!=='Q'&&t.r!=='O'&&!t.req.q&&!t.n.startsWith('Oath:')&&hasStats(reqAlts(t.req,false)));
          const clash=n=>S.sel.some(h=>(TBY.get(h).req.x||[]).includes(n)||(TBY.get(n).req.x||[]).includes(h));for(let j=0;j<Math.floor(rnd()*20);j++){const t=pick(pool);if(!S.sel.includes(t.n)&&!clash(t.n))S.sel.push(t.n)}
          if(rnd()<.5){const ms=DB.M.filter(m=>m.ty==='N'&&!oathTagOf(m.n)&&m.at.some(a=>a in S.atts)&&!(m.req.t||[]).length);for(let j=0;j<3&&ms.length;j++){const m=pick(ms).n;if(!S.mantras.includes(m))S.mantras.push(m)}}
          if(rnd()<.15)S.caps={WLL:{on:true,max:pick([0,20,40])}};
          if(rnd()<.1){const n=pick(pool).n;S.avoid=[n];S.sel=S.sel.filter(x=>x!==n)}
          if(rnd()<.15)S.allowOver=true;
          renderInputs();run();return P.n+' | '+S.wtype+' '+S.wtarget+' | '+JSON.stringify(S.atts)+' | '+(path[0]||'no path')+' | '+S.sel.length+' talents'}""", [i, SEED, ATT_SETS, PATHS])

    t0 = time.time()
    for i in (range(FROM, TO) if FROM is not None and FROM >= 0 else [] if FROM is not None else range(n_builds)):
        desc = setup(i); tag = f'build {i} [{desc}]'; counts['builds'] += 1
        wait(); opt(tag)
        autopick(tag)
        # change a stat floor mid-build, then optimize again
        pg.evaluate("(()=>{const a=ATTR[(Date.now()>>3)%ATTR.length];S.mins[a]=Math.max(S.mins[a]||0,40);renderInputs()})()"); opt(tag + ' after a stat change')
        # slider at the other end must still give a valid build
        pg.evaluate("S.prio=S.prio===20?80:20"); opt(tag + ' slider flipped')
        autopick(tag + ' second')
        if i % 4 == 0: tabs(tag)
        if i % 6 == 0: roundtrip(tag)
        if i % 5 == 0: print(f'{i}/{n_builds} builds, {len(problems)} problems, {time.time()-t0:.0f}s', flush=True)

    # ---------- every preset through the wizard ----------
    for n in (presets if SECTIONS else []):
        if n == 'Clean Slate': continue
        pg.evaluate(f"openWizard(PRESETS.find(p=>p.n==={json.dumps(n)}))"); pg.wait_for_timeout(200); pg.click('#wz-go'); pg.wait_for_timeout(300); wait()
        tag = f'preset {n}'; check(tag + ' loaded'); counts['builds'] += 1
        if n != 'Diluvian' and pg.evaluate("S.sel.length") > 0: problems.append(f'{tag}: preset started with {pg.evaluate("S.sel.length")} talents')
        autopick(tag); opt(tag); tabs(tag); roundtrip(tag)

    # ---------- AI build maker ----------
    AI = ['lightning steam path build', 'flame frost steam path', 'heavy strength bossraid', 'charisma mage with frostdraw and thundercall',
          'stealth gank build with shadowcast', 'ironsing bloodrend alloyblood path heavy build', 'pink flames build', 'black blood mage with flamecharm',
          'glass path frostdraw medium build', 'lava path flame light weapon', 'silentheart strength build', 'saintsworn mage', 'jetstriker agility pvp',
          'armor shredding heavy build', 'semi tanky light weapon chime build', 'reinforced armor tank', 'galebreathe pressure build with rapier',
          'blindseer willpower build', 'thundercall 100 frostdraw 40 mage', 'twisted puppets path', 'glass cannon dagger build', 'support charisma build',
          'specter path shadowcast', 'contractor bloodrend light weapon', 'lightning 80 flame 50 frost steam path', 'dual attunement flame thunder heavy']
    for txt in (AI[:max(6, int(len(AI) * SCALE))] if SECTIONS else []):
        pg.evaluate("openAI()"); pg.fill('#aitext', txt); pg.click('#ai-go'); pg.wait_for_timeout(300)
        if pg.is_visible('#aiqs'): pg.click('#aiq-skip'); pg.wait_for_timeout(300)
        pg.click('#wz-go'); pg.wait_for_timeout(400); wait(); pg.wait_for_timeout(600); wait()
        tag = f'AI "{txt}"'; check(tag); counts['builds'] += 1
        opt(tag); autopick(tag); tabs(tag)

    # ---------- popular deepwoken.co builds (REF): load their talents, optimize, compare ----------
    refs = pg.evaluate("REF.length"); kept_all = []
    for i in (range(0, refs, max(1, int(3 / SCALE)) if SCALE < 3 else 1) if SECTIONS else []):
        r = pg.evaluate("""i=>{const r=REF[i];const ok=OATHS.some(o=>o.n===r.o);S.manual=false;S.allowOver=false;S.oath=ok?r.o:'None';S.wtype=['LHT','MED','HVY'].includes(r.w)?r.w:'MED';S.wtarget=75;S.weapon='';
          S.atts={};r.a.forEach((a,j)=>{const k=a.toUpperCase().slice(0,3);if(ATT[k])S.atts[k]=j?40:80});if(S.oath==='Silentheart')S.atts={};
          S.sel=[...r.t].filter(n=>TBY.has(n)&&TBY.get(n).r!=='O'&&!n.startsWith('Oath:'));S.req=[];S.avoid=[];S.caps={};S.mantras=[];S.when={};S.preMin={};S.mins={};S.pin={};S.prio=50;S.dsplit=50;
          renderInputs();run();return {o:S.oath,w:S.wtype,a:S.atts,n:S.sel.length,names:S.sel}}""", i)
        tag = f'popular build {i} ({r["o"]} {r["w"]} {list(r["a"])} {r["n"]} talents)'; counts['builds'] += 1
        wait(); opt(tag)
        kept = pg.evaluate("names=>names.filter(n=>S.sel.includes(n)).length", r['names']); kept_all.append(kept / max(1, r['n']))
        if kept / max(1, r['n']) < 0.6: warns.append(f'{tag}: optimize kept only {kept}/{r["n"]} of its talents')
        if i % 5 == 0: tabs(tag)

    # ---------- real deepwoken.co build import (with stats) ----------
    fx = (ROOT / 'tests' / 'fixtures' / 'dwco-build.json').read_text()
    ok = pg.evaluate("async t=>{const r=await smartImport(t);return !!(r&&r.ok)}", fx); pg.wait_for_timeout(1500); wait()
    if not ok: problems.append('deepwoken.co fixture build does not import')
    else:
        check('deepwoken.co fixture import'); tabs('deepwoken.co fixture'); roundtrip('deepwoken.co fixture')
    bf = (ROOT / 'tests' / 'fixtures' / 'build-file.txt')
    if bf.exists():
        ok = pg.evaluate("async t=>{const r=await smartImport(t);return !!(r&&r.ok)}", bf.read_text()); pg.wait_for_timeout(1500); wait()
        if not ok: problems.append('build-file fixture does not import')
        else: check('build-file fixture import'); roundtrip('build-file fixture')

    # ---------- the visible buttons ----------
    pg.evaluate("S.manual=false;renderShrines();renderInputs()")
    pg.evaluate("openWizard(PRESETS.find(p=>p.n==='Chime'))"); pg.wait_for_timeout(200); pg.click('#wz-go'); pg.wait_for_timeout(300); wait()
    pg.evaluate("showTab('build')"); pg.wait_for_timeout(200)
    btn = pg.query_selector('[data-optimize]:visible')
    if btn and not btn.is_enabled(): problems.append('Optimize build button is disabled in optimizer mode'); btn = None
    if btn:
        btn.click(); pg.wait_for_timeout(500)
        try:
            pg.wait_for_function("document.querySelectorAll('#optpick-cards [data-optuse]').length>0||!document.getElementById('optpick').open", timeout=240000)
            pg.wait_for_function("[...document.querySelectorAll('#optpick-cards [data-optuse]')].every(b=>!b.disabled)||!document.getElementById('optpick').open", timeout=240000)
            c = pg.locator('#optpick-cards [data-optuse]').first
            if c.count(): c.click(); pg.wait_for_timeout(500); wait(); check('Optimize build button (plan picker)')
            else: problems.append('Optimize build button: no plan to pick')
        except Exception as e: problems.append('Optimize build button: ' + str(e)[:150])
    else: problems.append('no visible Optimize build button')
    for bid in ['autopick']:
        el = pg.query_selector('#' + bid)
        if el and el.is_visible(): el.click(); pg.wait_for_timeout(300); wait(); check('Auto-pick button')

    print(f"\nbuilds {counts['builds']}, checks {counts['checks']}, {time.time()-t0:.0f}s")
    if kept_all: print(f"popular builds: optimize kept {100*sum(kept_all)/len(kept_all):.0f}% of their talents on average (min {100*min(kept_all):.0f}%)")
    print(f"WARNINGS {len(warns)}"); [print('  ', w) for w in warns[:40]]
    KNOWN = []  # bugs A-F from the November 17, 2026 report are fixed; anything found now is new
    known = {}
    rest = []
    for x in problems:
        k = next((lab for key, lab in KNOWN if key in x), None)
        if k: known[k] = known.get(k, 0) + 1
        else: rest.append(x)
    print('KNOWN BUGS (noted for the owner):'); [print(f'   {v:4d}  {k}') for k, v in sorted(known.items())]
    problems[:] = rest
    uniq = []
    for x in problems:
        if x not in uniq: uniq.append(x)
    print(f"PROBLEMS {len(uniq)}"); [print('  ', x) for x in uniq[:150]]
    e2 = list(dict.fromkeys(errs)); print(f"PAGE ERRORS {len(e2)}"); [print('  ', x) for x in e2[:30]]
    b.close()
sys.exit(1 if problems or errs else 0)
