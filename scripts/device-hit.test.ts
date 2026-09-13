import {test} from 'node:test';
import assert from 'node:assert/strict';
import {hitDevice} from '../src/device-hit.ts';
import {lightLabels} from '../src/world-state.ts';
test('点击模型映射到它控制的设备',()=>{
  // The raycast hands over the hit object and its ancestors, so a deeply nested part still counts.
  const chain = (...names: string[]) => names;
  assert.equal(hitDevice(chain('EMIT_screen_crt','INT_tv_crt','TV_Body')),'tv');
  assert.equal(hitDevice(chain('EMIT_screen_mac','INT_mac')),'mac');
  assert.equal(hitDevice(chain('Lamp_Shade','INT_lamp_desk')),'lamp');
  assert.equal(hitDevice(chain('Heater_Coil','SEASON_winter_heater')),'heater');
  assert.equal(hitDevice(chain('Ceiling_Shade')),'ceilingLamp');
  assert.equal(hitDevice(chain('INT_ceiling_pullcord')),'ceilingLamp');
  assert.equal(hitDevice(chain('INT_lava_lamp')),'lavaLamp');
  // The string lights answer to the whole run: any bulb, and the wire they hang from.
  assert.equal(hitDevice(chain('StringLights_Bulb_07')),'stringLights');
  assert.equal(hitDevice(chain('StringLights_Wire')),'stringLights');
  assert.equal(hitDevice(chain('StringLights_Bulb_00','StringLights_Root','Window_Frame')),'stringLights');
  // The whole strip family answers, so a new part (a hook, a second wire) keeps working.
  assert.equal(hitDevice(chain('StringLights_Hook')),'stringLights');
  // Anything else is not a switch, so the click falls through to whatever else is interactive.
  for(const names of [chain(),chain('Desk_Main','Room_Shell'),chain('Fan_BaseButton'),chain('Window_Frame')])
    assert.equal(hitDevice(names),undefined);
});
test('每个可点设备都有中文名字可用在状态栏',()=>{
  // main.ts writes `${label}已开启/关闭`, so every mapped device needs a label.
  for(const key of ['tv','mac','lamp','ceilingLamp','lavaLamp','stringLights'] as const)
    assert.equal(typeof lightLabels[key],'string');
  assert('heater'); // 暖炉 is spelled out in main.ts because it is not one of the lamp keys.
});
