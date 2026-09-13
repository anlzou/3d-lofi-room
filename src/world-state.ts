export type Season = 'spring' | 'summer' | 'autumn' | 'winter';
export type Weather = 'clear' | 'cloudy' | 'overcast' | 'drizzle' | 'rain' | 'storm' | 'fog' | 'snow' | 'windy';

// Lights that expose an on/off switch plus a 0..1 intensity slider in the console.
// 1 means the tuned default output, so existing saves keep the intended look.
export const lightKeys = ['lamp', 'bedsideLamp', 'ceilingLamp', 'lavaLamp', 'stringLights', 'streetLamp', 'mac', 'tv'] as const;
export type LightKey = typeof lightKeys[number];
export type LightLevels = Record<LightKey, number>;
export const lightLabels: Record<LightKey, string> = { lamp:'台灯', bedsideLamp:'床头灯', ceilingLamp:'顶灯', lavaLamp:'熔岩灯', stringLights:'串灯', streetLamp:'路灯', mac:'Mac 屏', tv:'电视屏' };
export const seasonLabels: Record<Season, string> = { spring:'春', summer:'夏', autumn:'秋', winter:'冬' };
export const seasonMottos: Record<Season, string> = { spring:'新绿', summer:'长日', autumn:'黄昏', winter:'炉火' };
export const weatherLabels: Record<Weather, string> = { clear:'晴', cloudy:'多云', overcast:'阴天', drizzle:'细雨', rain:'雨', storm:'雷雨', fog:'雾', snow:'雪', windy:'风' };

export interface WorldState {
  // 2 is what this build writes; 1 is still read, because saves from before the fan's 摇头
  // switch existed carry it (see restoreState).
  schemaVersion: 1 | 2;
  season: Season;
  time: number;
  weather: Weather;
  autopilot: boolean;
  // 展示模式: the room runs its own day — street lamps follow the sun and the indoor
  // lights follow a human routine instead of the switches.
  showcase: boolean;
  audio: { enabled: boolean; masterVolume: number };
  camera: 'room' | 'desk' | 'window' | 'tv';
  devices: { lamp: boolean; bedsideLamp:boolean; ceilingLamp:boolean; lavaLamp:boolean; stringLights:boolean; streetLamp:boolean; tv: boolean; mac: boolean; windowOpen: boolean; fanSpeed: 0 | 1 | 2; heater: boolean };
  levels: LightLevels;
  // Look of the window string lights, drawn as a neon strip: hex colour, blink rate in Hz
  // (0 keeps the strip steady), plus the automatic hue cycle, the running chase and the
  // rainbow ramp that gives every bulb its own hue along the wire.
  strip: { color: string; blink: number; cycle: boolean; chase: boolean; rainbow: boolean };
}

