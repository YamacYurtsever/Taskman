import { useLocation } from 'react-router-dom';
import type { TaskFilter } from '../lib/types';
import { ThemeToggle } from './ThemeToggle';
import styles from './Topbar.module.css';

type TopbarProps = {
  filter: TaskFilter;
  setFilter: (filter: TaskFilter) => void;
};

const filters: TaskFilter[] = ['all', 'week', 'day'];

const label = (f: TaskFilter) =>
  f[0].toUpperCase() + f.slice(1);

const Topbar = ({ filter, setFilter }: TopbarProps) => {
  const { pathname } = useLocation();

  const showFilter =
    pathname === '/tasks' || pathname.startsWith('/list/');

  return (
    <div className={styles.topbar}>
      {showFilter && (
        <div className={styles.filterPills}>
          {filters.map(f => (
            <button
              key={f}
              className={
                filter === f
                  ? `${styles.filterPill} ${styles.active}`
                  : styles.filterPill
              }
              onClick={() => setFilter(f)}
            >
              {label(f)}
            </button>
          ))}
        </div>
      )}

      <ThemeToggle />
    </div>
  );
};

export { Topbar };
