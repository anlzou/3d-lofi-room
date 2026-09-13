"""Original 32-bar instrumental: Window Seat, 76 BPM. No samples or borrowed melody."""
from pathlib import Path
import numpy as np
import wave,json
SR=32000; BPM=76; beat=60/BPM; bars=32; length=bars*4*beat
n=round(length*SR); mix=np.zeros((n,2),np.float64);rng=np.random.default_rng(1999)
def put(signal,start,pan=0):
    indices=(np.arange(len(signal))+round(start*SR))%n
    mix[indices,0]+=signal*np.sqrt((1-pan)/2)
    mix[indices,1]+=signal*np.sqrt((1+pan)/2)
def note(midi,start,duration,volume,pan=0,bass=False):
    t=np.arange(round((duration+.8)*SR))/SR;freq=440*2**((midi-69)/12)
    attack=1-np.exp(-t/(.012 if bass else .022));release=np.exp(-np.maximum(t-duration,0)*7)
    env=attack*np.exp(-t/(2.8 if bass else 1.3))*release
    wobble=.0018*np.sin(2*np.pi*.7*t)
    s=np.sin(2*np.pi*freq*t+wobble)+.24*np.sin(2*np.pi*freq*2*t)*np.exp(-t*2)+.07*np.sin(2*np.pi*freq*3*t)
    put(s*env*volume,start,pan)
    if not bass:
        put(s*env*volume*.12,start+beat*.75,-pan)
        put(s*env*volume*.05,start+beat*1.5,pan)
chords=[[60,63,67,70,74],[56,60,63,67,70],[55,58,62,65,70],[58,62,65,67,72]]
roots=[36,32,39,34]
melodies=[[79,77,74,70,74],[75,79,77,72,70],[77,74,70,67,70],[74,72,70,65,67]]
for bar in range(bars):
    origin=bar*4*beat;section=(bar//2)%4
    for offset,velocity in [(0,.055),(2.65,.026)]:
        for j,pitch in enumerate(chords[section]):note(pitch,origin+offset*beat+j*.014,beat*2,.9*velocity,(-.35+j*.17))
    for offset,pitch,vel in [(0,roots[section],.12),(1.7,roots[section]+12,.07),(2.5,roots[section]+7,.08)]:note(pitch,origin+offset*beat,beat*.7,vel,0,True)
    if 4<=bar<28 and bar%2==0:
        for j,pitch in enumerate(melodies[section]):note(pitch,origin+(j*.7+.25)*beat,beat*.42,.032, .2)
    if bar<2 or bar>=30:continue
    for step in range(8):
        start=origin+(step*.5+(.075 if step%2 else 0))*beat+rng.uniform(-.007,.007)
        t=np.arange(int(SR*.09))/SR;noise=rng.normal(0,1,len(t));hat=np.diff(noise,prepend=0)*np.exp(-t*65)
        put(hat*(.012 if step%2 else .019),start,.38)
    for off in [0,1.6,2.75] if bar%4==3 else [0,2.5]:
        t=np.arange(int(SR*.32))/SR;phase=2*np.pi*(47*t+55*.027*(1-np.exp(-t/.027)));put(np.sin(phase)*np.exp(-t*15)*.24,origin+off*beat)
    for off in [1.045,3.045]:
        t=np.arange(int(SR*.18))/SR;noise=rng.normal(0,1,len(t));snare=(noise*.035+np.sin(2*np.pi*174*t)*.026)*np.exp(-t*24);put(snare,origin+off*beat,-.12)
# Soft tape saturation and a quiet noise floor; normalize with ample headroom.
mix=np.tanh(mix*1.25);mix*=.72/max(np.max(np.abs(mix)),1e-8)
out=Path(__file__).resolve().parents[1]/'public/audio';out.mkdir(exist_ok=True)
with wave.open(str(out/'window-seat.wav'),'wb') as f:
    f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes((mix*32767).astype('<i2').tobytes())
report={'title':'Window Seat / 窗边留座','bpm':BPM,'bars':bars,'seconds':n/SR,'sampleRate':SR,'peak':float(np.max(np.abs(mix))),'rms':float(np.sqrt(np.mean(mix**2))),'original':True,'samples':'All instruments synthesized in compose_bgm.py; no external recordings.'}
(out/'credits.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False))
