"""Build the GitHub-safe profile: outlined SVG + time-based animation, no scripts."""
from pathlib import Path
import copy
import json
import re
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
SRC = BASE / 'source'
ASSETS = BASE / 'assets'
ASSETS.mkdir(exist_ok=True)
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
def el(tag, attrs=None, **kwargs):
    return ET.Element('{%s}%s' % (NS, tag), dict(attrs or {}, **kwargs))
def decoded(s):
    try: return s.encode('latin1').decode('utf8')
    except (UnicodeEncodeError, UnicodeDecodeError): return s
def write_svg(root, path):
    ET.ElementTree(root).write(path, encoding='utf-8', xml_declaration=True)

config = json.loads((SRC/'content.json').read_text())
outlines = {x['text']:x for x in json.loads((SRC/'text-outlines.json').read_text())}
root = ET.parse(SRC/'figma-light.svg').getroot()
root.set('role', 'img')
root.set('aria-labelledby', 'profile-title profile-desc')
title = el('title', id='profile-title'); title.text = 'FengLi — AI × Product Thinking'
desc = el('desc', id='profile-desc'); desc.text = 'AI 产品探索工作台。技能：' + '、'.join(config['skills']) + '。个人网站、小红书与公众号的独立入口位于画面下方。'
root.insert(0, title); root.insert(1, desc)
nodes = {}
for n in root.iter():
    if 'id' in n.attrib: nodes[decoded(n.get('id'))] = n
def cls(n, name):
    n.set('class', name)
def parent(n):
    return next(p for p in root.iter() if n in list(p))

# Keep the Figma mask and stationary circle; rotate only the text, behind the artwork.
arcs = [n for name,n in nodes.items() if '浅色矢量文字' in name]
arc_parent = parent(arcs[0])
arc_group = el('g', id='orbit-motion', **{'class':'orbit'})
arc_parent.insert(list(arc_parent).index(arcs[0]), arc_group)
for n in arcs: arc_parent.remove(n); arc_group.append(n)

# Reveal individual code lines while preserving their isometric geometry.
for name,delay in [('Vector_36',0),('Vector_49',1.1)]:
    n = nodes[name]; p = parent(n); index = list(p).index(n)
    for i,d in enumerate(re.findall(r'M[^M]+',n.get('d'))):
        line = copy.deepcopy(n); line.set('id',name+'-line-'+str(i)); line.set('d',d)
        cls(line,'screen-line'); line.set('style',f'animation-delay:{-8+delay+i*.65}s')
        p.insert(index+i,line)
    p.remove(n)
for i,name in enumerate(['Vector_37','Vector_38']):
    cls(nodes[name], 'screen-line'); nodes[name].set('style',f'animation-delay:{-5.8+i*.7}s')
for name in ['Vector_39','Vector_50']: cls(nodes[name],'cursor')
for i,name in enumerate(['Vector_76','Vector_92','Vector_108','Vector_116']):
    cls(nodes[name], 'key'); nodes[name].set('style',f'animation-delay:{-i*1.31}s')

# Original idea wordmark; extra small outlined idea marks appear at different moments.
idea = next(n for name,n in nodes.items() if name.startswith('{ idea }'))
cls(idea,'idea'); idea.set('style','animation-delay:-1.5s')
desk = nodes['03 / 等距桌面']
bulb_holder = el('g',transform='translate(552 239)')
bulb = el('g',{'class':'idea','style':'animation-delay:-4.5s'})
bulb.append(el('path',d='M-7 0C-7-10 7-10 7 0C7 4 3 5 3 9H-3C-3 5-7 4-7 0ZM-3 12H3M-1 15H1M0-13V-17M-11-8L-14-10M11-8L14-10',fill='none',stroke='#5A75FB',**{'stroke-width':'1.6','stroke-linecap':'round','stroke-linejoin':'round'}))
bulb_holder.append(bulb); desk.append(bulb_holder)
spark_holder = el('g',transform='translate(408 307)')
spark = el('g',{'class':'idea','style':'animation-delay:-6.5s'})
spark.append(el('path',d='M0-8Q1-1 7 0Q1 1 0 8Q-1 1-7 0Q-1-1 0-8Z',fill='#5A75FB'))
spark_holder.append(spark); desk.append(spark_holder)
for i,name in enumerate(['Vector_132','Vector_133','Vector_134']):
    n=nodes[name]
    # Move outside the star's tight clip, so the motion is not cropped.
    p=parent(n)
    if p.get('clip-path'):
        outer=parent(p); outer.insert(list(outer).index(p),n); p.remove(n)
    cls(n,'star-float'); n.set('style',f'animation-delay:{-i*1.7}s')

