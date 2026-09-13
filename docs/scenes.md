# 场景与目录约定

项目名 **3d-lofi-room**，当前只有 `lofi-room` 一个场景（界面上的「四季房间 · Lofi Room」）。这份文档说明下一个场景该怎么接进来，让运行时不因为场景变多而变成一堆特例。

## 现状（单场景）

| 属于场景的东西 | 位置 |
| --- | --- |
| Blender 源工程 | `blender/lofi_room.blend` |
| 导出产物 | `public/models/demo.glb` |
| 光照图集 | `public/lighting/`（ao + night/dawn/noon/dusk） |
| 机位预设 | `src/main.ts` 的 `presets`（room / desk / window / tv） |
| 场景文档 | `docs/art-direction.md`、`docs/asset-list*.md`、各 phase 报告 |

属于**运行时**（与场景无关）的部分：`src/world-state.ts`（状态与作息）、`src/loading.ts`（加载进度）、`src/perf-governor.ts`（自适应分辨率）、`src/sun-shadow.ts`（阴影节流）、`src/light-fade.ts`（灯光缓动）、`src/console-drag.ts`（控制面板）、`src/style.css`、`index.html`。

## 加第二个场景时（尚未实施）

1. **模型与烘焙**：`blender/<scene>.blend` → `scripts/export_glb.py`（导出脚本已从 `bpy.data.filepath` 自动定位项目根）→ `public/models/<scene>.glb`；光照图集放 `public/lighting/<scene>/`。
2. **场景清单**：新建 `src/scenes.ts`，每个场景一条记录：
   ```ts
   export interface Scene {
     id: string;            // 出现在地址栏与 localStorage
     label: string;         // 选择器上显示的名字
     model: string;         // public/models/ 下的文件名
     lighting: string;      // public/lighting/ 下的目录
     presets: Record<string, { position: [number, number, number]; target: [number, number, number]; fov: number }>;
     // 该场景里能点的东西、能开的灯、作息里有哪些设备，都放这里
   }
   ```
3. **运行时改造**：`main.ts` 里现在写死的三样东西要改成从场景记录读取——`presets`、灯光锚点（`LIGHT_*`）、可交互对象名（`INT_*` / `EMIT_*`）。`WorldState` 增加 `scene: string`，`restoreState` 校验它；切换场景时重建 `roomLife` / `touchFeedback` 并按新场景的机位重置相机。
4. **加载**：`loading.ts` 的标称体积按场景记录给（现在写的是 lofi-room 的 2.76 MB / 2.62 MB）；`<link rel="preload">` 需要随场景变化，要么在运行时插入，要么两个场景都预加载（不推荐）。
5. **文档**：`docs/scenes/<scene>.md` 放该场景的美术与资产说明，根 `docs/` 只留跨场景的契约（本文件、`naming.md`、`state-machine.md`、`desktop.md`、`music.md`）。

## 现在不做的事

在第二个场景真正落地前不动目录结构：`src/` 保持扁平，模型仍在 `public/models/demo.glb`。过早抽公共层会把只有一份的实现拆散，反而更难改。
