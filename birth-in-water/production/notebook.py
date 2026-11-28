"""Build the web reader from the edition's editable research and production notes."""
from html import escape
from pathlib import Path
import subprocess
from urllib.parse import urlsplit

from lxml import etree,html

study=Path(__file__).resolve().parents[1]/'studies'
groups=[
 ('Film and sources',[('gallery-cut','The 79-second cut'),('field-notes','Research notes'),
                     ('camera-report','Camera and sources'),('return-study','The return'),
                     ('material-trial','Weight in water')]),
 ('Exhibition',[('gallery-rehearsal','Curatorial choices'),('visitor-test','Visitors and service'),
                ('projection-throw','Projector positions'),('room-sound','Speaker positions')]),
 ('Water and light',[('optics','Light at the shell'),('water-at-the-shell','The water field')]),
 ('Production',[('qa-2026-11-28','Verification log')])]
documents={key:label for _,items in groups for key,label in items}
if (study/'population-light.md').is_file():
    groups[2][1].append(('population-light','Moving population on glass'))
    documents['population-light']='Moving population on glass'
articles=[]
for key,label in documents.items():
    source=study/(key+'.md')
    content=subprocess.check_output(['pandoc','-f','markdown+autolink_bare_uris','-t','html5',
            '--wrap=none','--id-prefix',key+'--',str(source)],text=True)
    article=html.fragment_fromstring(content,create_parent='article')
    article.set('id',key)
    for a in article.iter('a'):
        url=a.get('href','')
        parts=urlsplit(url)
        if not parts.scheme and not parts.netloc and '/' not in parts.path:
            filename=Path(parts.path)
            if filename.suffix=='.md' and filename.stem in documents:
                target=filename.stem
                a.set('href','#'+target+('--'+parts.fragment if parts.fragment else ''))
    for image in article.iter('img'):
        image.set('loading','lazy')
    for table in list(article.iter('table')):
        wrapper=html.Element('div',attrib={'class':'table','tabindex':'0','aria-label':'Scrollable data table'})
        table.getparent().replace(table,wrapper);wrapper.append(table)
    footer=html.Element('p',attrib={'class':'source'});link=etree.SubElement(footer,'a',href=source.name)
    link.text='Download the editable notes';link.set('download','')
    article.append(footer)
    articles.append(html.tostring(article,encoding='unicode',method='html'))
nav=''.join('<section><h2>'+escape(group)+'</h2>'+''.join('<a href="#'+key+'">'+escape(label)+'</a>' for key,label in items)+'</section>' for group,items in groups)
page="""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Birth in Water · Production notebook</title>
<style>
*{box-sizing:border-box}html{background:#f3f0e7;color:#243832}body{margin:0;font:1rem/1.62 system-ui,sans-serif}a{color:#275953;text-underline-offset:.2em;overflow-wrap:anywhere}
header,.layout{max-width:1240px;margin:auto;padding:1rem clamp(1rem,4vw,3rem)}header{border-bottom:1px solid #b0bbaf;display:flex;gap:1.5rem;align-items:center;flex-wrap:wrap}header strong{font:1.3rem Georgia,serif}header a,nav a,.source a{font-size:.9rem}.layout{display:grid;grid-template-columns:210px minmax(0,1fr);gap:clamp(1.5rem,5vw,5rem);align-items:start;padding-bottom:5rem}
nav{position:sticky;top:.8rem;max-height:94vh;overflow:auto}nav section+section{margin-top:1rem}nav h2{font:600 .78rem/1.4 system-ui,sans-serif;color:#50685b;margin:.25rem 0}nav a{display:block;padding:.15rem 0;text-decoration:none}nav a[aria-current]{font-weight:700;text-decoration:underline}nav summary{cursor:pointer;font-weight:600;margin-bottom:.7rem}article{max-width:86ch;margin-bottom:4rem;min-width:0}article[hidden]{display:none}
h1,h2,h3{font-family:Georgia,serif;font-weight:400;line-height:1.12;color:#17332c}h1{font-size:clamp(2.3rem,5vw,4.25rem);letter-spacing:-.045em;margin:.5em 0 .45em}article h2{font-size:clamp(1.6rem,3vw,2.3rem);margin:1.7em 0 .35em}article h3{font-size:1.34rem}p{max-width:76ch}img{max-width:100%;height:auto}figure{margin:1.2rem 0}figcaption{color:#4d6558;font-size:.9rem}table{border-collapse:collapse;font-size:.91rem}.table{max-width:100%;overflow-x:auto}td,th{padding:.6rem .5rem;border-bottom:1px solid #b3bdaf;vertical-align:top;text-align:left}code{overflow-wrap:anywhere}pre{overflow:auto}blockquote{margin:1rem 0;border-inline-start:3px solid #91ad9d;padding-left:1rem}.source{border-top:1px solid #aeb9ae;margin-top:2rem;padding-top:1rem}
@media(max-width:740px){.layout{display:block}nav{position:static;max-height:none;border-bottom:1px solid #adb7ac;padding-bottom:.3rem;margin-bottom:1.3rem}nav details[open]{padding-bottom:1rem}header{gap:.6rem 1.2rem}.table{font-size:.86rem}}
@media print{nav,header,.source{display:none}.layout{display:block}article:not([hidden]){display:block}body{font-size:10pt}.table{overflow:visible}}
</style></head><body><header><strong>Production notebook</strong><a href="../">Birth in Water</a><a href="room.html">Exhibition study</a><a href="record.html">Sources and credits</a></header>
<div class="layout"><nav aria-label="Notebook contents"><details id="contents" open><summary>Contents</summary>NAVIGATION</details></nav><main>ARTICLES</main></div>
<script>
const chapters=Array.from(document.querySelectorAll('main article')),links=Array.from(document.querySelectorAll('nav a'));
const compact=window.matchMedia('(max-width:740px)'),contents=document.querySelector('#contents');
function choose(){
  const requested=document.getElementById(decodeURIComponent(location.hash.slice(1)));
  const chapter=requested?.closest('article')||chapters[0];
  for(const article of chapters)article.hidden=article!==chapter;
  for(const a of links){if(a.hash==='#'+chapter.id)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');}
  document.title=chapter.querySelector('h1').textContent+' · Birth in Water';
  contents.open=!compact.matches;
  if(requested && requested!==chapter)requested.scrollIntoView();else window.scrollTo(0,0);
}
choose();window.addEventListener('hashchange',choose);compact.addEventListener('change',()=>{contents.open=!compact.matches;});
</script></body></html>
"""
(study/'notebook.html').write_text(page.replace('NAVIGATION',nav).replace('ARTICLES','\n'.join(articles)))
