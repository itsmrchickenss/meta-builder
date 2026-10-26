import json,re,pathlib
HERE=pathlib.Path(__file__).resolve().parent
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment
D=json.load(open(HERE/'data.json'))
VERSION=re.search(r'^## (v[0-9.]+)',(HERE.parents[1]/'src'/'data'/'versions.txt').read_text(),re.M).group(1)
F='Arial'
f_norm=Font(name=F,size=10);f_bold=Font(name=F,size=10,bold=True);f_in=Font(name=F,size=10,color='0000FF');f_link=Font(name=F,size=10,color='008000')
f_h1=Font(name=F,size=14,bold=True);f_h2=Font(name=F,size=11,bold=True);f_head=Font(name=F,size=10,bold=True,color='FFFFFF')
fill_head=PatternFill('solid',fgColor='34495E');fill_in=PatternFill('solid',fgColor='FFF9C4');fill_out=PatternFill('solid',fgColor='E8F5E9');fill_sec=PatternFill('solid',fgColor='ECEFF1')
thin=Side(style='thin',color='BBBBBB');box=Border(top=thin,bottom=thin,left=thin,right=thin)
wrap=Alignment(wrap_text=True,vertical='top')
wb=Workbook()
def sheet(name,first=False):
    ws=wb.active if first else wb.create_sheet(name);ws.title=name;return ws
def header(ws,row,cols,widths=None):
    for i,c in enumerate(cols,1):
        x=ws.cell(row=row,column=i,value=c);x.font=f_head;x.fill=fill_head;x.alignment=Alignment(wrap_text=True,vertical='center')
    if widths:
        for i,w in enumerate(widths,1):ws.column_dimensions[get_column_letter(i)].width=w
def setall(ws):
    for row in ws.iter_rows():
        for c in row:
            if c.font is None or c.font.name!=F: c.font=Font(name=F,size=c.font.size if c.font else 10,bold=c.font.bold if c.font else False,color=c.font.color if c.font else None)

# ---------------- Read Me ----------------
ws=sheet('Read Me',True)
ws['A1']='Meta Builder: how every stat and talent is calculated';ws['A1'].font=f_h1
rows=[
('Version',VERSION+' (pre-release). Built from the app\'s own code and data, so the numbers match what the planner uses.'),
('Game data','deepwoken.co (talents, mantras, weapons, equipment, oaths, reference builds; October 2026). Traits: deepwoken.fandom.com/wiki/Traits.'),
('',''),
('Sheet','What it has'),
('Calculator','Type stats in the yellow cells (blue text) and every result recalculates: Power, points left, talent cap, health and effective health, weapon damage, mantra damage, trait effects.'),
('Formulas','Every calculation the app does, in plain words and as a formula, with where it lives in the code (src/template.html).'),
('Talents','All 622 talents: requirements, cheapest way to meet them, whether they can be taken before the shrine, popularity, take rate given stats, damage/PEN bonus, synergies, exclusives, description.'),
('Mantras','All 230 mantras: attunement, category, requirement, stat scaling, damage at levels 1-5, and live damage with the Calculator stats.'),
('Weapons','All 231 weapons: type, requirement, base damage, PEN, stat scaling, and live hit damage with the Calculator stats.'),
('Outfits','All outfits: physical/elemental armor, durability, requirement, talents they give.'),
('Equipment','All equipment pieces: slot, health/armor, pip slots, requirement, set, talents they give.'),
('Enchants','Weapon enchants and how each is counted.'),
('Oaths','Each oath\'s stat requirement options and notes.'),
('Presets','The starting presets (stats only).'),
('Constants','Fixed numbers the formulas use (budget, shrine, armor, pip values...).'),
('',''),
('Colours','Yellow cell with blue text = an input you can change. Green cell = a result (formula). Everything else is reference data.'),
('Codes','STR Strength, FTD Fortitude, AGL Agility, INT Intelligence, WLL Willpower, CHA Charisma, HVY/MED/LHT Heavy/Medium/Light weapon, FLM Flamecharm, ICE Frostdraw, LTN Thundercall, WND Galebreathe, SDW Shadowcast, IRN Ironsing, BLD Bloodrend, MND = highest of INT/WLL/CHA, BOD = highest of STR/FTD/AGL, PWR = Power.'),
]
for i,(a,b) in enumerate(rows,3):
    ws.cell(row=i,column=1,value=a).font=f_bold if a in ('Sheet','Colours','Codes','Version','Game data') else f_norm
    c=ws.cell(row=i,column=2,value=b);c.font=f_bold if a=='Sheet' else f_norm;c.alignment=wrap
ws.column_dimensions['A'].width=16;ws.column_dimensions['B'].width=120

