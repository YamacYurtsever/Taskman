import type { TaskFilter, ViewMode } from '../lib/types';
import { ThemeToggle } from './ThemeToggle';

type TopbarProps = {
  view: ViewMode;
  filter: TaskFilter;
  setFilter: (filter: TaskFilter) => void;
};

export function Topbar({ view, filter, setFilter }: TopbarProps) {
  const filters: TaskFilter[] = ['all', 'week', 'day'];

  return (
    <div id="topbar">
      <div id="filter-bar">
        {view === 'tasks' && (
          <div className="filter-pills">
            {filters.map(f => (
              <button key={f} className={`filter-pill${filter === f ? ' active' : ''}`} onClick={() => setFilter(f)}>
                {f[0].toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        )}
      </div>
      <ThemeToggle />
    </div>
  );
}
