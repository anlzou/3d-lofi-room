# Blender 构建脚本

build_scene.py 已实现：按 AGENTS.md 从空场景生成标准 Collections、灰模与三个候选相机。render_previews.py 在保存 .blend 后输出三张 Eevee 预览。Phase 2 分离 materials.py 等可复用模块，Phase 3 增加 bake.py。

所有导出均调用项目根目录 scripts/export_glb.py，不在此复制导出逻辑。CLI 参数 --save-export 可从空场景重建、保存和导出；实时建模仍按规则分步截图、保存和导出。