export const seasons: Season[] = ['spring', 'summer', 'autumn', 'winter'];
export const weathers: Weather[] = ['clear', 'cloudy', 'overcast', 'drizzle', 'rain', 'storm', 'fog', 'snow', 'windy'];
export function legalWeather(season: Season, weather: Weather): Weather {
  return weather === 'snow' && season !== 'winter' || weather === 'storm' && season === 'winter' ? 'cloudy' : weather;
}
// How much daylight the sun angle gives at this hour, on the same 06:00–18:00 arc the
// renderer uses. Exported so the room lighting and the showcase routine agree on dusk.
const smoothstep = (x: number, min: number, max: number) => {
  const t = Math.min(1, Math.max(0, (x - min) / (max - min)));
  return t * t * (3 - 2 * t);
};
export function daylightAt(hour: number): number {
  return smoothstep(Math.sin((((hour % 24) + 24) % 24 - 6) / 12 * Math.PI), -.12, .25);
}
export type ShowcaseDevices = WorldState['devices'];
export interface ShowcaseStep { id: string; label: string; devices: ShowcaseDevices }
// One plausible day for the room. Each row starts a stretch of the routine; the lamps in
// `on` light up for that stretch and everything else stays dark. Street lamps are handled
// separately below because they answer to the sun, not to the household.
const showcaseSteps: { start: number; id: string; label: string; on: Partial<ShowcaseDevices> }[] = [
  { start: 0, id: 'sleep', label: '深夜安睡', on: {} },
  { start: 6.6, id: 'wake', label: '起床', on: { bedsideLamp: true } },
  { start: 7.4, id: 'morning', label: '晨间', on: { ceilingLamp: true } },
  { start: 8.6, id: 'work-am', label: '上午工作', on: { lamp: true, mac: true } },
  { start: 12, id: 'lunch', label: '午休', on: { lamp: true, tv: true } },
  { start: 13.5, id: 'work-pm', label: '下午工作', on: { lamp: true, mac: true } },
  { start: 17.6, id: 'home', label: '傍晚回家', on: { ceilingLamp: true, tv: true, stringLights: true } },
  { start: 19.2, id: 'evening', label: '夜间', on: { ceilingLamp: true, lamp: true, tv: true, mac: true, lavaLamp: true, stringLights: true } },
  { start: 22.6, id: 'reading', label: '深夜阅读', on: { lamp: true, bedsideLamp: true, lavaLamp: true, stringLights: true } },
  { start: 23.6, id: 'wind-down', label: '准备睡觉', on: { bedsideLamp: true } },
];
const darkDevices: ShowcaseDevices = { lamp: false, bedsideLamp: false, ceilingLamp: false, lavaLamp: false, stringLights: false, streetLamp: false, tv: false, mac: false, windowOpen: false, fanSpeed: 0, heater: false };
export function showcaseAt(hour: number, season: Season, weather: Weather = 'clear'): ShowcaseStep {
  const h = ((hour % 24) + 24) % 24;
  let step = showcaseSteps[0];
  for (const candidate of showcaseSteps) if (candidate.start <= h) step = candidate;
  const daylight = daylightAt(h);
  const dark = daylight < .35;
  const home = h >= 6.6 && h < 8.6 || h >= 17.6 || h < 1;
  const wet = weather === 'rain' || weather === 'storm' || weather === 'drizzle' || weather === 'snow' || weather === 'fog';
  // A fan left running in a hot afternoon is being ignored, and a running fan sways on its own.
  const fanSpeed: 0 | 1 | 2 = season === 'summer' ? (h >= 12 && h < 16 ? 2 : h >= 9 && h < 18 ? 1 : 0) : 0;
  return {
    id: step.id, label: step.label,
    devices: {
      ...darkDevices, ...step.on,
      // The strip and the lava lamp are the room's night lights: they ignore the routine
      // and burn from dusk all the way to dawn, together with the street lamps outside.
      stringLights: dark,
      lavaLamp: dark,
      // Street lamps read the sky: on as the light fades, off once the sun is back.
      streetLamp: dark,
      // The window is aired on a warm dry afternoon and shut otherwise.
      windowOpen: season !== 'winter' && !wet && h >= 9 && h < 18,
      heater: season === 'winter' && daylight < .35 && home,
      fanSpeed,
    },
  };
}
export function restoreState(raw: unknown, query = ''): WorldState {
  const d = createDefaultState();
  const r = raw && typeof raw === 'object' ? raw as Partial<WorldState> : {};
  if (r.schemaVersion === 1 || r.schemaVersion === 2) {
    if (seasons.includes(r.season!)) d.season = r.season!;
    if (weathers.includes(r.weather!)) d.weather = r.weather!;
    if (Number.isFinite(r.time)) d.time = ((r.time! % 24) + 24) % 24;
    if (typeof r.autopilot === 'boolean') d.autopilot = r.autopilot;
    if (typeof r.showcase === 'boolean') d.showcase = r.showcase;
    if (['room','desk','window','tv'].includes(r.camera!)) d.camera = r.camera!;
    if (r.devices && typeof r.devices === 'object') for (const key of ['lamp','bedsideLamp','ceilingLamp','lavaLamp','stringLights','streetLamp','tv','mac','windowOpen','heater'] as const) {
      if (typeof r.devices[key] === 'boolean') d.devices[key] = r.devices[key];
    }
    // Older saves have no levels; they fall back to the tuned default output.
    if (r.levels && typeof r.levels === 'object') for (const key of lightKeys) {
      if (Number.isFinite(r.levels[key])) d.levels[key] = Math.max(0, Math.min(1, r.levels[key]));
    }
    if (r.strip && typeof r.strip === 'object') {
      if (typeof r.strip.color === 'string' && /^#[0-9a-f]{6}$/i.test(r.strip.color)) d.strip.color = r.strip.color.toLowerCase();
      if (Number.isFinite(r.strip.blink)) d.strip.blink = Math.max(0, Math.min(5, r.strip.blink));
      if (typeof r.strip.cycle === 'boolean') d.strip.cycle = r.strip.cycle;
      if (typeof r.strip.chase === 'boolean') d.strip.chase = r.strip.chase;
      if (typeof r.strip.rainbow === 'boolean') d.strip.rainbow = r.strip.rainbow;
    }
    if ([0,1,2].includes(r.devices?.fanSpeed!)) d.devices.fanSpeed = r.devices!.fanSpeed;
    if (Number.isFinite(r.audio?.masterVolume)) d.audio.masterVolume = Math.max(0, Math.min(1,r.audio!.masterVolume));
  }
  // Sound always requires a fresh gesture; stored settings cannot autoplay audio.
  const q = new URLSearchParams(query);
  if (seasons.includes(q.get('season') as Season)) { d.season = q.get('season') as Season; d.autopilot = false; }
  if (weathers.includes(q.get('weather') as Weather)) d.weather = q.get('weather') as Weather;
  if (q.has('time') && q.get('time')!.trim() && Number.isFinite(Number(q.get('time')))) {
    d.time = ((Number(q.get('time')) % 24) + 24) % 24; d.autopilot = false;
  }
  d.weather = legalWeather(d.season,d.weather);
  return d;
}
export function createDefaultState(): WorldState {
  return {
    // 展示模式 is on out of the box: a first visit opens on a room that is already living its
    // own day, starting late morning so there is light to see it by.
    schemaVersion: 2, season: 'autumn', time: 11 + 30 / 60, weather: 'clear', autopilot: false, showcase: true,
    audio: { enabled: false, masterVolume: 0.12 }, camera: 'room',
    devices: { lamp: true, bedsideLamp:false, ceilingLamp:false, lavaLamp:false, stringLights:false, streetLamp:true, tv: true, mac: true, windowOpen: false, fanSpeed: 0, heater: false },
    levels: { lamp: 1, bedsideLamp: 1, ceilingLamp: 1, lavaLamp: 1, stringLights: 1, streetLamp: 1, mac: 1, tv: 1 },
    strip: { color: '#ffb266', blink: 0, cycle: false, chase: false, rainbow: false },
  };
}
// How far the rainbow ramp travels from the first bulb to the last. Slightly under a full
// wheel keeps neighbours blending instead of hard-cutting from red back to red.
export const rainbowSpread = .85;
export function rainbowHue(baseHue: number, phase: number, drift = 0): number {
  return (((baseHue + phase * rainbowSpread + drift) % 1) + 1) % 1;
}
// The look 展示模式 gives the strip while it is in charge: a rainbow run (every bulb its own hue)
// that chases, with the colours drifting. The picked colour stays as the rainbow's base, and a
// user's own pace is left alone — a still strip would make the chase look broken, so a stopped
// one is given a starting speed. The caller keeps the user's settings aside and puts them back
// when the mode is switched off.
export function showcaseStrip(base: WorldState['strip']): WorldState['strip'] {
  return { color: base.color, blink: base.blink > 0 ? base.blink : 1, cycle: true, chase: true, rainbow: true };
}
// 展示模式 runs long, so the calendar moves with it: crossing midnight to a new day. A late
// hour dropping to an early one is the wrap; scrubbing around inside a day is not.
export function crossedMidnight(previousHour: number, hour: number): boolean {
  return previousHour > 20 && hour < 4;
}
// The new day brings the next season in the cycle and fresh weather that the season allows
// (no snow outside winter, no storms in winter). `roll` is 0..1 — the caller passes its own
// random value so the choice stays testable.
export function nextShowcaseDay(season: Season, weather: Weather, roll: number): { season: Season; weather: Weather } {
  const nextSeason = seasons[(seasons.indexOf(season) + 1) % seasons.length];
  const options = weathers.filter(w => w !== weather && legalWeather(nextSeason, w) === w);
  const picks = options.length ? options : weathers.filter(w => legalWeather(nextSeason, w) === w);
  return { season: nextSeason, weather: picks[Math.floor(roll * picks.length) % picks.length] };
}
// The fan's base carries three buttons read left to right from the room: the two cream ones
// pick the speeds and the red one on the right stops it. Only one lights at a time, so the
// row doubles as the fan's state readout while the slider panel is closed.
export interface FanButtonLamp { button: number; color: string; intensity: number }
export function fanButtonLamp(speed: 0 | 1 | 2): FanButtonLamp {
  if (speed === 0) return { button: 2, color: '#ff3516', intensity: .9 };
  return speed === 1 ? { button: 0, color: '#ffb259', intensity: 1.1 } : { button: 1, color: '#ffb259', intensity: 1.7 };
}
