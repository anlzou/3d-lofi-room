"""Render acceptance details from saved source in a separate background process."""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
assert bpy.app.background
p=ROOT/'blender/scripts/render_phase2.py'
for mode in ['tv','desk','cat']:
    exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),{'RENDER_MODE':mode})
