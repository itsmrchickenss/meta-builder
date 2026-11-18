// Quick check of the planner's core logic without a browser: node tests/core-test.js
// Loads index.html, runs everything before the UI section with a stubbed document, and optimizes every preset.
const fs=require('fs'),path=require('path');
const h=fs.readFileSync(path.join(__dirname,'..','index.html'),'utf8');
const blocks={};h.replace(/<script type="text\/plain" id="(\w+)">([\s\S]*?)<\/script>/g,(m,id,c)=>{blocks[id]=c});
global.document={getElementById:id=>({textContent:blocks[id]||'',style:{setProperty(){}}}),documentElement:{style:{setProperty(){}},dataset:{}},querySelectorAll:()=>[],addEventListener(){}};
global.localStorage={getItem:()=>null,setItem(){}};
let js=h.slice(h.lastIndexOf('<script>')+8,h.lastIndexOf('</script>')).split('// ================= UI =================')[0];
let fails=0;
eval('var last=null;'+js+`
// the Shrine of Order: attributes lose at most 25, attunements have no floor (100 Flamecharm with 1s elsewhere ends near 20)
{const P={STR:1,FTD:1,AGL:1,INT:1,WLL:1,CHA:1,FLM:100};const o=shrine(P).out;const ok=o.FLM<=25&&o.FLM>=15;if(!ok)fails++;console.log((ok?'ok  ':'FAIL')+' shrine: Flamecharm 100 -> '+o.FLM+' (attunements have no 25-point floor)');
 const Q={STR:90,AGL:1,FTD:1};const q=shrine(Q).out;const ok2=q.STR===65;if(!ok2)fails++;console.log((ok2?'ok  ':'FAIL')+' shrine: Strength 90 -> '+q.STR+' (attributes lose at most 25)')}
// talents that shrink below a stat: Million Ton Piercer gives its full +5% PEN only at 90 Strength
{const a=SCALE_MOD['Million Ton Piercer']({pen:.05,uncap:1},{STR:90}).pen,b=SCALE_MOD['Million Ton Piercer']({pen:.05,uncap:1},{STR:45}).pen;const ok=Math.abs(a-.05)<1e-9&&Math.abs(b-.025)<1e-9;if(!ok)fails++;console.log((ok?'ok  ':'FAIL')+' Million Ton Piercer PEN at 90 / 45 Strength: '+a+' / '+b)}
console.log('talents',DB.T.length,'mantras',DB.M.length,'weapons',DB.W.length,'gear',GEAR.length,'outfits',OUTFITS.length,'descriptions',TDESC.size,'synergy talents',SYN.size);
// Same steps as the Optimize button: fit the talent cap, then drop talents until the stats fit the budget
const opt=()=>{trimToCap();let r=compute({starts:4,iters:80});if(r.best&&r.best.free<0&&!r.best.impossible)r=trimToBudget(r).res;return r};
const MAN=DB.M.filter(m=>m.ty==='N'&&!oathTagOf(m.n)&&!(m.req&&m.req.t&&m.req.t.length)).slice(0,6).map(m=>m.n);
// presets with variations (every preset but Clean Slate): every variation x Fortitude option x weapon type (one type when the variation has no weapon)
const CASES=[];for(const P of PRESETS){CASES.push(P);if(P.variants)for(const v of P.variants){const wt=v.wtarget!=null?v.wtarget:P.wtarget;
  for(const f of v.ftd||P.ftdOpts||[null])for(const w of (wt>0&&!P.weapon?['LHT','MED','HVY']:[v.wtype||P.wtype])){
  const post={...v.post};if(f)post.FTD=f;CASES.push({...P,n:P.n+': '+v.n.split(' (')[0]+(f?' FTD '+f:'')+' '+w,pre:{...v.pre},post,wtype:w,wtarget:wt,atts:{...(v.atts||P.atts)},oath:v.oath||(P.oathByW?P.oathByW[w]:P.oath),variants:null})}}}
// the first variation is the preset itself ("Use preset as is" loads the same stats)
for(const P of PRESETS){if(!P.variants)continue;const v=P.variants[0];const post={...v.post};if(v.ftd)post.FTD=v.ftd[0];
  const same=(a,b)=>JSON.stringify(Object.entries(a).sort())===JSON.stringify(Object.entries(b).sort());const ok=same(v.pre,P.pre)&&same(post,P.post)&&(!v.atts||same(v.atts,P.atts))&&(v.wtarget==null||v.wtarget===P.wtarget);
  if(!ok)fails++;console.log((ok?'ok  ':'FAIL')+' first variation = preset: '+P.n)}
for(const P of CASES){for(const withM of [0,1]){S.oath=P.oath;S.wtype=P.wtype;S.wtarget=P.wtarget;S.atts={...P.atts};S.preMin={...P.pre};S.mins={...P.post};S.sel=P.t.filter(n=>TBY.has(n));S.mantras=withM?MAN.slice():[];S.req=[];S.avoid=[];S.caps={};
  const r=opt();const c=counts(closure());const ok=r.best&&!r.best.impossible&&r.best.free>=0&&c.nTal<=c.cap;if(!ok)fails++;
  console.log((ok?'ok  ':'FAIL')+' '+(P.n+(withM?' +6 mantras':'')).padEnd(60)+' free '+String(r.best?r.best.free:'-').padStart(4)+'  talents '+c.nTal+'/'+c.cap)}}
// every preset's oath is met by its own stats after the shrine (attributes lose at most 25 at the shrine)
for(const P of CASES){if(!P.oath||P.oath==='None')continue;S.wtype=P.wtype;S.wtarget=P.wtarget;S.atts={...P.atts};
  const f={};ALL.forEach(k=>f[k]=Math.max(P.post[k]||0,P.atts[k]||0,k===P.wtype?P.wtarget:0,P.pre[k]?P.pre[k]-25:0));
  const al=oathAltsOf(findO(P.oath));const c=al?bestCost(al,f):0;const ok=c===0;if(!ok)fails++;
  console.log((ok?'ok  ':'FAIL')+' oath fits: '+P.n.padEnd(20)+' '+P.oath+(ok?'':' (short '+c+')'))}
// wanted stats: each one is reached before the shrine or after it (the optimizer picks), within budget, never re-raised after the shrine
for(const [W,wt,mins] of [[{STR:40,AGL:65,CHA:40},'MED',{FTD:50}],[{STR:100,AGL:40},'HVY',{FTD:50}],[{INT:90,WLL:40},'LHT',{FTD:50}],[{AGL:65},'LHT',{AGL:50,FTD:50}],[{CHA:90,STR:40,AGL:40},'MED',{FTD:50}]]){
  S.oath='None';S.wtype=wt;S.wtarget=80;S.atts={};S.preMin={};S.mins={...mins};S.want={...W};S.sel=[];S.mantras=[];S.req=[];S.avoid=[];S.caps={};
  const r=opt();const b=r.best;const met=b&&Object.entries(W).every(([k,v])=>b.P[k]>=v||b.final[k]>=v);const ok=b&&!b.impossible&&b.free>=0&&met&&!b.reup&&Object.keys(b.wantAt||{}).length===Object.keys(W).length;if(!ok)fails++;
  console.log((ok?'ok  ':'FAIL')+' wanted '+JSON.stringify(W).padEnd(30)+' '+Object.entries(b?b.wantAt:{}).map(([k,w])=>k+' '+w+' ('+b.P[k]+'->'+b.final[k]+')').join(', ')+'  free '+(b?b.free:'-'))}
S.want={};
// Diluvian: Brick Wall, Dawnwalker and the FTD/WLL talents
{const D=PRESETS.find(p=>p.n==='Diluvian');const ok=D&&D.oath==='Dawnwalker'&&D.t.includes('Brick Wall')&&D.t.includes('Perseverance')&&D.t.length>=30&&!D.t.includes('Echoing Lunatic');if(!ok)fails++;
  console.log((ok?'ok  ':'FAIL')+' Diluvian talents: '+(D?D.t.length:0))}
`);
process.exit(fails?1:0);