# Rebuild the full, unclipped vocabulary with the exact local Humnst777 font outlines.
ticker=nodes['08 / 斜向文字带']
for child in list(ticker):
    if child.tag.endswith('g'):ticker.remove(child)
local=el('g',transform='matrix(.9878608584 -.1553409845 .1553409845 .9878608584 37.716796875 748.7109375)')
clip=el('clipPath',id='ticker-window');clip.append(el('rect',x='0',y='0',width='1520',height='72'))
local.append(clip)
window=el('g',{'clip-path':'url(#ticker-window)'})
moving=el('g',id='ticker-motion',**{'class':'ticker'})
row=el('g',id='skill-row')
x=0
for word in config['skills']:
    shape=outlines[word]
    item=el('g',transform=f'translate({x:.3f} 0)')
    item.append(el('path',d='M7 28Q8 35 13 36Q8 37 7 44Q6 37 1 36Q6 35 7 28Z',fill='#5A75FB'))
    item.append(el('path',d=shape['d'],fill='#37383D',transform=f'translate(31 {36-shape["height"]/2:.3f})'))
    row.append(item)
    x += shape['advance']+81
period=x
moving.append(row)
for shift in [-period,period]:
    moving.append(el('use',href='#skill-row',transform=f'translate({shift:.3f} 0)'))
window.append(moving);local.append(window);ticker.append(local)

style=el('style')
style.text=f'''
.orbit {{ transform-origin:1056.5px 291.5px; animation:orbit {config['motion']['orbit_seconds']}s linear infinite; }}
@keyframes orbit {{ to {{ transform:rotate(360deg); }} }}
.cursor {{ animation:blink 1.3s steps(1,end) infinite; }}
@keyframes blink {{ 0%,48%,100% {{ opacity:1; }} 49%,90% {{ opacity:.12; }} }}
.screen-line {{ animation:code 8s linear infinite; }}
@keyframes code {{ 0%,8% {{ clip-path:inset(0 100% 0 0);opacity:.25; }} 36%,82% {{ clip-path:inset(0 0 0 0);opacity:1; }} 95%,100% {{ clip-path:inset(0 0 0 0);opacity:.15; }} }}
.key {{ animation:press 5.6s ease-in-out infinite; }}
@keyframes press {{ 0%,8%,15%,22%,100% {{ transform:translateY(0);fill:#F4FBFF; }} 10%,12%,18%,20% {{ transform:translateY(1.7px);fill:#B8C5FC; }} }}
.idea {{ animation:idea 8s ease-in-out infinite; }}
@keyframes idea {{ 0%,12%,78%,100% {{ opacity:0;transform:translateY(8px); }} 28%,45% {{ opacity:1;transform:translateY(-3px); }} 68% {{ opacity:0;transform:translateY(-20px); }} }}
.star-float {{ animation:float 6.4s ease-in-out infinite; }}
@keyframes float {{ 0%,100% {{opacity:.25;transform:translateY(5px);}} 40% {{opacity:1;}} 80% {{opacity:0;transform:translateY(-10px);}} }}
.ticker {{ animation:ticker {period/config['motion']['ticker_pixels_per_second']:.3f}s linear infinite; }}
@keyframes ticker {{ from {{transform:translateX(-130.834px);}} to {{transform:translateX({period-130.834:.3f}px);}} }}
@media (prefers-reduced-motion:reduce) {{ .orbit,.cursor,.screen-line,.key,.idea,.star-float,.ticker {{animation:none!important;}} .idea {{opacity:.65;}} .ticker {{transform:translateX(-130.834px);}} }}
'''
root.insert(2,style)
write_svg(root, ASSETS/'profile-light.svg')
static=copy.deepcopy(root)
static.remove(next(n for n in static if n.tag.endswith('style')))
write_svg(static,ASSETS/'profile-light-static.svg')