# ---------------- Constants ----------------
wc=sheet('Constants')
header(wc,1,['Name','Value','Meaning'],[28,12,90])
consts=[('BUDGET',330,'Stat points a Power 20 character has (330).'),('SHRINE_POWER',8,'The Shrine of Order can only be used at Power 8 or higher.'),('SHRINE_POINTS',135,'Points invested to reach Power 8: 15*8+15.'),
('SHRINE_MAX_DROP',25,'Shrine of Order: an attribute never ends more than 25 below its pre-shrine value. Attunements are exempt: no floor, 100 can drop to about 20.'),('ARMOR',0.3,'Generic target armor used for damage numbers: hits are multiplied by 1-(1-PEN)*ARMOR.'),
('PEN_PHYS',35,'Physical penetration assumed against your armor (%) when computing your resistance.'),('PEN_ELE',20,'Elemental penetration assumed against your armor (%).'),('BASE_HP',220,'Base health before Power and Fortitude.'),('HP_PER_POWER',4,'Health per Power level (Power 20 assumed for gear).'),
('HP_PER_FTD_TO_50',0.5,'Health per Fortitude point up to 50.'),('HP_PER_FTD_PAST_50',0.25,'Health per Fortitude point above 50.'),('DMG_SOFTCAP',0.25,'Talent damage bonus counts in full up to +25%, half past it.'),('DMG_HARDCAP',0.5,'Talent damage bonus is capped at +50%.'),
('PEN_CAP',0.5,'Weapon PEN is capped at 50% unless a talent removes the cap.'),('STR_PEN_PER_10',0.01,'Every 10 Strength adds 1% weapon PEN.'),('SOULBREAKER_DMG',0.025,'Soulbreaker oath adds +2.5% damage bonus.'),
('TRAIT_TOTAL',12,'Trait points in total.'),('TRAIT_MAX',6,'Most points in one trait.'),('VIT_HP',10,'Health per Vitality point.'),('ERU_ETHER',30,'Ether per Erudition point.'),('ERU_TEMPO',5,'Tempo per Erudition point (and +5% tempo gain).'),
('PRO_SCALING',0.065,'Proficiency: weapon stat scaling multiplied by 1+6.5% per point.'),('PRO_PEN',0.025,'Proficiency: weapon PEN per point.'),('SNG_SCALING',0.065,'Songchant: mantra stat scaling multiplied by 1+6.5% per point.'),('SNG_PEN',0.025,'Songchant: mantra PEN per point.'),('SNG_OATH_DMG',0.02,'Songchant: oath and monster mantra damage per point (shown only).'),
('TALENT_CAP_BASE',52,'Talent cap = 52 + (12 - normal mantras) x 2.'),('SYN_PTS',15,'One synergy weight counts like a talent 15% of builds take.'),('COMBO_PTS',10,'Value of a true mantra combo in the optimizer.')]
for i,(n,v,m) in enumerate(consts,2):
    wc.cell(row=i,column=1,value=n).font=f_bold;wc.cell(row=i,column=2,value=v).font=f_norm;c=wc.cell(row=i,column=3,value=m);c.font=f_norm;c.alignment=wrap
r=len(consts)+3
wc.cell(row=r,column=1,value='Equipment pip values (health / physical / elemental per pip, by slot and rarity)').font=f_h2;r+=1
header(wc,r,['Slot','Pip stat','Common / Uncommon / Rare / Legendary']);r+=1
slot={'H':'Head','A':'Arms','L':'Legs','T':'Torso','F':'Face','E':'Earrings','R':'Ring'};stat={'H':'Health','P':'Physical armor','E':'Elemental armor'}
for s,d in D['pipv'].items():
    for st,v in d.items():
        wc.cell(row=r,column=1,value=slot[s]).font=f_norm;wc.cell(row=r,column=2,value=stat[st]).font=f_norm;wc.cell(row=r,column=3,value=' / '.join(f"{k}:{x}" for k,x in v.items())).font=f_norm;r+=1
wc.freeze_panes='A2'

# ---------------- Weapons (data first, so the Calculator can look them up) ----------------
ww=sheet('Weapons')
def scal(s):
    p=[x.strip() for x in s.split(',') if x.strip()];out=[]
    for x in p[:3]:
        k,v=x.rsplit(' ',1);out+= [k,float(v)]
    while len(out)<6: out+=['',0]
    return out
header(ww,1,['Weapon','Type','Requirement','Base damage','PEN','Scale stat 1','Coef 1','Scale stat 2','Coef 2','Scale stat 3','Coef 3','Hit with Calculator stats'],[30,12,34,11,8,10,8,10,8,10,8,14])
W=sorted(D['weapons'],key=lambda w:w['n'])
for i,w in enumerate(W,2):
    s=scal(w['sc'] or '')
    vals=[w['n'],w['ty'],w['req'],w['d'],w['p']]+s
    for j,v in enumerate(vals,1): ww.cell(row=i,column=j,value=v).font=f_norm
    # live hit: same formula as the Calculator, using its stats, traits and bonuses
    st=lambda col:f'IFERROR({col}{i}*INDEX(Calculator!$E$6:$E$23,MATCH({chr(ord(col)-1)}{i},Calculator!$A$6:$A$23,0)),0)'
    h=f'({st("G")}+{st("I")}+{st("K")})'
    ww.cell(row=i,column=12,value=f'=D{i}*(1+0.75*{h}*(1+Constants!$B$23*Calculator!$C$27)/1000)*(1+Calculator!$C$45+Calculator!$C$37)*Calculator!$C$39*(1-(1-MIN(Calculator!$C$44,MIN(1,E{i}+Calculator!$E$6/10*Constants!$B$16+Calculator!$C$36+Calculator!$C$40+Constants!$B$24*Calculator!$C$27)))*Constants!$B$6)').font=f_norm
    ww.cell(row=i,column=12).fill=fill_out;ww.cell(row=i,column=12).number_format='0.0'
ww.freeze_panes='B2';ww.auto_filter.ref=f'A1:L{len(W)+1}'
NW=len(W)+1

