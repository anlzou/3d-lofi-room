// Adaptive resolution, in both directions. The room starts at a sensible native-ish ratio and
// this watches the frame times: while the machine has headroom the buffer is pushed past native
// (supersampling, which is what actually removes the stair-stepping on thin geometry), and when
// frames get long it backs off again. Every change reallocates the drawing buffer, so the steps
// are spaced out by a cooldown rather than chased frame by frame.
//
// Frame times are compared against the display's own budget, not an absolute number: on a 60 Hz
// screen a machine with headroom reports ~16.7 ms no matter how fast it is, so the "there is
// room to grow" threshold sits just under one refresh, and any resolution that pushes frames
// past the struggling threshold is remembered so the climb cannot immediately walk back into it.
export const governorFloor = .62;
export const governorCeiling = 2;
const STRUGGLING_MS = 20;
const HEADROOM_MS = 17;
const DROP_STEP = .85;
const RISE_STEP = 1.15;
const DROP_COOLDOWN = 1.5;
const RISE_COOLDOWN = 1.2;
// One slow frame is an outlier (a tab switch, a texture upload, a GC pause), not a verdict; a
// short run of them is. Three frames is a fifth of a second even at 15 fps.
const SLOW_STREAK = 3;
// A bad patch must not cap the picture for the whole session: after this long spent comfortable
// the remembered ceiling is allowed to creep back up towards the maximum.
const HEAL_SECONDS = 30;
const HEAL_STEP = .1;
// Shader compilation and the first frames after load are always slow; judging them would shrink
// the picture for a machine that is actually fine.
const WARMUP_FRAMES = 90;
export function frameGovernor() {
  let scale = 1, average = 16.7, cooldown = 0, warmup = WARMUP_FRAMES, ceiling = governorCeiling;
  let slow = 0, comfortable = 0;
  return {
    scale: () => scale,
    /** The highest scale this machine has been shown to hold, up to the ceiling. */
    ceiling: () => ceiling,
    /** Feed one frame's duration in milliseconds; true when the scale changed. */
    sample(frameMs: number) {
      average = average * .9 + frameMs * .1;
      if (warmup > 0) { warmup--; return false; }
      if (!(frameMs > 0) || frameMs > 1000) { slow = 0; return false; }
      slow = frameMs > STRUGGLING_MS ? slow + 1 : 0;
      comfortable = average < HEADROOM_MS ? comfortable + frameMs / 1000 : 0;
      cooldown -= frameMs / 1000;
      if (cooldown > 0) return false;
      if (slow >= SLOW_STREAK && average > STRUGGLING_MS) {
        slow = 0;
        if (scale <= governorFloor) return false;
        scale = Math.max(governorFloor, scale * DROP_STEP);
        // That much resolution was too much for this machine: do not walk straight back into it.
        ceiling = Math.max(governorFloor, Math.min(ceiling, scale * 1.2));
        cooldown = DROP_COOLDOWN;
        return true;
      }
      if (average < HEADROOM_MS && scale < ceiling) {
        scale = Math.min(ceiling, scale * RISE_STEP);
        cooldown = RISE_COOLDOWN;
        return true;
      }
      if (comfortable > HEAL_SECONDS && ceiling < governorCeiling) {
        ceiling = Math.min(governorCeiling, ceiling + HEAL_STEP);
        comfortable = 0;
        return false;
      }
      return false;
    },
  };
}
// Starting buffer target: a big screen should not render four times the pixels of a small one.
export const pixelBudget = 2.6e6;
// How far the governor may push it while frames stay comfortable. Sharpness is worth pixels,
// but not unbounded ones — above this the cost climbs faster than the eye notices.
export const sharpenBudget = 4.2e6;
/** The ratio the room starts at: the device's own pixels, capped by the starting budget. */
export function pixelRatioFor(width: number, height: number, devicePixelRatio_ = 1) {
  const covered = Math.max(1, width * height);
  return Math.min(Math.max(devicePixelRatio_, 1), 1.5, Math.max(1, Math.sqrt(pixelBudget / covered)));
}
/** Where the governor's scale lands, never past what the sharpen budget allows for this screen. */
export function bufferRatio(width: number, height: number, base: number, scale: number) {
  const covered = Math.max(1, width * height);
  const mostAllowed = Math.max(base, Math.min(base * governorCeiling, Math.sqrt(sharpenBudget / covered)));
  return Math.min(Math.max(base * scale, base * governorFloor), mostAllowed);
}
