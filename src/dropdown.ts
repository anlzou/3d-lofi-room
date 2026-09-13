// A select whose list opens inside the page instead of the operating system's popup. The native
// popup is drawn by the system — on phones it takes over the screen — and it cannot be styled to
// match the console around it.
//
// The list is appended to <body> rather than to the control: the console scrolls, and anything
// positioned inside a scroll container is clipped by it. It also has to live outside the panel's
// backdrop-filter ancestor, which would otherwise become the containing block for a fixed element.
export interface DropdownOption<T extends string> { value: T; label: string }
export interface Dropdown<T extends string> { set(value: T): void; element: HTMLButtonElement }

export function dropdown<T extends string>(host: HTMLElement, options: DropdownOption<T>[], initial: T, onPick: (value: T) => void, ariaLabel: string): Dropdown<T> {
  const toggle = document.createElement('button');
  toggle.type = 'button';
  toggle.className = 'dropdown-toggle';
  toggle.setAttribute('aria-haspopup', 'listbox');
  toggle.setAttribute('aria-expanded', 'false');
  toggle.setAttribute('aria-label', ariaLabel);
  const menu = document.createElement('div');
  menu.className = 'dropdown-menu';
  menu.setAttribute('role', 'listbox');
  menu.setAttribute('aria-label', ariaLabel);
  menu.hidden = true;
  const items = options.map(option => {
    const item = document.createElement('button');
    item.type = 'button';
    item.className = 'dropdown-option';
    item.dataset.value = option.value;
    item.setAttribute('role', 'option');
    item.textContent = option.label;
    menu.append(item);
    return item;
  });
  host.append(toggle);
  document.body.append(menu);
  let value = initial;
  const render = () => {
    toggle.textContent = options.find(option => option.value === value)?.label ?? '';
    for (const item of items) item.setAttribute('aria-selected', String(item.dataset.value === value));
  };
  const place = () => {
    // Anchored to the button in viewport coordinates, and flipped up when there is no room below.
    const box = toggle.getBoundingClientRect();
    const width = Math.max(box.width, 132);
    menu.style.width = `${width}px`;
    menu.style.left = `${Math.min(Math.max(8, box.left), Math.max(8, innerWidth - width - 8))}px`;
    const below = box.bottom + 4, height = menu.offsetHeight;
    menu.style.top = `${below + height > innerHeight - 8 ? Math.max(8, box.top - height - 4) : below}px`;
  };
  const open = () => {
    menu.hidden = false;
    toggle.setAttribute('aria-expanded', 'true');
    place();
    (items.find(item => item.dataset.value === value) ?? items[0]).focus();
  };
  const close = (focusToggle = false) => {
    if (menu.hidden) return;
    menu.hidden = true;
    toggle.setAttribute('aria-expanded', 'false');
    if (focusToggle) toggle.focus();
  };
  const pick = (next: T) => { value = next; render(); close(true); onPick(next); };
  toggle.onclick = () => menu.hidden ? open() : close(true);
  toggle.onkeydown = event => {
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') { event.preventDefault(); open(); }
  };
  menu.onkeydown = event => {
    const at = items.indexOf(document.activeElement as HTMLButtonElement);
    if (event.key === 'Escape') { event.preventDefault(); close(true); return; }
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault();
      items[(at + (event.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length].focus();
      return;
    }
    if (event.key === 'Home' || event.key === 'End') {
      event.preventDefault();
      items[event.key === 'Home' ? 0 : items.length - 1].focus();
    }
  };
  for (const item of items) item.onclick = () => pick(item.dataset.value as T);
  // The button can be dragged or scrolled away, so the list closes rather than chase it.
  addEventListener('scroll', () => close(), true);
  addEventListener('resize', () => close());
  document.addEventListener('pointerdown', event => {
    const target = event.target as Node;
    if (!host.contains(target) && !menu.contains(target)) close();
  }, true);
  render();
  menu.dataset.for = ariaLabel;
  return { set: next => { value = next; render(); }, element: toggle };
}