# ---------------- Mantras ----------------
wm=sheet('Mantras')
header(wm,1,['Mantra','Attunement','Category','Type','Requirement','Scale stat 1','Coef 1','Scale stat 2','Coef 2','Lv1','Lv2','Lv3','Lv4','Lv5','Level with Calculator stats','Hit with Calculator stats'],[28,14,9,7,30,10,8,10,8,8,8,8,8,8,12,14])
cat={'C':'Combat','M':'Mobility','S':'Support','W':'Wildcard'}
M=sorted(D['mantras'],key=lambda m:m['n'])
for i,m in enumerate(M,2):
    s=scal(m['sc'] or '')[:4];lv=m['lv'] or ['','','','','']
    vals=[m['n'],m['at'],cat.get(m['c'],m['c']),m['ty'],m['req']]+s+lv
    for j,v in enumerate(vals,1): wm.cell(row=i,column=j,value=v).font=f_norm
    if m['lv']:
        att=m['at'].split(' + ')[0]
        wm.cell(row=i,column=15,value=f'=MAX(1,MIN(5,1+INT(IFERROR(INDEX(Calculator!$E$6:$E$23,MATCH("{att}",Calculator!$A$6:$A$23,0)),0)/20)))').font=f_norm
        sc=lambda c:f'IFERROR({c}{i}/10*INDEX(Calculator!$E$6:$E$23,MATCH({chr(ord(c)-1)}{i},Calculator!$A$6:$A$23,0))/100,0)'
        wm.cell(row=i,column=16,value=f'=INDEX(J{i}:N{i},O{i})*(1+({sc("G")}+{sc("I")})*(1+Constants!$B$25*Calculator!$C$28))*(1+Calculator!$C$45)*(1-(1-MIN(0.5,Constants!$B$26*Calculator!$C$28))*Constants!$B$6)').font=f_norm
        for c in (15,16): wm.cell(row=i,column=c).fill=fill_out
        wm.cell(row=i,column=16).number_format='0.0'
wm.freeze_panes='B2';wm.auto_filter.ref=f'A1:P{len(M)+1}'
NM=len(M)+1

# ---------------- Calculator ----------------
wk=sheet('Calculator');wb.move_sheet('Calculator',offset=-(len(wb.sheetnames)-2))
wk['A1']='Calculator';wk['A1'].font=f_h1
wk['A2']='Change the yellow cells. Green cells are formulas. Take the "Before shrine", "Shrine leaves" and "Final" numbers from the app\'s stats table (Stats tab).';wk['A2'].font=f_norm
wk['A4']='Stats';wk['A4'].font=f_h2
for j,h in enumerate(['Code','Stat','Before shrine','Shrine leaves','Final','Added after shrine'],1):
    c=wk.cell(row=5,column=j,value=h);c.font=f_head;c.fill=fill_head
names=[('STR','Strength'),('FTD','Fortitude'),('AGL','Agility'),('INT','Intelligence'),('WLL','Willpower'),('CHA','Charisma'),('HVY','Heavy weapon'),('MED','Medium weapon'),('LHT','Light weapon'),('FLM','Flamecharm'),('ICE','Frostdraw'),('LTN','Thundercall'),('WND','Galebreathe'),('SDW','Shadowcast'),('IRN','Ironsing'),('BLD','Bloodrend')]
ex={'STR':(1,22,22),'FTD':(50,25,25),'AGL':(40,22,22),'INT':(0,0,0),'WLL':(40,22,22),'CHA':(1,22,25),'MED':(1,22,92),'LTN':(50,22,22),'IRN':(1,22,90)}
for i,(k,n) in enumerate(names,6):
    a,b,c=ex.get(k,(0,0,0))
    wk.cell(row=i,column=1,value=k).font=f_bold;wk.cell(row=i,column=2,value=n).font=f_norm
    for j,v in ((3,a),(4,b),(5,c)):
        x=wk.cell(row=i,column=j,value=v);x.font=f_in;x.fill=fill_in;x.border=box
    x=wk.cell(row=i,column=6,value=f'=MAX(0,E{i}-D{i})');x.font=f_norm;x.fill=fill_out
wk.cell(row=22,column=1,value='MND').font=f_bold;wk.cell(row=22,column=2,value='Mind (highest of INT/WLL/CHA)').font=f_norm;wk['E22']='=MAX(E9,E10,E11)';wk['E22'].fill=fill_out
wk.cell(row=23,column=1,value='BOD').font=f_bold;wk.cell(row=23,column=2,value='Body (highest of STR/FTD/AGL)').font=f_norm;wk['E23']='=MAX(E6,E7,E8)';wk['E23'].fill=fill_out
wk['A24']='Example values are the Iron Samurai example build.';wk['A24'].font=Font(name=F,size=9,italic=True)
def inp(r,label,val,note=None,fmt=None):
    wk.cell(row=r,column=1,value=label).font=f_norm;wk.merge_cells(start_row=r,start_column=1,end_row=r,end_column=2)
    x=wk.cell(row=r,column=3,value=val);x.font=f_in;x.fill=fill_in;x.border=box
    if fmt:x.number_format=fmt
    if note:wk.cell(row=r,column=4,value=note).font=Font(name=F,size=9,color='666666')
def out(r,label,formula,note=None,fmt=None):
    wk.cell(row=r,column=1,value=label).font=f_bold;wk.merge_cells(start_row=r,start_column=1,end_row=r,end_column=2)
    x=wk.cell(row=r,column=3,value=formula);x.font=f_norm;x.fill=fill_out;x.border=box
    if fmt:x.number_format=fmt
    if note:wk.cell(row=r,column=4,value=note).font=Font(name=F,size=9,color='666666')
