import * as THREE from 'three';
import type { WorldState } from './world-state';
import {fanButtonLamp, rainbowHue} from './world-state';
import type {LightFadeKey} from './light-fade';
import {eventClock} from './events';
import {audioActivity} from './audio-activity';
// `fade` is the eased 0..1 output of each device switch, owned by main.ts, so glows ramp in
// and out on the same curve as the real lights instead of popping.
export function roomLife(root: THREE.Object3D, scene: THREE.Scene, state: WorldState, fade: (key: LightFadeKey) => number = () => 1) {
  const coils: THREE.MeshStandardMaterial[]=[];
  const lampMats:{mat:THREE.MeshStandardMaterial;strength:number}[]=[];
  root.getObjectByName('INT_lamp_desk')?.traverse(o=>{if(o instanceof THREE.Mesh){const original=o.material as THREE.MeshStandardMaterial;if(original.emissive?.getHex()){const m=original.clone();o.material=m;lampMats.push({mat:m,strength:m.emissiveIntensity});}}});
  // Shade materials are shared with static props in Blender (paper/cream are used by
  // 140+ meshes), so each lamp shade gets a private clone that keeps the baked lightmap
  // and still glows on its own. main.ts keeps these meshes out of the static batch.
  const shadeGlow = (list:{mat:THREE.MeshStandardMaterial;strength:number}[],name:string,color:string,strength:number,toneMapped=true) => {
    const shade=root.getObjectByName(name);
    if(!(shade instanceof THREE.Mesh)||Array.isArray(shade.material))return;
    const original=shade.material as THREE.MeshStandardMaterial,m=original.clone();
    m.onBeforeCompile=original.onBeforeCompile;m.customProgramCacheKey=original.customProgramCacheKey;
    m.emissive.set(color);m.emissiveIntensity=0;m.toneMapped=toneMapped;
    shade.material=m;list.push({mat:m,strength});
  };
  const ceilingGlow:{mat:THREE.MeshStandardMaterial;strength:number}[]=[];
  shadeGlow(ceilingGlow,'Ceiling_Shade','#ffb469',.9);
  // The bedtime shade is small paper, so it needs the desk lamp's authored glow level (3)
  // and a bypass of ACES to stay a warm lit surface instead of washing out to beige.
  const bedsideGlow:{mat:THREE.MeshStandardMaterial;strength:number}[]=[];
  shadeGlow(bedsideGlow,'Nightlight_Shade','#ffd2a0',3,false);
  // The pole lamps were authored with the warm emissive lens material, so they keep it
  // and only get dimmed by their own slider.
  const streetGlow:{mat:THREE.MeshStandardMaterial;strength:number}[]=[];
  shadeGlow(streetGlow,'Exterior_StreetLamp_Lens_F','#ff8f3a',2.4);
  shadeGlow(streetGlow,'Exterior_StreetLamp_Lens_B','#ff8f3a',2.4);
  // Lava-lamp wax and string-light bulbs share their Blender materials with static
  // props (MAT_P2_Terracotta / MAT_P2_Cream), so they each get a private clone whose
  // glow follows the panel sliders. The bulbs batch into one mesh in main.ts.
  const lavaGlow:{mat:THREE.MeshStandardMaterial;strength:number}[]=[];
  const wax:THREE.Mesh[]=[];
  root.traverse(o=>{if(o instanceof THREE.Mesh&&o.name.startsWith('ANIM_lava_wax_'))wax.push(o);});
  if(wax.length){
    const original=wax[0].material as THREE.MeshStandardMaterial,m=original.clone();
    m.onBeforeCompile=original.onBeforeCompile;m.customProgramCacheKey=original.customProgramCacheKey;
    m.emissive.set('#ff7a3c');m.emissiveIntensity=0;
    for(const block of wax)block.material=m;
    lavaGlow.push({mat:m,strength:1.2});
  }
  // The fan's base carries its physical switch row: the two cream buttons pick the speeds
  // and the red one stops it. They sit outside the fan root and share their Blender
  // materials with 200+ props, so each gets its own clone (keeping the baked lightmap
  // shader) and main.ts keeps them out of the static batch. One of them lights per state.
  const fanButtons:THREE.MeshStandardMaterial[]=[];
  {
    const meshes:THREE.Mesh[]=[];
    root.traverse(o=>{if(o instanceof THREE.Mesh&&/^Fan_BaseButton/.test(o.name)&&!Array.isArray(o.material))meshes.push(o);});
    // Read the row the way the room sees it: left to right across the base.
    const places=meshes.map(mesh=>({mesh,x:new THREE.Box3().setFromObject(mesh).getCenter(new THREE.Vector3()).x}));
    places.sort((a,b)=>a.x-b.x);
    for(const {mesh} of places){
      const original=mesh.material as THREE.MeshStandardMaterial,m=original.clone();
      m.onBeforeCompile=original.onBeforeCompile;m.customProgramCacheKey=original.customProgramCacheKey;
      m.emissive.set('#000000');m.emissiveIntensity=0;m.toneMapped=false;
      mesh.material=m;fanButtons.push(m);
    }
  }
  // 摇头 is part of running the fan rather than a switch of its own: the head sways while the
  // blades turn, wider and quicker with each speed, and eases back to centre when it stops.
  const fanHead=root.getObjectByName('ANIM_fan_head');
  const fanSwing=[0,.5,.62],fanRate=[.55,.55,.8];
  let fanSway=0,fanPhase=0;
  // The globe keeps a faint light of its own, day and night. Its continents are their own facets
  // inside Globe_Sphere (the MAT_P2_Sage primitive of a multi-material mesh), so an emissive on that
  // material reads as a map of softly lit land — no texture needed, and the oceans stay dark.
  // The sphere is kept out of static batching in main.ts, because a batch renders its own copy of
  // the geometry and hides these source meshes — a glow set here would never be drawn.
  // Deliberately emissive only: a real light here spills onto the wall behind the shelf, which reads
  // as the wall glowing rather than the globe.
  const globeLand:{mat:THREE.MeshStandardMaterial;strength:number}[]=[];
  root.getObjectByName('Globe_Sphere')?.traverse(o=>{
    if(!(o instanceof THREE.Mesh)||Array.isArray(o.material))return;
    const original=o.material as THREE.MeshStandardMaterial;
    if(original.name!=='MAT_P2_Sage')return;
    const m=original.clone();
    m.onBeforeCompile=original.onBeforeCompile;m.customProgramCacheKey=original.customProgramCacheKey;
    m.emissive.set('#ffcf8f');m.emissiveIntensity=0;m.toneMapped=false;
    o.material=m;globeLand.push({mat:m,strength:.18});
  });
  // One soft radial sprite drives every additive halo in the room.
  const haloTexture = (() => {
    const canvas=document.createElement('canvas');canvas.width=canvas.height=64;
    const hc=canvas.getContext('2d')!,g=hc.createRadialGradient(32,32,0,32,32,31);
    g.addColorStop(0,'rgba(255,255,255,.95)');g.addColorStop(.35,'rgba(255,255,255,.35)');g.addColorStop(1,'rgba(255,255,255,0)');
    hc.fillStyle=g;hc.fillRect(0,0,64,64);
    const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;return texture;
  })();
  // The pole lamps face downwards, so a camera-facing halo carries their glow from the
  // high room camera where the lens itself is hidden behind its own head.
  const streetHaloPositions:number[]=[];
  for(const name of ['LIGHT_street_lamp_F','LIGHT_street_lamp_B']){
    const anchor=root.getObjectByName(name);
    if(anchor)anchor.getWorldPosition(new THREE.Vector3()).toArray(streetHaloPositions,streetHaloPositions.length);
  }
  let streetHalo:THREE.Points|undefined,streetHaloColors:THREE.BufferAttribute|undefined;
  if(streetHaloPositions.length){
    const geometry=new THREE.BufferGeometry();
    geometry.setAttribute('position',new THREE.Float32BufferAttribute(streetHaloPositions,3));
    streetHaloColors=new THREE.BufferAttribute(new Float32Array(streetHaloPositions.length),3);
    geometry.setAttribute('color',streetHaloColors);
    streetHalo=new THREE.Points(geometry,new THREE.PointsMaterial({size:.22,map:haloTexture,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,vertexColors:true,sizeAttenuation:true,toneMapped:false}));
    streetHalo.name='StreetLampHalo';streetHalo.frustumCulled=false;scene.add(streetHalo);
  }
  // The window string lights act like a neon run: every bulb gets its own material and a
  // shared additive halo, so each bulb glows on its own and the strip can chase, blink and
  // take a custom colour. main.ts keeps these bulbs out of the static batch (dynamicMesh).
  const stripBulbs:{mat:THREE.MeshStandardMaterial;phase:number}[]=[];
  const bulbMeshes:THREE.Mesh[]=[];
  root.traverse(o=>{if(o instanceof THREE.Mesh&&o.name.startsWith('StringLights_Bulb_'))bulbMeshes.push(o);});
  bulbMeshes.sort((a,b)=>a.getWorldPosition(new THREE.Vector3()).x-b.getWorldPosition(new THREE.Vector3()).x);
  const haloPositions=new Float32Array(bulbMeshes.length*3);
  for(const [i,bulb] of bulbMeshes.entries()){
    const original=bulb.material as THREE.MeshStandardMaterial,m=original.clone();
    m.onBeforeCompile=original.onBeforeCompile;m.customProgramCacheKey=original.customProgramCacheKey;
    // Bypass ACES on the bulbs so the neon colour stays saturated instead of washing to white.
    m.toneMapped=false;m.emissiveIntensity=0;
    bulb.material=m;
    stripBulbs.push({mat:m,phase:bulbMeshes.length>1?i/(bulbMeshes.length-1):0});
    bulb.getWorldPosition(new THREE.Vector3()).toArray(haloPositions,i*3);
  }
  let stripHalo:THREE.Points|undefined,stripHaloColors:THREE.BufferAttribute|undefined;
  if(bulbMeshes.length){
    const geometry=new THREE.BufferGeometry();
    geometry.setAttribute('position',new THREE.BufferAttribute(haloPositions,3));
    stripHaloColors=new THREE.BufferAttribute(new Float32Array(bulbMeshes.length*3),3);
    geometry.setAttribute('color',stripHaloColors);
    stripHalo=new THREE.Points(geometry,new THREE.PointsMaterial({size:.072,map:haloTexture,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,vertexColors:true,sizeAttenuation:true,toneMapped:false}));
    stripHalo.name='StripHalo';stripHalo.frustumCulled=false;scene.add(stripHalo);
  }
  const neon=new THREE.Color();let appliedNeon='';
  const bulbColor=new THREE.Color();
  const stripHsl={h:0,s:0,l:0},stripBase=new THREE.Color();
  // 0 on the rate slider keeps the strip steady. Above that it either blinks as a whole
  // (with a slight stagger along the wire) or, in chase mode, runs a comet bulb by bulb.
  const stripWave=(phase:number,now:number)=>{
    const rate=state.strip.blink;
    if(rate<=0)return 1;
    if(state.strip.chase){
      const wrapped=((now*rate-phase)%1+1)%1;
      const away=Math.min(wrapped,1-wrapped);
      const pulse=Math.max(0,1-away/.22);
      return .12+.88*pulse*pulse;
    }
    return .15+.85*(.5+.5*Math.cos(2*Math.PI*(now*rate-phase*.15)));
  };
  root.traverse(o=>{if(o instanceof THREE.Mesh&&o.name.startsWith('EMIT_heater_coil')){const m=(o.material as THREE.MeshStandardMaterial).clone();o.material=m;coils.push(m);}});
  const screens: {mesh: THREE.Mesh; mat: THREE.MeshStandardMaterial; canvas: HTMLCanvasElement; ctx: CanvasRenderingContext2D; texture: THREE.CanvasTexture; tv:boolean}[]=[];
  for(const name of ['EMIT_screen_mac','EMIT_screen_crt','EMIT_screen_scope','EMIT_screen_flip']) {
    const mesh=root.getObjectByName(name) as THREE.Mesh;
    if(!mesh)continue;
    const mat=(mesh.material as THREE.MeshStandardMaterial).clone();mesh.material=mat;
    const canvas=document.createElement('canvas');canvas.width=256;canvas.height=192;
    const texture=new THREE.CanvasTexture(canvas);texture.flipY=false;texture.colorSpace=THREE.SRGBColorSpace;texture.magFilter=THREE.NearestFilter;
    const uv=mesh.geometry.getAttribute('uv');
    if(uv){let u0=Infinity,v0=Infinity,u1=-Infinity,v1=-Infinity;for(let i=0;i<uv.count;i++){u0=Math.min(u0,uv.getX(i));u1=Math.max(u1,uv.getX(i));v0=Math.min(v0,uv.getY(i));v1=Math.max(v1,uv.getY(i));}if(u1>u0&&v1>v0){texture.repeat.set(1/(u1-u0),1/(v1-v0));texture.offset.set(-u0/(u1-u0),-v0/(v1-v0));}}
    mat.map=texture;mat.emissiveMap=texture;mat.emissive.set('#ffffff');mat.emissiveIntensity=.8;
    screens.push({mesh,mat,canvas,ctx:canvas.getContext('2d')!,texture,tv:name.endsWith('crt')});
  }
  const count=180,xyz=new Float32Array(count*3);
  for(let i=0;i<count;i++){xyz[i*3]=-2+Math.random()*4;xyz[i*3+1]=Math.random()*4;xyz[i*3+2]=-2.5-Math.random()*.6;}
  const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.BufferAttribute(xyz,3));
  const mat=new THREE.PointsMaterial({color:'#c5dce7',size:.018,transparent:true,opacity:0,depthWrite:false});
  const particles=new THREE.Points(geo,mat);particles.frustumCulled=false;scene.add(particles);
  const seasonal: {material:THREE.MeshStandardMaterial;base:THREE.Color}[]=[];
  const seen=new Set<THREE.Material>();
  root.traverse(o=>{if(o instanceof THREE.Mesh){for(const m of Array.isArray(o.material)?o.material:[o.material])if(m instanceof THREE.MeshStandardMaterial&&!seen.has(m)&&m.name==='MAT_Runtime_Canopy'){seen.add(m);seasonal.push({material:m,base:m.color.clone()});}}});
  let elapsed=0,lastFrame=-1,lastPower='',fallSpeed=1.9;
  const events=eventClock();
  const movers:{o:THREE.Object3D;p:THREE.Vector3;r:THREE.Euler}[]=[];
  root.traverse(o=>{if(/^ANIM_(plant_|windchime|blinds_|lava_wax_|speaker_)/.test(o.name))movers.push({o,p:o.position.clone(),r:o.rotation.clone()});});
  const steamCanvas=document.createElement('canvas');steamCanvas.width=64;steamCanvas.height=64;
  const sc=steamCanvas.getContext('2d')!,gradient=sc.createRadialGradient(32,32,0,32,32,31);gradient.addColorStop(0,'rgba(240,230,212,.7)');gradient.addColorStop(1,'rgba(240,230,212,0)');sc.fillStyle=gradient;sc.fillRect(0,0,64,64);
  const steamTex=new THREE.CanvasTexture(steamCanvas);
  const wisps:{sprite:THREE.Sprite;base:THREE.Vector3;offset:number;kettle:boolean}[]=[];
  for(const name of ['SOCKET_steam_coffee','SOCKET_steam_kettle']){const socket=root.getObjectByName(name);if(!socket)continue;const base=socket.getWorldPosition(new THREE.Vector3());for(let i=0;i<3;i++){const sprite=new THREE.Sprite(new THREE.SpriteMaterial({map:steamTex,transparent:true,depthWrite:false,opacity:0}));scene.add(sprite);wisps.push({sprite,base,offset:i/3,kettle:name.endsWith('kettle')});}}
  let nextGust=7,gustStart=-100;
  return {
    update(dt:number) {
      elapsed+=dt;
      const event=events.tick(dt,state.devices);
      if(elapsed>nextGust){gustStart=elapsed;nextGust=elapsed+25+Math.sin(elapsed*1.73)*10;window.dispatchEvent(new Event('room-gust'));}
      const gustAge=elapsed-gustStart,gust=gustAge<7?Math.sin(Math.PI*gustAge/7)**2:0;
      for(const m of movers){m.o.position.copy(m.p);m.o.rotation.copy(m.r);
        if(m.o.name.startsWith('ANIM_plant'))m.o.rotation.z+=Math.sin(elapsed*2.7)*gust*.085;
        if(m.o.name==='ANIM_windchime')m.o.rotation.z+=Math.sin(elapsed*3.8)*gust*.085;
        if(m.o.name.startsWith('ANIM_blinds'))m.o.rotation.x+=Math.sin(elapsed*2.2)*gust*.025;
        if(m.o.name.startsWith('ANIM_lava'))m.o.position.y+=Math.sin(elapsed*.48+Number(m.o.name.slice(-1))*2)*.012;
        if(m.o.name.startsWith('ANIM_speaker')&&audioActivity.playing)m.o.rotation.x+=Math.sin(audioActivity.time()*76/60*Math.PI*2)*.013;
      }
      for(const w of wisps){const t=(elapsed*.24+w.offset)%1;w.sprite.position.copy(w.base).add(new THREE.Vector3(Math.sin(t*5+w.offset)*.018,t*.24,0));w.sprite.scale.setScalar(.045+t*.085);(w.sprite.material as THREE.SpriteMaterial).opacity=(w.kettle&&!state.devices.heater?0:1)*Math.sin(t*Math.PI)*.48;}
      for(const m of coils)m.emissiveIntensity=THREE.MathUtils.damp(m.emissiveIntensity,2.5*fade('heater'),2,dt);
      for(const m of lampMats)m.mat.emissiveIntensity=THREE.MathUtils.damp(m.mat.emissiveIntensity,m.strength*state.levels.lamp*fade('lamp'),3,dt);
      for(const m of ceilingGlow)m.mat.emissiveIntensity=THREE.MathUtils.damp(m.mat.emissiveIntensity,m.strength*state.levels.ceilingLamp*fade('ceilingLamp'),3,dt);
      for(const m of bedsideGlow)m.mat.emissiveIntensity=THREE.MathUtils.damp(m.mat.emissiveIntensity,m.strength*state.levels.bedsideLamp*fade('bedsideLamp'),3,dt);
      for(const m of streetGlow)m.mat.emissiveIntensity=THREE.MathUtils.damp(m.mat.emissiveIntensity,m.strength*state.levels.streetLamp*fade('streetLamp'),3,dt);
      const streetLevel=state.levels.streetLamp*fade('streetLamp');
      if(streetHalo)streetHalo.visible=streetLevel>0;
      if(streetHaloColors){const warm=streetLevel*streetLevel;for(let i=0;i<streetHaloColors.count;i++)streetHaloColors.setXYZ(i,warm*.96,warm*.54,warm*.22);streetHaloColors.needsUpdate=true;}
      for(const m of lavaGlow)m.mat.emissiveIntensity=THREE.MathUtils.damp(m.mat.emissiveIntensity,m.strength*state.levels.lavaLamp*fade('lavaLamp'),3,dt);
      // Fan: the head sweeps while it runs, and the base row reads back the state — red on the
      // stop button when it is still, amber on whichever speed button is holding it on.
      if(fanHead){
        const speed=state.devices.fanSpeed;
        fanSway=THREE.MathUtils.damp(fanSway,speed?fanSwing[speed]:0,2.2,dt);
        fanPhase+=dt*fanRate[speed||1];
        fanHead.rotation.y=Math.sin(fanPhase)*fanSway;
      }
      const lit=fanButtonLamp(state.devices.fanSpeed);
      for(const [i,m] of fanButtons.entries()){
        if(i===lit.button)m.emissive.set(lit.color);
        m.emissiveIntensity=THREE.MathUtils.damp(m.emissiveIntensity,i===lit.button?lit.intensity:0,6,dt);
      }
      // The globe fades up once and then stays: a steady, faint land glow, not another switch.
      for(const g of globeLand)g.mat.emissiveIntensity=THREE.MathUtils.damp(g.mat.emissiveIntensity,g.strength,1.2,dt);
      // Neon strip: every bulb carries its own material and halo, so the whole run reacts
      // to the colour picker, the auto hue cycle, the blink rate and the chase. The rainbow
      // ramp gives each bulb its own hue, so the chase travels through a colour gradient.
      const stripLevel=state.levels.stringLights*fade('stringLights');
      const rainbow=state.strip.rainbow;
      const neonKey=`${state.strip.color}:${state.strip.cycle}:${rainbow}`;
      if(neonKey!==appliedNeon||state.strip.cycle){
        appliedNeon=neonKey;
        stripBase.set(state.strip.color);
        stripBase.getHSL(stripHsl,THREE.SRGBColorSpace);
        neon.copy(stripBase);
        if(state.strip.cycle){
          // Rotate only the hue, so the picked colour keeps its own saturation and lightness.
          neon.setHSL((stripHsl.h+elapsed*.11)%1,stripHsl.s,stripHsl.l,THREE.SRGBColorSpace);
        }
        if(!rainbow)for(const b of stripBulbs)b.mat.emissive.copy(neon);
      }
      if(stripHalo)stripHalo.visible=stripLevel>0;
      for(const [i,b] of stripBulbs.entries()){
        const level=stripLevel*stripWave(b.phase,elapsed);
        b.mat.emissiveIntensity=level*2.6;
        if(rainbow){
          // Bulb 0 starts at the picked colour and the ramp walks the wheel from there; with
          // the hue cycle on the whole rainbow slides, so the gradient flows along the wire.
          bulbColor.setHSL(rainbowHue(stripHsl.h,b.phase,state.strip.cycle?elapsed*.11:0),stripHsl.s,stripHsl.l,THREE.SRGBColorSpace);
          b.mat.emissive.copy(bulbColor);
        }
        const glow=rainbow?bulbColor:neon;
        if(stripHaloColors)stripHaloColors.setXYZ(i,glow.r*level*level,glow.g*level*level,glow.b*level*level);
      }
      if(stripHaloColors)stripHaloColors.needsUpdate=true;
      const frame=Math.floor(elapsed*8);
      const power=`${state.devices.tv}:${state.devices.mac}:${state.levels.tv}:${state.levels.mac}`;
      if(frame!==lastFrame||power!==lastPower){lastFrame=frame;lastPower=power;for(const s of screens){
        const on=['EMIT_screen_scope','EMIT_screen_flip'].includes(s.mesh.name)||(s.tv?state.devices.tv:state.devices.mac),c=s.ctx;
        c.fillStyle=on?(s.tv?'#263c60':'#c3d1b6'):'#080c12';c.fillRect(0,0,256,192);
        s.mat.emissiveIntensity=on?.8*state.levels[s.tv?'tv':'mac']*fade(s.tv?'tv':'mac'):0;
        if(s.mesh.name==='EMIT_screen_flip'){
          const now=new Date();c.fillStyle='#242b2b';c.fillRect(0,0,256,192);c.fillStyle='#efe4c6';c.font='bold 68px monospace';c.textAlign='center';c.fillText(String(now.getMonth()+1).padStart(2,'0'),65,119);c.fillText(String(now.getDate()).padStart(2,'0'),192,119);c.font='19px monospace';c.fillText('MONTH',65,160);c.fillText('DAY',192,160);c.textAlign='start';c.fillStyle='#161b1b';c.fillRect(124,0,7,192);
        }else if(s.mesh.name==='EMIT_screen_scope'){
          c.fillStyle='#101f1b';c.fillRect(0,0,256,192);c.strokeStyle='#2e4c3e';c.lineWidth=1;for(let i=0;i<8;i++){c.beginPath();c.moveTo(i*32,0);c.lineTo(i*32,192);c.stroke();c.beginPath();c.moveTo(0,i*24);c.lineTo(256,i*24);c.stroke();}
          c.strokeStyle='#b4ec99';c.lineWidth=3;c.beginPath();for(let x=0;x<256;x++){const y=96+Math.sin(x*.065-elapsed*3)*35+Math.sin(x*.13+elapsed)*8;x?c.lineTo(x,y):c.moveTo(x,y);}c.stroke();
        }else if(on&&s.tv){
          c.fillStyle='#d99b81';c.fillRect(0,112,256,80);c.fillStyle='#f1dca2';c.fillRect(194,22,22,22);
          for(let i=0;i<8;i++){c.fillStyle='#4a7269';c.fillRect(i*40-((frame*2)%40),104-(i%3)*8,24,12);}
          const y=90-Math.abs(Math.sin(elapsed*2))*22;c.fillStyle='#f4e6ba';c.fillRect(100,y,12,12);c.fillStyle='#ba6267';c.fillRect(98,y+12,16,15);c.fillStyle='#263443';c.fillRect(98,y+27,6,5);c.fillRect(109,y+27,6,5);
          c.fillStyle='#f2dfaa';c.font='10px monospace';c.fillText('LITTLE EVENING   001',12,15);
        } else if(on){
          c.fillStyle='#13231d';c.fillRect(0,0,256,192);c.fillStyle='#98cfa1';c.font='12px monospace';
          const lines=['$ room --listen','[ok] loading memories','sync /home/window','render sunset .. done','audio buffer ready','read diary.txt','[ok] world is quiet','compile little dreams'];
          const row=Math.floor(elapsed*7),scroll=(elapsed*7%1)*17;
          for(let i=0;i<13;i++)c.fillText(lines[(row+i)%lines.length],8,i*17-scroll);
        }
        if(on&&event==='mac-note'&&s.mesh.name==='EMIT_screen_mac'){c.fillStyle='#f1ddba';c.fillRect(35,68,190,64);c.strokeStyle='#455448';c.strokeRect(35,68,190,64);c.fillStyle='#455448';c.font='12px monospace';c.fillText('Time for a little',47,93);c.fillText('stretch.',47,112);}
        if(on&&event==='tv-static'&&s.tv){for(let i=0;i<20;i++){c.fillStyle=i%2?'#87948b':'#293e4b';c.fillRect(0,(i*13+frame*7)%192,256,3);}}
        s.texture.needsUpdate=true;
      }}
      const wet=['drizzle','rain','storm','snow'].includes(state.weather);
      mat.opacity=THREE.MathUtils.damp(mat.opacity,wet?(state.weather==='drizzle'?.25:.65):0,1,dt);mat.size=THREE.MathUtils.damp(mat.size,state.weather==='snow'?.035:.015,.7,dt);
      fallSpeed=THREE.MathUtils.damp(fallSpeed,state.weather==='snow'?.24:1.9,.7,dt);
      for(let i=0;i<count;i++){xyz[i*3+1]-=dt*fallSpeed;if(xyz[i*3+1]<0)xyz[i*3+1]=4;}
      geo.attributes.position.needsUpdate=true;
      const target=new THREE.Color({spring:'#81a16a',summer:'#557b55',autumn:'#b0764b',winter:'#83938a'}[state.season]);
      for(const s of seasonal)s.material.color.lerp(state.season==='autumn'?s.base:target,1-Math.exp(-dt*.5));
    },
  };
}
