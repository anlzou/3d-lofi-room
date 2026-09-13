export type RoomEvent='mac-note'|'tv-static';
export function eventClock(seed=1999){
  let clock=0,next=40,active:{kind:RoomEvent;until:number}|undefined;
  const cooldown:Record<RoomEvent,number>={'mac-note':0,'tv-static':0};
  const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
  return {tick(dt:number,devices:{mac:boolean;tv:boolean}){
    clock+=Math.max(0,Math.min(dt,.25));
    if(active&&(clock>=active.until||!devices[active.kind==='mac-note'?'mac':'tv']))active=undefined;
    if(!active&&clock>=next){
      const eligible=(['mac-note','tv-static'] as RoomEvent[]).filter(k=>clock>=cooldown[k]&&devices[k==='mac-note'?'mac':'tv']);
      if(eligible.length){const kind=eligible[Math.floor(random()*eligible.length)];active={kind,until:clock+(kind==='mac-note'?5:1.2)};cooldown[kind]=clock+(kind==='mac-note'?120:180);}
      next=clock+30+random()*120;
    }
    return active?.kind;
  }};
}