wk['A25']='Traits (separate 12-point pool, max 6 each)';wk['A25'].font=f_h2
inp(26,'Vitality',4,'+10 health per point');inp(27,'Proficiency',4,'weapon scaling x(1+6.5%/pt), +2.5% weapon PEN/pt');inp(28,'Songchant',4,'mantra scaling x(1+6.5%/pt), +2.5% mantra PEN/pt');inp(29,'Erudition',0,'+30 ether, +5 tempo, +5% tempo gain per point')
out(30,'Trait points left','=Constants!$B$18-SUM(C26:C29)','must not go below 0; each trait at most 6')
wk['A32']='Weapon and damage bonuses';wk['A32'].font=f_h2
inp(33,'Weapon (name from the Weapons sheet)','Shattered Katana','pick any name in the Weapons sheet')
for x in ('C33',):wk[x].font=f_in
dv=DataValidation(type='list',formula1=f'=Weapons!$A$2:$A${NW}',allow_blank=False);wk.add_data_validation(dv);dv.add('C33')
out(34,'Base damage',f'=INDEX(Weapons!$D$2:$D${NW},MATCH(C33,Weapons!$A$2:$A${NW},0))')
out(35,'Weapon PEN',f'=INDEX(Weapons!$E$2:$E${NW},MATCH(C33,Weapons!$A$2:$A${NW},0))',fmt='0.0%')
inp(36,'Extra PEN from talents',0,'sum of talent PEN (Talents sheet, PEN column)',fmt='0.0%')
inp(37,'Unique damage bonus (not capped)',0,'talents marked unique add outside the cap',fmt='0.0%')
inp(38,'Talent damage bonus (raw sum)',0.3,'sum of the Damage column of your talents',fmt='0.0%')
inp(39,'Enchant hit multiplier',1,'Enchants sheet: e.g. Deferred 1.07')
inp(40,'Enchant PEN',0,'Enchants sheet: e.g. Sear 0.05',fmt='0.0%')
inp(41,'Soulbreaker oath? (1 = yes)',0,'adds +2.5% damage bonus')
inp(42,'PEN cap removed by a talent? (1 = yes)',0,'some talents lift the 50% cap')
out(43,'Talent damage bonus incl. oath','=C38+Constants!$B$17*C41',fmt='0.0%')
out(44,'PEN cap','=IF(C42=1,1,Constants!$B$15)',fmt='0%')
out(45,'Damage bonus after soft cap','=IF(C43>Constants!$B$13,MIN(Constants!$B$14,Constants!$B$13+(C43-Constants!$B$13)/2),C43)','full to +25%, half past it, max +50%',fmt='0.0%')
out(46,'Weapon stat scaling sum (h)',f'=IFERROR(INDEX(Weapons!$G$2:$G${NW},MATCH(C33,Weapons!$A$2:$A${NW},0))*INDEX($E$6:$E$23,MATCH(INDEX(Weapons!$F$2:$F${NW},MATCH(C33,Weapons!$A$2:$A${NW},0)),$A$6:$A$23,0)),0)+IFERROR(INDEX(Weapons!$I$2:$I${NW},MATCH(C33,Weapons!$A$2:$A${NW},0))*INDEX($E$6:$E$23,MATCH(INDEX(Weapons!$H$2:$H${NW},MATCH(C33,Weapons!$A$2:$A${NW},0)),$A$6:$A$23,0)),0)+IFERROR(INDEX(Weapons!$K$2:$K${NW},MATCH(C33,Weapons!$A$2:$A${NW},0))*INDEX($E$6:$E$23,MATCH(INDEX(Weapons!$J$2:$J${NW},MATCH(C33,Weapons!$A$2:$A${NW},0)),$A$6:$A$23,0)),0)','sum of scaling coefficient x final stat')
out(47,'Scaled damage','=C34*(1+0.75*C46*(1+Constants!$B$23*C27)/1000)','base x (1 + 0.75 x h x (1 + 6.5% x Proficiency) / 1000)',fmt='0.0')
out(48,'PEN before cap','=C35+E6/10*Constants!$B$16+C36+C40+Constants!$B$24*C27','weapon PEN + Strength/10 x 1% + talents + enchant + 2.5% x Proficiency',fmt='0.0%')
out(49,'PEN used','=MIN(C44,MIN(1,C48))',fmt='0.0%')
out(50,'Weapon hit vs armor','=C47*(1+C45+C37)*C39*(1-(1-C49)*Constants!$B$6)','scaled x (1 + bonus) x enchant x (1 - (1 - PEN) x 30% armor)',fmt='0.0')
wk['A52']='Mantra damage';wk['A52'].font=f_h2
inp(53,'Mantra (name from the Mantras sheet)','Rising Thunder','pick a combat mantra')
dv2=DataValidation(type='list',formula1=f'=Mantras!$A$2:$A${NM}',allow_blank=False);wk.add_data_validation(dv2);dv2.add('C53')
out(54,'Mantra level (from its attunement)',f'=IFERROR(INDEX(Mantras!$O$2:$O${NM},MATCH(C53,Mantras!$A$2:$A${NM},0)),"no damage data")','level = 1 + attunement / 20 (1 to 5)')
out(55,'Mantra hit vs armor',f'=IFERROR(INDEX(Mantras!$P$2:$P${NM},MATCH(C53,Mantras!$A$2:$A${NM},0)),"no damage data")','level damage x (1 + scaling x (1 + 6.5% x Songchant)) x (1 + bonus) x (1 - (1 - PEN) x 30%)',fmt='0.0')
wk['A57']='Points and Power';wk['A57'].font=f_h2
out(58,'Points before the shrine','=SUM(C6:C21)')
out(59,'Power at the shrine','=MAX(0,MIN(20,INT((C58-15)/15)))','Power = (points - 15) / 15, rounded down, 0 to 20')
out(60,'Shrine of Order allowed?','=IF(C59>=Constants!$B$3,"yes","no: needs Power 8 (135 points)")')
out(61,'Shrine refund (points the shrine returns)','=IF(C59>=Constants!$B$3,C58-SUM(D6:D21),0)','shrine leaves fewer points than went in; the rest come back')
out(62,'Points added after the shrine','=SUM(F6:F21)')
out(63,'Attunement free points','=MAX(0,COUNTIF(E15:E21,">0")-1)','every attunement after the first gets its first point free')
out(64,'Points used','=C58-C61+C62-C63')
out(65,'Points left (of 330)','=Constants!$B$2-C64')
out(66,'Final Power','=MAX(0,MIN(20,INT((C64-15)/15)))')
out(67,'Points to next Power','=IF(C66>=20,"max",15*(C66+2)-C64)')
wk['A69']='Talents and health';wk['A69'].font=f_h2
inp(70,'Normal mantras in the build',8)
out(71,'Talent cap','=Constants!$B$28+(12-C70)*2','52 + (12 - normal mantras) x 2')
inp(72,'Health from equipment pips',150,'Armor tab: health from pips and items')
inp(73,'Physical armor % from equipment',40,'Armor tab: physical armor')
out(74,'Health','=Constants!$B$9+20*Constants!$B$10+MIN(E7,50)*Constants!$B$11+MAX(E7-50,0)*Constants!$B$12+Constants!$B$20*C26+C72','220 + 4 x Power 20 + Fortitude (0.5 each to 50, 0.25 past) + 10 x Vitality + gear',fmt='0')
out(75,'Physical resistance','=MIN(0.95,C73/100*(1-Constants!$B$7/100))','armor % x (1 - 35% assumed penetration)',fmt='0.0%')
out(76,'Effective health vs physical','=C74/(1-C75)',fmt='0')
out(77,'Ether from Erudition','=Constants!$B$21*C29');out(78,'Tempo from Erudition','=Constants!$B$22*C29')
wk.column_dimensions['A'].width=10;wk.column_dimensions['B'].width=30;wk.column_dimensions['C'].width=16;wk.column_dimensions['D'].width=14;wk.column_dimensions['E'].width=10;wk.column_dimensions['F'].width=16
for r in range(26,79):
    if wk.cell(row=r,column=4).value and wk.cell(row=r,column=3).value is not None: pass
