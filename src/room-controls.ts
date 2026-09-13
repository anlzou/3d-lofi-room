import { restoreState, legalWeather, seasons, weathers, seasonLabels, seasonMottos, weatherLabels, lightKeys, lightLabels, type Season, type Weather, type LightKey } from './world-state';
import {audioActivity} from './audio-activity';
export function roomControls(onChange: () => void) {
  let raw: unknown;
  try { raw = JSON.parse(localStorage.getItem('lofi-room-v1') ?? 'null'); } catch { /* Private storage may be unavailable. */ }
  const state = restoreState(raw, location.search);
  const panel = document.createElement('details'); panel.className = 'room-panel';
  const stripExtra = `<div class="lamp-extra"><input type="color" data-color="stringLights" aria-label="串灯颜色" title="串灯颜色" /><input type="range" class="blink" min="0" max="5" step="0.1" data-blink="stringLights" aria-label="串灯节奏" /><output class="blink-value" data-blink-value="stringLights">常亮</output></div><div class="lamp-flags"><button data-flag="cycle" aria-pressed="false">自动变色</button><button data-flag="chase" aria-pressed="false">顺序点亮</button><button data-flag="rainbow" aria-pressed="false" title="每个灯泡颜色不同，沿灯串渐变过渡">彩虹</button></div>`;
  const lampRow = (key: LightKey) => `<div class="lamp-entry" data-row="${key}"><div class="lamp-row"><span class="lamp-name">${lightLabels[key]}</span><button class="switch" data-device="${key}" aria-pressed="false" aria-label="${lightLabels[key]}开关"><span></span></button><input class="level" type="range" min="0" max="100" step="5" data-level="${key}" aria-label="${lightLabels[key]}强度" /><output class="level-value" data-value="${key}">100%</output></div>${key==='stringLights'?stripExtra:''}</div>`;
  const rows = (keys: LightKey[]) => keys.map(lampRow).join('');
  panel.innerHTML = `<summary>灯光 · 屏幕 · 环境 · 声音</summary><div class="panel-groups">
    <section class="panel-card"><h2>灯光</h2>${rows(['lamp','bedsideLamp','ceilingLamp','lavaLamp','stringLights','streetLamp'])}</section>
    <section class="panel-card"><h2>屏幕</h2>${rows(['mac','tv'])}</section>
    <section class="panel-card"><h2>环境</h2><div class="panel-pair">
    <label>季节<select aria-label="季节" id="season">${seasons.map(s => `<option value="${s}">${seasonLabels[s]} · ${seasonMottos[s]}</option>`).join('')}</select></label>
    <label>窗外<select aria-label="天气" id="weather">${weathers.map(w => `<option value="${w}">${weatherLabels[w]}</option>`).join('')}</select></label>
    </div><div class="panel-buttons"><button data-device="heater">暖炉</button><button id="fan">风扇 · 停</button><button id="auto">跟随本地时间</button></div></section>
    <section class="panel-card"><h2>声音</h2><div class="panel-buttons"><button id="sound">开启环境声</button><button id="music" aria-pressed="false">播放窗边留座 ♫</button><button id="chime" aria-pressed="false">风铃声 · 关</button></div>
    <label class="volume-row">音量<input id="volume" aria-label="音量" type="range" min="0" max="1" step=".01" /></label></section></div>`;
  document.querySelector('.console-body')!.append(panel);
  const select = <T extends HTMLElement>(s: string) => panel.querySelector<T>(s)!;
  const save = () => { try { localStorage.setItem('lofi-room-v1',JSON.stringify(state)); } catch { /* Nonessential persistence. */ } };
  const sync = () => {
    select<HTMLSelectElement>('#season').value = state.season;
    select<HTMLSelectElement>('#weather').value = state.weather;
    panel.querySelectorAll<HTMLButtonElement>('[data-device]').forEach(b => {
      const on = state.devices[b.dataset.device as 'lamp']; b.setAttribute('aria-pressed',String(on));
    });
    for(const key of lightKeys){
      panel.querySelector(`[data-row="${key}"]`)!.classList.toggle('is-off',!state.devices[key]);
      const percent = String(Math.round(state.levels[key] * 100));
      const slider = panel.querySelector<HTMLInputElement>(`[data-level="${key}"]`)!;
      if (slider.value !== percent) slider.value = percent;
      panel.querySelector<HTMLOutputElement>(`[data-value="${key}"]`)!.textContent = `${percent}%`;
    }
    const neon = select<HTMLInputElement>('[data-color="stringLights"]');
    if (neon.value !== state.strip.color) neon.value = state.strip.color;
    neon.disabled = state.strip.cycle;
    select<HTMLInputElement>('[data-blink="stringLights"]').value = String(state.strip.blink);
    select<HTMLOutputElement>('[data-blink-value="stringLights"]').textContent = state.strip.chase
      ? (state.strip.blink > 0 ? `${state.strip.blink.toFixed(1)} 圈/秒` : '顺序 · 停')
      : state.strip.blink > 0 ? `${state.strip.blink.toFixed(1)} Hz` : '常亮';
    panel.querySelectorAll<HTMLButtonElement>('[data-flag]').forEach(b => b.setAttribute('aria-pressed',String(state.strip[b.dataset.flag as 'cycle'])));
    select<HTMLButtonElement>('#fan').textContent = ['风扇 · 停','风扇 · 慢','风扇 · 快'][state.devices.fanSpeed];
    select('#auto').setAttribute('aria-pressed',String(state.autopilot));
    document.querySelector('#season-label')!.textContent = `${state.season.toUpperCase()}, 2026`;
  };
  const changed = () => { sync(); save(); onChange(); };
  select('#season').addEventListener('change', e => { state.season=(e.target as HTMLSelectElement).value as Season;state.autopilot=false;state.weather=legalWeather(state.season,state.weather);changed(); });
  select('#weather').addEventListener('change', e => { state.weather=legalWeather(state.season,(e.target as HTMLSelectElement).value as Weather);changed(); });
  panel.querySelectorAll<HTMLButtonElement>('[data-device]').forEach(b => b.onclick=()=>{const k=b.dataset.device as 'lamp';state.devices[k]=!state.devices[k];changed();});
  panel.querySelectorAll<HTMLInputElement>('[data-level]').forEach(input => input.oninput=()=>{state.levels[input.dataset.level as LightKey]=Number(input.value)/100;changed();});
  select<HTMLInputElement>('[data-color="stringLights"]').oninput=e=>{state.strip.color=(e.target as HTMLInputElement).value.toLowerCase();changed();};
  select<HTMLInputElement>('[data-blink="stringLights"]').oninput=e=>{state.strip.blink=Number((e.target as HTMLInputElement).value);changed();};
  panel.querySelectorAll<HTMLButtonElement>('[data-flag]').forEach(b => b.onclick=()=>{
    const key=b.dataset.flag as 'cycle'|'chase'|'rainbow';
    state.strip[key]=!state.strip[key];
    // Turning the chase on with a still strip would look broken, so give it a starting pace.
    if(key==='chase'&&state.strip.chase&&state.strip.blink===0)state.strip.blink=1;
    // 彩虹 is a look of its own: it wants a run of bulbs and a ramp that keeps moving,
    // so switching it on also starts the chase and the hue cycle.
    if(key==='rainbow'&&state.strip.rainbow){
      state.strip.chase=true;
      state.strip.cycle=true;
      if(state.strip.blink===0)state.strip.blink=1;
    }
    changed();
  });
  select('#fan').onclick=()=>{state.devices.fanSpeed=((state.devices.fanSpeed+1)%3) as 0|1|2;changed();};
  select('#auto').onclick=()=>{state.autopilot=!state.autopilot;changed();};
  let audio: AudioContext | undefined, gain: GainNode | undefined;
  const music=new Audio(`${import.meta.env.BASE_URL}audio/window-seat.wav`);music.loop=true;music.preload='none';music.volume=state.audio.masterVolume;
  audioActivity.time=()=>music.currentTime;
  for(const event of ['play','pause','volumechange','ended'])music.addEventListener(event,()=>{audioActivity.playing=!music.paused&&!music.muted&&music.volume>0;});
  let chimeOn=false,chimeAudio:AudioContext|undefined;
  select('#chime').onclick=async()=>{chimeOn=!chimeOn;if(chimeOn){chimeAudio??=new AudioContext();await chimeAudio.resume();}select('#chime').textContent=chimeOn?'风铃声 · 开':'风铃声 · 关';select('#chime').setAttribute('aria-pressed',String(chimeOn));};
  window.addEventListener('room-gust',()=>{if(!chimeOn||!chimeAudio||document.hidden||music.muted)return;const ac=chimeAudio;for(const [i,f] of [784,1046,1175].entries()){const o=ac.createOscillator(),g=ac.createGain(),t=ac.currentTime+i*.16;o.frequency.value=f;g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(state.audio.masterVolume*.08,t+.008);g.gain.exponentialRampToValueAtTime(.00001,t+1.7);o.connect(g);g.connect(ac.destination);o.start(t);o.stop(t+1.8);}});
  let musicOn=false;
  select('#music').onclick=async()=>{
    try{if(musicOn){music.pause();musicOn=false;}else{await music.play();musicOn=true;}
      select('#music').textContent=musicOn?'暂停窗边留座 ♫':'播放窗边留座 ♫';select('#music').setAttribute('aria-pressed',String(musicOn));
    }catch{select('#music').textContent='音乐暂不可用，点击重试';}
  };
  async function sound() {
    try {
      if (!audio) {
        audio=new AudioContext();gain=audio.createGain();gain.gain.value=0;gain.connect(audio.destination);
        const buffer=audio.createBuffer(1,audio.sampleRate*3,audio.sampleRate),data=buffer.getChannelData(0);
        let n=0;for(let i=0;i<data.length;i++){n=(n+(Math.random()*2-1)*.03)/1.02;data[i]=n;}
        const src=audio.createBufferSource();src.buffer=buffer;src.loop=true;
        const filter=audio.createBiquadFilter();filter.type='lowpass';filter.frequency.value=650;src.connect(filter);filter.connect(gain);src.start();
      }
      state.audio.enabled=!state.audio.enabled;await audio.resume();
      gain!.gain.setTargetAtTime(state.audio.enabled&&!music.muted?state.audio.masterVolume:0,audio.currentTime,.3);
      select('#sound').textContent=state.audio.enabled?'关闭环境声':'开启环境声';save();
    } catch { select('#sound').textContent='声音暂不可用'; }
  }
  select('#sound').onclick=()=>void sound();
  select<HTMLInputElement>('#volume').value=String(state.audio.masterVolume);
  select('#volume').oninput=e=>{state.audio.masterVolume=Number((e.target as HTMLInputElement).value);music.volume=state.audio.masterVolume;if(audio&&gain)gain.gain.setTargetAtTime(state.audio.enabled&&!music.muted?state.audio.masterVolume:0,audio.currentTime,.2);save();};
  document.addEventListener('visibilitychange',()=>{if(chimeAudio)void(document.hidden||!chimeOn?chimeAudio.suspend():chimeAudio.resume());if(audio)void(document.hidden?audio.suspend():state.audio.enabled?audio.resume():audio.suspend());if(document.hidden)music.pause();else if(musicOn)void music.play().catch(()=>{musicOn=false;select('#music').textContent='播放窗边留座 ♫';select('#music').setAttribute('aria-pressed','false');});});
  window.addEventListener('keydown',e=>{
    if ((e.target as HTMLElement)?.closest('input,select,button,textarea') || e.repeat) return;
    if(e.code==='KeyM'){music.muted=!music.muted;if(audio&&gain)gain.gain.setTargetAtTime(music.muted?0:state.audio.enabled&&!music.muted?state.audio.masterVolume:0,audio.currentTime,.2);}
    if(e.code==='Escape')panel.open=false;
    const i=['Digit1','Digit2','Digit3','Digit4'].indexOf(e.code);
    if(i>=0){state.season=seasons[i];state.weather=legalWeather(state.season,state.weather);state.autopilot=false;changed();}
  });
  sync();
  return {state,save,sync};
}

