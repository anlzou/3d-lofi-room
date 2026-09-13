import * as THREE from 'three';
import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';
import { clone as cloneRig } from 'three/addons/utils/SkeletonUtils.js';

// Warrior.fbx replaces the two window-sill robots (INT_mecha_A / INT_mecha_B). It is not part of
// the Blender → GLB pipeline the room's own content follows (see AGENTS.md): it is a third-party
// asset that arrives as a runtime import under public/models, and the mecha it stands in for are
// only hidden. The layout, the lightmaps and demo.glb are all left exactly as they were, so a
// rebuild of the model never has to know about this file.
const anchors = ['INT_mecha_A', 'INT_mecha_B'] as const;
const height = .3;                                    // metres: the mecha it replaces are 25 cm tall
const facing = 0;                                     // its own forward already looks into the room
// Its own clip names, in the language the room speaks. `idle` is the resting state; every other
// clip is played once and then falls back to it.
const clipLabels: Record<string, string> = {
  idle: '待机', atk01: '战士挥出一剑', hurt: '战士挨了一下', win: '战士举起武器', yunxuan: '战士有点晕',
  shuimian: '战士睡着了', enter: '战士亮了个相', mv_tar21: '战士走了两步',
};

export interface Warriors {
  /** Hand the rig the next clip when one of these names (a click's object chain) is its root. */
  play(names: string[]): string | undefined;
  /** Playback rate for every rig, straight from the console's speed slider. */
  setSpeed(speed: number): void;
  update(dt: number): void;
}

interface Rig { root: THREE.Group; mixer: THREE.AnimationMixer; clips: THREE.AnimationAction[]; next: number }

export async function loadWarriors(root: THREE.Object3D, scene: THREE.Scene, url: string): Promise<Warriors | undefined> {
  const loader = new FBXLoader();
  // The atlas is a sibling of the FBX rather than embedded in it, so the loader has to be told
  // where to look: without this the model arrives with no texture at all.
  loader.setResourcePath(url.slice(0, url.lastIndexOf('/') + 1));
  const source = await loader.loadAsync(url);
  const bounds = new THREE.Box3().setFromObject(source);
  // The model is authored 73 cm tall with its feet on its own origin, so one scale factor and the
  // origin it already has are enough to stand it on the sill.
  const scale = height / Math.max(.0001, bounds.max.y - bounds.min.y);
  source.traverse(object => {
    if (!(object instanceof THREE.Mesh)) return;
    const materials = Array.isArray(object.material) ? object.material : [object.material];
    for (const material of materials) {
      const map = (material as THREE.MeshPhongMaterial).map;
      if (map) map.colorSpace = THREE.SRGBColorSpace;
    }
  });
  const rigs: Rig[] = [];
  for (const [index, anchorName] of anchors.entries()) {
    const anchor = root.getObjectByName(anchorName);
    if (!anchor) continue;
    const place = anchor.getWorldPosition(new THREE.Vector3());
    const group = new THREE.Group();
    group.name = `Warrior_${String.fromCharCode(65 + index)}`;
    const model = cloneRig(source) as THREE.Object3D;
    model.scale.setScalar(scale);
    model.rotation.y = facing;
    group.add(model);
    group.position.copy(place);
    scene.add(group);
    anchor.visible = false;
    model.traverse(o => {
      if (o instanceof THREE.Mesh) {
        o.castShadow = true; o.receiveShadow = true;
        // A skinned mesh's rest bounding box is smaller than the poses it will strike, and a culled
        // warrior mid-swing would blink out of the room.
        o.frustumCulled = false;
      }
    });
    const mixer = new THREE.AnimationMixer(model);
    const clips = source.animations.map(clip => {
      const action = mixer.clipAction(clip, model);
      action.setLoop(THREE.LoopRepeat, Infinity);
      return action;
    });
    // It opens on the model's own rest pose and every clip loops, so the warriors are never still;
    // `next` starts one past that pose, because a first click should be a move you can see.
    clips[0]?.play();
    rigs.push({ root: group, mixer, clips, next: 1 });
  }
  if (!rigs.length) return undefined;
  return {
    play(names) {
      const rig = rigs.find(candidate => names.includes(candidate.root.name));
      if (!rig || !rig.clips.length) return undefined;
      const action = rig.clips[rig.next % rig.clips.length];
      rig.next += 1;
      for (const entry of rig.clips) if (entry !== action) entry.fadeOut(.25);
      action.reset();
      action.setLoop(THREE.LoopRepeat, Infinity);
      action.fadeIn(.25).play();
      return clipLabels[action.getClip().name] ?? '战士动了动';
    },
    setSpeed(speed) { for (const rig of rigs) rig.mixer.timeScale = speed; },
    update(dt) { for (const rig of rigs) rig.mixer.update(dt); },
  };
}
