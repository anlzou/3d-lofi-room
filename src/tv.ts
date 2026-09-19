import * as THREE from 'three';

// 电视画面直接打开网址。屏幕打开时加载网页；关掉屏幕时卸掉页面，声音一起停。
// 跨域页面读不到 history，前进后退用这里自己的记录。
const STORAGE_KEY = 'lofi-tv-v1';
const CSS_W = 880;

type Px = { x: number; y: number };

// Maps the element's top-left rectangle onto the four screen pixels. Percent
// translates are not used: Safari resolves them against the wrong box.
function adj3(m: number[]): number[] {
  return [
    m[4] * m[8] - m[5] * m[7], m[2] * m[7] - m[1] * m[8], m[1] * m[5] - m[2] * m[4],
    m[5] * m[6] - m[3] * m[8], m[0] * m[8] - m[2] * m[6], m[2] * m[3] - m[0] * m[5],
    m[3] * m[7] - m[4] * m[6], m[1] * m[6] - m[0] * m[7], m[0] * m[4] - m[1] * m[3],
  ];
}
function mul3(a: number[], b: number[]): number[] {
  const c = new Array<number>(9);
  for (let i = 0; i < 3; i++) {
    for (let j = 0; j < 3; j++) {
      let n = 0;
      for (let k = 0; k < 3; k++) n += a[3 * i + k] * b[3 * k + j];
      c[3 * i + j] = n;
    }
  }
  return c;
}
function mul3v(m: number[], v: number[]): number[] {
  return [
    m[0] * v[0] + m[1] * v[1] + m[2] * v[2],
    m[3] * v[0] + m[4] * v[1] + m[5] * v[2],
    m[6] * v[0] + m[7] * v[1] + m[8] * v[2],
  ];
}
function basisToPoints(x1: number, y1: number, x2: number, y2: number, x3: number, y3: number, x4: number, y4: number): number[] {
  const m = [x1, x2, x3, y1, y2, y3, 1, 1, 1];
  const v = mul3v(adj3(m), [x4, y4, 1]);
  return mul3(m, [v[0], 0, 0, 0, v[1], 0, 0, 0, v[2]]);
}
function quadMatrix(w: number, h: number, d1: Px, d2: Px, d3: Px, d4: Px): string | null {
  const t = mul3(basisToPoints(d1.x, d1.y, d2.x, d2.y, d3.x, d3.y, d4.x, d4.y), adj3(basisToPoints(0, 0, w, 0, 0, h, w, h)));
  const norm = t[8];
  if (!Number.isFinite(norm) || Math.abs(norm) < 1e-8) return null;
  for (let i = 0; i < 9; i++) t[i] /= norm;
  if (t.some(n => !Number.isFinite(n) || Math.abs(n) > 1e7)) return null;
  const m = [t[0], t[3], 0, t[6], t[1], t[4], 0, t[7], 0, 0, 1, 0, t[2], t[5], 0, t[8]];
  return `matrix3d(${m.join(',')})`;
}

type Site = { id: string; url: string; description: string; enabled: boolean };

const DEFAULT_SITES: Site[] = [
  { id: 'site-1', url: 'https://www.bilibili.com/video/BV1U1421r7SM', description: 'Ｌｏｆｉ｜轻音乐', enabled: true },
  { id: 'site-2', url: 'https://www.bilibili.com/video/BV1zHq8BgEJ4', description: '𝟭𝟵𝟵𝟯 𝗗𝗜𝗦𝗥𝗨𝗣𝗧 𝗧𝗛𝗘 𝗗𝗥𝗘𝗔𝗠𝗦𝗧𝗔𝗧𝗘', enabled: true },
  { id: 'site-3', url: 'https://github.com/anlzou', description: 'GitHub • anlzou', enabled: true },
];

export type Tv = {
  setMode: (tv: boolean) => void;
  syncPower: () => void;
  resume: () => void;
  unload: () => void;
  mount: (mesh: THREE.Mesh, camera: THREE.Camera, host: HTMLElement) => void;
  render: () => void;
  resize: () => void;
};

