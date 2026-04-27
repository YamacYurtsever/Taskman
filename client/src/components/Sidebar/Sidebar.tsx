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
  isMobile: boolean;
  isOpen: boolean;
  onClose: () => void;
};

const navItems = [
  { path: '/calendar', label: MSG.calendar },
  { path: '/daysheet', label: MSG.daysheet },
];

const listPath = '/list/';

const Sidebar = ({ data, filter, act, refresh, isMobile, isOpen, onClose }: SidebarProps) => {
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
  const closeIfMobile = () => {
    if (isMobile) {
      onClose();
    }
  };
  const navigateTo = (path: string) => {
    navigate(path);
    closeIfMobile();
  };

  return (
    <aside
      className={cx(styles.sidebar, isMobile && styles.mobileSidebar, isOpen && styles.mobileSidebarOpen)}
    >
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
              onClick={() => navigateTo(path)}
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
              onClick={() => navigateTo('/tasks')}
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
                  selectGroup={id => navigateTo(`/tasks?group=${id}`)}
                  selectList={id => navigateTo(`/list/${id}`)}
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
