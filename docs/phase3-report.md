# Phase 3：首版间接光与渲染优化

保留已验收的家具布局、主机位与 78,338 三角面。新增秋日清晨 07:00、正午 12:00、黄昏 17:20、深夜 00:00 四组 Cycles 间接漫反射，随现有时间滑条连续混合；直接光和阴影仍由网页实时计算。

## 实现与边界

- 独立 LightmapUV 覆盖所有模型网格，保留原贴图 UV。烘焙使用临时细分代理（154,834 面），128 samples，把 CORNER 属性上的 AO / INDIRECT-only DIFFUSE 采样栅格化为贴图。这是插值间接光方案，不是逐像素全屋路径追踪光照。
- AO 2048²，四张间接光各 1024²，5 px 扩边并轻度平滑。线性光以 `sqrt(linear / 4)` 编码，网页解码后混合相邻时段，避免重复乘入材质底色。
- 新图集的 RGBA8 GPU 预算含 mipmaps 约 42.7 MiB；原有贴图另约 3.5 MiB。此数值不包含阴影贴图、帧缓冲和几何缓冲。
- 猫和织物增加克制的 sheen，木桌增加薄涂层；未新增陈设或改变模型姿态。风扇活动部件不套用静态间接光图。
- 静态台灯阴影缓存；静止主机位 115 draws，首次阴影刷新帧实测 205 draws。没有据此声称达到指定设备的 60 FPS。
- 唯一导出脚本启用 Draco，GLB 从带第二套 UV 的未压缩 6,947,040 字节降到约 2.62 MB。解码器从本站加载，不依赖 CDN。

目前只有秋日四时段，尚未完成四季十六组光照、天气、完整交互与事件。现有太阳阴影保持动态；静态间接光与未来移动物件/季节变化需要配套更新。

## 工程与复现

`blender/lofi_room.blend` 是当前源，内嵌原贴图及五张新烘焙图。UV 阶段应用了原模型的修改器；保留 `blender/lofi_room-phase2-approved.blend` 供可编辑造型回溯。材质库为 `blender/materials/phase3-materials.blend`。

```powershell
blender --background --python blender/scripts/build_phase3.py -- --bake --raster-python '<PYTHON_EXECUTABLE>' --save-export
```

脚本从已验收 Phase 2 源重建 UV，保存临时干净场景，再进行代理烘焙；烘焙后重新载入干净场景、打包图集，最后通过 `scripts/export_glb.py` 发布。省略 `--save-export` 会更新烘焙中间数据和网页图集，但不会覆盖正式源或 GLB。仅重建 UV 和打包已有图集时可省略 `--bake`。

## 验证

- `npm run build`：类型检查与生产构建；Vite 仍提示主 JS 大于默认 500 kB 阈值，后续可继续拆分加载。
- `node --experimental-strip-types --test scripts/lightmap.test.ts`：全天权重、相邻混合、午夜与四个时段边界连续性。
- `node scripts/verify_glb.mjs`：三角面预算、所有网格 UV2、35 个挂点、七段钟契约、屏幕贴图、正缩放、图集尺寸与预算。
- `node scripts/validate_gltf.mjs`：0 errors、0 warnings。验证器不解码 Draco，因此另保留未压缩版校验报告；压缩几何也经过真实网页加载验证。非二次幂原贴图产生信息级提示，未隐藏错误或警告。
- 完整后台重建通过，日志见 `blender/phase3-rebuild.log`。最终源打包与唯一导出通过，GLB 为 2,621,920 字节，见 `blender/phase3-publish.log`。MCP 视口仍返回黑图，视觉验收使用实际网页。
- 收尾时桌面 Blender 已切换到另一项目，未修改那个场景；通过独立后台进程 `phase3_publish.py` 打包本项目已保存源，五张光照图均确认内嵌。释放检查返回无活动占用。

[黄昏网页](../blender/renders/phase3-web-dusk.png) · [深夜网页](../blender/renders/phase3-web-night.png) · [桌面近景](../blender/renders/phase3-web-desk.png)
