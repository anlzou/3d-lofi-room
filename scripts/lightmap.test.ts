import assert from 'node:assert/strict';
import test from 'node:test';
import { lightmapBlend } from '../src/baked-lighting.ts';
const values = [.2, .7, 1.8, .9];
const sample = (hour: number) => {
  const t = lightmapBlend(hour);
  return values[t.a] * (1 - t.mix) + values[t.b] * t.mix;
};
test('keyframes select the correct bake without a brightness jump', () => {
  for (const h of [0, 7, 12, 17 + 20 / 60, 24]) {
    assert(Math.abs(sample(h - 1e-6) - sample(h + 1e-6)) < 1e-5);
  }
  assert.equal(sample(12), values[2]);
  assert.equal(sample(24), sample(0));
  assert.equal(sample(-1), sample(23));
});
test('all times use two adjacent maps with bounded linear weights', () => {
  for (let hour = -24; hour <= 48; hour += .017) {
    const t = lightmapBlend(hour);
    assert(t.mix >= 0 && t.mix <= 1);
    assert.equal(t.b, (t.a + 1) % 4);
    assert(t.a >= 0 && t.a < 4);
  }
});
