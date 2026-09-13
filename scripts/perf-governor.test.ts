import {test} from 'node:test';
import assert from 'node:assert/strict';
import {frameGovernor,pixelRatioFor,bufferRatio,governorCeiling,governorFloor} from '../src/perf-governor.ts';

// Frames the governor ignores while shaders compile; tests feed them so the real rules apply.
const WARMUP = 90;
const feed = (governor, frames, ms) => { let changes = 0; for (let i = 0; i < frames; i++) if (governor.sample(ms)) changes++; return changes; };
const warm = governor => feed(governor, WARMUP, 16);

test('a comfortable machine gets more resolution than it started with',()=>{
  const governor=frameGovernor();
  assert.equal(governor.scale(),1,'the room starts at its base ratio');
  warm(governor);
  // 60 Hz with headroom: frames report one refresh, which is room to grow.
  feed(governor,600,16.7);
  assert(governor.scale()>1.4,`a fast machine should climb, got ${governor.scale()}`);
  assert(governor.scale()<=governorCeiling);
  // It keeps climbing until the ceiling, then stops changing.
  assert.equal(feed(governor,2000,16.7),0,'no further changes at the ceiling');
});
test('a struggling machine gives up resolution and keeps away from what hurt',()=>{
  const governor=frameGovernor();
  warm(governor);
  feed(governor,600,33);
  assert(governor.scale()<.8,`a struggling machine should back off, got ${governor.scale()}`);
  assert(governor.scale()>=governorFloor,'the floor keeps the picture from going mushy');
  const hurt=governor.ceiling();
  // Frames recover, but the climb must not walk straight back into the resolution that hurt.
  feed(governor,400,16.7);
  assert(governor.scale()<=hurt,`climbed past the remembered ceiling (${hurt})`);
});
test('one long frame is smoothed away, sustained load is not',()=>{
  const governor=frameGovernor();
  warm(governor);
  // Holding a steady one-frame-per-refresh is exactly the headroom this is looking for.
  feed(governor,200,16.5);
  const grown=governor.scale();
  assert(grown>1,'a machine keeping up should have been given more resolution');
  // One hitch lifts the average but does not cross the struggling threshold on its own.
  governor.sample(34);
  assert(governor.scale()>=grown,'one hitch must not drop the resolution');
  // A single very long frame (a tab switch, a texture upload) is an outlier too.
  governor.sample(400);
  assert(governor.scale()>=grown,'one very long frame must not drop the resolution either');
});
test('one bad patch does not cap the picture for the rest of the session',()=>{
  const governor=frameGovernor();
  warm(governor);
  feed(governor,600,33);
  const hurt=governor.ceiling();
  assert(hurt<governorCeiling,'sustained struggle should have capped the ceiling');
  // A minute of comfortable frames heals that memory, so the machine gets another chance.
  feed(governor,12000,5);
  assert(governor.ceiling()>hurt,`the ceiling should creep back up, still ${governor.ceiling()}`);
  assert(governor.ceiling()<=governorCeiling);
  assert(governor.scale()>hurt,'and the resolution should have followed it');
});
test('every step is spaced out, so the buffer is never resized in bursts',()=>{
  for(const ms of [16.7,30]){
    const governor=frameGovernor();
    warm(governor);
    let frames=0,steps=0,last=-1;
    while(frames<4000&&steps<3){
      frames++;
      if(governor.sample(ms)){
        steps++;
        if(last>=0)assert(frames-last>4,`two steps only ${frames-last} frames apart at ${ms} ms`);
        last=frames;
      }
    }
    assert.equal(steps,3,`expected three steps at ${ms} ms`);
  }
});
test('the buffer is capped by area, and starts at the device pixels',()=>{
  // A laptop screen keeps its own device pixels, up to the 1.5x ceiling of detail.
  assert.equal(pixelRatioFor(1280,720,2),1.5);
  assert.equal(pixelRatioFor(1280,720,1),1);
  // A larger screen hits the area cap before it hits the 1.5x ceiling.
  const capped=pixelRatioFor(1600,900,2);
  assert(Math.abs(capped-Math.sqrt(2.6e6/(1600*900)))<1e-9,`expected the area cap, got ${capped}`);
  // A 4K monitor would render four times the pixels for no visible gain, so it stops at 1x.
  assert.equal(pixelRatioFor(3840,2160,2),1);
  assert.equal(pixelRatioFor(3840,2160,.75),1,'never below one device pixel');
});
test('supersampling is allowed up to the sharpen budget and no further',()=>{
  // A 1080p-ish window: a fast machine may render at twice the base ratio.
  const base=pixelRatioFor(1280,720,1);
  assert.equal(bufferRatio(1280,720,base,2),2);
  assert.equal(bufferRatio(1280,720,base,governorFloor),base*governorFloor);
  // A 4K screen is already past the sharpen budget at 1x: no climbing, but still able to drop.
  const big=pixelRatioFor(3840,2160,1);
  assert.equal(bufferRatio(3840,2160,big,2),big,'a 4K screen must not supersample four times over');
  assert.equal(bufferRatio(3840,2160,big,governorFloor),big*governorFloor);
  // A 1440p screen has some room, just not the full doubling.
  const mid=pixelRatioFor(2560,1440,1);
  const climbed=bufferRatio(2560,1440,mid,2);
  assert(climbed>mid&&climbed<mid*2,`expected partial headroom, got ${climbed}`);
});


