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
for(const P of PRESETS){for(const withM of [0,1]){S.oath=P.oath;S.wtype=P.wtype;S.wtarget=P.wtarget;S.atts={...P.atts};S.preMin={...P.pre};S.mins={...P.post};S.sel=P.t.filter(n=>TBY.has(n));S.mantras=withM?MAN.slice():[];S.req=[];S.avoid=[];S.caps={};
  const r=opt();const c=counts(closure());const ok=r.best&&!r.best.impossible&&r.best.free>=0&&c.nTal<=c.cap;if(!ok)fails++;
  console.log((ok?'ok  ':'FAIL')+' '+(P.n+(withM?' +6 mantras':'')).padEnd(32)+' free '+String(r.best?r.best.free:'-').padStart(4)+'  talents '+c.nTal+'/'+c.cap)}}
`);
process.exit(fails?1:0);
