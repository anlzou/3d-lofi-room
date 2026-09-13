import * as THREE from 'three';
import type {WorldState} from './world-state';
export function touchFeedback(root:THREE.Object3D,scene:THREE.Scene,state:WorldState){
 const get=(name:string)=>root.getObjectByName(name);
 const drawer=get('ANIM_drawer_upper'),phone=get('ANIM_phone'),bin=get('ANIM_bin'),paper=get('ANIM_bin_paper'),globe=get('ANIM_globe');
 const bases=new Map<THREE.Object3D,THREE.Vector3>();for(const o of [drawer,phone,bin,paper])if(o)bases.set(o,o.position.clone());
 const slats: {o:THREE.Object3D;y:number;x:number;index:number}[]=[];
 root.traverse(o=>{if(o.name.startsWith('ANIM_blinds_slat_'))slats.push({o,y:o.position.y,x:o.rotation.x,index:Number(o.name.slice(-2))});});
 let open=true,blindsOpen=true,blind=0,phoneTime=10,binTime=10,globeSpeed=.22;
 const flashes:{m:THREE.MeshStandardMaterial;color:THREE.Color;strength:number;time:number}[][]=[];
 for(const name of ['INT_mecha_A','INT_mecha_B']){const list:typeof flashes[number]=[];get(name)?.traverse(o=>{if(o instanceof THREE.Mesh&&!Array.isArray(o.material)){const original=o.material as THREE.MeshStandardMaterial,m=original.clone();m.onBeforeCompile=original.onBeforeCompile;m.customProgramCacheKey=original.customProgramCacheKey;o.material=m;list.push({m,color:m.emissive.clone(),strength:m.emissiveIntensity,time:10});}});flashes.push(list);}
 const bedside=new THREE.PointLight('#ffd39a',0,2,2);const lamp=get('INT_bedside_lamp');if(lamp){lamp.getWorldPosition(bedside.position);bedside.position.y+=.2;scene.add(bedside);}
 return {
  activate(names:string[]){
   if(names.includes('ANIM_drawer_upper')){open=!open;return '抽屉'+(open?'打开':'合上');}
   if(names.some(n=>n==='ANIM_fan_head'||n==='SEASON_summer_fan')){state.devices.fanSpeed=((state.devices.fanSpeed+1)%3) as 0|1|2;return ['风扇停止','风扇慢速','风扇快速'][state.devices.fanSpeed];}
   if(names.includes('ANIM_phone')){phoneTime=0;return '电话轻轻响动';}
   if(names.includes('INT_bedside_lamp')){state.devices.bedsideLamp=!state.devices.bedsideLamp;return '床头灯'+(state.devices.bedsideLamp?'开启':'关闭');}
   if(names.includes('ANIM_globe')){globeSpeed=5.5;return '地球仪转起来了';}
   if(names.some(n=>n.startsWith('ANIM_blinds_slat_'))){blindsOpen=!blindsOpen;return blindsOpen?'百叶窗收起':'百叶窗放下';}
   if(names.includes('ANIM_bin')||names.includes('ANIM_bin_paper')){binTime=0;return '纸团轻轻跳了一下';}
   for(let i=0;i<2;i++)if(names.includes('INT_mecha_'+['A','B'][i])){for(const f of flashes[i])f.time=0;return '小小的回应';}
   return undefined;
  },
  update(dt:number){
   phoneTime+=dt;binTime+=dt;
   if(drawer)drawer.position.z=THREE.MathUtils.damp(drawer.position.z,bases.get(drawer)!.z+(open?0:-.18),8,dt);
   if(phone)phone.position.x=bases.get(phone)!.x+(phoneTime<1?Math.sin(phoneTime*65)*.008*(1-phoneTime):0);
   const jump=binTime<.6?Math.sin(binTime/.6*Math.PI)*.025:0;
   if(bin)bin.position.y=bases.get(bin)!.y+jump;
   if(paper)paper.position.y=bases.get(paper)!.y+(binTime<.75?Math.sin(binTime/.75*Math.PI)*.045:0);
   globeSpeed=THREE.MathUtils.damp(globeSpeed,.22,.85,dt);if(globe)globe.rotation.y+=dt*globeSpeed;
   blind=THREE.MathUtils.damp(blind,blindsOpen?0:1,5,dt);for(const s of slats){s.o.position.y=s.y-blind*s.index*.08;s.o.rotation.x=s.x+blind*.8;}
   bedside.intensity=THREE.MathUtils.damp(bedside.intensity,state.devices.bedsideLamp?1.8*state.levels.bedsideLamp:0,5,dt);
   for(const list of flashes)for(const f of list){f.time+=dt;const v=f.time<.65?Math.sin(f.time/.65*Math.PI)*.45:0;f.m.emissive.copy(f.color).lerp(new THREE.Color('#ffe8b1'),v);f.m.emissiveIntensity=f.strength+v;}
  }
 };
}
