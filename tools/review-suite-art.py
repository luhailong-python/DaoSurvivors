"""Build review contact sheets; this is layout/compositing, not AI art generation."""
import json
import html
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
inventory = json.loads((ROOT / 'docs/ui-suite/UI_COVERAGE.json').read_text(encoding='utf-8-sig'))
out = ROOT / 'designs/ui-suite/review'
out.mkdir(parents=True, exist_ok=True)
font = ImageFont.truetype(str(ROOT / 'art/fonts/NotoSansSC-Regular.otf'), 20)
for start in range(0, len(inventory['screens']), 8):
    rows = inventory['screens'][start:start+8]
    sheet = Image.new('RGB', (1920, 2320), '#f5f0dd')
    draw = ImageDraw.Draw(sheet)
    for i, row in enumerate(rows):
        x, y = i % 2 * 960, i // 2 * 580
        with Image.open(ROOT / row['screenPath']) as im:
            sheet.paste(im.convert('RGB').resize((960, 540), Image.Resampling.LANCZOS), (x, y))
        draw.text((x+12,y+546), row['id']+' '+row['interface']+' / '+row['state'], font=font, fill='#25523a')
    sheet.save(out / f'contact-{start+1:02d}-{start+len(rows):02d}.jpg', quality=92)
overview_ids=['04-main-menu','05-character-select','16-powerup-overview','25-battle-hud','29-upgrade-new','34-treasure-five','40-victory','51-control-states']
# Compact8-screen overview at four columns/two rows.
compact=Image.new('RGB',(3840,1160),'#f5f0dd')
for i,key in enumerate(overview_ids):
    row=next(r for r in inventory['screens'] if r['id']==key);x,y=i%4*960,i//4*580
    with Image.open(ROOT/row['screenPath']) as im:compact.paste(im.convert('RGB').resize((960,540),Image.Resampling.LANCZOS),(x,y))
    ImageDraw.Draw(compact).text((x+15,y+548),row['interface']+' / '+row['state'],font=font,fill='#25523a')
compact.save(ROOT/'designs/ui-suite/overview.jpg',quality=94)
cards=[]
for row in inventory['screens']:
    key=html.escape(row['id']);label=html.escape(row['interface']+' · '+row['state'])
    cards.append(f'<article><a href="screens/{key}.png"><img loading="lazy" src="screens/{key}.png" alt="{label}"></a><div><small>{key} · {html.escape(row["system"])}</small><h2>{label}</h2><a href="preview/?view={key}">查看状态预览 →</a></div></article>')
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>道途幸存者 · UI美术全览</title><style>@font-face{font-family:Noto;src:url('../../art/fonts/NotoSansSC-Regular.otf')}*{box-sizing:border-box}body{margin:0;padding:30px;background:#153d31;color:#f7eed4;font-family:Noto,sans-serif}header{max-width:1800px;margin:0 auto 28px}h1{font-size:32px;font-weight:500;letter-spacing:4px}header p{color:#bdc9ac;font-size:15px;line-height:1.8}nav{display:flex;gap:20px}a{color:#d6c28b}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:24px;max-width:1800px;margin:auto}article{background:#f5efdc;color:#315b40;border:1px solid #c1ac6f;border-radius:12px;overflow:hidden}img{display:block;width:100%;aspect-ratio:16/9;object-fit:contain}article>div{padding:14px 18px 20px}small{font-size:12px;color:#808467}h2{font-size:18px;font-weight:500;margin:8px 0 14px}article a{font-size:14px;color:#54734d}</style><header><h1>道途幸存者 · UI 美术全览</h1><p>52张整屏／状态／流程图 · 临时名称 · 玉绿、纸绢与暖金的道家Q版手绘方向<br>UI设计预览；Unity接入留待下一阶段。角色、敌人、动画等非UI美术按整款游戏总账另行验收。</p><nav><a href="preview/?view=04-main-menu">进入状态预览</a><a href="../../docs/ui-suite/UI_COVERAGE.md">功能与资源总清单</a><a href="../../docs/ui-suite/ACCEPTANCE.md">UI验收记录</a></nav></header><main>'''+''.join(cards)+'</main></html>'
(ROOT/'designs/ui-suite/gallery.html').write_text(page,encoding='utf-8')
print(json.dumps({'contactSheets':len(list(out.glob('contact-*.jpg'))),'screens':len(inventory['screens']),'gallery':'designs/ui-suite/gallery.html','overview':'designs/ui-suite/overview.jpg'}))
