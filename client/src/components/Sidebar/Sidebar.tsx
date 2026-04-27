import { useState } from 'react';
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import logoUrl from '../../../logo.png';
import type { StateResponse, TaskFilter } from '../../lib/types';
import { MSG, cx } from '../../lib/utils';
import styles from './Sidebar.module.css';
import { SidebarNewListRow } from './SidebarListRow';
import { SidebarNav } from './SidebarNav';
import type { Action, EditState } from './Sidebar.shared';

type SidebarProps = {
  data: StateResponse | null;
  filter: TaskFilter;
  act: Action;
  refresh: () => Promise<void>;
};

const navItems = [
  { path: '/calendar', label: MSG.calendar },
  { path: '/daysheet', label: MSG.daysheet },
];

const listPath = '/list/';

const Sidebar = ({ data, filter, act, refresh }: SidebarProps) => {
  const [editState, setEditState] = useState<EditState>(null);

  const navigate = useNavigate();
  const { pathname } = useLocation();
  const [searchParams] = useSearchParams();

  const selectedList = pathname.startsWith(listPath) ? pathname.slice(listPath.length) : null;
  const selectedGroup = searchParams.get('group');
  const inTasks = pathname === '/tasks' || pathname.startsWith(listPath);

  const cancelEdit = () => {
    setEditState(null);
    refresh();
  };

  const addList = () => setEditState({ type: 'new-list' });
  const cancelNewList = () => setEditState(null);

  return (
    <aside className={styles.sidebar}>
      <div className={styles.sidebarLogo}>
        <img src={logoUrl} alt="" />
        <p>Taskman</p>
      </div>

      <div className={styles.sidebarLists}>
        <div className={styles.listNav}>
          {navItems.map(({ path, label }) => (
            <button
              key={path}
              className={cx(styles.navItem, styles.navTop, pathname === path && styles.active)}
              onClick={() => navigate(path)}
            >
              {label}
            </button>
          ))}

          <div className={styles.navSection}>
            <button
              className={cx(
                styles.navItem,
                styles.navTop,
                inTasks && !selectedList && !selectedGroup && styles.active,
              )}
              onClick={() => navigate('/tasks')}
            >
              {MSG.tasks}
            </button>

            <div className={styles.navSectionBody}>
              {data && (
                <SidebarNav
                  data={data}
                  filter={filter}
                  selectedGroup={selectedGroup}
                  selectedList={selectedList}
                  editState={editState}
                  setEditState={setEditState}
                  selectGroup={id => navigate(`/tasks?group=${id}`)}
                  selectList={id => navigate(`/list/${id}`)}
                  act={act}
                  cancelEdit={cancelEdit}
                />
              )}

              {editState?.type === 'new-list' ? (
                <SidebarNewListRow act={act} cancel={cancelNewList} />
              ) : (
                <button className={styles.newListBtn} onClick={addList}>
                  {MSG.newList}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
};

export { Sidebar };
