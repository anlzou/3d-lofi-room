import {test} from 'node:test';import assert from 'node:assert/strict';import * as THREE from 'three';
import {touchFeedback} from '../src/touch-feedback.ts';import {createDefaultState} from '../src/world-state.ts';
test('drawer toggles without drift; garbage feedback is bounded and returns home',()=>{
 const root=new THREE.Group(),scene=new THREE.Scene(),state=createDefaultState();
 for(const name of ['ANIM_drawer_upper','ANIM_bin','ANIM_bin_paper','ANIM_blinds_slat_04']){const o=new THREE.Group();o.name=name;root.add(o);}
 const t=touchFeedback(root,scene,state),d=root.getObjectByName('ANIM_drawer_upper')!;
 t.activate(['ANIM_drawer_upper']);for(let i=0;i<120;i++)t.update(1/60);assert(Math.abs(d.position.z+.18)<.001);
 t.activate(['ANIM_drawer_upper']);for(let i=0;i<120;i++)t.update(1/60);assert(Math.abs(d.position.z)<.001);
 t.activate(['ANIM_bin']);for(let i=0;i<90;i++){t.update(1/60);assert(root.getObjectByName('ANIM_bin')!.position.y<=.0251);assert(root.getObjectByName('ANIM_bin_paper')!.position.y<=.0451);}
 assert.equal(root.getObjectByName('ANIM_bin')!.position.y,0);
 t.activate(['ANIM_blinds_slat_04']);for(let i=0;i<600;i++)t.update(1/60);assert(root.getObjectByName('ANIM_blinds_slat_04')!.rotation.x<=.8001);
});
