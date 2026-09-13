# 目录与资产契约

项目名 3d-lofi-room（包名 `3d-lofi-room`，打包产物 `3D-Lofi-Room-Portable-<版本>.exe`）；场景名仍是「慢慢房间 · Lofi Room」。本项目 AGENTS.md 的目录、命名与唯一导出入口优先于参考提示词的示例目录。

| 路径 | 责任 |
| --- | --- |
| blender/lofi_room.blend | 唯一模型源工程（场景 `lofi-room`），Phase 1 生成 |
| blender/scripts/ | 可复现的 bpy 构建、材质与烘焙脚本 |
| blender/renders/ | 分阶段预览、候选图与验收截图（仅 README/文档引用的那些仍在线） |
| blender/lighting/ | Cycles 烘焙中间数据（`.npy`），供 `scripts/raster_lightmaps.py` 重出图集 |
| scripts/export_glb.py | 唯一 GLB 导出入口 |
| public/models/demo.glb | 导出产物，Phase 1 生成 |
| public/lighting/ | 运行时光照图集（ao + 四时段），由烘焙数据栅格化而来 |
| src/ | Vite + TypeScript + Three.js 运行时 |
| docs/ | 美术、资产与状态契约；阶段报告保留作过程证据 |

多场景的目录约定见 [`scenes.md`](scenes.md)。

## 可清理候选（尚未删除）

这些文件已不再被运行时引用，但删之前想清楚：本目录**不是 git 仓库**，删除不可恢复。

| 候选 | 体积 | 说明 |
| --- | --- | --- |
| `dist/` | 20 MB | Vite 构建产物，`pnpm build` 可随时重建（已在 `.gitignore`） |
| `blender/*-backup.blend`、`*-before-*.blend`、`phase3-prepared-cache.blend` | 18.4 MB | 模型的历史快照，是当前唯一的版本历史 |
| `blender/renders/` 中未被引用的图 | 约 20 MB | 29 张里 14 张被 README/文档引用 |
| `blender/lighting/*.npy` | 27 MB | 重出图集要用；删了就得重跑 Cycles 烘焙 |
| `docs/phase*-report.md`、`*-manifest.json`、`asset-list*.md` | 约 0.7 MB | 阶段过程记录，不影响运行 |
| `scripts/annotate_plan.py`、`scripts/draw_screen_art.py` | 20 KB | 一次性产物脚本，已无文档引用 |

Collections 固定 ROOM_SHELL / FURNITURE / PROPS / LIGHTS / CAMERAS。窗外模型放 ROOM_SHELL 下的 Exterior 子集合。灯光和相机仅放对应专用集合，导出排除。

静态对象采用语义化 PascalCase。按 Phase 1.5 用户明确要求，交互、可动、发光、挂点、季节对象使用 INT_ / ANIM_ / EMIT_ / SOCKET_ / SEASON_ 前缀；LIGHT_ 表示网页光源位置 Empty，实际 Blender 灯光仍只在 LIGHTS 集合。

运行时角色使用 Blender 自定义属性（glTF extras，后续在唯一导出脚本启用 export_extras）描述：role = interactive / animated / emissive / socket / static / collider；interaction = lamp / tv / mac / window；season = all / spring / summer / autumn / winter。父级对象可交互，子部件独立枢轴；屏幕与特效挂点保持独立名称。支持多角色时用 roles 字符串数组的 JSON 字符串并在加载入口解析。

唯一导出器现已选择 Mesh 和 Empty，并启用 export_extras，保留枢轴及挂点；排除 LIGHTS / CAMERAS。`node scripts/verify_glb.mjs` 检查命名、屏幕发光贴图、正缩放、三角面预算和相机灯光排除。

构建脚本需从空场景确定性重建，并保留随机种子。未生成模型前不创建空 .blend 或伪造 GLB。每次模型修改必须按 AGENTS.md 完成截图、保存、导出、浏览器验证及释放实例。
