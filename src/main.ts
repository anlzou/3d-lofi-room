import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { loadWarriors, type Warriors } from './warrior';
import { loadBakedLighting } from './baked-lighting';
import { roomControls } from './room-controls';
import { consoleDrag } from './console-drag';
import {lightFade} from './light-fade';
import { sunShadowClock } from './sun-shadow';
import { loadingProgress } from './loading';
import { frameGovernor, pixelRatioFor, bufferRatio } from './perf-governor';
import { roomLife } from './room-life';
import { legalWeather, lightLabels, lightKeys, daylightAt, showcaseAt, crossedMidnight, nextShowcaseDay, showcaseStrip, seasonLabels, seasonMottos, weatherLabels, type WorldState } from './world-state';
import { hitDevice } from './device-hit';
import { dropdown } from './dropdown';
import {touchFeedback} from './touch-feedback';

const app = document.querySelector<HTMLDivElement>('#app')!;
const status = document.querySelector<HTMLElement>('#status')!;
const loadBar = document.querySelector<HTMLProgressElement>('#load-progress')!;
const retry = document.querySelector<HTMLButtonElement>('#retry')!;
// The loading line lives where the status always is (bottom left), so a slow network is
// explained on the spot instead of leaving an empty room on screen.
const progress = loadingProgress();
const loadingStartedAt = performance.now();
let lastProgressAt = loadingStartedAt;
const paintProgress = (stage: Parameters<typeof progress.label>[0]) => {
  lastProgressAt = performance.now();
  loadBar.hidden = false;
  loadBar.value = Math.round(progress.value() * 100);
  const { loaded, total } = progress.estimate();
  const mb = (bytes: number) => (bytes / 1e6).toFixed(1);
  status.textContent = `${progress.label(stage)} ${loadBar.value}% · ${mb(loaded)} / ${mb(total)} MB`;
};
const finishProgress = () => { loadBar.hidden = true; retry.hidden = true; };
const failLoading = (reason: string, error: unknown) => {
  console.error('[lofi] load failed', error);
  status.textContent = reason;
  status.classList.add('error');
  loadBar.hidden = true;
  retry.hidden = false;
};
retry.addEventListener('click', () => location.reload());
// Slow connections get told what is happening, and after a while they also get a way out.
const slowNetworkWatch = window.setInterval(() => {
  if (loaded) { clearInterval(slowNetworkWatch); return; }
  const idle = performance.now() - lastProgressAt;
  const waiting = performance.now() - loadingStartedAt;
  if (waiting > 45000) retry.hidden = false;
  if (idle > 12000) status.textContent = '网络较慢，仍在继续加载…（可以再等一会，或点重试 ↻）';
}, 2000);
const slider = document.querySelector<HTMLInputElement>('#time')!;
const clock = document.querySelector<HTMLOutputElement>('#clock')!;
const phase = document.querySelector<HTMLElement>('#day-label')!;
const pause = document.querySelector<HTMLButtonElement>('#pause')!;
const stats = document.querySelector<HTMLElement>('#stats')!;
const cameraHost = document.querySelector<HTMLElement>('#camera-drop')!;
const fullscreen = document.querySelector<HTMLButtonElement>('#fullscreen')!;
let hour = 11 + 30 / 60;
// Last minute written to the clock, so an unchanged clock or phase is not rewritten per frame.
let shownMinutes = -1;
const settings = roomControls(() => { hour=settings.state.time; updateLight(); life?.update(0); }, index => { warriorSceneWanted = index; });
// Every light is multiplied by this eased 0..1 value, so switches flip instantly while the
// room fades. 展示模式 uses the slow curve; manual taps keep the quick one.
const fade = lightFade(settings.state.devices);
// The control panel starts as the bottom-centre ring button; the same dock is draggable.
const dock = document.querySelector<HTMLElement>('.dock')!;
const dockToggle = document.querySelector<HTMLButtonElement>('#dock-toggle')!;
const dockDrag = consoleDrag(dock);
dockToggle.addEventListener('click', () => {
  const open = dock.classList.toggle('open');
  dockToggle.setAttribute('aria-expanded', String(open));
  dockDrag.reposition();
});
// The ring's pressed look is class driven: mobile browsers can leave :active stuck on
// a button after a tap, which would leave the ring shrunk until the next touch.
const ringPressed = (on: boolean) => dockToggle.classList.toggle('pressed', on);
dockToggle.addEventListener('pointerdown', () => ringPressed(true));
document.addEventListener('pointerup', () => ringPressed(false), true);
document.addEventListener('pointercancel', () => ringPressed(false), true);
hour=settings.state.time;
let life: ReturnType<typeof roomLife> | undefined;
let touch:ReturnType<typeof touchFeedback>|undefined;
// The window-sill warriors are a runtime import (see warrior.ts), so they can be absent.
let warriors:Warriors|undefined;
// 窗台对打 state: the beat last announced, the script the console asked for, and the desk lamp's
// setting to hand back once the scene is over.
let warriorBeat='';
let warriorSceneWanted=0;
let warriorLampBefore:boolean|undefined;
const screenLights: {light:THREE.PointLight;tv:boolean}[]=[];
// Meshes kept out of static batching because their material is driven at runtime:
// the pendant and bedside shades glow on demand, and every string-light bulb animates.
// GLTFLoader drops the dots in Blender's .001 suffixes, so the fan buttons arrive as
// Fan_BaseButton / Fan_BaseButton001 / Fan_BaseButton002. All three must stay unbatched to
// light up on their own (see room-life).
const dynamicMesh = /^(Ceiling_Shade|Nightlight_Shade|Exterior_StreetLamp_Lens_[FB]|StringLights_(Bulb_\d+|Wire)|Fan_BaseButton[\d.]*)$/;
// A multi-material object arrives as a group with one child mesh per primitive, so the globe's
// continents are children of Globe_Sphere rather than a name of their own. Their material is
// driven at runtime too, so the whole sphere stays unbatched: three small meshes, and the land
// keeps a glow that batching would otherwise throw away with the hidden source meshes.
const dynamicMeshParent = /^Globe_Sphere[\d.]*$/;
// The globe's three latitude rings are dropped outright: at this size they read as loose circles
// floating around the sphere instead of part of it. The Blender source keeps them (AGENTS.md makes
// it the source of truth), so deleting them there later needs nothing changed here.
const droppedMesh = /^Globe_Parallel[\d.]*$/;
// The globe's three latitude rings read as clutter on such a low-poly sphere, so the web build
// hides them. They stay out of static batching to remain addressable by name — a batch is built
// from their geometry and hides the sources, leaving nothing to switch off. Delete them in
// Blender and re-export to drop the geometry for good.
const hiddenMesh = /^Globe_Parallel[\d.]*$/;
let ceilingLight: THREE.PointLight | undefined;
let lavaLight: THREE.PointLight | undefined;
const streetLights: THREE.PointLight[] = [];
let weatherDim=1;
// The last size the renderer was told about, so repeated resize events cost nothing.
let resizedWidth=0,resizedHeight=0;
let playing = false;
let loaded = false;
let frame = 0;
let lastTime = 0;
const sunShadow = sunShadowClock();
let fanBlades: THREE.Object3D | undefined;
let baked: Awaited<ReturnType<typeof loadBakedLighting>> | undefined;
const clockSegments: THREE.Mesh[] = [];
const sleepMarks: { sprite: THREE.Sprite; base: THREE.Vector3; offset: number }[] = [];
const digitSegments = ['abcdef', 'bc', 'abdeg', 'abcdg', 'bcfg', 'acdfg', 'acdefg', 'abc', 'abcdefg', 'abcdfg'];
const scene = new THREE.Scene();
scene.background = new THREE.Color('#282b34');
const camera = new THREE.PerspectiveCamera(40, innerWidth / innerHeight, .05, 80);
const renderer = new THREE.WebGLRenderer({ antialias: true });
const governor = frameGovernor();
// Sharpness is adaptive in both directions: the base ratio is the device's own pixels, and the
// governor pushes the buffer past that while frames stay comfortable (supersampling is what
// actually removes the stair-stepping) and backs off when they do not. Only the drawing buffer
// changes here: the canvas keeps the CSS size it was given, so a ratio change never rewrites the
// element's style and never re-lays-out the page mid-frame.
const applyPixelRatio = () => {
  const wanted = bufferRatio(innerWidth, innerHeight, pixelRatioFor(innerWidth, innerHeight, devicePixelRatio || 1), governor.scale());
  if (Math.abs(renderer.getPixelRatio() - wanted) < .02) return false;
  renderer.setPixelRatio(wanted);
  renderer.setSize(innerWidth, innerHeight, false);
  return true;
};
// The element keeps this CSS size for the rest of the session; only the buffer behind it is
// retuned below, so a ratio change never re-lays-out the page.
renderer.setSize(innerWidth, innerHeight);
applyPixelRatio();
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.shadowMap.enabled = true;
// Soft PCF, not the hard one: the sun's map is rebuilt a dozen times a second while the clock
// runs, and a hard filter makes the shadow edge crawl and speckle between rebuilds.
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
// Nothing is redrawn on its own: the sun's map is refreshed by sunShadowClock as it turns, and
// every other map only when something in the room actually changed (see refreshShadows).
renderer.shadowMap.autoUpdate = false;
app.appendChild(renderer.domElement);
// Bound to the fixed, full-viewport wrapper rather than the canvas: a phone that has just gone
// fullscreen can still be reporting the old size for a frame or two, and a drag on the uncovered
// strip would otherwise land on nothing at all. The wrapper is a sibling of every panel, so
// touching the room always rotates it and touching the console never does.
const controls = new OrbitControls(camera, app);
controls.enableDamping = true;
controls.enablePan = false;
controls.minDistance = 2;
controls.maxDistance = 16;
controls.minPolarAngle = .25;
controls.maxPolarAngle = Math.PI * .49;
const presets = {
  room: { position: [-5.72, 5.588, 7.89], target: [0, 1.10, -.25], fov: 40 },
  desk: { position: [-3.5, 2.9, 3], target: [-.72, 1.28, -1.06], fov: 37 },
  window: { position: [-3.6, 3.1, 4.7], target: [-.25, 1.45, -.95], fov: 40 },
  // Sitting in front of the CRT: the screen centre and its facing direction come from the
  // model (EMIT_screen_crt), two metres out along that normal, eyes a little above the tube.
  tv: { position: [-.53, 1.09, 2.65], target: [-1.67, .77, 1.01], fov: 34 },
};
function setCamera() {
  const choice = settings.state.camera;
  const p = presets[choice] ?? presets.room;
  controls.target.fromArray(p.target);
  camera.position.fromArray(p.position);
  if (innerWidth < 650 && choice === 'room') {
    camera.position.sub(controls.target).multiplyScalar(1.35).add(controls.target);
  }
  camera.fov = p.fov;
  camera.setViewOffset(innerWidth, innerHeight, 0, innerHeight * .055, innerWidth, innerHeight);
  camera.updateProjectionMatrix();
  controls.update();
}
// The camera list opens inside the page: the native select popup is drawn by the system and takes
// over the screen on phones, which looks nothing like the console around it.
const cameraChoices: { value: WorldState['camera']; label: string }[] = [
  { value: 'room', label: '01 全景' },
  { value: 'desk', label: '02 桌面' },
  { value: 'window', label: '03 窗边' },
  { value: 'tv', label: '04 电视' },
];
dropdown<WorldState['camera']>(cameraHost, cameraChoices, settings.state.camera, value => {
  settings.state.camera = value;
  settings.save();
  setCamera();
}, '机位');
setCamera();
const ambient = new THREE.HemisphereLight('#d4deed', '#665044', 1.2);
scene.add(ambient);
const sun = new THREE.DirectionalLight('#ffcd93', 2);
sun.castShadow = true;
// The sun's map is rebuilt a dozen times a second while the clock runs, so it stays at 1024:
// with the ±4 frustum below that is 7.8 mm per texel, about 1.5 screen pixels on the room
// camera, and the pass costs a quarter of what 2048 did. The bake, not this map, carries the
// room's light, so the softer edge is a fair trade for a shadow that can keep up.
sun.shadow.mapSize.set(1024, 1024);
Object.assign(sun.shadow.camera, { left: -4, right: 4, top: 4, bottom: -4, near: .1, far: 25 });
sun.shadow.bias = -.00015;
// Two texels of the 1024 map: enough slack that self-shadowing cannot come and go as the sun
// turns, which reads as flicker on flat surfaces.
sun.shadow.normalBias = .02;
// The sun slides all day long, so its map is refreshed on demand (see updateLight); every
// other shadow map is left alone while that happens.
sun.shadow.autoUpdate = false;
sun.target.position.set(0, .7, 0);
scene.add(sun, sun.target);
const fill = new THREE.DirectionalLight('#a8c7ff', .4);
fill.position.set(-3, 4, 5);
scene.add(fill);
const lamp = new THREE.PointLight('#ffbb73', 2.5, 6, 2);
lamp.position.set(-1.45, 1.18, -1.18);
lamp.castShadow = true;
lamp.shadow.mapSize.set(512, 512);
lamp.shadow.bias = -.0002;
lamp.shadow.normalBias = .015;
lamp.shadow.autoUpdate = false;
lamp.shadow.needsUpdate = true;
scene.add(lamp);
// A full refresh, for when a lamp was switched or the room changed: rebuild both maps.
// Day-to-day sun movement only asks for the sun's map, which skips the lamp's pass.
function refreshShadows() { renderer.shadowMap.needsUpdate = true; sun.shadow.needsUpdate = true; lamp.shadow.needsUpdate = true; }
const heaterGlow = new THREE.PointLight('#e97f37', .5, 4, 2);
heaterGlow.position.set(.37, .26, -.16);
scene.add(heaterGlow);
const night = new THREE.Color('#181f33');
const day = new THREE.Color('#8b959b');
// 晨曦 and 夕阳 are not the same light. Sunrise comes up through the night's haze, so it reads
// pinker, softer and a little cooler; by sunset the air has dried out and the same low angle
// lands deeper, redder and heavier on the room.
const sunriseSky = new THREE.Color('#c2877c');
const sunsetSky = new THREE.Color('#9d5836');
const dawnWarm = new THREE.Color('#ffd2a6');
const duskWarm = new THREE.Color('#ff9450');
const noon = new THREE.Color('#fff0d8');
const moon = new THREE.Color('#91afff');
// The hemisphere light is the room's own sky: its upper half carries the hour's colour and the
// floor half bounces it back warm, so the whole room picks up the hour instead of only the sunlit
// patches. These are the colours the window is filtering at that time.
const skyDay = new THREE.Color('#d4deed');
const skyDawn = new THREE.Color('#ffd9cd');
const skyDusk = new THREE.Color('#ffb077');
const skyNight = new THREE.Color('#3a4460');
const groundDay = new THREE.Color('#665044');
const groundGold = new THREE.Color('#75503a');
// The cool bounce keeps the shadowed side from going flat, so it stays blue — but it steps back
// as the sun drops, because a full-strength blue fill averages the golden hour away.
const fillDay = new THREE.Color('#a8c7ff');
const fillGold = new THREE.Color('#86a8ff');
function updateLight() {
  baked?.update(hour);
  const angle = ((hour - 6) / 12) * Math.PI;
  const height = Math.sin(angle);
  const daylight = daylightAt(hour);
  // The sun slides continuously, so its shadow has to keep up with it: refreshing on whole
  // hour steps made the shadow tick across the floor. Refresh on a small change of sun angle
  // instead, and never more often than the budget below, so a fast clock cannot spend the
  // frame on shadows. Night needs none of it — the sun is not lighting anything.
  if (sunShadow.due(angle, performance.now(), daylight > .05)) {
    renderer.shadowMap.needsUpdate = true;
    sun.shadow.needsUpdate = true;
  }
  const gold = 1 - THREE.MathUtils.smoothstep(height, .1, .65);
  // Dawn on the way up, dusk on the way down: the same geometry, two different skies.
  const rising = hour < 12;
  // A low sun also sits lower in the sky, so its light comes in flatter through the window: the
  // golden hour throws shadows the length of the floor instead of the short midday ones.
  sun.position.set(Math.cos(angle) * 4, 1 + Math.max(.08, Math.abs(height)) * 5.9, -5);
  // The moon tint only steps in once the sun is genuinely going out: mixing it in from the start
  // of the golden hour washes the dawn peach and the dusk orange back toward blue.
  // The moonlight tint belongs only to a sun that is going out: mixing it in as soon as daylight
  // starts to fall washes both golden hours out to the same pink and costs the sunset its orange.
  sun.color.copy(noon).lerp(rising ? dawnWarm : duskWarm, gold).lerp(moon, 1 - THREE.MathUtils.smoothstep(daylight, 0, .35));
  sun.intensity = daylight * (1.8 + Math.max(0, height)) * weatherDim;
  ambient.color.copy(skyDay).lerp(rising ? skyDawn : skyDusk, gold).lerp(skyNight, 1 - daylight);
  ambient.groundColor.copy(groundDay).lerp(groundGold, gold);
  ambient.intensity = daylight * (1 + gold * .12);
  fill.color.copy(fillDay).lerp(fillGold, gold);
  fill.intensity = daylight * (.45 - gold * .2);
  lamp.intensity = (2.5 + (1 - daylight) * 3.5) * settings.state.levels.lamp * fade.value('lamp');
  // The pendant hangs far above the room, so it needs a lot more output than the desk
  // lamp to read as "lights on" (measured on the room floor, not on its own shade).
  if (ceilingLight) ceilingLight.intensity = (6 + (1 - daylight) * 9) * settings.state.levels.ceilingLamp * fade.value('ceilingLamp');
  if (lavaLight) lavaLight.intensity = .9 * settings.state.levels.lavaLamp * fade.value('lavaLamp');
  // The two pole lamps sit outside the window, so their pool of light stays outdoors.
  for (const light of streetLights) light.intensity = 3 * settings.state.levels.streetLamp * fade.value('streetLamp');
  // The string-light strip owns its own light and blink timing in room-life.ts.
  heaterGlow.intensity = (.12 + (1 - daylight) * 1.35) * fade.value('heater');
  for(const s of screenLights)s.light.intensity=(s.tv?1.4:.6)*settings.state.levels[s.tv?'tv':'mac']*fade.value(s.tv?'tv':'mac');
  (scene.background as THREE.Color).copy(day).lerp(rising ? sunriseSky : sunsetSky, gold * .8).lerp(night, 1 - daylight);
  renderer.toneMappingExposure = 1;
  const minutes = Math.round(hour * 60) % 1440;
  // Writing to the DOM every frame is wasted work: the clock, the phase line and the slider
  // only change when the minute does, so each is compared before it is touched.
  if (minutes !== shownMinutes) {
    shownMinutes = minutes;
    clock.value = `${String(Math.floor(minutes / 60)).padStart(2, '0')}:${String(minutes % 60).padStart(2, '0')}`;
    const digits = clock.value.replace(':', '');
    for (const segment of clockSegments) {
      segment.visible = digitSegments[Number(digits[segment.userData.digit_index])].includes(segment.userData.segment);
    }
    const label = hour < 5 || hour >= 19.5 ? '夜色 · NIGHT' : hour < 8.5 ? '晨曦 · DAWN' : hour >= 16.5 ? '夕阳 · GOLDEN HOUR' : '日间 · DAYLIGHT';
    if (label !== phase.textContent) phase.textContent = label;
  }
  if (Math.abs(Number(slider.value) - hour) > .004) slider.value = String(hour);
}
updateLight();
slider.addEventListener('input', () => { hour = Number(slider.value);settings.state.time=hour;settings.state.autopilot=false;settings.sync();settings.save(); updateLight(); });
function togglePlay() {
  settings.state.autopilot=false;settings.sync();
  playing = !playing;
  pause.textContent = playing ? 'Ⅱ 暂停时间' : '▷ 时间流动';
  pause.setAttribute('aria-pressed', String(playing));
}
pause.addEventListener('click', togglePlay);
// 展示模式: leave the room to play by itself. Street lamps answer to the sun, the indoor
// lights follow a day of work and rest, and the screens, fan, heater and window come along.
const showcaseButton = document.querySelector<HTMLButtonElement>('#showcase')!;
let showcaseStep = '';
let showcaseHour = hour;
let showcaseStartedPlay = false;
const describeChange = (before: WorldState['devices'], after: WorldState['devices']) => {
  const on: string[] = [], off: string[] = [];
  for (const key of lightKeys) {
    if (before[key] === after[key]) continue;
    (after[key] ? on : off).push(lightLabels[key]);
  }
  if (before.heater !== after.heater) (after.heater ? on : off).push('暖炉');
  if (before.fanSpeed !== after.fanSpeed) (after.fanSpeed ? on : off).push('风扇');
  const parts: string[] = [];
  if (on.length) parts.push(`开启${on.join('、')}`);
  if (off.length) parts.push(`关闭${off.join('、')}`);
  return parts.join('，');
};
function applyShowcase(announce = false) {
  // The calendar moves with the showcase: past midnight the room turns to the next season
  // and draws fresh weather, so a long-running demo never sits in the same month forever.
  const rolled = crossedMidnight(showcaseHour, hour) ? rollShowcaseDay() : '';
  showcaseHour = hour;
  const step = showcaseAt(hour, settings.state.season, settings.state.weather);
  // One announcement per stretch of the routine: a manual toggle inside a stretch stays
  // put until the clock reaches the next one.
  if (step.id === showcaseStep && !announce && !rolled) return false;
  if (rolled) showcaseStep = '';
  const before: WorldState['devices'] = { ...settings.state.devices };
  showcaseStep = step.id;
  Object.assign(settings.state.devices, step.devices);
  settings.sync();
  settings.save();
  updateLight();
  const change = describeChange(before, settings.state.devices);
  if (change || announce || rolled) status.textContent = [`${clock.value} · ${step.label}`, rolled, change].filter(Boolean).join(' · ');
  return true;
}
function rollShowcaseDay() {
  const { season, weather } = nextShowcaseDay(settings.state.season, settings.state.weather, Math.random());
  settings.state.season = season;
  settings.state.weather = weather;
  return `新的一天 · ${seasonLabels[season]} · ${seasonMottos[season]} · 窗外：${weatherLabels[weather]}`;
}
// In 展示模式 the strip plays as a neon night light: it cycles its colour and runs the
// chase while it is on. Whatever the strip looked like before is kept and put back when
// the mode is switched off, so the showcase never eats a hand-tuned setting.
let stripBeforeShowcase: WorldState['strip'] | undefined;
function takeOverStrip() {
  stripBeforeShowcase ??= { ...settings.state.strip };
  Object.assign(settings.state.strip, showcaseStrip(stripBeforeShowcase));
  settings.sync();
}
function releaseStrip() {
  if (!stripBeforeShowcase) return;
  Object.assign(settings.state.strip, stripBeforeShowcase);
  stripBeforeShowcase = undefined;
  settings.sync();
}
function setShowcase(on: boolean, announce = true) {
  settings.state.showcase = on;
  showcaseButton.setAttribute('aria-pressed', String(on));
  if (on) {
    // A routine needs a moving clock, so switch the time flow on and remember whose idea it was.
    showcaseStartedPlay = !playing;
    if (!playing) togglePlay();
    showcaseStep = '';
    showcaseHour = hour;
    takeOverStrip();
    applyShowcase(true);
    if (announce) status.textContent += ' · 展示模式已开启（串灯彩虹 + 顺序点亮，天黑起亮到天亮）';
  } else {
    if (showcaseStartedPlay && playing) togglePlay();
    showcaseStartedPlay = false;
    releaseStrip();
    if (announce) status.textContent = '展示模式已关闭 · 灯光交回手动控制';
  }
  settings.save();
}
showcaseButton.addEventListener('click', () => setShowcase(!settings.state.showcase));
if (settings.state.showcase) setShowcase(true, false);
async function toggleFullscreen() {
  try {
    if (document.fullscreenElement) await document.exitFullscreen();
    else await document.documentElement.requestFullscreen();
  } catch { status.textContent = '当前浏览器不支持全屏，可使用 F11'; }
}
fullscreen.addEventListener('click', toggleFullscreen);
document.addEventListener('fullscreenchange', () => {
  fullscreen.textContent = document.fullscreenElement ? '退出全屏 ↙' : '全屏 ↗';
});
// The one prompt that survives ambient mode: it sits where the status line normally is,
// shows up whenever the interface is hidden, then fades out on its own.
const ambientHint = document.querySelector<HTMLElement>('#ambient-hint')!;
let ambientHintTimer = 0;
const showAmbientHint = () => {
  ambientHint.classList.add('show');
  clearTimeout(ambientHintTimer);
  ambientHintTimer = window.setTimeout(() => ambientHint.classList.remove('show'), 4200);
};
const hideAmbientHint = () => { clearTimeout(ambientHintTimer); ambientHint.classList.remove('show'); };
// Ambient mode (隐藏 / H) hides every panel. A double click — or a double tap on a
// touchscreen — anywhere in the room brings the interface back, so someone on a phone
// without a keyboard is never stranded outside the controls.
const enterAmbient = () => {
  document.body.classList.add('hide-ui');
  status.textContent = '已进入隐藏模式 · 双击屏幕退出';
  showAmbientHint();
};
const leaveAmbient = () => {
  if (!document.body.classList.contains('hide-ui')) return;
  document.body.classList.remove('hide-ui');
  hideAmbientHint();
  status.textContent = '控制面板已恢复 · 双击画面或按 H 可再次隐藏';
};
document.querySelector('#hide')!.addEventListener('click', enterAmbient);
// Tapping the room while hidden brings the prompt back, so the way out stays discoverable
// after the first one has faded.
document.addEventListener('click', () => { if (document.body.classList.contains('hide-ui')) showAmbientHint(); });
let lastCanvasTap = 0;
document.addEventListener('dblclick', leaveAmbient);
document.addEventListener('pointerup', (event) => {
  if (event.pointerType === 'mouse') return;
  const now = event.timeStamp;
  // 400ms matches the usual system double-click speed, so a relaxed double tap still
  // counts while two deliberate separate taps do not.
  if (now - lastCanvasTap < 400) { lastCanvasTap = 0; leaveAmbient(); } else lastCanvasTap = now;
});
window.addEventListener('keydown', (event) => {
  if (event.target instanceof HTMLInputElement || event.target instanceof HTMLSelectElement || event.target instanceof HTMLButtonElement || event.target instanceof HTMLTextAreaElement) return;
  if (event.code === 'KeyH') { if (document.body.classList.contains('hide-ui')) leaveAmbient(); else enterAmbient(); return; }
  if (event.code === 'KeyF') { void toggleFullscreen(); return; }
  if (event.target instanceof HTMLInputElement || event.target instanceof HTMLSelectElement || event.target instanceof HTMLButtonElement) return;
  if (event.code === 'Space') { event.preventDefault(); togglePlay(); }
  if (event.code === 'ArrowLeft' || event.code === 'ArrowRight') {
    event.preventDefault(); hour = (hour + (event.code === 'ArrowLeft' ? -.5 : .5) + 24) % 24;settings.state.time=hour;settings.state.autopilot=false;settings.sync();settings.save(); updateLight();
  }
});
const draco = new DRACOLoader();
draco.setDecoderPath(`${import.meta.env.BASE_URL}decoders/`);
// One frame's worth of breathing room, so the progress bar can paint before the main thread
// disappears into Draco decoding and geometry batching.
const nextFrame = () => new Promise<void>(resolve => requestAnimationFrame(() => resolve()));
/** Streams a file so the bar reports real bytes even on a slow connection. */
async function download(url: string, onBytes: (sent: number, total: number) => void) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${response.status} ${response.statusText} for ${url}`);
  const total = Number(response.headers.get('content-length') ?? 0);
  if (!response.body) return await response.arrayBuffer();
  const reader = response.body.getReader();
  const chunks: Uint8Array[] = [];
  let sent = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
    sent += value.length;
    onBytes(sent, total);
  }
  const buffer = new Uint8Array(sent);
  let at = 0;
  for (const chunk of chunks) { buffer.set(chunk, at); at += chunk.length; }
  onBytes(sent, sent);
  return buffer.buffer;
}
const roomLoader = new GLTFLoader().setDRACOLoader(draco);
const roomBase = import.meta.env.BASE_URL;
// The lightmaps and the model are independent downloads, so they run together and the bar
// counts both. The model is streamed, so a slow connection watches bytes arrive rather than a
// frozen "loading"; and decoding two megabytes is left until after a paint.
const lightingReady = loadBakedLighting((sent, total) => progress.report('lighting', sent, total));
lightingReady.catch(() => { /* Reported by the driver below. */ });
const ready = async (gltf: Awaited<ReturnType<typeof roomLoader.parseAsync>>) => {
  baked = await lightingReady;
  progress.done('lighting');
  let triangles = 0;
  let meshes = 0;
  let canopyMaterial:THREE.MeshStandardMaterial|undefined;
  gltf.scene.traverse((obj) => {
    if (obj instanceof THREE.Mesh) {
      if(obj.name.startsWith('Tree_Canopy')){canopyMaterial??=(obj.material as THREE.MeshStandardMaterial).clone();canopyMaterial.name='MAT_Runtime_Canopy';obj.material=canopyMaterial;}
      let moving = false;
      for (let p: THREE.Object3D | null = obj; p; p = p.parent) {
        if (p.name === 'ANIM_fan_blades' || p.name === 'ANIM_fan_head') moving = true;
      }
      if (!moving && !obj.name.startsWith('EMIT_')) {
        obj.material = Array.isArray(obj.material) ? obj.material.map(m => baked!.material(m)) : baked!.material(obj.material);
      }
      obj.castShadow = !obj.userData.noShadow;
      obj.receiveShadow = true;
      meshes++;
      triangles += (obj.geometry.index?.count ?? obj.geometry.attributes.position.count) / 3;
    }
  });
  scene.add(gltf.scene);
  gltf.scene.updateMatrixWorld(true);
  // Grazing angles are where detail smears: let the hardware follow the view direction when it
  // samples the wood, walls and props, instead of picking one mip and blurring it. One-off, and
  // it costs nothing per frame.
  const maxAnisotropy = renderer.capabilities.getMaxAnisotropy();
  const sharpened = new Set<THREE.Texture>();
  gltf.scene.traverse((obj) => {
    if (!(obj instanceof THREE.Mesh)) return;
    for (const material of Array.isArray(obj.material) ? obj.material : [obj.material]) {
      if (!(material instanceof THREE.MeshStandardMaterial)) continue;
      for (const map of [material.map, material.normalMap, material.roughnessMap, material.metalnessMap]) {
        if (!map || sharpened.has(map) || !(map.anisotropy < 4)) continue;
        sharpened.add(map);
        map.anisotropy = Math.min(4, maxAnisotropy);
        map.needsUpdate = true;
      }
    }
  });
  fanBlades = gltf.scene.getObjectByName('ANIM_fan_blades');
  const redSegment = gltf.scene.getObjectByName('EMIT_clock_segment_0_b') as THREE.Mesh;
  gltf.scene.traverse((obj) => {
    if (obj instanceof THREE.Mesh && obj.name.startsWith('EMIT_clock_segment_')) {
      obj.material = redSegment.material;
      obj.castShadow = false;
      clockSegments.push(obj);
    }
  });
  const catSocket = gltf.scene.getObjectByName('SOCKET_emoji_cat');
  if (catSocket) {
    const canvas = document.createElement('canvas'); canvas.width = canvas.height = 128;
    const ctx = canvas.getContext('2d')!;
    ctx.strokeStyle = '#eee5d2'; ctx.lineWidth = 15; ctx.lineCap = ctx.lineJoin = 'round';
    ctx.beginPath(); ctx.moveTo(37, 33); ctx.lineTo(91, 33); ctx.lineTo(37, 94); ctx.lineTo(91, 94); ctx.stroke();
    const texture = new THREE.CanvasTexture(canvas); texture.colorSpace = THREE.SRGBColorSpace;
    const base = catSocket.getWorldPosition(new THREE.Vector3());
    for (let i = 0; i < 3; i++) {
      const material = new THREE.SpriteMaterial({ map: texture, transparent: true, opacity: .5, depthWrite: false, toneMapped: false });
      const sprite = new THREE.Sprite(material); sprite.scale.setScalar(.06 + i * .012);
      scene.add(sprite); sleepMarks.push({ sprite, base: base.clone(), offset: i });
    }
  }
  // Preserve named pivots and sockets; batch only static meshes in memory.
  // Source geometry and the exported GLB retain their complete object names.
  const batches = new Map<THREE.Object3D, Map<THREE.Material, THREE.BufferGeometry[]>>();
  const sources: THREE.Mesh[] = [];
  gltf.scene.traverse((obj) => {
    if (!(obj instanceof THREE.Mesh) || Array.isArray(obj.material)) return;
    if (/^(INT_|ANIM_|EMIT_|SEASON_)/.test(obj.name) || obj.children.length || obj.userData.noShadow) return;
    if (dynamicMesh.test(obj.name) || dynamicMeshParent.test(obj.parent?.name ?? '')) return;
    // Rings the room does without: handled before the batch so no copy of them is drawn either.
    if (droppedMesh.test(obj.name)) { obj.visible = false; return; }
    if (hiddenMesh.test(obj.name)) return;
    let owner: THREE.Object3D = scene;
    for (let p = obj.parent; p; p = p.parent) {
      if (/^(INT_|ANIM_|EMIT_|SEASON_)/.test(p.name)) { owner = p; break; }
    }
    const geometry = obj.geometry.index ? obj.geometry.toNonIndexed() : obj.geometry.clone();
    geometry.applyMatrix4(new THREE.Matrix4().copy(owner.matrixWorld).invert().multiply(obj.matrixWorld));
    for (const attribute of Object.keys(geometry.attributes)) {
      if (!['position', 'normal', 'uv', 'uv1'].includes(attribute)) geometry.deleteAttribute(attribute);
    }
    if (!geometry.attributes.normal) geometry.computeVertexNormals();
    if (!geometry.attributes.uv) geometry.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(geometry.attributes.position.count * 2), 2));
    const materials = batches.get(owner) ?? new Map<THREE.Material, THREE.BufferGeometry[]>();
    const list = materials.get(obj.material) ?? [];
    list.push(geometry); materials.set(obj.material, list); batches.set(owner, materials); sources.push(obj);
  });
  for (const [owner, materials] of batches) for (const [material, geometries] of materials) {
    const merged = mergeGeometries(geometries);
    if (!merged) throw new Error('Static geometry batch failed');
    const batch = new THREE.Mesh(merged, material);
    batch.name = `StaticBatch_${material.name}`;
    batch.castShadow = true; batch.receiveShadow = true;
    owner.add(batch);
    for (const geometry of geometries) geometry.dispose();
  }
  for (const obj of sources) obj.visible = false;
  // see hiddenMesh: the rings live on in the .blend, the runtime just does not draw them.
  gltf.scene.traverse((obj) => { if (hiddenMesh.test(obj.name)) obj.visible = false; });
  // Eevee/Cycles lights stay in Blender. Runtime screen bounce follows exported faces.
  for (const name of ['EMIT_screen_mac', 'EMIT_screen_crt']) {
    const screen = gltf.scene.getObjectByName(name);
    if (screen) {
      const bounce = new THREE.PointLight('#9bcaff', name.endsWith('crt') ? 1.4 : .6, 2.4, 2);
      screen.getWorldPosition(bounce.position);
      const front = new THREE.Vector3(0, 0, 1).transformDirection(screen.matrixWorld);
      bounce.position.addScaledVector(front, .08);
      scene.add(bounce);screenLights.push({light:bounce,tv:name.endsWith('crt')});
    }
  }
  // Blender's LIGHT_ ceiling anchor drives the pendant; the paper shade itself
  // stays unbatched so it can glow (see runtimeMaterials).
  const ceilingAnchor = gltf.scene.getObjectByName('LIGHT_ceiling');
  if (ceilingAnchor) {
    ceilingLight = new THREE.PointLight('#ffc78a', 0, 5.4, 2);
    ceilingAnchor.getWorldPosition(ceilingLight.position);
    scene.add(ceilingLight);
  }
  // Lava lamp and window string lights reuse their Blender light anchors too.
  const lavaAnchor = gltf.scene.getObjectByName('LIGHT_lava_lamp');
  if (lavaAnchor) {
    lavaLight = new THREE.PointLight('#ff9d5c', 0, 1.5, 2);
    lavaAnchor.getWorldPosition(lavaLight.position);
    scene.add(lavaLight);
  }
  // The window string lights deliberately get no room light: only the bulbs themselves
  // glow (see room-life), so the strip never washes the wall behind it.
  // The two pole lamps keep their Blender LIGHT_ anchors for their own warm pools.
  for (const name of ['LIGHT_street_lamp_F', 'LIGHT_street_lamp_B']) {
    const anchor = gltf.scene.getObjectByName(name);
    if (!anchor) continue;
    const light = new THREE.PointLight('#ffb469', 0, 3.2, 2);
    anchor.getWorldPosition(light.position);
    scene.add(light);streetLights.push(light);
  }
  life=roomLife(gltf.scene,scene,settings.state,fade.value);
  touch=touchFeedback(gltf.scene,scene,settings.state);
  life.update(0);
  const ray=new THREE.Raycaster(),pointer=new THREE.Vector2();
  let downX=0,downY=0;
  // The tap test listens where the controls grabbed the pointer, not on the canvas: OrbitControls
  // captures the pointer on its own domElement, so a release only ever fires there — which is how
  // clicking a model in the room quietly stopped working. The raycast still measures against the
  // canvas, since that is the rectangle the camera's projection maps onto.
  app.addEventListener('pointerdown',e=>{downX=e.clientX;downY=e.clientY;});
  app.addEventListener('pointerup',e=>{
    if(e.button!==0||Math.hypot(e.clientX-downX,e.clientY-downY)>5)return;
    const box=renderer.domElement.getBoundingClientRect();pointer.set((e.clientX-box.left)/box.width*2-1,-(e.clientY-box.top)/box.height*2+1);
    ray.setFromCamera(pointer,camera);
    const hit=ray.intersectObjects(scene.children,true).find(h=>{let p:THREE.Object3D|null=h.object;while(p){if(!p.visible)return false;p=p.parent;}return h.object instanceof THREE.Mesh;});
    if(!hit)return;
    const names:string[]=[];for(let p:THREE.Object3D|null=hit.object;p;p=p.parent)names.push(p.name);
    const feedback=touch?.activate(names);if(feedback){settings.sync();settings.save();status.textContent=feedback;refreshShadows();return;}
    // The warriors answer to their own clips rather than to a switch, so a click on one plays the
    // next move instead of toggling a device.
    const played=warriors?.play(names);if(played){status.textContent=played;return;}
    const key=hitDevice(names);
    if(key){settings.state.devices[key]=!settings.state.devices[key];settings.sync();settings.save();updateLight();status.textContent=`${key==='heater'?'暖炉':lightLabels[key]}已${settings.state.devices[key]?'开启':'关闭'}`;}
  });
  loaded = true;
  draco.dispose();
  updateLight();
  refreshShadows();
  renderer.render(scene, camera);
  const shadowRefreshCalls = renderer.info.render.calls;
  renderer.render(scene, camera);
  stats.textContent = `${triangles.toLocaleString('en-US')} TRIANGLES · ${renderer.info.render.calls} DRAWS`;
  // The room is living its own day by default, so say so instead of only offering the camera.
  progress.done('build');
  finishProgress();
  clearInterval(slowNetworkWatch);
  status.classList.remove('error');
  // Once the room is up, say how to get into it: the ring opens the console, and the room itself
  // answers to clicks. The line is deliberately short — 展示模式 starts announcing its routine here.
  const readyHint = '拖动旋转 · 点底部圆环开控制面板，也可直接点房间里的模型互动';
  status.textContent = settings.state.showcase
    ? `房间已就绪 · 展示模式进行中（可按「展示模式」接管）· ${readyHint}`
    : `房间已就绪 · ${readyHint}`;
  console.info('[lofi] GLB loaded', JSON.stringify({ triangles, meshes, shadowRefreshCalls, steadyCalls: renderer.info.render.calls, clockSegments: clockSegments.length, fan: !!fanBlades, sleepMarks: sleepMarks.length }));
};
// Both downloads start here, and the room is assembled once the model has landed.
void (async () => {
  try {
    paintProgress('model');
    const buffer = await download(`${roomBase}models/demo.glb`, (sent, total) => {
      progress.report('model', sent, total);
      paintProgress('model');
    });
    paintProgress('decode');
    await nextFrame();
    const gltf = await roomLoader.parseAsync(buffer, `${roomBase}models/`);
    progress.done('decode');
    paintProgress('build');
    await nextFrame();
    await ready(gltf);
    // The room is already standing before the warriors arrive, so an FBX that fails to load leaves
    // the room exactly as it was — with the mecha it always had.
    try {
      warriors = await loadWarriors(gltf.scene, scene, `${roomBase}models/Warrior.fbx`);
      refreshShadows();
    } catch (error) { console.warn('[lofi] Warrior.fbx 未加载，保留窗户上的机甲', error); }
  } catch (error) {
    clearInterval(slowNetworkWatch);
    failLoading('房间加载失败 · 请检查网络后点击重试 ↻', error);
  }
})();
function resize(force = false) {
  // The URL bar, the keyboard and the fullscreen transition all fire this more than once for the
  // same result: only the first one for a given size has work to do.
  if (!force && innerWidth === resizedWidth && innerHeight === resizedHeight) return;
  resizedWidth = innerWidth; resizedHeight = innerHeight;
  camera.aspect = innerWidth / innerHeight;
  camera.setViewOffset(innerWidth, innerHeight, 0, innerHeight * .055, innerWidth, innerHeight);
  camera.updateProjectionMatrix();
  // The window itself changed, so the element's CSS size has to follow; the ratio is recomputed
  // for the new area by the next applyPixelRatio call through the same path.
  renderer.setPixelRatio(bufferRatio(innerWidth, innerHeight, pixelRatioFor(innerWidth, innerHeight, devicePixelRatio || 1), governor.scale()));
  renderer.setSize(innerWidth, innerHeight);
}
window.addEventListener('resize', () => resize());
// Entering fullscreen hides a phone's URL bar and turning the phone swaps the viewport, and Chrome
// may still report the previous size inside the event itself, so settle it again on the next
// frames. Rotating the phone is the case that matters most: without it the canvas keeps the old
// orientation's shape and the room looks — and drags — broken.
const settleViewport = () => {
  resize(true);
  requestAnimationFrame(() => { resize(true); requestAnimationFrame(() => resize(true)); });
};
window.addEventListener('orientationchange', settleViewport);
document.addEventListener('fullscreenchange', settleViewport);
document.addEventListener('webkitfullscreenchange', settleViewport);
// The visual viewport reports the URL bar sliding away before the layout does.
window.visualViewport?.addEventListener('resize', () => resize());
function animate(now: number) {
  if (document.hidden) { frame = 0; return; }
  const delta = lastTime ? Math.min((now - lastTime) / 1000, .1) : 0;
  lastTime = now;
  if (settings.state.autopilot) {
    const date=new Date();hour=date.getHours()+date.getMinutes()/60+date.getSeconds()/3600;
    settings.state.season=(['winter','spring','summer','autumn'] as const)[Math.floor(((date.getMonth()+1)%12)/3)];
    settings.state.weather=legalWeather(settings.state.season,settings.state.weather);
    settings.sync();
  } else if (playing && loaded) hour=(hour+delta/6)%24;
  settings.state.time=hour;
  if (settings.state.showcase) applyShowcase();
  // Ease every light before anything reads its value this frame.
  fade.update(delta, settings.state.devices, settings.state.showcase);
  weatherDim=THREE.MathUtils.damp(weatherDim,settings.state.weather==='clear'?1:settings.state.weather==='cloudy'?.72:.3,.6,delta);
  updateLight();life?.update(delta);touch?.update(delta);
  if (warriors) {
    warriors.setSpeed(settings.state.warriorSpeed);
    warriors.update(delta);
    // The console's 互动动画 menu is the only way in and out of a script: 不播放 stops it.
    if (warriorSceneWanted !== warriors.sceneIndex()) {
      const was = warriors.sceneIndex();
      const now = warriors.selectScene(warriorSceneWanted);
      warriorBeat = '';
      if (now && !was) {
        // The scene is lit by the desk lamp, and the room's own switch goes back afterwards.
        warriorLampBefore = settings.state.devices.lamp;
        settings.state.devices.lamp = true;
        settings.sync();
        settings.save();
      } else if (!now && was && warriorLampBefore !== undefined) {
        settings.state.devices.lamp = warriorLampBefore;
        warriorLampBefore = undefined;
        settings.sync();
        settings.save();
        status.textContent = '互动动画已停止 · 台灯交回控制台';
      }
    }
    if (warriors.scenePlaying()) {
      // 展示模式 could switch the lamp back off between beats, so hold it while a script runs.
      if (!settings.state.devices.lamp) { settings.state.devices.lamp = true; settings.sync(); }
      const beat = warriors.sceneBeat();
      if (beat && beat !== warriorBeat) { warriorBeat = beat; status.textContent = beat; }
    }
  }
  if (fanBlades) fanBlades.rotation.z += delta * [0, 7, 38][settings.state.devices.fanSpeed];
  for (const { sprite, base, offset } of sleepMarks) {
    const breath = (Math.sin(now / 1300 - offset * .8) + 1) / 2;
    sprite.position.copy(base).add(new THREE.Vector3(offset * .025, offset * .065 + breath * .018, 0));
    (sprite.material as THREE.SpriteMaterial).opacity = .18 + breath * .48;
  }
  // Judge the frame just gone, then resize before drawing: reallocating the buffer after the
  // present step can leave a frame unpainted on some drivers.
  if (loaded && governor.sample(delta * 1000)) applyPixelRatio();
  controls.update();
  renderer.render(scene, camera);
  frame = requestAnimationFrame(animate);
}
document.addEventListener('visibilitychange', () => {
  cancelAnimationFrame(frame);
  frame = 0;
  lastTime = 0;
  if (!document.hidden) frame = requestAnimationFrame(animate);
});
frame = requestAnimationFrame(animate);
