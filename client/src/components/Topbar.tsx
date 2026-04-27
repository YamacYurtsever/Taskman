import { useLocation } from 'react-router-dom';
import type { TaskFilter } from '../lib/types';
import { ThemeToggle } from './ThemeToggle';
import styles from './Topbar.module.css';

type TopbarProps = {
  filter: TaskFilter;
  setFilter: (filter: TaskFilter) => void;
};

export function Topbar({ filter, setFilter }: TopbarProps) {
  const location = useLocation();
  const showFilter = location.pathname === '/tasks' || location.pathname.startsWith('/list/');
  const filters: TaskFilter[] = ['all', 'week', 'day'];

  return (
    <div className={styles.topbar}>
      <div>
        {showFilter && (
          <div className={styles.filterPills}>
            {filters.map(f => (
              <button
                key={f}
                className={[styles.filterPill, filter === f ? styles.active : ''].filter(Boolean).join(' ')}
                onClick={() => setFilter(f)}
              >
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
