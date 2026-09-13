import {test} from 'node:test';import assert from 'node:assert/strict';import {eventClock} from '../src/events.ts';
test('fixed seed reproduces events and powered-off devices remain quiet',()=>{
  const a=eventClock(),b=eventClock(),off=eventClock();let count=0;
  for(let i=0;i<6000;i++){const x=a.tick(.1,{mac:true,tv:true});assert.equal(x,b.tick(.1,{mac:true,tv:true}));assert.equal(off.tick(.1,{mac:false,tv:false}),undefined);if(x)count++;}
  assert(count>0);
});
test('switching a device off cancels its event immediately',()=>{const a=eventClock();for(let i=0;i<400;i++)a.tick(.1,{mac:true,tv:false});assert.equal(a.tick(.1,{mac:false,tv:false}),undefined);});
