import type { LightKey } from './world-state';

// Which device a click on a piece of the room should switch. main.ts hands over the hit object's
// name chain (the object itself and its ancestors), so this stays a pure name → device mapping
// that can be asserted in tests instead of only being reachable through a raycast.
export type HitDevice = LightKey | 'heater';

export function hitDevice(names: string[]): HitDevice | undefined {
  const has = (...wanted: string[]) => wanted.some(name => names.includes(name));
  if (has('INT_tv_crt', 'EMIT_screen_crt')) return 'tv';
  if (has('INT_mac', 'EMIT_screen_mac')) return 'mac';
  if (has('INT_lamp_desk')) return 'lamp';
  if (has('SEASON_winter_heater')) return 'heater';
  if (has('INT_ceiling_pullcord', 'Ceiling_Shade')) return 'ceilingLamp';
  if (has('INT_lava_lamp')) return 'lavaLamp';
  // The window string lights answer to the whole run, bulbs and the wire they hang from: the wire
  // is by far the easier thing to hit, and both read as "the string lights" to whoever clicks.
  if (names.some(name => name.startsWith('StringLights_'))) return 'stringLights';
  return undefined;
}
