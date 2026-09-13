# Phase 1 · 灰模与端到端验证

日期：2026-09-05。阶段已完成，尚未进入资产精修。

## 产物

- blender/lofi_room.blend：源工程，标准五个 Collections。
- blender/scripts/build_scene.py：确定性灰模构建；空场景保护；修改器后三角面断言。
- blender/scripts/render_previews.py：三个 Eevee 构图候选。
- public/models/demo.glb：由 scripts/export_glb.py 生成，1,524,284 bytes。
- blender/renders/phase1-{room,desk,window}-2026-09-05.png。
- 网页：时刻滑块、加速播放/暂停、三机位、OrbitControls、全屏、隐藏 UI 与键盘恢复；后台取消 RAF。

## 实际检查

- Blender 5.2.1 LTS，经 MCP 两轮实体视口检查；树冠下移 0.9 米改善窗口视线。
- 应用修改器后 21,592 三角面，140 网格；全部对象无负缩放。
- .blend 保存并回读 filepath；GLB SIZE/MAGIC 断言通过，输出 EXPORT_OK。
- 三张 Eevee 渲染已打开检查：推荐 Room 全景，桌面近景用于设备精修；Window 为中景备选。
- 浏览器确认 GLB 加载；滑块到午夜后时钟和灯光更新；播放推进时间；机位切换与隐藏/恢复 UI 均工作。
- 初次浏览器报告 PCFSoftShadowMap 弃用警告，已改为 PCFShadowMap。
- npm run build（含严格 TypeScript 检查）通过。Three.js 主包约 624 kB，构建仍有体积建议，后续优化阶段处理。

## 取舍与待办

当前使用统一默认 Principled 灰材质，树为体块，设备屏幕无内容。这里验收比例、构图和管线，不代表最终美术效果。夜景保留环境补光，实时台灯尚不投影。未完成 lightmap、压缩、四季、天气、音频、事件、长期性能验收。

默认全景最适合长时间观看；桌面近景的前景天线之后可随构图精修调整。下一阶段第一批精修桌面、Mac、键鼠、CRT 与窗框，建立正式暖色材质与屏幕内容，再加入用户要求的其他生活细节。
