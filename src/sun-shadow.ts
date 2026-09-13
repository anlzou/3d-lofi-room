// The sun slides all day, so its shadow map has to keep up with it. The old rule rebuilt the
// map every 0.03 h of clock time: at the showcase pace (an hour every six seconds) that is
// 5.5 rebuilds a second, each one moving the shadow about half a degree, which reads as the
// shadow ticking across the floor. This keeps every step tiny instead, while holding the
// rebuild rate to something a frame can afford.
//
// The sun turns 15° an hour, so 0.0035 rad (0.2°) of travel is about 1.4 screen pixels on the
// room camera: below the step where an eye can see a jump. The interval is the safety net for
// a dragged time slider, which would otherwise ask for far more rebuilds than frames exist.
export const shadowAngleStep = .0035;
export const shadowMinInterval = 1 / 24;
export function sunShadowClock() {
  let angle = -1, at = 0;
  return {
    /**
     * True when the sun's shadow map is worth rebuilding now.
     * `now` is a millisecond timestamp, `lit` says whether the sun is lighting the room at all
     * (a night-time sun casts no visible shadow, so nothing is rebuilt until it comes back).
     */
    due(nextAngle: number, now: number, lit: boolean) {
      if (!lit) return false;
      // The first call after dark always rebuilds, since the sun will have moved a long way.
      const moved = angle < 0 || Math.abs(nextAngle - angle) > shadowAngleStep;
      if (!moved || (angle >= 0 && now - at <= shadowMinInterval)) return false;
      angle = nextAngle;
      at = now;
      return true;
    },
    /** Forget the last rebuild, so the next `due` call always says yes. */
    reset() { angle = -1; at = 0; },
  };
}
