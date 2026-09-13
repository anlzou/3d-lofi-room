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
// Its own clip names, in the language the room speaks. The names are the exporter's, not ours, so
// what each one actually does is written down here (and in docs/warrior-scene.md): `atk01` throws
// the strike, `hurt` is the one that goes down, and the two chase clips are `enter` / `mv_tar21`.
const clipLabels: Record<string, string> = {
  idle: '战士待机', atk01: '战士出手攻击', hurt: '战士被打飞', win: '战士胜利挑衅',
  yunxuan: '战士晕眩', shuimian: '战士睡着了', enter: '战士追了上去', mv_tar21: '战士追了上去',
};
// Clips that are cycles rather than one-shots: the chase and the sleep loop while they are held,
// everything else plays through once and holds its last pose (a taunt or a knockback that restarts
// itself reads as a glitch).
const looping = new Set(['idle', 'enter', 'mv_tar21', 'shuimian']);

// --- 窗台对打: the scripted duel from docs/warrior-scene.md ----------------------------
// Both warriors keep their spot on the sill — the scene only turns them and swaps clips, so it
// reads as a fight at the window without anything drifting into the room.
//
// Facing is a script decision, not a clip's: every clip turns its own root towards the room as it
// plays, so the yaw has to live on a wrapper *around* the animated model or the animation simply
// overwrites it. Yaw is measured from "facing into the room" (0); the two stand side by side, so
// facing each other is ±90°, and chasing the other's back is both of them turned the same way.
const HOME = 0, MEET_A = Math.PI / 2, MEET_B = -Math.PI / 2;
// Settle time for a 90° turn: ζ ≈ 0.75 gives the small overshoot the script asks for, and the
// stiffness puts the turn at roughly 0.45 s — but only if the spring is stepped in small slices,
// which is what half a slow frame's dt would not be.
const TURN_STIFFNESS = 140, TURN_DAMPING = 17, TURN_BLEND = .25, TURN_SUBSTEP = 1 / 60;
// How far the follower's turn trails the leader's in a chase: enough that they are never quite in
// step, which is what reads as one of them running after the other.
const CHASE_LAG = .22;
type Aim = 'room' | 'each-other' | 'behind';
// Facing is kept per warrior and is sticky, so a beat can turn just one of them: the plain string
// turns both, the object form turns only the side it names and leaves the other as it was. That is
// how 小骷鬼 stays asleep facing the room while 小鬼骷 turns to look at it — and only comes round
// once it has been hit.
type AimCue = Aim | { a?: Aim; b?: Aim };
interface Beat {
  at: number;                                        // seconds into the scene
  a?: { clip: string };
  b?: { clip: string };
  // Sticky: a beat that does not say how to face keeps the way the previous one set. `a` is the
  // left warrior (小鬼骷), `b` the right one (小骷鬼).
  aim?: AimCue;
  chase?: { leader: 'a' | 'b'; amp: number; period: number };
  label: string;
}
// Every clip plays at its own speed here; the console's 战士动作速度 slider is the one place that
// makes the whole thing faster or slower (see setSpeed).
//
// A script is a list of beats and a length, nothing more — the same pair, the same clips, the same
// facing rules — so the console's dropdown just picks which one runs.
export interface Script { name: string; label: string; length: number; beats: Beat[] }
// The cast, by the names the room calls them. Rig 0 stands on the left, on the desk-lamp side
// (anchor INT_mecha_A, x ≈ −1.23); rig 1 stands on the right (INT_mecha_B, x ≈ −0.57). Script
// titles and beat labels are written with these two constants, so the status line names who is
// doing what instead of saying 左/右 — and there is one place to change if they get renamed.
const LEFTY = '小鬼骷', RIGHTY = '小骷鬼';
export const scripts: Script[] = [
  {
    name: 'duel', label: `${LEFTY} vs ${RIGHTY}`, length: 16,
    beats: [
      { at: 0, a: { clip: 'idle' }, b: { clip: 'idle' }, aim: 'room', label: `捉弄 · 两位小战士就位` },
      { at: 1.6, aim: 'each-other', label: `捉弄 · 转身面对面` },
      { at: 3.0, a: { clip: 'win' }, label: `捉弄 · ${LEFTY}挑衅` },
      { at: 5.9, a: { clip: 'atk01' }, label: `捉弄 · ${LEFTY}出手` },
      { at: 6.8, a: { clip: 'idle' }, b: { clip: 'hurt' }, label: `捉弄 · ${RIGHTY}被打飞` },
      { at: 7.8, a: { clip: 'enter' }, b: { clip: 'mv_tar21' }, aim: 'behind', chase: { leader: 'b', amp: .3, period: 2.2 }, label: `捉弄 · ${RIGHTY}带路，${LEFTY}追着后背跑` },
      { at: 9.8, a: { clip: 'mv_tar21' }, b: { clip: 'enter' }, chase: { leader: 'a', amp: .3, period: 2.2 }, label: `捉弄 · 换手，${LEFTY}带路` },
      { at: 11.8, a: { clip: 'atk01' }, b: { clip: 'hurt' }, aim: 'each-other', chase: undefined, label: `捉弄 · ${RIGHTY}又挨一下` },
      { at: 12.9, a: { clip: 'win' }, b: { clip: 'yunxuan' }, label: `捉弄 · ${RIGHTY}晕在原地` },
      { at: 14.2, a: { clip: 'idle' }, b: { clip: 'shuimian' }, label: `捉弄 · ${RIGHTY}睡着了` },
    ],
  },
  {
    name: 'wake', label: `赖床的${RIGHTY}`, length: 16,
    beats: [
      { at: 0, a: { clip: 'idle' }, b: { clip: 'shuimian' }, aim: 'room', label: `叫早 · ${RIGHTY}在窗台打瞌睡` },
      { at: 2.0, aim: { a: 'each-other' }, label: `叫早 · ${LEFTY}转过身` },
      { at: 3.2, a: { clip: 'atk01' }, label: `叫早 · ${LEFTY}出手叫醒` },
      { at: 4.4, b: { clip: 'yunxuan' }, aim: { b: 'each-other' }, label: `叫早 · ${RIGHTY}挨了一下才转身` },
      { at: 5.8, b: { clip: 'atk01' }, label: `叫早 · ${RIGHTY}反击` },
      { at: 7.0, a: { clip: 'hurt' }, label: `叫早 · ${LEFTY}被打飞` },
      { at: 8.0, b: { clip: 'win' }, label: `叫早 · ${RIGHTY}得意` },
      { at: 11.0, a: { clip: 'enter' }, b: { clip: 'mv_tar21' }, aim: 'behind', chase: { leader: 'b', amp: .3, period: 2.2 }, label: `叫早 · ${RIGHTY}带路，${LEFTY}追着后背跑` },
      { at: 13.0, a: { clip: 'idle' }, b: { clip: 'shuimian' }, aim: 'each-other', chase: undefined, label: `叫早 · ${RIGHTY}又睡着了` },
      { at: 14.6, a: { clip: 'idle' }, b: { clip: 'idle' }, aim: 'room', label: `叫早 · 收场归位` },
    ],
  },
];

