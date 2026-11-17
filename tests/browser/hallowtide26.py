# Hallowtide 2026 content: new weapons have damage and requirements, the two hybrid paths work in the AI build maker,
# and the new outfits and equipment load.
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
URL=(ROOT/'index.html').as_uri()
from playwright.sync_api import sync_playwright
ST="(()=>({oath:S.oath,atts:S.atts,w:S.weapon,wt:S.wtype+' '+S.wtarget,req:S.req,m:S.mantras,free:last.best.free,cap:(()=>{const c=counts(closure());return c.nTal+'/'+c.cap})()}))()"
NEW_W=["Corvidirge Severants","Silas's Cenotaph","Cursed Flames","Alloyblood Daggers","Alloyblood Spear","Alloyblood Axe","Infected","Ironcry"]
NEW_G=["Familiar Prosthetic Arm","Thorned Blazer","Harvestman's Halo","Harvestman's Cloak","Wreath of the Ardenstar","Raudra's Finger","Raudra's Pendant Earrings","Coffin Earrings"]
NEW_O=["Familiar Vagrant's Armor","Familiar Sage's Armor","Familiar Prince's Armor","Familiar Arachnid's Cloak"]
fails=[]
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':900});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(2500)
    for n in NEW_W:
        r=pg.evaluate("n=>{const w=WBY.get(n),d=WDMG.get(n);return {w:!!w,d:!!d,req:w&&fmtReq(w.req)}}",n)
        print('weapon',n,r)
        if not(r['w'] and r['d']): fails.append('weapon '+n)
    r=pg.evaluate("GEAR.filter(g=>%s.includes(g.n)).map(g=>g.n+' '+g.ty+' hp'+g.hp+' '+g.tal.join(';'))"%str(NEW_G))
    print('gear',r)
    if len(r)!=len(NEW_G): fails.append('gear')
    r=pg.evaluate("(()=>{try{return OUTFITS.filter(o=>%s.includes(o.n)).map(o=>o.n)}catch(e){return document.getElementById('dwgear').textContent.split('\\n').filter(l=>%s.some(n=>l.startsWith(n+'|'))).length}})()"%(str(NEW_O),str(NEW_O)))
    print('outfits',r)
    for n in ["Composite Path: Alloyblood","Exotherm Path: Sanguine Blaze","Hypoferritinemia"]:
        print('talent',n,pg.evaluate("n=>{const t=TBY.get(n);return t&&{c:t.c,req:fmtReq(t.req)}}",n))
    for n in ["Infused Slash","Rising Plasma","Cauterize"]:
        if not pg.evaluate("n=>!!MBY.get(n)",n): fails.append('mantra '+n)
    def ai(txt,want):
        pg.evaluate("openAI()");pg.fill('#aitext',txt);pg.click('#ai-go');pg.wait_for_timeout(400)
        if pg.is_visible('#aiqs'): pg.click('#aiq-skip');pg.wait_for_timeout(400)
        d=pg.inner_text('#wizform p.hint');pg.click('#wz-go');pg.wait_for_timeout(500)
        pg.wait_for_function("!document.getElementById('results').classList.contains('busy')",timeout=90000);pg.wait_for_timeout(800)
        s=pg.evaluate(ST);print('\n>>',txt);print('  read:',d[:500]);print('  ',s)
        if want not in s['req']: fails.append('ai '+txt)
        if 'Hypoferritinemia' in s['req']: fails.append('ai pulled Hypoferritinemia: '+txt)
    ai("ironsing bloodrend alloyblood path heavy build","Composite Path: Alloyblood")
    ai("sanguine blaze bloodrend flamecharm mage","Exotherm Path: Sanguine Blaze")
    # pick a new weapon and check the damage shows
    print('weaponOf',pg.evaluate("weaponOf(\"Silas's Cenotaph\")"))
    print('errs',errs);fails+= ['page error' for _ in errs]
    print('FAILS',fails if fails else 'none');b.close()