function normalizeUrl(raw: string): string | null {
  const text = raw.trim();
  if (!text) return null;
  try {
    const url = new URL(/^https?:\/\//i.test(text) ? text : `https://${text}`);
    if (url.protocol !== 'http:' && url.protocol !== 'https:') return null;
    return url.href;
  } catch {
    return null;
  }
}

function loadSites(): { sites: Site[]; currentId: string } {
  try {
    const raw = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? 'null') as { sites?: Site[]; currentId?: string } | null;
    if (raw && Array.isArray(raw.sites) && raw.sites.length > 0) {
      const sites = raw.sites.filter(s => s && typeof s.url === 'string' && typeof s.id === 'string').map(s => ({
        id: String(s.id),
        url: String(s.url),
        description: String(s.description || s.url),
        enabled: s.enabled !== false,
      }));
      if (sites.length) return { sites, currentId: String(raw.currentId ?? sites[0].id) };
    }
  } catch { /* Private storage may be unavailable. */ }
  return { sites: DEFAULT_SITES.map(s => ({ ...s })), currentId: DEFAULT_SITES[0].id };
}

const BLANK_PAGE = new URL('tv-blank.html', document.baseURI).href;

export function createTv(opts: {
  roomPanel: HTMLDetailsElement;
  powered: () => boolean;
  setPowered: (on: boolean) => void;
  level: () => number;
  setLevel: (value: number) => void;
  musicOn: () => boolean;
  onMusic: (on: boolean) => void;
}): Tv {
  const saved = loadSites();
  let sites = saved.sites;
  let currentId = saved.currentId;
  let roomWasOpen = false;
  let watching = false;
  const stack: string[] = [];
  let index = -1;

  const panel = document.createElement('details');
  panel.className = 'room-panel tv-panel';
  panel.hidden = true;
  panel.innerHTML = `<summary>画面 · 浏览 · 网址</summary><div class="panel-groups">
    <details class="panel-card" open><summary>画面</summary>
      <div class="lamp-entry" data-power-row><div class="lamp-row"><span class="lamp-name">电视</span><button type="button" class="switch" data-act="power" aria-pressed="false" aria-label="电视开关"><span></span></button><input class="level" type="range" min="0" max="100" step="5" data-act="level" aria-label="电视强度" /><output class="level-value" data-level-value>100%</output></div></div>
      <div class="panel-buttons"><button type="button" data-act="music">播放音乐 ♫</button></div>
    </details>
    <details class="panel-card" open><summary>浏览</summary>
      <div class="panel-buttons"><button type="button" data-act="back">后退</button><button type="button" data-act="forward">前进</button><button type="button" data-act="refresh">刷新</button></div>
      <label class="field-row">地址<input type="url" data-act="url" spellcheck="false" autocomplete="off" placeholder="输入网址" aria-label="地址" /></label>
      <div class="panel-buttons"><button type="button" data-act="go">打开</button></div>
    </details>
    <details class="panel-card" open><summary>网址</summary>
      <div class="tv-sites" data-sites></div>
      <p class="tv-empty" data-empty hidden>还没有网址</p>
      <div class="panel-buttons"><button type="button" data-act="add">添加网址</button></div>
      <div class="tv-form" data-form hidden>
        <label class="field-row">网址<input type="url" data-draft="url" spellcheck="false" autocomplete="off" aria-label="新网址" /></label>
        <label class="field-row">名称<input type="text" data-draft="name" autocomplete="off" aria-label="名称" /></label>
        <p class="tv-note" data-error hidden></p>
        <div class="panel-buttons"><button type="button" data-act="save">保存</button><button type="button" data-act="cancel">取消</button></div>
      </div>
    </details>
  </div>`;
  opts.roomPanel.parentElement!.append(panel);

  const pick = <T extends HTMLElement>(sel: string) => panel.querySelector<T>(sel)!;
  const urlInput = pick<HTMLInputElement>('[data-act="url"]');
  const backBtn = pick<HTMLButtonElement>('[data-act="back"]');
  const forwardBtn = pick<HTMLButtonElement>('[data-act="forward"]');
  const refreshBtn = pick<HTMLButtonElement>('[data-act="refresh"]');
  const powerBtn = pick<HTMLButtonElement>('[data-act="power"]');
  const levelInput = pick<HTMLInputElement>('[data-act="level"]');
  const levelValue = pick<HTMLOutputElement>('[data-level-value]');
  const form = pick<HTMLElement>('[data-form]');
  const error = pick<HTMLElement>('[data-error]');
  const draftUrl = pick<HTMLInputElement>('[data-draft="url"]');
  const draftName = pick<HTMLInputElement>('[data-draft="name"]');

  const glass = document.createElement('div');
  glass.style.position = 'absolute';
  glass.style.left = '0';
  glass.style.top = '0';
  glass.style.margin = '0';
  glass.style.transformOrigin = '0 0';
  glass.style.zIndex = '1';
  glass.style.display = 'none';
  glass.style.overflow = 'hidden';
  glass.style.background = '#14181c';
  glass.style.pointerEvents = 'none';
  glass.style.touchAction = 'auto';
  const dress = (frame: HTMLIFrameElement, title: string) => {
    frame.title = title;
    frame.style.position = 'absolute';
    frame.style.inset = '0';
    frame.style.width = '100%';
    frame.style.height = '100%';
    frame.style.border = '0';
    frame.style.background = '#14181c';
    frame.setAttribute('referrerpolicy', 'no-referrer');
    frame.setAttribute('allow', 'fullscreen; autoplay; encrypted-media; picture-in-picture');
    frame.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox allow-modals allow-presentation');
  };
  // The playing page is shown only while the set is on. Closing it drops the
  // document, so a cross-origin video cannot keep playing out of sight.
  const media = document.createElement('iframe');
  const blank = document.createElement('iframe');
  dress(media, '电视画面');
  dress(blank, '无声画面');
  media.style.display = 'none';
  blank.style.display = 'none';
  blank.src = BLANK_PAGE;
  glass.append(blank, media);
  glass.addEventListener('pointerdown', e => e.stopPropagation());
  glass.addEventListener('wheel', e => e.stopPropagation(), { passive: true });
  let camera: THREE.Camera | undefined;
  let mesh: THREE.Mesh | undefined;
  let hostEl: HTMLElement | undefined;
  let canvasEl: HTMLCanvasElement | null = null;
  let placed = false;
  let loaded = '';
  let parked = true;
  let shown = '';
  const reveal = () => {
    const next = parked ? 'off' : 'media';
    if (shown === next) return;
    shown = next;
    media.style.display = parked ? 'none' : 'block';
    blank.style.display = 'none';
  };

  const persist = () => { try { localStorage.setItem(STORAGE_KEY, JSON.stringify({ sites, currentId })); } catch { /* Nonessential persistence. */ } };
  const showError = (text: string) => { error.hidden = false; error.textContent = text; };
  const clearError = () => { error.hidden = true; error.textContent = ''; };

  const paintNav = () => {
    const url = index >= 0 ? stack[index] : '';
    if (document.activeElement !== urlInput) urlInput.value = url;
    backBtn.disabled = index <= 0;
    forwardBtn.disabled = index < 0 || index >= stack.length - 1;
    refreshBtn.disabled = index < 0;
  };

  const renderSites = () => {
    const list = pick<HTMLElement>('[data-sites]');
    list.replaceChildren();
    pick<HTMLElement>('[data-empty]').hidden = sites.length > 0;
    for (const site of sites) {
      const row = document.createElement('div');
      row.className = 'tv-site';
      row.classList.toggle('is-off', !site.enabled);
      const open = document.createElement('button');
      open.type = 'button';
      open.dataset.act = 'open';
      open.dataset.id = site.id;
      open.textContent = site.description || site.url;
      open.title = site.url;
      open.setAttribute('aria-pressed', String(site.id === currentId));
      open.disabled = !site.enabled;
      const enable = document.createElement('button');
      enable.type = 'button';
      enable.className = 'switch';
      enable.dataset.act = 'enable';
      enable.dataset.id = site.id;
      enable.setAttribute('aria-pressed', String(site.enabled));
      enable.setAttribute('aria-label', `${site.description}开关`);
      enable.append(document.createElement('span'));
      const del = document.createElement('button');
      del.type = 'button';
      del.dataset.act = 'del';
      del.dataset.id = site.id;
      del.textContent = '删除';
      row.append(open, enable, del);
      list.append(row);
    }
  };

  const showing = () => opts.powered();
  const center = new THREE.Vector3();
  const front = new THREE.Vector3();
  const widthAxis = new THREE.Vector3();
  const heightAxis = new THREE.Vector3();
  const toCamera = new THREE.Vector3();
  const rayDir = new THREE.Vector3();
  const ndc = new THREE.Vector3();
  const viewPos = new THREE.Vector3();
  const corners = [new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3()];
  const raycaster = new THREE.Raycaster();
  const wallSides = new Map<THREE.Material, THREE.Side>();
  let cssH = 1;
  let worldW = 0;
  let worldH = 0;
  let walls: THREE.Mesh[] = [];

  // The tube is a flat quad: local X is the picture width, local Y its height, local +Z the glass.
  const place = () => {
    if (!mesh) return;
    mesh.updateWorldMatrix(true, false);
    const geo = mesh.geometry;
    if (!geo.boundingBox) geo.computeBoundingBox();
    const box = geo.boundingBox;
    if (!box) return;
    const size = box.getSize(new THREE.Vector3());
    const pos = new THREE.Vector3();
    const quat = new THREE.Quaternion();
    const scl = new THREE.Vector3();
    mesh.matrixWorld.decompose(pos, quat, scl);
    const worldWidth = size.x * Math.abs(scl.x);
    const worldHeight = size.y * Math.abs(scl.y);
    if (worldWidth < 1e-4 || worldHeight < 1e-4) return;
    widthAxis.set(1, 0, 0).applyQuaternion(quat);
    heightAxis.set(0, 1, 0).applyQuaternion(quat);
    if (heightAxis.dot(new THREE.Vector3(0, 1, 0)) < 0) {
      heightAxis.negate();
      widthAxis.negate();
    }
    widthAxis.normalize();
    heightAxis.normalize();
    front.set(0, 0, 1).transformDirection(mesh.matrixWorld).normalize();
    center.copy(box.getCenter(new THREE.Vector3())).multiply(scl).applyQuaternion(quat).add(pos);
    worldW = worldWidth;
    worldH = worldHeight;
    cssH = Math.max(1, Math.round(CSS_W * worldH / worldW));
    glass.style.width = `${CSS_W}px`;
    glass.style.height = `${cssH}px`;
    media.style.width = `${CSS_W}px`;
    media.style.height = `${cssH}px`;
    blank.style.width = `${CSS_W}px`;
    blank.style.height = `${cssH}px`;
    placed = true;
  };

  // CSS has no depth, so the page would paint over the cabinet once the camera
  // walks behind the glass. Hide it on that side and bring it back in front.
  const inFront = () => placed && !!camera && front.dot(toCamera.copy(camera.position).sub(center)) > 0.02;

  // The glass test is an infinite plane: orbiting past a side wall can leave
  // the camera in the front half-space while the wall sits in between. Walls
  // face inward, so a camera outside the room only meets their back faces.
  const collectWalls = () => {
    if (!mesh) return;
    let root: THREE.Object3D = mesh;
    while (root.parent) root = root.parent;
    const found: THREE.Mesh[] = [];
    root.traverse(obj => {
      if (obj instanceof THREE.Mesh && /^Wall_(Back|Right|Left|Front)/.test(obj.name)) found.push(obj);
    });
    if (found.length) walls = found;
  };
  const blockedByWall = () => {
    if (!camera || walls.length === 0) return false;
    rayDir.copy(center).sub(camera.position);
    const len = rayDir.length();
    if (len < 1e-3) return false;
    rayDir.multiplyScalar(1 / len);
    raycaster.set(camera.position, rayDir);
    raycaster.near = 0;
    raycaster.far = len - 0.03;
    if (raycaster.far <= 0) return false;
    for (const wall of walls) {
      const mats = Array.isArray(wall.material) ? wall.material : [wall.material];
      for (const mat of mats) {
        if (!mat || wallSides.has(mat)) continue;
        wallSides.set(mat, mat.side);
        mat.side = THREE.DoubleSide;
      }
    }
    const hits: THREE.Intersection[] = [];
    let hit = false;
    try {
      for (const wall of walls) {
        if (!wall.visible) continue;
        hits.length = 0;
        wall.raycast(raycaster, hits);
        if (hits.length > 0) { hit = true; break; }
      }
    } finally {
      for (const [mat, side] of wallSides) mat.side = side;
      wallSides.clear();
    }
    return hit;
  };

  const projectCorner = (world: THREE.Vector3, rect: DOMRect, originX: number, originY: number): Px | null => {
    if (!camera) return null;
    viewPos.copy(world).applyMatrix4(camera.matrixWorldInverse);
    if (viewPos.z > -0.02) return null;
    ndc.copy(world).project(camera);
    return {
      x: (ndc.x + 1) * 0.5 * rect.width + originX,
      y: (1 - ndc.y) * 0.5 * rect.height + originY,
    };
  };
  const placeOnGlass = () => {
    if (!hostEl) return false;
    const canvas = canvasEl && canvasEl.isConnected ? canvasEl : hostEl.querySelector('canvas');
    canvasEl = canvas;
    const rect = canvas?.getBoundingClientRect();
    if (!rect || rect.width < 2 || rect.height < 2) return false;
    const hostRect = hostEl.getBoundingClientRect();
    const originX = rect.left - hostRect.left;
    const originY = rect.top - hostRect.top;
    const hx = worldW * 0.5;
    const hy = worldH * 0.5;
    corners[0].copy(center).addScaledVector(front, 0.001).addScaledVector(widthAxis, -hx).addScaledVector(heightAxis, hy);
    corners[1].copy(center).addScaledVector(front, 0.001).addScaledVector(widthAxis, hx).addScaledVector(heightAxis, hy);
    corners[2].copy(center).addScaledVector(front, 0.001).addScaledVector(widthAxis, -hx).addScaledVector(heightAxis, -hy);
    corners[3].copy(center).addScaledVector(front, 0.001).addScaledVector(widthAxis, hx).addScaledVector(heightAxis, -hy);
    const px = corners.map(c => projectCorner(c, rect, originX, originY));
    if (px.some(p => !p)) return false;
    const [tl, tr, bl, br] = px as Px[];
    const transform = quadMatrix(CSS_W, cssH, tl, tr, bl, br);
    if (!transform) return false;
    glass.style.transform = transform;
    return true;
  };

  const paintScreen = () => {
    if (index < 0) return;
    const url = stack[index];
    if (loaded === url && media.getAttribute('src')) return;
    loaded = url;
    media.src = url;
  };

  const load = (url: string) => {
    if (document.activeElement !== urlInput) urlInput.value = url;
    paintNav();
    paintScreen();
  };

  const navigate = (raw: string) => {
    const url = normalizeUrl(raw);
    if (!url) { showError('请输入 http 或 https 网址'); return; }
    clearError();
    if (stack[index] !== url) {
      stack.splice(index + 1);
      stack.push(url);
      index = stack.length - 1;
    }
    const hit = sites.find(s => s.url === url);
    if (hit) currentId = hit.id;
    persist();
    renderSites();
    load(url);
  };

  const openForm = (open: boolean) => {
    form.hidden = !open;
    pick<HTMLButtonElement>('[data-act="add"]').hidden = open;
    if (open) { clearError(); draftUrl.focus(); }
  };

  panel.addEventListener('click', e => {
    const button = (e.target as HTMLElement).closest('button');
    if (!button || !panel.contains(button)) return;
    const act = button.dataset.act;
    const id = button.dataset.id;
    if (act === 'power' || act === 'music') { opts.onMusic(!opts.powered()); return; }
    if (act === 'back' && index > 0) { index -= 1; load(stack[index]); return; }
    if (act === 'forward' && index < stack.length - 1) { index += 1; load(stack[index]); return; }
    if (act === 'refresh' && index >= 0 && showing()) {
      const url = stack[index];
      loaded = url;
      let reloaded = false;
      try {
        if (media.contentWindow) { media.contentWindow.location.reload(); reloaded = true; }
      } catch { reloaded = false; }
      if (!reloaded) {
        loaded = '';
        media.src = 'about:blank';
        window.setTimeout(() => { loaded = url; media.src = url; }, 0);
      }
      return;
    }
    if (act === 'go') { navigate(urlInput.value); return; }
    if (act === 'add') { draftUrl.value = ''; draftName.value = ''; openForm(true); return; }
    if (act === 'cancel') { openForm(false); return; }
    if (act === 'save') {
      const url = normalizeUrl(draftUrl.value);
      if (!url) { showError('请输入 http 或 https 网址'); return; }
      const description = draftName.value.trim() || url;
      const idNew = `site-${Date.now()}`;
      sites.push({ id: idNew, url, description, enabled: true });
      currentId = idNew;
      persist();
      renderSites();
      openForm(false);
      navigate(url);
      return;
    }
    if (!id) return;
    if (act === 'open') {
      const site = sites.find(s => s.id === id);
      if (!site || !site.enabled) return;
      currentId = site.id;
      persist();
      renderSites();
      navigate(site.url);
      return;
    }
    if (act === 'enable') {
      const site = sites.find(s => s.id === id);
      if (!site) return;
      site.enabled = !site.enabled;
      persist();
      renderSites();
      return;
    }
    if (act === 'del') {
      sites = sites.filter(s => s.id !== id);
      if (currentId === id) currentId = sites.find(s => s.enabled)?.id ?? sites[0]?.id ?? '';
      persist();
      renderSites();
    }
  });
  urlInput.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); navigate(urlInput.value); } });
  draftUrl.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); pick<HTMLButtonElement>('[data-act="save"]').click(); } });
  levelInput.addEventListener('input', () => opts.setLevel(Number(levelInput.value) / 100));

  renderSites();
  paintNav();
  reveal();
  syncPower();

  function syncPower() {
    const on = opts.powered();
    powerBtn.setAttribute('aria-pressed', String(on));
    pick<HTMLElement>('[data-power-row]').classList.toggle('is-off', !on);
    const percent = String(Math.round(opts.level() * 100));
    if (document.activeElement !== levelInput && levelInput.value !== percent) levelInput.value = percent;
    levelValue.textContent = `${percent}%`;
    const music = pick<HTMLButtonElement>('[data-act="music"]');
    music.textContent = on ? '关闭音乐 ♫' : '播放音乐 ♫';
    music.setAttribute('aria-pressed', String(on));
    reveal();
  }

  function unload() {
    parked = true;
    loaded = '';
    media.src = 'about:blank';
    reveal();
    paintNav();
  }

  function resume() {
    parked = false;
    if (index < 0) {
      const site = sites.find(s => s.enabled);
      if (!site) { reveal(); paintNav(); return; }
      currentId = site.id;
      persist();
      renderSites();
      navigate(site.url);
    } else {
      paintScreen();
    }
    reveal();
    paintNav();
  }

  return {
    setMode(tv) {
      if (tv) {
        roomWasOpen = opts.roomPanel.open;
        panel.open = true;
      }
      opts.roomPanel.hidden = tv;
      panel.hidden = !tv;
      if (!tv) opts.roomPanel.open = roomWasOpen;
      watching = tv;
      syncPower();
    },
    syncPower,
    unload,
    resume,
    mount(next, cam, host) {
      mesh = next;
      camera = cam;
      hostEl = host;
      canvasEl = host.querySelector('canvas');
      host.append(glass);
      place();
      collectWalls();
      reveal();
    },
    render() {
      if (!camera) return;
      if (!placed) place();
      if (walls.length === 0) collectWalls();
      const on = showing() && inFront() && !blockedByWall() && placeOnGlass();
      glass.style.display = on ? 'block' : 'none';
      const hit = on && watching ? 'auto' : 'none';
      glass.style.pointerEvents = hit;
      media.style.pointerEvents = hit;
      blank.style.pointerEvents = hit;
    },
    resize() { canvasEl = hostEl?.querySelector('canvas') ?? null; },
  };
}