# Separate, real anchors. The artwork itself is a single link to the website.
buttons=[('website','个人网站',True),('xiaohongshu','小红书',False),('wechat','公众号',False)]
for key,label,primary in buttons:
    shape=outlines[label]
    button=el('svg',viewBox='0 0 240 60',width='240',height='60')
    button.append(el('rect',x='1',y='1',width='238',height='58',rx='29',fill='#5A75FB' if primary else '#F4FBFF',stroke='#5A75FB',**{'stroke-width':'1.4'}))
    button.append(el('ellipse',cx='28',cy='30',rx='10',ry='7',fill='none',stroke='#F4FBFF' if primary else '#5A75FB',transform='rotate(-30 28 30)'))
    button.append(el('path',d=shape['d'],fill='#F4FBFF' if primary else '#37383D',transform=f'translate({120-shape["width"]/2:.3f} {30-shape["height"]/2:.3f})'))
    button.append(el('path',d='M204 36L216 24M205 24H216V35',fill='none',stroke='#F4FBFF' if primary else '#5A75FB',**{'stroke-width':'1.8','stroke-linecap':'round','stroke-linejoin':'round'}))
    write_svg(button,ASSETS/f'link-{key}.svg')

links=config['links']
hero=f'<a href="{links["website"]}"><img src="assets/profile-light.svg" width="100%" alt="FengLi — AI × Product Thinking。等距 AI 工作台与循环滚动的软件、技术名称。点击访问个人网站。" /></a>'
anchors='\n  '.join(f'<a href="{links[key]}"><img src="assets/link-{key}.svg" width="200" alt="{label}'+(' · 阅读文章进入公众号' if key=='wechat' else '')+'" /></a>' for key,label,_ in buttons)
readme=hero+'\n\n<p align="center">\n  '+anchors+'\n</p>\n\n<p align="center"><sub>画面链接至个人网站 · 社交主页请使用独立按钮</sub></p>\n'
(BASE/'README.md').write_text(readme)
preview='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FengLi · GitHub 浅色主页预览</title><style>
*{box-sizing:border-box}body{margin:0;background:#fff;color:#37383d;font:14px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}header{max-width:1100px;margin:28px auto 18px;padding:0 20px;display:flex;gap:18px;align-items:center}header small{color:#777}button{border:1px solid #d1d9e0;background:transparent;color:inherit;border-radius:6px;padding:7px 12px;cursor:pointer}main{max-width:940px;margin:0 auto 36px;border:1px solid #d1d9e0;border-radius:6px;padding:24px}.readme-label{font:12px monospace;margin-bottom:16px;color:#777}article img{max-width:100%;vertical-align:middle}article> a img{display:block}article p{margin:18px 0 0}article p a{display:inline-block;margin:4px}article sub{font-size:11px;color:#737b83}body.dark{background:#0d1117;color:#f0f6fc}body.dark main{border-color:#3d444d}@media(max-width:600px){header{margin:14px auto;flex-wrap:wrap}main{padding:12px;margin:0 8px}article p a img{width:190px}}
</style><header><strong>GitHub README · 浅色版</strong><small>实际 SVG 图片模式</small><button id="theme">切换外围深浅色</button><button id="mobile">手机宽度</button></header><main><div class="readme-label">FengLi-AI / README.md</div><article>'''+readme+'''</article></main><script>document.getElementById('theme').onclick=()=>document.body.classList.toggle('dark');document.getElementById('mobile').onclick=()=>{let m=document.querySelector('main');m.style.maxWidth=m.style.maxWidth?'':'390px'};</script></html>'''
(BASE/'index.html').write_text(preview)
print(json.dumps({'svg_bytes':(ASSETS/'profile-light.svg').stat().st_size,'skills':len(config['skills']),'ticker_period':period,'links':3},ensure_ascii=False))