wk.column_dimensions['D'].width=14
for r in list(range(26,30))+list(range(30,79)):
    c=wk.cell(row=r,column=4)
    if isinstance(c.value,str) and not str(c.value).startswith('='): wk.merge_cells(start_row=r,start_column=4,end_row=r,end_column=9) if r not in (5,) else None
wk.freeze_panes='A4'

# ---------------- Formulas (documentation) ----------------
wf=sheet('Formulas');wb.move_sheet('Formulas',offset=-(len(wb.sheetnames)-3))
header(wf,1,['Area','What','How it is calculated','Formula','In the code'],[16,30,70,60,22])
FX=[
('Points','Stat budget','A Power 20 character has 330 points. Points used = points before the shrine - shrine refund + points added after - free attunement points - Shrine of Mastery refunds.','used = preSum - refund + postSum - max(0, attunements-1) - mastery','evaluate()'),
('Points','Power','Power from points invested.','Power = clamp(floor((points - 15) / 15), 0, 20)','powerAt()'),
('Points','Next Power','Points still needed for the next Power level.','15 x (Power + 2) - points used','renderFinal()'),
('Points','Free attunement points','Every attunement after the first gets its first point free.','discount = max(0, number of attunements above 0 - 1)','evaluate()'),
('Shrine of Order','When it can be used','Only at Power 8 or higher (135 points invested before it). Below that the plan skips the shrine and the stats carry straight through.','allowed = Power(preSum) >= 8','evaluate(), SHRINE_PWR'),
('Shrine of Order','Averaging (deepwoken.co algorithm)','Every stat above 0 is set to the average of the invested stats. No attribute may end more than 25 below its pre-shrine value: those are pinned at pre - 25 and the difference is taken evenly from the others (repeat until stable; attunements are exempt: they have no floor and can drop all the way to the average, e.g. 100 to about 20). Then values are rounded down, and leftover whole points are handed out one each to the unpinned stats while none would pass 100. Anything left is refunded.','avg = sum/count; pinned k: pre_k - 25; others share the rest; floor; distribute remainder; refund = what is left','shrine()'),
('Shrine of Order','Pre-shrine is the peak','An attribute (STR..CHA) raised above 1 before the shrine gets no points after it: either about 1 before and the rest after, or high before and the shrine brings it down. Weapon and attunement stats may be raised again (top builds do Ironsing 60 -> 80). Breaking it costs 20 points per point in the optimizer score.','penalty = 20 x sum of points added after the shrine to attributes that were > 1 before','evaluate() reup'),
('Shrine of Mastery','Refunds','Up to 3 points come off before (pre) or after (post) the Order shrine and are refunded; talents already taken stay.','used -= mastery points','evaluate(), masteryOf()'),
('Requirements','Talent requirement options','A talent can need stats (min values), "one of" groups (each option merged into the minimums, up to 16 options), combined sums (e.g. 75 combined weapon), prerequisite talents and mantras. Body = highest of STR/FTD/AGL, Mind = highest of INT/WLL/CHA, any weapon / any attunement expand into one option per stat.','alternatives = expand(stats) x expand(one-of groups); each alternative = {min:{stat:value}, sum:[[stats],value]}','reqAlts(), expandStats()'),
('Requirements','Prerequisite chains','A talent\'s requirement includes the stat needs of every prerequisite talent before it (merged as the highest of each stat).','chain(t) = merge(req(t), chain(each prerequisite))','chainAlts(), chainStatic()'),
('Requirements','Cost to meet','Points needed to meet an alternative from given stats: the sum of what each minimum is short, plus what each combined sum is short. The cheapest alternative counts.','cost = sum max(0, min_k - stat_k) + sum max(0, sumValue - sum of its stats); bestCost = min over alternatives','altCost(), bestCost()'),
('Requirements','Taken before the shrine','A talent can be taken before the shrine if every alternative uses only minimums (no combined sums) and the pre-shrine stats meet it; then the shrine may lower those stats and it stays.','canPre = has stats and no combined sums; taken pre if cost(alt, preStats) = 0','canPre(), evaluate()'),
('Requirements','Silentheart','Weapon stat requirements on weapons are 25 lower.','weapon req = max(0, req - 25)','reqAlts() isWeaponReq'),
('Requirements','Weapon type filling','When a combined weapon/attunement sum needs points, they go first to your weapon type, then your attunements, then stats your weapon scales with, then the highest.','fillPriority order','fillPriority(), applyAlt()'),
('Talents','Talent cap','How many talents fit. Each normal mantra uses 2 talent slots.','cap = 52 + (12 - normal mantras) x 2','counts()'),
('Talents','Popularity','Share of 802 top-rated and most-viewed deepwoken.co builds that take the talent.','POP = builds with talent / builds','POP (data: pop)'),
('Talents','Take rate given stats','Of 500 top deepwoken.co builds whose stats allow the talent, the share that take it (shown when at least 5 builds qualify).','rate = k / m','condRate(), CONDD (data: cond.txt)'),
('Talents','Value of a talent','Used when dropping talents and in Optimize trimming. Weapon/attunement talents (kit) count much more; the damage<->talent options slider shifts weight between damage talents and popular/synergy talents.','value = 90 x kit + 60 x key talent + (1 + popularity + synergy x 15) x (0.4 + 1.2 x slider) + (damage + PEN) x 100 x (0.2 + 3.6 x (1 - slider))','talentVal(), kitOf()'),
('Talents','Kit (your weapon / attunement)','1 when a talent (with its prerequisites) needs your weapon type stat or one of your attunements, or its category names them.','kit = 1 if req stats include weapon type or an attunement, else 0','kitOf()'),
('Talents','Auto-pick','Fills open talent slots with talents your stats already reach (before or after the shrine), skipping ones that would pull in a new mantra, best value per slot first.','value per slot = ((popularity if >= 3) + synergy x 15) x (0.4 + 1.2 x slider) + damage x (0.2 + 3.6 x (1 - slider)) + 90 x kit, divided by (1 + missing prerequisites)','autoPickList()'),
('Talents','Suggestions (recommendations)','Talents that fit or are close, ranked: synergies first, then take rate given stats, plus the kit bonus. Similar reference builds decide which talents show up.','rank = (10 + synergy weight if any synergy) + share + 0.8 x kit','recommendations()'),
('Talents','Status of a talent','In build / Avoided / Above your stat limit / Blocked by an exclusive / Needs another oath / Fits (now or before the shrine) / Close (+15 points or less) / Far.','cost = min(cost at final stats, cost at pre-shrine stats if it can be taken pre)','statusOf()'),
('Talents','Synergies','Pairs of talents that work together, each with a weight; a synergy counts like a talent 15% of builds take per weight unit.','synergy value = sum of weights x 15','SYN, synOf()'),
('Talents','Likely talents (screenshot)','Talents the read stats allow, ranked by take rate given stats, how often they appear with the talents you saw (reference builds), synergy and kit.','score = 0.55 x take rate + 0.9 x co-occurrence + 0.12 x synergy + 0.35 x kit','likelyTalents()'),
('Damage','Weapon scaling','Sum of each scaling coefficient x your final stat (Mind/Body use the highest of their stats).','h = sum(coef_k x stat_k)','damageOf()'),
('Damage','Scaled weapon damage','Proficiency multiplies the stat part.','scaled = base x (1 + 0.75 x h x (1 + 0.065 x Proficiency) / 1000)','damageOf()'),
('Damage','Talent damage bonus','Sum of talent damage bonuses (+2.5% for Soulbreaker). Full to +25%, half past it, capped at +50%. Unique bonuses add outside the cap.','m = raw <= 0.25 ? raw : min(0.5, 0.25 + (raw - 0.25)/2)','damageOf()'),
('Damage','Weapon PEN','Weapon PEN + 1% per 10 Strength + talent PEN + enchant PEN + 2.5% per Proficiency, capped at 50% (100% if a talent removes the cap); some talents multiply instead.','pen = min(cap, min(1, raw) x multiplier)','damageOf()'),
('Damage','Talents that shrink below a stat','Some bonuses scale with your final stat (Deepwoken wiki, Talents page): Million Ton Piercer +5% PEN in full only at 90 Strength, Ether Overdrive the same at 90 Intelligence, Cheap Shot loses 0.11% of its PEN multiplier per Agility below 65 (min 7.22% at 40), Overflowing Dam loses 0.125% damage per Intelligence below 40 (min 6.875% at 15).','MTP pen = 0.05 x min(1, STR/90); EO pen = 0.05 x min(1, INT/90); Cheap Shot = max(0.0722, 0.10 - 0.0011 x max(0, 65 - AGL)); Dam = max(0.06875, 0.10 - 0.00125 x max(0, 40 - INT))','SCALE_MOD, damageOf()'),
('Damage','Weapon hit vs armor','Against 30% armor.','hit = scaled x (1 + m + unique) x enchant hit x (1 - (1 - pen) x 0.3)','damageOf()'),
('Damage','Mantra level','From the attunement value.','level = clamp(1 + floor(attunement / 20), 1, 5)','mLevel()'),
('Damage','Mantra hit','Level damage, scaling from stats (Songchant multiplies it), talent bonus, and Songchant PEN against 30% armor. Combat mantras of each attunement are averaged.','hit = lv[level] x (1 + sum(coef/10 x stat/100) x (1 + 0.065 x Songchant)) x (1 + m) x (1 - (1 - min(0.5, 0.025 x Songchant)) x 0.3)','mantraDamage()'),
('Damage','Damage split','The M1 <-> mantra slider weights weapon and mantra damage in the optimizer score.','dmg% = (1 - split) x weapon% + split x mantra%','evaluate()'),
('Health','Health','Power 20 assumed.','hp = 220 + 4 x 20 + 0.5 x min(FTD, 50) + 0.25 x max(FTD - 50, 0) + 10 x Vitality + gear health','gearStats()'),
('Health','Resistance and effective health','Armor % reduced by assumed penetration (35% physical, 20% elemental), capped at 95%.','res = min(0.95, armor/100 x (1 - pen/100)); EHP = hp / (1 - res)','gearStats()'),
('Equipment','Optimize equipment','Reach minimum health (default 500) and minimum physical armor (default 50%) first; then health x (1/(1-res))^a, where the Health<->Armor slider sets a. Elemental pips are never chosen; Transfusion Ring is never picked.','score = deficits ? -1e6 - 10 x HP short - 40 x armor short : hp x (1/(1-res))^a','gearScore(), optimizeGear()'),
('Traits','Trait pool','12 points in total (one at most even Power levels), at most 6 per trait. They don\'t use stat points.','sum(traits) <= 12; each <= 6','TRAITS, tr()'),
('Traits','Suggested traits','Weapon builds: Proficiency 6 + Vitality 6. Mantra builds (split >= 75% or Hero\'s Blade): Songchant 6, Erudition 3, Vitality 3. Hybrid: 4/4/4 Vitality/Proficiency/Songchant.','by damage split','suggestTraits()'),
('Optimizer','Score of a stat plan','Points left count most; then damage and talent options, weighted by the damage<->talent options slider. Over a stat limit or breaking the pre-shrine rule costs 20 per point.','score = (330 - used) + 2 x (1 - slider) x dmg% + 2 x slider x talent options / 10; free = 330 - used - 20 x capOver - 20 x reup','evaluate()'),
('Optimizer','Search','Hill climbing over pre-shrine stats from several starting points, keeping the best score.','starts x iterations random moves','searchStats(), compute()'),
('Optimizer','Fitting the budget','1) drop talents that are blocked by limits, 2) trim to the talent cap (lowest value per slot), 3) drop the talent that frees the most points per value, repeat, 4) if required talents + floors alone are over, lower floors 5 at a time (not ones you set in Adjustments), 5) rebuild picks from most to least valuable while they fit.','see steps','optimizeAll(), trimToCap(), trimToBudget(), easeFloors(), rebuildToBudget()'),
('Optimizer','Damage <-> talent options trade','Toward damage: weapon/attunement targets rise toward 100, paid for by the least useful non-damage talents, open slots get damage talents. Toward talent options: targets fall toward the weapon requirement / 40 and freed points go to popular and synergy talents. 35-65 keeps the build; undone if it cannot be paid for.','targets move by (distance from middle x 2)','sliderRebalance()'),
('Optimizer','Spending leftover points','Each step adds the amount (1, 5, the next mantra level, or the next talent threshold) to the stat with the best gain per point; gain blends damage and talent options by the slider. Retried with fewer points if it would go over budget.','gain = ((1 - slider) x dmg% + max(slider, 0.05) x talent options / 10) per point','optimizeAll() spend'),
('AI build maker','Attunements','One named: 80 (mage 100). Two: 80/40, raised to 80/80 if 40+ points are left (mage or "dual": 80/80). Three or more: the first one 80 (mage 100), the rest 40.','see rule','aiParse(), wizardApply()'),
('AI build maker','Oath','The oath you name is kept; otherwise the starting preset\'s default; with no preset, the most common oath in similar top builds that fits. Silentheart is never picked automatically for attunement or mage builds.','see rule','aiParse(), wizardApply()'),
('Import','deepwoken.co','deepwoken.co blocks other sites from reading its builds. The bookmark runs on the build page, reads the build there and opens Meta Builder with it in the address (#dwco=...), which imports on load.','n/a','DWCO_SNIP, dwbFromCoJson()'),
]
for i,row in enumerate(FX,2):
    for j,v in enumerate(row,1):
        c=wf.cell(row=i,column=j,value=v);c.font=f_bold if j==1 else f_norm;c.alignment=wrap
