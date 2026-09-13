# 给 Codex 的提示词(复制即用)

> 用法：先打开 Blender，再在本项目文件夹打开 Codex，
> 粘贴下面的提示词。

---

## ① 首次建模(开工提示词)

```text
这个项目是做一个 Lofi 风格的 3D 房间网页 Demo。环境已经全部配置好:
blender_mcp 已在 Codex 里注册,Blender 打开后桥接自动启动,不需要你安装任何东西。

开工前:
1. 先读取本项目的 AGENTS.md,严格遵守里面的流程、命名和 bpy 陷阱注意事项。
2. 确认 Blender 正在运行(用 blender_mcp 的 list_blender_instances 检查;
   如果没开,提醒我打开 Blender)。
3. Blender 当前场景可能属于其他项目,先执行
   bpy.ops.wm.read_homefile(use_empty=True) 新建空场景,
   按约定创建 ROOM_SHELL / FURNITURE / PROPS / LIGHTS / CAMERAS Collections。

任务:在 Blender 中建一个 Lofi 风格的温馨小房间(窗口夕阳光、书桌、床、
地毯、台灯、绿植、耳机等,风格温暖低饱和)。要求:
- 严格按 AGENTS.md 的流程:检查场景 → bpy 建模 → viewport 截图检查 →
  修改 → 再截图,多轮迭代直到构图和比例合理
- 面向实时渲染:总面数 < 80k,硬表面用 Bevel Modifier,法线正确,无负缩放
- 材质用 Principled BSDF(Metal/Rough + Emission 做灯光/屏幕发光),
  命名以 MAT_ 开头,对象语义化命名
- 灯光和相机放进 LIGHTS / CAMERAS Collection(导出会被自动排除)
- 保存为 blender/lofi_room.blend 并回读 filepath 确认
- 用 exec(open(r'<PROJECT_ROOT>\scripts\export_glb.py',
  encoding='utf-8').read()) 导出 GLB,确认输出 EXPORT_OK
- 运行 pnpm dev,在浏览器里打开页面检查模型渲染、Console 无错误、
  材质和光影正常;不满意就回 Blender 改,重新导出,再刷新验证
- 全程只连 localhost,不要动 Blender 里其他项目的文件
- 结束时调用 release_blender_instance 释放控制权
```

---

## ② 日常迭代(后续修改模型)

```text
读取 AGENTS.md 后按标准流程修改模型:<具体需求,比如"给房间加一扇
落地窗,窗外做渐变黄昏天空色">。全程用 viewport 截图自查,改完保存
blender/lofi_room.blend,执行 scripts/export_glb.py 导出,刷新网页
验证效果,直到满意。结束释放 Blender 控制权。
```

---

## ③ 只想检查连接(最小验证)

```text
用 blender_mcp 检查当前 Blender:list_blender_instances + get_scene_info,
告诉我 Blender 版本、当前场景和对象列表。只读,不要改任何东西。
```
