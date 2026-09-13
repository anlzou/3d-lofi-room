"""Create an engineering contact sheet: numbered plan + complete, exact object registry."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,math,textwrap
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'docs/scene-manifest.json').read_text(encoding='utf-8'))
W,H=4800,5500
im=Image.new('RGB',(W,H),'#f0ede6');d=ImageDraw.Draw(im)
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/consola.ttf',n)
sans=lambda n:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
d.text((90,55),'LOFI ROOM / PHASE 1.5',font=sans(65),fill='#262a2c')
d.text((90,140),'LAYOUT REGISTER   |   2026-09-05   |   METRES   |   ALL SEASON PLACEHOLDERS VISIBLE',font=font(26),fill='#6c6b64')
plan=Image.open(ROOT/'blender/renders/phase15-plan-2026-09-05.png').convert('RGB').resize((2380,2380))
im.paste(plan,(60,220))
placed=[]
for i,g in enumerate(data['groups'],1):
    x=60+g['plan_uv'][0]*2380;y=220+g['plan_uv'][1]*2380
    lx,ly=x,y
    for radius in range(0,420,30):
        found=False
        for k in range(16):
            a=k*math.tau/16;xx=x+math.cos(a)*radius;yy=y+math.sin(a)*radius
            if 95<xx<2385 and 245<yy<2570 and all((xx-px)**2+(yy-py)**2>70**2 for px,py in placed):
                lx,ly=xx,yy;found=True;break
        if found:break
    placed.append((lx,ly))
    d.line((x,y,lx,ly),fill='#f8d395',width=3)
    d.ellipse((x-4,y-4,x+4,y+4),fill='#f8d395')
    d.ellipse((lx-25,ly-25,lx+25,ly+25),fill='#242c32',outline='#f8d395',width=3)
    label=f'{i:02}';b=d.textbbox((0,0),label,font=font(26));d.text((lx-(b[2]-b[0])/2,ly-17),label,font=font(26),fill='#fff1d6')
    ly2=245+(i-1)*64
    d.text((2510,ly2),f'{i:02}  {g["key"]}',font=font(27),fill='#a56a35')
    d.text((2800,ly2),g['label'],font=sans(25),fill='#282e31')
    d.text((2800,ly2+30),f'{g["priority"]} / layout 1.5 / refinement 2 / runtime 4 / {g["zone"]}',font=font(18),fill='#72756d')
d.text((2510,2540),'Ceiling hidden for plan only. All exact names and XY below.',font=font(23),fill='#5a635f')
d.line((80,2670,4720,2670),fill='#b4b4aa',width=3)
d.text((90,2700),f'COMPLETE OBJECT INDEX / {len(data["objects"])} OBJECTS    [world X,Y in metres]',font=font(34),fill='#242c32')
rows=math.ceil(len(data['objects'])/6)
for idx,o in enumerate(data['objects']):
    col=idx//rows;row=idx%rows;x=85+col*787;y=2770+row*31
    n=o['name'];xy=f'{o["position"][0]:+.2f},{o["position"][1]:+.2f}'
    f=font(20 if len(n)<43 else 17)
    color='#945a2f' if n.split('_')[0] in ['INT','ANIM','EMIT','SOCKET','SEASON','LIGHT'] else '#353b3d'
    d.text((x,y),n,font=f,fill=color)
    d.text((x+626,y),xy,font=font(16),fill='#7a817c')
d.text((90,5390),'Source: blender/lofi_room.blend | Full machine-readable registry: docs/scene-manifest.json',font=font(24),fill='#687069')
out=ROOT/'blender/renders/phase15-plan-annotated-2026-09-05.png'
im.save(out)
im.resize((1200,1375)).save(ROOT/'blender/renders/phase15-plan-overview.png')
print('ANNOTATED_PLAN_OK',out,len(data['objects']))

# Final agreed scope; per-object rows retain priority and subsequent production phase.
lines=['# Phase 1.5 最终布局资产清单','',
'本清单按当前已摆放灰模定稿。Phase 1.5 已建立位置与占位；Phase 2 精修造型材质；Phase 3 UV/烘焙；Phase 4 实现动画交互。灰模中季节物件同时显示以便检查占地，运行时功能尚未开启。','',
'| 编号 | 资产组 | 优先级 | 布局 | 精修 | 动效/交互 |','| --- | --- | --- | --- | --- | --- |']
for i,g in enumerate(data['groups'],1):lines.append(f'| {i:02} | {g["label"]} | {g["priority"]} | 1.5 完成 | 2 | 4 |')
lines+=['','## 明确取舍','',
'- 选落地植物，未增鱼缸；选滑板，未增吉他；选熔岩灯，未增霓虹牌；选泡面碗，未增零食袋，均为本轮提示词允许的二选一。',
'- 海报、照片、票根与便签先共用灰色纸片语言，图案和文字在 Phase 2 精修；没有因此删除位置。',
'- 暖炉是电热器灰模，冬季猫窝使用 SOCKET_cat_heater；所有灯具位置已摆放，夜景只开启台灯和屏幕。',
'- 补充了唱片收纳箱、床下收纳盒、地毯翘边，强化使用痕迹。',
'- 未将原始模型合并或删掉。网页仅将不可交互的静态网格按材质临时合批，GLB 保留名称和挂点。',
'','## 精确对象名索引','',
'下表逐项覆盖源场景全部对象（包括不可见挂点、预览灯光与相机）。P0 为房间/英雄设备/窗外主要骨架，其余为 P1；灯光相机仅预览，不随 GLB 导出。','',
'| 对象名 | 优先级 | 当前阶段 | 下一阶段 | 类型 |','| --- | --- | --- | --- | --- |']
p0=set()
for g in data['groups']:
    if g['priority']=='P0':p0.update(g['objects'])
for o in data['objects']:
    name=o['name'];priority='P0' if name in p0 or name.startswith(('Wall_','Floor_','Room_','Window_','Tree_','Exterior_','Mac_','Crt_','Desk_')) else 'P1'
    nxt='4 接入' if o['type']=='EMPTY' or name.startswith(('INT_','ANIM_','SOCKET_','LIGHT_')) else '2 精修 / 3 UV烘焙'
    if o['type'] in ['LIGHT','CAMERA']:nxt='预览配置，不导出'
    lines.append(f'| `{name}` | {priority} | 1.5 已摆放 | {nxt} | {o["type"]} |')
(ROOT/'docs/asset-list.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
