import {test} from 'node:test';
import assert from 'node:assert/strict';
import {restoreState,legalWeather,seasons,weathers,lightKeys,daylightAt,showcaseAt,rainbowHue,crossedMidnight,nextShowcaseDay,showcaseStrip} from '../src/world-state.ts';
test('corrupt storage and untrusted values keep safe defaults',()=>{
  for(const raw of [null,42,'bad',{}, {schemaVersion:1,time:Infinity,season:'bad',devices:null,audio:{enabled:true,masterVolume:9}}]){
    const s=restoreState(raw);assert.equal(s.season,'autumn');assert.equal(s.audio.enabled,false);assert(Number.isFinite(s.time));assert(s.audio.masterVolume<=1);
  }
});
test('URL overrides persistence then normalizes incompatible weather',()=>{
  const s=restoreState({schemaVersion:1,season:'winter',weather:'snow',time:12,autopilot:true},'?season=summer&time=-1');
  assert.equal(s.weather,'cloudy');assert.equal(s.time,23);assert.equal(s.autopilot,false);
});
test('weather matrix permits snow only in winter and excludes winter storms',()=>{
  for(const s of seasons)for(const w of weathers){const v=legalWeather(s,w);assert(v!=='snow'||s==='winter');assert(v!=='storm'||s!=='winter');}
});
test('ceiling lamp defaults to off and only accepts persisted booleans',()=>{
  assert.equal(restoreState(null).devices.ceilingLamp,false);
  assert.equal(restoreState({schemaVersion:1,devices:{ceilingLamp:true}}).devices.ceilingLamp,true);
  assert.equal(restoreState({schemaVersion:1,devices:{ceilingLamp:'yes'}}).devices.ceilingLamp,false);
});
test('light levels default to the tuned output and are clamped to 0..1',()=>{
  const fresh=restoreState(null);
  for(const key of lightKeys)assert.equal(fresh.levels[key],1);
  const s=restoreState({schemaVersion:1,levels:{lamp:9,bedsideLamp:-3,ceilingLamp:.4,lavaLamp:'x',stringLights:null,tv:0,mac:.55}});
  assert.equal(s.levels.lamp,1);assert.equal(s.levels.bedsideLamp,0);assert.equal(s.levels.ceilingLamp,.4);
  assert.equal(s.levels.lavaLamp,1);assert.equal(s.levels.stringLights,1);assert.equal(s.levels.tv,0);assert.equal(s.levels.mac,.55);
});
test('lava lamp and string lights stay off until switched on',()=>{
  const d=restoreState(null);
  assert.equal(d.devices.lavaLamp,false);assert.equal(d.devices.stringLights,false);
  const s=restoreState({schemaVersion:1,devices:{lavaLamp:true,stringLights:true}});
  assert.equal(s.devices.lavaLamp,true);assert.equal(s.devices.stringLights,true);
});
test('street lamps ship switched on with their own level',()=>{
  const d=restoreState(null);
  assert.equal(d.devices.streetLamp,true);assert.equal(d.levels.streetLamp,1);
  const s=restoreState({schemaVersion:1,devices:{streetLamp:false},levels:{streetLamp:.4}});
  assert.equal(s.devices.streetLamp,false);assert.equal(s.levels.streetLamp,.4);
  assert.equal(restoreState({schemaVersion:1,levels:{streetLamp:4}}).levels.streetLamp,1);
});
test('string-light strip colour and blink rate are validated',()=>{
  const d=restoreState(null);
  assert.equal(d.strip.color,'#ffb266');assert.equal(d.strip.blink,0);
  assert.equal(d.strip.cycle,false);assert.equal(d.strip.chase,false);
  const ok=restoreState({schemaVersion:1,strip:{color:'#3AD8FF',blink:9,cycle:true,chase:true}});
  assert.equal(ok.strip.color,'#3ad8ff');assert.equal(ok.strip.blink,5);
  assert.equal(ok.strip.cycle,true);assert.equal(ok.strip.chase,true);
  const bad=restoreState({schemaVersion:1,strip:{color:'red',blink:-2,cycle:'yes',chase:1}});
  assert.equal(bad.strip.color,'#ffb266');assert.equal(bad.strip.blink,0);
  assert.equal(bad.strip.cycle,false);assert.equal(bad.strip.chase,false);
});
test('daylight helper tracks the same 06:00-18:00 sun arc as the renderer',()=>{
  assert.equal(daylightAt(12),1);assert.equal(daylightAt(0),0);
  // Dusk and dawn both sit below the street-lamp threshold.
  assert(daylightAt(18.5)<.35);assert(daylightAt(5.5)<.35);
  assert(daylightAt(17.5)>.35);assert(daylightAt(7)>.35);
});
test('showcase routine follows a day of work, evening and rest',()=>{
  // The strip, the lava lamp and the street lamps are night lights, so they are skipped here.
  const nightLights=['stringLights','lavaLamp','streetLamp'] as const;
  const asleep=showcaseAt(3,'autumn');
  for(const key of lightKeys)if(!nightLights.includes(key as 'stringLights'))assert.equal(asleep.devices[key],false,`${key} should be off while asleep`);
  const work=showcaseAt(10,'autumn');
  assert.equal(work.devices.lamp,true);assert.equal(work.devices.mac,true);
  assert.equal(work.devices.ceilingLamp,false);assert.equal(work.devices.tv,false);
  const evening=showcaseAt(20,'autumn');
  for(const key of ['lamp','ceilingLamp','lavaLamp','stringLights','tv','mac'] as const)assert.equal(evening.devices[key],true,`${key} should be on in the evening`);
  const bedtime=showcaseAt(23.8,'autumn');
  assert.equal(bedtime.devices.bedsideLamp,true);assert.equal(bedtime.devices.ceilingLamp,false);
  assert.equal(bedtime.devices.tv,false);assert.equal(bedtime.devices.lamp,false);
  // 23:59 and 00:01 land in different stretches of the same night.
  assert.equal(showcaseAt(23.99,'autumn').id,'wind-down');assert.equal(showcaseAt(0.01,'autumn').id,'sleep');
});
test('showcase night lights burn from dusk to dawn whatever the routine says',()=>{
  // Deep night, morning, evening and the small hours all keep them on.
  for(const h of [21,23.5,1,3,5.9]){
    const s=showcaseAt(h,'autumn');
    assert.equal(s.devices.stringLights,true,`strip at ${h}:00`);
    assert.equal(s.devices.lavaLamp,true,`lava lamp at ${h}:00`);
  }
  // Daylight, including the stretches where people are home, keeps them off.
  for(const h of [7.4,12,15,17]){
    const s=showcaseAt(h,'autumn');
    assert.equal(s.devices.stringLights,false,`strip at ${h}:00`);
    assert.equal(s.devices.lavaLamp,false,`lava lamp at ${h}:00`);
  }
  // They come on with dusk and go out with sunrise, together with the street lamps.
  // The threshold sits near 17:57 and 06:08, so 18:36 and 06:18 are safely inside each side.
  const dusk=showcaseAt(18.6,'autumn'),dawn=showcaseAt(6.3,'autumn');
  assert.equal(dusk.devices.stringLights,true);assert.equal(dusk.devices.streetLamp,true);
  assert.equal(dawn.devices.stringLights,false);assert.equal(dawn.devices.streetLamp,false);
});
test('showcase street lamps answer to the sun rather than the clock',()=>{
  assert.equal(showcaseAt(22,'autumn').devices.streetLamp,true);
  assert.equal(showcaseAt(3,'summer').devices.streetLamp,true);
  assert.equal(showcaseAt(12,'autumn').devices.streetLamp,false);
  assert.equal(showcaseAt(18.6,'autumn').devices.streetLamp,true);
});
test('showcase comfort rules respect season and weather',()=>{
  const winterEvening=showcaseAt(20,'winter');
  assert.equal(winterEvening.devices.heater,true);assert.equal(winterEvening.devices.windowOpen,false);
  assert.equal(showcaseAt(3,'winter').devices.heater,false,'nobody heats an empty room at 03:00');
  const summerNoon=showcaseAt(13,'summer');
  assert.equal(summerNoon.devices.fanSpeed,2);assert.equal(summerNoon.devices.heater,false);
  assert.equal(summerNoon.devices.windowOpen,true);
  assert.equal(showcaseAt(13,'autumn','rain').devices.windowOpen,false);
  assert.equal(showcaseAt(13,'autumn').devices.fanSpeed,0);
});
test('every camera preset is accepted and anything else falls back to the wide shot',()=>{
  for(const camera of ['room','desk','window','tv'])assert.equal(restoreState({schemaVersion:1,camera}).camera,camera);
  assert.equal(restoreState({schemaVersion:1,camera:'sofa'}).camera,'room');
  assert.equal(restoreState({schemaVersion:1,camera:9}).camera,'room');
  assert.equal(restoreState(null).camera,'room');
});
test('a fresh room opens at 11:30 with the showcase already running',()=>{
  const fresh=restoreState(null);
  assert(Math.abs(fresh.time-(11+30/60))<1e-6,'the first visit should start at 11:30');
  assert.equal(fresh.showcase,true,'展示模式 is the default mode');
  // A stored choice still wins, and a nonsense value falls back to the default.
  assert.equal(restoreState({schemaVersion:1,showcase:false}).showcase,false);
  assert.equal(restoreState({schemaVersion:1,time:22,showcase:false}).time,22);
  assert.equal(restoreState({schemaVersion:1,showcase:'yes'}).showcase,true);
});
test('rainbow ramp walks the hue wheel from the first bulb to the last',()=>{
  // Bulb 0 keeps the picked hue, every later bulb sits further along the wheel.
  assert(Math.abs(rainbowHue(.2,0)-.2)<1e-9);
  const ramp=[0,.25,.5,.75,1].map(p=>rainbowHue(0,p));
  for(let i=1;i<ramp.length;i++)assert(ramp[i]>ramp[i-1],'the ramp must rise bulb by bulb');
  assert(Math.abs(rainbowHue(.95,1)-.8)<1e-9,'the ramp wraps past the top of the wheel');
  assert(rainbowHue(.2,.5,.1)>rainbowHue(.2,.5),'drift slides the whole rainbow');
  assert.equal(rainbowHue(-.1,.5),rainbowHue(.9,.5),'negative hues wrap the same way');
});
test('strip rainbow flag only accepts persisted booleans',()=>{
  assert.equal(restoreState(null).strip.rainbow,false);
  assert.equal(restoreState({schemaVersion:1,strip:{rainbow:true}}).strip.rainbow,true);
  assert.equal(restoreState({schemaVersion:1,strip:{rainbow:'yes'}}).strip.rainbow,false);
});
test('展示模式 hands the strip a rainbow that chases',()=>{
  const look=showcaseStrip({color:'#3ad8ff',blink:0,cycle:false,chase:false,rainbow:false});
  assert.equal(look.rainbow,true,'every bulb should get its own hue');
  assert.equal(look.cycle,true,'and the ramp should keep drifting');
  assert.equal(look.chase,true,'lit in sequence');
  assert.equal(look.blink,1,'a stopped strip would make the chase look broken');
  assert.equal(look.color,'#3ad8ff','the picked colour stays as the rainbow base');
  const paced=showcaseStrip({color:'#ffb266',blink:3,cycle:false,chase:false,rainbow:false});
  assert.equal(paced.blink,3,'a pace the user already chose is left alone');
});
test('a new showcase day starts when the clock wraps past midnight',()=>{
  assert.equal(crossedMidnight(23.9,0.02),true);assert.equal(crossedMidnight(20.5,3.9),true);
  // Moving around inside a day is not a new day.
  assert.equal(crossedMidnight(20,3),false);assert.equal(crossedMidnight(23,23.5),false);
  assert.equal(crossedMidnight(4,1),false);assert.equal(crossedMidnight(12,11.5),false);
});
test('each showcase day steps to the next season with legal, different weather',()=>{
  for(const season of seasons){
    const expected=seasons[(seasons.indexOf(season)+1)%seasons.length];
    for(const roll of [0,.25,.5,.75,.999]){
      const day=nextShowcaseDay(season,'clear',roll);
      assert.equal(day.season,expected,'the seasons must cycle in order');
      assert.notEqual(day.weather,'clear','the weather should change from one day to the next');
      assert.equal(legalWeather(day.season,day.weather),day.weather,`${day.weather} is not legal in ${day.season}`);
    }
  }
  // Snow only ever arrives with winter, and winter never gets a storm.
  for(const roll of [0,.3,.6,.9])assert.notEqual(nextShowcaseDay('autumn','clear',roll).weather,'snow');
  const pick=nextShowcaseDay('spring','snow',0);
  assert.equal(pick.weather,legalWeather('spring',pick.weather));
  assert.equal(nextShowcaseDay('winter','storm',0).weather,nextShowcaseDay('winter','storm',0).weather,'the roll decides, so it is repeatable');
});
