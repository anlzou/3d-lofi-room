"""Read-only source audit and complete asset inventory."""
import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
dg=bpy.context.evaluated_depsgraph_get();rows=[]
for o in sorted(bpy.context.scene.objects,key=lambda x:x.name):
    tri=0
    if o.type=='MESH':
        ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();tri=len(me.loop_triangles);ev.to_mesh_clear()
    assert min(o.scale)>0,o.name
    if o.type=='LIGHT':assert 'LIGHTS' in [c.name for c in o.users_collection],o.name
    if o.type=='CAMERA':assert 'CAMERAS' in [c.name for c in o.users_collection],o.name
    priority='P0' if o.name.startswith(('Mac_','Crt_','Fan_','Cat_','Phone_','PS1_','GameConsole','Game_Controller','EMIT_screen_mac','EMIT_screen_crt','EMIT_clock','Window_','Room_','Wall_')) else 'P1'
    rows.append({'name':o.name,'type':o.type,'priority':priority,'triangles':tri,'collections':[c.name for c in o.users_collection],'parent':o.parent.name if o.parent else None,'phase':2,'nextPhase':4 if o.type=='EMPTY' or o.name.startswith(('ANIM_','INT_','SOCKET_','SEASON_')) else 3})
report={'source':bpy.data.filepath,'triangles':sum(r['triangles'] for r in rows),'objects':len(rows),'negativeScales':0,'assets':rows}
assert report['triangles']<80000
(ROOT/'docs/phase2-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
p=ROOT/'docs/asset-list.md';backup=ROOT/'docs/asset-list-phase15.md'
if not backup.exists():backup.write_text(p.read_text(encoding='utf-8'),encoding='utf-8')
header='''# Phase 2 定稿资产清单

保持 Phase 1.5 家具布局和主机位。当前造型、首版材质与原创印刷/屏幕画面已完成；Phase 3 处理烘焙和进一步优化，Phase 4 处理完整交互、天气与事件。

| 区域 | 定稿内容 | 优先级 | 状态 / 后续 |
| --- | --- | --- | --- |
| 桌面主角 | 米色 Compact Macintosh、凸面玻璃、软驱、提手、半透明键鼠及简化电路 | P0 | 2 完成；屏幕系统 4 |
| 桌面配件 | 3×4 电话、同向听筒、卷线、Modem、音箱、机械翻页钟、台历、杯碗、笔筒、便签、随身听、耳机、软盘、两张裸碟、两片磁带 | P1 | 2 完成 |
| 桌下 | 主机、排插、插头、5 根垂落设备线 | P1 | 2 完成 |
| 电视区 | CRT 原创像素画、初代 PS 外形主机/手柄/连线、VCR、DVD 叠放、录像带、DVD 盒、遥控器 | P0 | 2 完成；换台/按键 4 |
| 窗台 | 两个机甲摆件、小仙人球、盆栽、小鸟、带花茎的花、风铃与可动百叶 | P1 | 2 完成；风/雨/花瓣 4 |
| 右墙 | 三张原创套色网点海报、软木板照片票根、墙钟、长架、异尺寸书、海陆地球仪 | P1 | 2 完成 |
| 右侧低书架 | 两个坐姿 Fumo、书与收纳盒、滑板、熔岩灯 | P1 | 2 完成 |
| 床区 | 压痕枕头、抱枕、起伏被子、漫画、床下收纳、成对棉拖鞋 | P1 | 2 完成 |
| 床头柜 | 上下双抽屉、拉开约 18 cm 的上抽屉、磁带与相片收纳、小相框、灯、红光七段数字钟 | P0 | 2 完成；数字钟已随房间时间更新 |
| 地毯 | 圆垫睡姿橘猫、6 块积木、Game Boy 与半抽卡带、少量杂志 | P0 | 2 完成；猫动作与互动 4 |
| 地板边缘 | 有茎叶的落地植物、唱片箱、垃圾桶与两枚漏投纸团 | P1 | 2 完成 |
| 季节摆件 | 双层网罩风扇、发热管暖炉、完整水壶、春花、椅背毯、围巾、冷饮 | P1 | 2 完成；风扇慢转，其余季节切换 4 |
| 窗外 | 有干枝的树、电线杆与两根线、围栏、低细节房屋剪影 | P1 | 保留布局；2 材质完成 |
| 灯具与挂点 | 台灯、顶灯拉线、灯串路径、熔岩灯、四个猫位、蒸汽/天气挂点、猫头 ZZZ 挂点 | P1 | 2 完成；仅猫 ZZZ 试运行动效 |

本轮不增加第三个机甲、声卡和额外垃圾袋；以两只 Fumo 与电视柜设备的可读性优先。移除了旧的抽象手办和重复灰色积木，用对应成品替换。未增加清单之外的新陈设。窗外延续既有三栋简化房屋，不新增街区。

以下逐对象索引由保存源场景自动生成。灯光和相机仅用于 Blender 检查，不进入 GLB。P0 为近景主角与空间骨架，P1 为配景；不可见挂点继续保留。

'''
header+=f"源场景：{report['objects']} 个对象，{report['triangles']:,} 三角面，无负缩放。\n\n"
header+='| 对象名 | 优先级 | 当前阶段 | 下一阶段 | 类型 | 三角面 |\n| --- | --- | --- | --- | --- | --- |\n'
p.write_text(header+'\n'.join(f"| `{r['name']}` | {r['priority']} | 2 | {r['nextPhase']} | {r['type']} | {r['triangles']} |" for r in rows)+'\n',encoding='utf-8')
print('PHASE2_AUDIT_OK',json.dumps({k:v for k,v in report.items() if k!='assets'}))
