"""Build the website: python3 src/build.py  (run from the repo root)

Fills the @@PLACEHOLDERS@@ in src/template.html with the files in src/data/,
wraps the result in src/head.html, and writes index.html (what GitHub Pages serves)
plus dist/meta-builder.html (the bare page, used for the Claude artifact).
"""
import os
here=os.path.dirname(os.path.abspath(__file__)); root=os.path.dirname(here)
r=lambda f:open(os.path.join(here,'data',f),encoding='utf-8').read().strip()
t=open(os.path.join(here,'template.html'),encoding='utf-8').read()
m={'@@DATA@@':r('part1.txt')+'\n'+r('part2.txt'),'@@BUILDS@@':r('builds.txt'),'@@WDMG@@':r('wdmg.txt'),'@@POP@@':r('pop.txt'),
   '@@MDMG@@':r('mdmg.txt'),'@@SYN@@':r('syn.txt'),'@@GEAR@@':r('gear.txt'),'@@TDESC@@':r('tdesc.txt'),'@@COND@@':r('cond.txt'),'@@VERSIONS@@':r('versions.txt')}
# the newest version (first '## vX' heading in versions.txt) is the badge next to the title
import re as _re
m['@@VER@@']=_re.search(r'^## (v[0-9.]+)',m['@@VERSIONS@@'],_re.M).group(1)
# the desktop app version this page needs (app/package.json shellVersion); older apps are told to download the new one
import json as _j0
try:m['@@SHELL@@']=str(int(_j0.load(open(os.path.join(root,'app','package.json'),encoding='utf-8')).get('shellVersion',1)))
except Exception:m['@@SHELL@@']='1'
for k,v in m.items(): t=t.replace(k,v)
assert '@@' not in t, 'a placeholder was left unfilled'
os.makedirs(os.path.join(root,'dist'),exist_ok=True)
open(os.path.join(root,'dist','meta-builder.html'),'w',encoding='utf-8').write(t)
head=open(os.path.join(here,'head.html'),encoding='utf-8').read()
open(os.path.join(root,'index.html'),'w',encoding='utf-8').write(head+t.rstrip('\n')+'\n</body>\n</html>\n')
# the app (Node server + Electron desktop app) serves the same page; its version follows versions.txt (v0.32 -> 0.32.0)
os.makedirs(os.path.join(root,'app','www'),exist_ok=True)
open(os.path.join(root,'app','www','index.html'),'w',encoding='utf-8').write(head+t.rstrip('\n')+'\n</body>\n</html>\n')
import json as _json
pj=os.path.join(root,'app','package.json')
if os.path.exists(pj):
  pkg=_json.load(open(pj,encoding='utf-8'));ver=m['@@VER@@'].lstrip('v')+'.0'
  if pkg.get('version')!=ver:
    pkg['version']=ver;open(pj,'w',encoding='utf-8').write(_json.dumps(pkg,indent=2)+'\n')
print('built index.html, dist/meta-builder.html and app/www/index.html,',len(t),'bytes')