wf.freeze_panes='C2';wf.auto_filter.ref=f'A1:E{len(FX)+1}'

# ---------------- Talents ----------------
wt=sheet('Talents')
rar={'A':'Advanced','R':'Rare','C':'Common','O':'Oath','Q':'Quest','E':'Equipment','M':'Murmur','I':'Innate','G':'Origin'}
header(wt,1,['Talent','Category','Rarity','Pickable','Requirement','Cheapest way to meet it (with prerequisites)','Points needed from 0','Can be taken before the shrine','Popularity (% of top builds)','Builds that can take it','Builds that take it','Take rate given stats','Damage bonus','PEN bonus','Unique bonus','Synergies (weight)','Exclusive with','Description'],[26,18,10,8,38,38,10,10,11,10,10,11,9,9,8,40,24,90])
T=sorted(D['talents'],key=lambda t:t['n'])
for i,t in enumerate(T,2):
    vals=[t['n'],t['c'],rar.get(t['r'],t['r']),'yes' if t['pick'] else 'no',t['full'] or t['req'],t['cheap'],t['cheapCost'] if t['cheapCost']!=float('inf') else 'n/a','yes' if t['pre'] else 'no',t['pop']/100,t['m'],t['k'],None,t['dmg'],t['pen'],'yes' if t['uniq'] else '',t['syn'],t['excl'],t['desc']]
    for j,v in enumerate(vals,1):
        c=wt.cell(row=i,column=j,value=v);c.font=f_norm
    wt.cell(row=i,column=12,value=f'=IF(J{i}>=5,K{i}/J{i},"too few builds")').fill=fill_out
    for col in (9,12,13,14): wt.cell(row=i,column=col).number_format='0.0%'