export interface Warriors {
  /** Hand the rig the next clip when one of these names (a click's object chain) is its root. */
  play(names: string[]): string | undefined;
  /** Playback rate for every rig and for the duel's own clock, straight from the console slider. */
  setSpeed(speed: number): void;
  update(dt: number): void;
  /** Which script runs: 0 for none, otherwise 1-based into `scripts` (they are exported so the
   *  console can build its menu straight from the same table). */
  selectScene(index: number): number;
  scenePlaying(): boolean;
  sceneIndex(): number;
  /** The beat the running script is in, or undefined when nothing is playing. */
  sceneBeat(): string | undefined;
}

interface Rig { root: THREE.Group; turn: THREE.Group; model: THREE.Object3D; mixer: THREE.AnimationMixer; clips: THREE.AnimationAction[]; next: number; active?: THREE.AnimationAction }

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
    // The script turns `turn`; the clips animate the model inside it, so a clip that swings the
    // character back round to face the room cannot wipe out the turn the duel just asked for.
    const turn = new THREE.Group();
    const model = cloneRig(source) as THREE.Object3D;
    model.scale.setScalar(scale);
    model.rotation.y = facing;
    turn.add(model);
    group.add(turn);
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
    const idle = clips.find(action => action.getClip().name === 'idle') ?? clips[0];
    idle?.play();
    rigs.push({ root: group, turn, model, mixer, clips, next: 1, active: idle });
  }
  if (!rigs.length) return undefined;
  const state = { script: 0, speed: 1, time: 0, beat: -1, aim: ['room', 'room'] as Aim[], yaw: [HOME, HOME], vel: [0, 0] };
  const cue = (rig: Rig, name: string) => {
    const action = rig.clips.find(entry => entry.getClip().name === name);
    if (!action || action === rig.active) return;
    for (const entry of rig.clips) if (entry !== action) entry.fadeOut(TURN_BLEND);
    // No per-clip speed-ups: a clip plays at the pace it was authored at, and the console's
    // 战士动作速度 slider is the one control that makes the duel faster or slower.
    const cycles = looping.has(name);
    action.reset();
    action.timeScale = 1;
    action.setLoop(cycles ? THREE.LoopRepeat : THREE.LoopOnce, cycles ? Infinity : 1);
    action.clampWhenFinished = !cycles;
    action.fadeIn(TURN_BLEND).play();
    rig.active = action;
  };
  // A damped spring rather than a plain lerp: a 90° turn overshoots a couple of degrees and settles
  // back, which is what makes the two of them read as bodies turning instead of dials rotating. It
  // is integrated in fixed sub-steps, because one 100 ms step (a phone dropping frames) would make
  // the same spring overshoot by 30° and hand back a turn nobody asked for.
  const settle = (index: number, target: number, dt: number) => {
    const rig = rigs[index];
    if (!rig) return;
    target += Math.round((state.yaw[index] - target) / (Math.PI * 2)) * Math.PI * 2;
    const steps = Math.max(1, Math.ceil(dt / (1 / 120)));
    const slice = dt / steps;
    for (let i = 0; i < steps; i++) {
      state.vel[index] += (TURN_STIFFNESS * (target - state.yaw[index]) - TURN_DAMPING * state.vel[index]) * slice;
      state.yaw[index] += state.vel[index] * slice;
    }
    rig.turn.rotation.y = state.yaw[index];
  };
  return {
    play(names) {
      // The duel owns both warriors while it runs, so a stray click cannot break the choreography.
      if (state.script) return undefined;
      const rig = rigs.find(candidate => names.includes(candidate.root.name));
      if (!rig || !rig.clips.length) return undefined;
      const action = rig.clips[rig.next % rig.clips.length];
      rig.next += 1;
      for (const entry of rig.clips) if (entry !== action) entry.fadeOut(TURN_BLEND);
      action.reset();
      action.timeScale = 1;
      action.setLoop(THREE.LoopRepeat, Infinity);
      action.fadeIn(TURN_BLEND).play();
      rig.active = action;
      return clipLabels[action.getClip().name] ?? '战士动了动';
    },
    setSpeed(speed) { state.speed = speed; for (const rig of rigs) rig.mixer.timeScale = speed; },
    selectScene(index) {
      const next = Number.isFinite(index) && index >= 1 && index <= scripts.length ? Math.floor(index) : 0;
      const changed = next !== state.script;
      state.script = next;
      if (changed) {
        state.time = 0; state.beat = -1; state.aim = ['room', 'room']; state.vel[0] = 0; state.vel[1] = 0;
      }
      // Leaving the menu's 不播放 slot hands both of them straight back to the resting pose; the
      // springs walk them home from wherever they were.
      if (!next) for (const rig of rigs) cue(rig, 'idle');
      return next;
    },
    scenePlaying() { return state.script > 0; },
    sceneIndex() { return state.script; },
    sceneBeat() {
      const script = scripts[state.script - 1];
      return script ? script.beats[Math.max(0, state.beat)]?.label : undefined;
    },
    update(dt) {
      for (const rig of rigs) rig.mixer.update(dt);
      const script = scripts[state.script - 1];
      // The running script's clock takes the console's speed slider too, so beats, clips and turns
      // stay in step whether it is played at 1× or at half speed.
      const step = dt * state.speed;
      if (script) {
        state.time = (state.time + step) % script.length;
        let index = 0;
        for (let i = 0; i < script.beats.length; i++) if (script.beats[i].at <= state.time) index = i;
        if (index !== state.beat) {
          state.beat = index;
          const beat = script.beats[index];
          // The aim is sticky and kept per warrior: a beat that does not say otherwise keeps the
          // standing arrangement, so the two of them stay squared up for the whole fight instead of
          // turning away between blows. Writing only 'a' or 'b' turns just that one.
          if (typeof beat.aim === 'string') state.aim = [beat.aim, beat.aim];
          else if (beat.aim) {
            if (beat.aim.a) state.aim[0] = beat.aim.a;
            if (beat.aim.b) state.aim[1] = beat.aim.b;
          }
          if (beat.a) cue(rigs[0], beat.a.clip);
          if (beat.b) cue(rigs[1], beat.b.clip);
        }
      }
      const beat = script ? script.beats[Math.max(0, state.beat)] : undefined;
      if (!beat) { settle(0, HOME, step); settle(1, HOME, step); return; }
      for (const index of [0, 1]) {
        const aim = state.aim[index];
        let target = HOME;
        if (aim === 'each-other') target = index === 0 ? MEET_A : MEET_B;
        if (aim === 'behind' && beat.chase) {
          // Both turned the same way, the follower a beat behind: on the sill that reads as one
          // warrior running after the other's back, which is the only chase it allows.
          const leader = beat.chase.leader === 'a' ? 0 : 1;
          const base = leader === 0 ? MEET_B : MEET_A;
          const phase = (state.time - beat.at - (index === leader ? 0 : CHASE_LAG)) * Math.PI * 2 / beat.chase.period;
          target = base + Math.sin(phase) * beat.chase.amp;
        }
        settle(index, target, step);
      }
    },
  };
}
