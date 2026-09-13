// The dock floats freely: open it with the ring button, move it by dragging the ring
// button or any non-interactive spot inside the panel. The spot is remembered per browser,
// and the ⟲ button folds the panel away and puts the ring back above the bottom edge.
const STORAGE_KEY = 'lofi-room-console-v1';
export function consoleDrag(node: HTMLElement) {
  let left = 0, top = 0, startX = 0, startY = 0, startLeft = 0, startTop = 0, detached = false;
  // The ring button doubles as the drag handle: a press only becomes a drag after the
  // pointer travels, and the click that follows a real drag is swallowed.
  let fromHandle = false, moved = false, swallowClick = false, pressedId: number | null = null, threshold = 4;
  const bound = () => {
    const rect = node.getBoundingClientRect();
    left = boundTo(left, 8, Math.max(8, innerWidth - rect.width - 8));
    top = boundTo(top, 8, Math.max(8, innerHeight - rect.height - 8));
  };
  const apply = () => {
    bound();
    node.style.left = `${left}px`; node.style.top = `${top}px`;
    node.style.bottom = 'auto'; node.style.transform = 'none';
    detached = true;
    node.classList.add('moved');
  };
  const detach = () => {
    if (detached) return;
    const rect = node.getBoundingClientRect();
    left = rect.left; top = rect.top;
    apply();
  };
  const save = () => { try { localStorage.setItem(STORAGE_KEY, JSON.stringify({ left, top })); } catch { /* Nonessential persistence. */ } };
  const reset = () => {
    detached = false;
    swallowClick = false;
    node.style.left = ''; node.style.top = ''; node.style.bottom = ''; node.style.transform = '';
    node.classList.remove('moved');
    // Resetting the spot also folds the panel away, so the ring lands back in its default
    // place above the bottom edge instead of staying wherever it was parked.
    node.classList.remove('open');
    node.querySelector('#dock-toggle')?.setAttribute('aria-expanded', 'false');
    try { localStorage.removeItem(STORAGE_KEY); } catch { /* Nonessential persistence. */ }
  };
  node.addEventListener('pointerdown', event => {
    if (event.button !== 0) return;
    const target = event.target as HTMLElement;
    // Keep controls, sliders, selects and the settings summary clickable.
    if (target.closest('input,select,textarea,a,label,summary')) return;
    const touch = event.pointerType === 'touch';
    fromHandle = !!target.closest('[data-drag-handle]');
    // On touch only the handle drags, so the panel itself keeps scrolling normally.
    if (touch && !fromHandle) return;
    if (!fromHandle && target.closest('button')) return;
    // Fingers jitter, so touch needs a wider slop before a tap turns into a drag.
    threshold = touch ? 9 : 4;
    detach();
    startX = event.clientX; startY = event.clientY; startLeft = left; startTop = top;
    moved = false;
    pressedId = event.pointerId;
    // Pointer capture is deliberately deferred to the first move: capturing on press
    // retargets the click to the dock and would stop the ring button from toggling.
  });
  node.addEventListener('pointermove', event => {
    if (pressedId !== event.pointerId) return;
    const dx = event.clientX - startX, dy = event.clientY - startY;
    if (!moved) {
      if (Math.hypot(dx, dy) < threshold) return;
      moved = true;
      node.setPointerCapture(event.pointerId);
      node.classList.add('dragging');
    }
    left = startLeft + dx;
    top = startTop + dy;
    apply();
  });
  const finish = (event: PointerEvent) => {
    if (pressedId !== event.pointerId) return;
    pressedId = null;
    if (node.hasPointerCapture(event.pointerId)) node.releasePointerCapture(event.pointerId);
    node.classList.remove('dragging');
    if (!moved) return;
    save();
    if (fromHandle) {
      // A press that travelled is a move, not a toggle.
      swallowClick = true;
      setTimeout(() => { swallowClick = false; }, 300);
    }
    moved = false;
  };
  node.addEventListener('click', event => {
    if (!swallowClick) return;
    swallowClick = false;
    event.stopPropagation();
    event.preventDefault();
  }, true);
  node.addEventListener('pointerup', finish);
  node.addEventListener('pointercancel', finish);
  node.querySelector('#console-reset')?.addEventListener('click', reset);
  addEventListener('resize', () => { if (detached) apply(); });
  try {
    const raw = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? 'null') as { left?: number; top?: number } | null;
    if (Number.isFinite(raw?.left) && Number.isFinite(raw?.top)) {
      left = raw!.left!; top = raw!.top!;
      requestAnimationFrame(apply);
    }
  } catch { /* Nonessential persistence. */ }
  // Exposed so callers can re-clamp after the dock grows or shrinks.
  return { reposition: () => { if (detached) apply(); } };
}
function boundTo(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}
