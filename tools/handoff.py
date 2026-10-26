"""Builds the handoff page (dist/handoff.html) from NOTES.md, for starting a new chat. Publish it to the handoff artifact."""
import markdown,pathlib,re,html
ROOT=pathlib.Path(__file__).resolve().parents[1]
notes=(ROOT/'NOTES.md').read_text()
ver=re.search(r'^## (v[0-9.]+)',(ROOT/'src'/'data'/'versions.txt').read_text(),re.M).group(1)
body=markdown.markdown(notes,extensions=['tables','fenced_code','sane_lists'])
body=re.sub(r'<table>','<div class="tw"><table>',body);body=body.replace('</table>','</table></div>')
starter=f"""I'm continuing work on Meta Builder, my Deepwoken Shrine of Order build planner (currently {ver}).
Repo: itsmrchickenss/meta-builder (please attach it). Read CLAUDE.md and NOTES.md in the repo first; they have the rules I've set, every formula, the file layout, how to build, test and publish, and the version history.
Handoff notes: https://claude.ai/artifact/YBSQSo98nCQC84rkSZVZE3
Website: https://itsmrchickenss.github.io/meta-builder/
Claude artifact to update: https://claude.ai/artifact/BoupUctZcdQwYCUpkDoyFn
What I want next: """
page=f'''<title>Meta Builder Handoff</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&family=Alegreya+Sans:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* layout: one reading column, a pinned "start a new chat" card at the top, notes below */
:root{{--bg:#f3f1ec;--panel:#ffffff;--ink:#1d2427;--dim:#5d6a6c;--line:#d9d4c8;--accent:#8a5f16;--wash:#f5ecd9;
  --f-display:"IM Fell English SC",Georgia,serif;--f-body:"Alegreya Sans","Segoe UI",system-ui,sans-serif;--f-mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#0c1418;--panel:#121e24;--ink:#e6dccb;--dim:#97a39f;--line:#2a3d45;--accent:#c9a35a;--wash:#2a2414;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#0c1418;--panel:#121e24;--ink:#e6dccb;--dim:#97a39f;--line:#2a3d45;--accent:#c9a35a;--wash:#2a2414;color-scheme:dark}}
body{{background:var(--bg);color:var(--ink);font-family:var(--f-body);font-size:16px;line-height:1.55;padding-block:28px 60px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
main{{max-width:860px;margin:0 auto;display:grid;gap:22px}}
h1{{font-family:var(--f-display);font-weight:400;font-size:clamp(28px,5vw,40px);margin:0;text-wrap:balance}}h1 small{{font-family:var(--f-mono);font-size:13px;color:var(--dim);margin-left:8px}}
.lede{{color:var(--dim);margin:0}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:16px 18px;display:grid;gap:10px}}
.card h2{{margin:0;font-size:18px}}.card ol{{margin:0;padding-left:20px;display:grid;gap:4px}}
textarea{{width:100%;box-sizing:border-box;min-height:190px;font-family:var(--f-mono);font-size:13px;background:var(--bg);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:10px;resize:vertical}}
button{{font:inherit;font-weight:700;background:var(--accent);color:var(--panel);border:0;border-radius:6px;padding:8px 14px;cursor:pointer;justify-self:start}}button:focus-visible{{outline:2px solid var(--ink);outline-offset:2px}}
#msg{{color:var(--dim);font-size:14px;margin:0;min-height:1.2em}}
.notes{{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:6px 22px 22px;min-width:0}}
.notes h1{{font-size:26px;margin-top:16px}}.notes h2{{font-family:var(--f-display);font-weight:400;font-size:23px;margin:28px 0 8px;border-bottom:1px solid var(--line);padding-bottom:4px;text-wrap:balance}}
.notes p,.notes li{{max-width:72ch}}.notes code{{font-family:var(--f-mono);font-size:.86em;background:var(--wash);padding:1px 4px;border-radius:3px;overflow-wrap:anywhere}}
.notes a{{color:var(--accent);overflow-wrap:anywhere}}.notes strong{{color:var(--ink)}}
.tw{{overflow-x:auto}}.notes table{{border-collapse:collapse;font-size:14px;min-width:560px}}.notes th,.notes td{{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}}.notes th{{color:var(--dim);font-size:12px;text-transform:uppercase;letter-spacing:.06em}}
</style>
<main>
  <header><h1>Meta Builder Handoff<small>{html.escape(ver)}</small></h1><p class="lede">Everything a new chat needs to keep building Meta Builder: the owner's rules, how it's built and shipped, every formula, and what's been done.</p></header>
  <section class="card" aria-labelledby="start">
    <h2 id="start">Start a new chat</h2>
    <ol><li>Open a new chat and attach the GitHub repo <code>itsmrchickenss/meta-builder</code>.</li><li>Paste the message below and finish the last line with what you want changed.</li></ol>
    <textarea id="starter" aria-label="Message to paste into a new chat">{html.escape(starter)}</textarea>
    <button type="button" id="copy">Copy message</button><p id="msg" aria-live="polite"></p>
  </section>
  <article class="notes">{body}</article>
</main>
<script>
document.getElementById('copy').addEventListener('click',async()=>{{const t=document.getElementById('starter');const m=document.getElementById('msg');
  try{{await navigator.clipboard.writeText(t.value);m.textContent='Copied. Paste it into the new chat.'}}catch(e){{t.focus();t.select();m.textContent='Press Ctrl+C (Cmd+C on Mac) to copy the selected message.'}}}});
</script>
'''
(ROOT/'dist').mkdir(exist_ok=True)
out=ROOT/'dist'/'handoff.html';out.write_text(page);print('wrote',out)
