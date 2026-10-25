import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
URL=(ROOT/'index.html').as_uri()
from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch();errs=[]
    for w in (1280,390):
        pg=b.new_page(viewport={'width':w,'height':900});pg.on('pageerror',lambda e:errs.append(str(e)))
        sent=[]
        def rt(r):
            sent.append(json.loads(r.request.post_data));r.fulfill(status=200,headers={'content-type':'application/json','access-control-allow-origin':'*'},body='{"success":true}')
        pg.route('**/api.web3forms.com/**',rt)
        pg.goto(URL);pg.wait_for_timeout(2000)
        pg.click('#t-bug');pg.wait_for_timeout(300)
        print(w,'hscroll',pg.evaluate("document.documentElement.scrollWidth>innerWidth"),'tab visible',pg.is_visible('#bugform'))
        pg.fill('#bugwhat','Optimize went over budget on Chime');pg.click('#bugsend');pg.wait_for_timeout(500);print('  no key:',pg.inner_text('#bugmsg'))
        if w==1280:
            # pretend the key is set: patch the sender by re-evaluating with a key
            pg.evaluate("(()=>{const src=sendBug.toString().replace(\"if(!BUG_KEY)\",\"if(false)\").replace(\"access_key:BUG_KEY\",\"access_key:'test-key'\");window.sendBug=eval('('+src+')')})()")
            pg.fill('#bugwhat','Optimize went over budget on Chime');pg.click('#bugsend');pg.wait_for_timeout(800)
            print('  with key:',pg.inner_text('#bugmsg'),'| payload subject:',sent and sent[0]['subject'],'| has build link:','#dw1' in (sent[0]['message'] if sent else ''))
            pg.evaluate("document.getElementById('tabbar').style.position='static'");pg.locator('#tab-bug').screenshot(path=str(pathlib.Path('/tmp')/'mb-shot.png'))
    print('errs',errs);b.close()
