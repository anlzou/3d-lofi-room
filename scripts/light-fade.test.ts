import {test} from 'node:test';
import assert from 'node:assert/strict';
import {lightFade,lightFadeKeys,type LightFadeKey} from '../src/light-fade.ts';
import {lightKeys} from '../src/world-state.ts';

const devices = (on: LightFadeKey[] = []) => Object.fromEntries(lightFadeKeys.map(k => [k, on.includes(k)])) as Record<LightFadeKey, boolean>;

test('light fade starts where the room already is',()=>{
  const fade=lightFade(devices(['lamp','streetLamp']));
  assert.equal(fade.value('lamp'),1);assert.equal(fade.value('streetLamp'),1);
  assert.equal(fade.value('ceilingLamp'),0);assert.equal(fade.value('heater'),0);
});
test('showcase turns fade in and out instead of popping',()=>{
  const fade=lightFade(devices());
  const target=devices(['ceilingLamp']);
  fade.update(.1,target,true);
  const early=fade.value('ceilingLamp');
  assert(early>0&&early<.2,`a tenth of a second should barely light up, got ${early}`);
  let previous=early;
  for(let i=0;i<20;i++){
    fade.update(.1,target,true);
    const value=fade.value('ceilingLamp');
    assert(value>=previous,'the fade must never step back');assert(value<=1,'the fade must never overshoot');
    previous=value;
  }
  assert(previous>.6&&previous<1,`two seconds in it should be mostly lit, got ${previous}`);
  // It settles exactly on the switch, so a lamp reaches full output and a true zero.
  for(let i=0;i<400;i++)fade.update(.05,target,true);
  assert.equal(fade.value('ceilingLamp'),1);
  for(let i=0;i<400;i++)fade.update(.05,devices(),true);
  assert.equal(fade.value('ceilingLamp'),0);
});
test('manual taps stay quick while showcase takes its time',()=>{
  const manual=lightFade(devices()),gentle=lightFade(devices());
  const target=devices(['lamp']);
  manual.update(.25,target,false);gentle.update(.25,target,true);
  assert(manual.value('lamp')>.8,`a tapped switch should be almost there, got ${manual.value('lamp')}`);
  assert(gentle.value('lamp')<.2,`showcase should still be rising, got ${gentle.value('lamp')}`);
});
test('every switch that drives light has its own fade value',()=>{
  // The list is written out in light-fade.ts, so this is what keeps it in step with the
  // device switches the panel and the room agree on.
  const faded=new Set<string>(lightFadeKeys);
  for(const key of lightKeys)assert(faded.has(key),`${key} needs a fade`);
  assert(faded.has('heater'),'the heater coil glows too');
  assert.equal(lightFadeKeys.length,lightKeys.length+1,'one fade per light plus the heater');
  const fade=lightFade(devices(['tv','mac']));
  assert.equal(Object.keys(fade.snapshot()).length,lightFadeKeys.length);
  assert.equal(fade.value('tv'),1);assert.equal(fade.value('mac'),1);
});
