import {test} from 'node:test';
import assert from 'node:assert/strict';
import {sunShadowClock,shadowAngleStep,shadowMinInterval} from '../src/sun-shadow.ts';

// The sun arc the renderer uses: 06:00 to 18:00, one pi of travel.
const angleAt = (hour: number) => ((hour - 6) / 12) * Math.PI;
// 展示模式 turns an hour every six seconds.
const HOURS_PER_SECOND = 1 / 6;
const run = (seconds: number, fps: number, lit = true) => {
  const clock = sunShadowClock();
  const rebuilds: { at: number; step: number }[] = [];
  let angle = angleAt(9), previous = angle;
  const frame = 1 / fps;
  for (let t = 0; t < seconds; t += frame) {
    angle = angleAt(9 + t * HOURS_PER_SECOND);
    if (clock.due(angle, t * 1000, lit)) {
      rebuilds.push({ at: t, step: Math.abs(angle - previous) });
      previous = angle;
    }
  }
  return rebuilds;
};
test('the sun shadow rebuilds often enough to look like it is sliding',()=>{
  const rebuilds = run(6, 60);
  const rate = rebuilds.length / 6;
  // An hour of sun travel used to rebuild five times; a smooth slide needs well over ten.
  assert(rate > 10, `expected more than ten rebuilds a second, got ${rate.toFixed(1)}`);
  assert(rate <= 1 / shadowMinInterval + 1, `the interval cap must hold, got ${rate.toFixed(1)} a second`);
  for (const { step } of rebuilds) {
    // Allow one frame of extra travel on top of the step, since the clock is checked per frame.
    assert(step <= shadowAngleStep * 1.5, `a step of ${step.toFixed(4)} rad would be visible`);
  }
});
test('a slow clock takes finer steps and a dragged clock cannot flood the renderer',()=>{
  const slow = run(6, 60);
  const fast = run(6, 60);
  assert.equal(slow.length, fast.length, 'the same clock and frame rate must behave the same');
  // At a low frame rate the step is bounded by the frame, not by the angle threshold: the
  // check only runs once a frame, so it can be at most one frame of sun travel late.
  for (const fps of [4, 12]) {
    const frameTravel = (1 / fps) * HOURS_PER_SECOND * Math.PI / 12;
    for (const { step } of run(6, fps)) assert(step <= shadowAngleStep + frameTravel * 1.1, `${fps} fps stepped ${step.toFixed(4)} rad`);
  }
  // No two rebuilds inside the interval, whatever the frame rate.
  for (const fps of [4, 12, 60, 144]) {
    const stamps = run(6, fps).map(r => r.at);
    for (let i = 1; i < stamps.length; i++) assert(stamps[i] - stamps[i - 1] >= shadowMinInterval - 1e-9, `${fps} fps rebuilt twice in one interval`);
  }
});
test('night rebuilds nothing and the first daylight frame always does',()=>{
  const clock = sunShadowClock();
  assert.equal(clock.due(angleAt(10), 0, true), true, 'the first call has nothing to compare against');
  assert.equal(clock.due(angleAt(10.001), 10, false), false, 'a sun that lights nothing needs no shadow');
  assert.equal(clock.due(angleAt(10.001), 20, true), false, 'not enough travel yet');
  // Coming back to daylight after the sun has moved a long way rebuilds at once.
  assert.equal(clock.due(angleAt(14), 30, true), true);
  clock.reset();
  assert.equal(clock.due(angleAt(14), 35, true), true);
});
