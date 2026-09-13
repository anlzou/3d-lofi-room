import * as THREE from 'three';

// Cycles INDIRECT-only bakes, encoded with sqrt(linear / 4) for dark-area precision.
const hours = [0, 7, 12, 17 + 20 / 60, 24];
export function lightmapBlend(hour: number) {
  const h = ((hour % 24) + 24) % 24;
  const i = hours.findIndex((end, i) => i > 0 && h < end) - 1;
  const a = Math.max(0, i);
  return { a, b: (a + 1) % 4, mix: (h - hours[a]) / (hours[a + 1] - hours[a]) };
}

export async function loadBakedLighting(onProgress?: (sent: number, total: number) => void) {
  const loader = new THREE.TextureLoader();
  const names = ['night', 'dawn', 'noon', 'dusk'];
  // Five textures arrive in parallel, so the reported figure is the sum of their downloads;
  // a host that sends no Content-Length leaves that slot at zero and is simply not counted.
  const sent = [0, 0, 0, 0, 0], sizes = [0, 0, 0, 0, 0];
  const report = () => onProgress?.(sent.reduce((a, b) => a + b, 0), sizes.reduce((a, b) => a + b, 0));
  const [ao, ...maps] = await Promise.all(['ao', ...names].map((name, index) => new Promise<THREE.Texture>((resolve, reject) => {
    loader.load(`${import.meta.env.BASE_URL}lighting/${name}.png`, texture => {
      texture.flipY = false; texture.channel = 1; texture.colorSpace = THREE.NoColorSpace;
      texture.anisotropy = 4;
      sizes[index] = sizes[index] || sent[index];
      resolve(texture);
    }, event => {
      if (event.total) sizes[index] = event.total;
      sent[index] = event.loaded;
      report();
    }, reject);
  })));
  const uniforms = { bakeA: { value: maps[3] }, bakeB: { value: maps[0] }, bakeMix: { value: 0 } };
  const cache = new Map<THREE.Material, THREE.Material>();
  return {
    update(hour: number) {
      const t = lightmapBlend(hour);
      uniforms.bakeA.value = maps[t.a]; uniforms.bakeB.value = maps[t.b]; uniforms.bakeMix.value = t.mix;
    },
    material(original: THREE.Material): THREE.Material {
      if (!(original instanceof THREE.MeshStandardMaterial) || original.transparent || original.emissiveIntensity > 0 && original.emissive.getHex() !== 0) return original;
      if (cache.has(original)) return cache.get(original)!;
      const m = original.clone();
      m.aoMap = ao; m.aoMapIntensity = .35;
      m.lightMap = maps[0]; m.lightMapIntensity = Math.PI * 1.8;
      m.onBeforeCompile = shader => {
        Object.assign(shader.uniforms, uniforms);
        shader.fragmentShader = 'uniform sampler2D bakeA; uniform sampler2D bakeB; uniform float bakeMix;\n' + shader.fragmentShader;
        shader.fragmentShader = shader.fragmentShader.replace('#include <lights_fragment_maps>',
          THREE.ShaderChunk.lights_fragment_maps.replace('vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );',
            `vec3 a = texture2D(bakeA, vLightMapUv).rgb;
             vec3 b = texture2D(bakeB, vLightMapUv).rgb;
             vec4 lightMapTexel = vec4(mix(a*a, b*b, bakeMix)*4.0, 1.0);`));
      };
      m.customProgramCacheKey = () => 'lofi-cycles-bounce-v1';
      cache.set(original, m); return m;
    },
  };
}
