import { useState } from 'react';
import type { ReactNode } from 'react';
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import logoUrl from '../../static/logo.png';
import { API } from '../lib/api';
import { CheckIcon, DeleteIcon, EditIcon, MoveIcon } from './icons';
import type { Group, StateResponse, TaskFilter, TaskList } from '../lib/types';
import { MSG, pendingFor, sortByName } from '../lib/utils';
import styles from './Sidebar.module.css';

type Action = (path: string, body: unknown) => Promise<void>;

type SidebarProps = {
  data: StateResponse | null;
  filter: TaskFilter;
  act: Action;
  refresh: () => Promise<void>;
};

type EditState =
  | { type: 'list'; id: string }
  | { type: 'group'; id: string }
  | { type: 'move-list'; id: string }
  | { type: 'new-list' }
  | null;

export function Sidebar({ data, filter, act, refresh }: SidebarProps) {
  const [editState, setEditState] = useState<EditState>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();

  const selectedList = location.pathname.startsWith('/list/') ? location.pathname.slice(6) : null;
  const selectedGroup = searchParams.get('group');
  const isTasks = location.pathname === '/tasks' || location.pathname.startsWith('/list/');
  const isCalendar = location.pathname === '/calendar';
  const isDaysheet = location.pathname === '/daysheet';

  const cancelEdit = () => {
    setEditState(null);
    refresh();
  };

  const listButton = (list: TaskList) => {
    if (!data) return null;
    const count = pendingFor(data, list.id, filter).length;
    const active = selectedList === list.id;

    if (editState?.type === 'list' && editState.id === list.id) {
      return <RenameListRow key={list.id} list={list} act={act} cancel={cancelEdit} />;
    }
    if (editState?.type === 'move-list' && editState.id === list.id) {
      return <MoveListRow key={list.id} list={list} groups={data.groups} act={act} cancel={cancelEdit} />;
    }

    return (
      <button
        key={list.id}
        className={[styles.navItem, styles.navList, active ? styles.active : ''].filter(Boolean).join(' ')}
        onClick={() => navigate(`/list/${list.id}`)}
      >
        {list.name}
        <div className={styles.right}>
          <div className={styles.actions}>
            {data.groups.length > 0 && (
              <button className={`${styles.action} ${styles.mov}`} title="Move to group" onClick={e => {
                e.stopPropagation();
                setEditState({ type: 'move-list', id: list.id });
              }}><MoveIcon /></button>
            )}
            <button className={`${styles.action} ${styles.edt}`} title="Rename" onClick={e => {
              e.stopPropagation();
              setEditState({ type: 'list', id: list.id });
            }}><EditIcon /></button>
            <button className={`${styles.action} ${styles.del}`} title="Delete" onClick={e => {
              e.stopPropagation();
              if (confirm(`Delete list "${list.name}" and all its tasks?`)) act(API.deleteList, { list: list.name });
            }}><DeleteIcon /></button>
          </div>
          {count ? <span className={styles.count}>{count}</span> : null}
        </div>
      </button>
    );
  };

  return (
    <aside className={styles.sidebar}>
      <div className={styles.sidebarLogo}>
        <img src={logoUrl} />
        <p>Taskman</p>
      </div>
      <div className={styles.sidebarLists}>
        <div className={styles.listNav}>
          <button
            className={[styles.navItem, styles.navTop, isCalendar ? styles.active : ''].filter(Boolean).join(' ')}
            onClick={() => navigate('/calendar')}
          >
            {MSG.calendar}
          </button>
          <button
            className={[styles.navItem, styles.navTop, isDaysheet ? styles.active : ''].filter(Boolean).join(' ')}
            onClick={() => navigate('/daysheet')}
          >
            {MSG.daysheet}
          </button>
          <div className={styles.navSection}>
            <button
              className={[styles.navItem, styles.navTop, isTasks && !selectedList && !selectedGroup ? styles.active : ''].filter(Boolean).join(' ')}
              onClick={() => navigate('/tasks')}
            >
              {MSG.tasks}
            </button>
            <div className={styles.navSectionBody}>
              {data && (
                <TaskNav
                  data={data}
                  selectedGroup={selectedGroup}
                  listButton={listButton}
                  selectGroup={id => navigate(`/tasks?group=${id}`)}
                  act={act}
                />
              )}
              {editState?.type === 'new-list'
                ? <NewListRow act={act} cancel={() => setEditState(null)} />
                : <button className={styles.newListBtn} onClick={() => setEditState({ type: 'new-list' })}>{MSG.newList}</button>}
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}

function TaskNav({ data, selectedGroup, listButton, selectGroup, act }: {
  data: StateResponse;
  selectedGroup: string | null;
  listButton: (list: TaskList) => ReactNode;
  selectGroup: (id: string) => void;
  act: Action;
}) {
  const seen = new Set<string>();

  return (
    <>
      {sortByName(data.groups).map(group => {
        const lists = sortByName(data.lists.filter(l => l.groupId === group.id));
        if (!lists.length) return null;
        lists.forEach(l => seen.add(l.id));
        return (
          <div key={group.id} className={styles.navGroup}>
            <GroupHeader
              group={group}
              active={selectedGroup === group.id}
              selectGroup={() => selectGroup(group.id)}
              act={act}
            />
            <div className={styles.navGroupLists}>{lists.map(listButton)}</div>
          </div>
        );
      })}
      {sortByName(data.lists.filter(l => !seen.has(l.id))).map(listButton)}
    </>
  );
}

function GroupHeader({ group, active, selectGroup, act }: {
  group: Group;
  active: boolean;
  selectGroup: () => void;
  act: Action;
}) {
  const [renaming, setRenaming] = useState(false);
  const [name, setName] = useState(group.name);

  if (renaming) {
    const save = () => {
      const newName = name.trim();
      if (newName && newName !== group.name) act(API.renameGroup, { group: group.name, newName });
      else setRenaming(false);
    };
    return (
      <div className={[styles.navItem, styles.navGroupHeader, styles.renameRow].join(' ')}>
        <input autoComplete="off" value={name} autoFocus onChange={e => setName(e.target.value)} onKeyDown={e => {
          if (e.key === 'Enter') save();
          if (e.key === 'Escape') setRenaming(false);
        }} />
        <div className={styles.right}>
          <div className={styles.actions}>
            <button className={`${styles.action} ${styles.sav}`} title="Save" onClick={save}><CheckIcon /></button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <button
      className={[styles.navItem, styles.navGroupHeader, active ? styles.active : ''].filter(Boolean).join(' ')}
      onClick={selectGroup}
    >
      {group.name}
      <div className={styles.right}>
        <div className={styles.actions}>
          <button className={`${styles.action} ${styles.edt}`} title="Rename" onClick={e => {
            e.stopPropagation();
            setRenaming(true);
          }}><EditIcon /></button>
          <button className={`${styles.action} ${styles.del}`} title="Delete group" onClick={e => {
            e.stopPropagation();
            if (confirm(`Delete group "${group.name}"? Lists will be ungrouped.`)) act(API.deleteGroup, { group: group.name });
          }}><DeleteIcon /></button>
        </div>
      </div>
    </button>
  );
}

function RenameListRow({ list, act, cancel }: { list: TaskList; act: Action; cancel: () => void }) {
  const [name, setName] = useState(list.name);
  const save = () => {
    const newName = name.trim();
    if (newName && newName !== list.name) act(API.renameList, { list: list.name, newName });
    else cancel();
  };

  return (
    <div className={[styles.navItem, styles.navList, styles.renameRow].join(' ')}>
      <input autoComplete="off" value={name} autoFocus onChange={e => setName(e.target.value)} onKeyDown={e => {
        if (e.key === 'Enter') save();
        if (e.key === 'Escape') cancel();
      }} />
      <div className={styles.right}>
        <div className={styles.actions}>
          <button className={`${styles.action} ${styles.sav}`} title="Save" onClick={save}><CheckIcon /></button>
        </div>
      </div>
    </div>
  );
}

function MoveListRow({ list, groups, act, cancel }: { list: TaskList; groups: Group[]; act: Action; cancel: () => void }) {
  const currentGroup = groups.find(g => g.id === list.groupId);
  const [group, setGroup] = useState(currentGroup?.name || '');

  return (
    <div className={[styles.navItem, styles.navList, styles.moveRow].join(' ')}>
      <select className={styles.moveSelect} value={group} autoFocus onChange={e => setGroup(e.target.value)}>
        <option value="">No group</option>
        {sortByName(groups).map(g => <option key={g.id} value={g.name}>{g.name}</option>)}
      </select>
      <div className={styles.right}>
        <div className={styles.actions}>
          <button className={`${styles.action} ${styles.sav}`} title="Save" onClick={async () => { await act(API.moveList, { list: list.name, group }); cancel(); }}><CheckIcon /></button>
        </div>
      </div>
    </div>
  );
}

function NewListRow({ act, cancel }: { act: Action; cancel: () => void }) {
  const [name, setName] = useState('');
  const save = () => {
    const trimmed = name.trim();
    if (trimmed) act(API.addList, { list: trimmed });
    else cancel();
  };

  return (
    <div className={[styles.newListInput, styles.renameRow, styles.navItem].join(' ')}>
      <input placeholder={MSG.listName} autoComplete="off" value={name} autoFocus onChange={e => setName(e.target.value)} onKeyDown={e => {
        if (e.key === 'Enter') save();
        if (e.key === 'Escape') cancel();
      }} />
      <div className={styles.right}>
        <div className={styles.actions}>
          <button className={`${styles.action} ${styles.sav}`} title="Add" onClick={save}><CheckIcon /></button>
        </div>
      </div>
    </div>
  );
}