wt.freeze_panes='B2';wt.auto_filter.ref=f'A1:R{len(T)+1}'

# ---------------- Outfits / Equipment / Enchants / Oaths / Presets ----------------
wo=sheet('Outfits');header(wo,1,['Outfit','Physical armor %','Elemental armor %','Durability','Requirement','Talents it gives'],[34,14,14,11,24,40])
for i,o in enumerate(sorted(D['outfits'],key=lambda o:o['n']),2):
    for j,v in enumerate([o['n'],o['p'],o['e'],o['dur'],o['req'],o['tal']],1): wo.cell(row=i,column=j,value=v).font=f_norm
wo.freeze_panes='B2';wo.auto_filter.ref=f'A1:F{len(D["outfits"])+1}'
we=sheet('Equipment');header(we,1,['Item','Slot','Health','Physical armor','Elemental armor','Pip slots (rarity)','Requirement','Set','Talents it gives'],[32,10,8,10,10,18,20,14,40])
for i,g in enumerate(sorted(D['gear'],key=lambda g:(g['ty'],g['n'])),2):
    for j,v in enumerate([g['n'],slot.get(g['ty'],g['ty']),g['hp'],g['pp'],g['ep'],g['pips'],g['req'],g['set'],g['tal']],1): we.cell(row=i,column=j,value=v).font=f_norm
