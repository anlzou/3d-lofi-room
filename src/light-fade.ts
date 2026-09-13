// Switches flip the instant they are tapped, but the light itself eases in and out: the
// room is never lit by an abrupt pop. 展示模式 turns are slow — a whole day is passing — so a
// scene change reads as dusk falling rather than a bulb snapping on. Manual taps stay quick
// so the console still feels responsive.
//
// The key list mirrors world-state's lightKeys plus the heater; scripts/light-fade.test.ts
// guards the two against drifting apart. It is written out here so this module keeps working
// without a runtime import (it is the one thing unit tests load directly through Node).
export const lightFadeKeys = ['lamp', 'bedsideLamp', 'ceilingLamp', 'lavaLamp', 'stringLights', 'streetLamp', 'mac', 'tv', 'heater'] as const;
export type LightFadeKey = typeof lightFadeKeys[number];
const SHOWCASE_LAMBDA = .55;
const MANUAL_LAMBDA = 7;
// Frame-rate independent easing, the same curve THREE.MathUtils.damp uses.
const ease = (from: number, to: number, lambda: number, dt: number) => from + (to - from) * (1 - Math.exp(-lambda * dt));
export function lightFade(devices: Record<LightFadeKey, boolean>) {
  const values = {} as Record<LightFadeKey, number>;
  // Start where the room already is, so a reload does not fade the room up from black.
  for (const key of lightFadeKeys) values[key] = devices[key] ? 1 : 0;
  return {
    /** 0 is fully off, 1 is fully on; renderers multiply their output by this. */
    value: (key: LightFadeKey) => values[key],
    /** Eases every light towards the current switches. */
    update(dt: number, target: Record<LightFadeKey, boolean>, gentle: boolean) {
      const lambda = gentle ? SHOWCASE_LAMBDA : MANUAL_LAMBDA;
      for (const key of lightFadeKeys) {
        const goal = target[key] ? 1 : 0;
        const next = ease(values[key], goal, lambda, dt);
        // Snap the last sliver, otherwise a light never quite reaches zero or full.
        values[key] = Math.abs(goal - next) < .002 ? goal : next;
      }
    },
    snapshot: () => ({ ...values }),
  };
}
