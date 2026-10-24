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
   '@@MDMG@@':r('mdmg.txt'),'@@SYN@@':r('syn.txt'),'@@GEAR@@':r('gear.txt'),'@@TDESC@@':r('tdesc.txt')}
for k,v in m.items(): t=t.replace(k,v)
assert '@@' not in t, 'a placeholder was left unfilled'
os.makedirs(os.path.join(root,'dist'),exist_ok=True)
open(os.path.join(root,'dist','meta-builder.html'),'w',encoding='utf-8').write(t)
head=open(os.path.join(here,'head.html'),encoding='utf-8').read()
open(os.path.join(root,'index.html'),'w',encoding='utf-8').write(head+t.rstrip('\n')+'\n</body>\n</html>\n')
print('built index.html and dist/meta-builder.html,',len(t),'bytes')
