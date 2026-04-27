import { state, el } from './core.js';
import { render } from './app.js';

export function renderTopbar() {
  const bar = document.getElementById('filter-bar');
  bar.replaceChildren();
  if (state.view !== 'tasks') return;
  bar.append(
    el('div', { class: 'filter-pills' },
      ...['all', 'week', 'day'].map(f =>
        el('button', {
          class: 'filter-pill' + (state.filter === f ? ' active' : ''),
          on: { click: () => { state.filter = f; render(); } },
        }, f[0].toUpperCase() + f.slice(1)),
      ),
    ),
  );
}