we.freeze_panes='B2';we.auto_filter.ref=f'A1:I{len(D["gear"])+1}'
wn=sheet('Enchants');header(wn,1,['Enchant','Always-on hit multiplier','Added PEN','Sometimes (shown, not counted)','Extra damage trigger','What it does'],[28,14,10,14,30,90])
for i,e in enumerate(D['enchants'],2):
    for j,v in enumerate([e['n'],e['hit'],e['pen'],e['cond'],e['pt'],e['d']],1):
        c=wn.cell(row=i,column=j,value=v);c.font=f_norm;c.alignment=wrap
wn.freeze_panes='B2'
wa=sheet('Oaths');header(wa,1,['Oath','Requirement','Stat options (any one)','Note'],[18,50,60,50])
for i,o in enumerate(D['oaths'],2):
    for j,v in enumerate([o['n'],o['req'],o['alts'],o['note']],1):
        c=wa.cell(row=i,column=j,value=v);c.font=f_norm;c.alignment=wrap
wa.freeze_panes='B2'
wp=sheet('Presets');header(wp,1,['Preset','Description','Oath','Weapon target','Attunements','Before shrine','After shrine'],[24,70,14,14,18,26,22])
for i,p in enumerate(D['presets'],2):
    for j,v in enumerate([p['n'],p['d'],p['oath'],p['w'],p['atts'],p['pre'],p['post']],1):
        c=wp.cell(row=i,column=j,value=v);c.font=f_norm;c.alignment=wrap
wp.freeze_panes='B2'
# order sheets
order=['Read Me','Calculator','Formulas','Talents','Mantras','Weapons','Outfits','Equipment','Enchants','Oaths','Presets','Constants']
wb._sheets=[wb[n] for n in order]
wb.save(HERE.parents[1]/'docs'/'Meta Builder formulas.xlsx');print('saved')
