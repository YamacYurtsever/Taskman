import { useState } from 'react';
import type { ReactNode } from 'react';
import logoUrl from '../../static/logo.png';
import { API } from '../lib/api';
import { CheckIcon, DeleteIcon, EditIcon, MoveIcon } from './icons';
import type { Group, StateResponse, TaskFilter, TaskList, ViewMode } from '../lib/types';
import { MSG, pendingFor, sortByName } from '../lib/utils';

type Action = (path: string, body: unknown) => Promise<void>;

type SidebarProps = {
  data: StateResponse | null;
  view: ViewMode;
  filter: TaskFilter;
  selectedList: string | null;
  selectedGroup: string | null;
  setView: (view: ViewMode) => void;
  selectList: (id: string | null) => void;
  selectGroup: (id: string | null) => void;
  act: Action;
  refresh: () => Promise<void>;
};

type EditState =
  | { type: 'list'; id: string }
  | { type: 'group'; id: string }
  | { type: 'move-list'; id: string }
  | { type: 'new-list' }
  | null;

export function Sidebar({ data, view, filter, selectedList, selectedGroup, setView, selectList, selectGroup, act, refresh }: SidebarProps) {
  const [editState, setEditState] = useState<EditState>(null);

  const navigate = (nextView: ViewMode, listId: string | null = null, groupId: string | null = null) => {
    setView(nextView);
    if (nextView === 'tasks') {
      selectList(listId);
      selectGroup(groupId);
    } else {
      selectList(null);
      selectGroup(null);
    }
  };

  const cancelEdit = () => {
    setEditState(null);
    refresh();
  };

  const listButton = (list: TaskList) => {
    if (!data) return null;
    const count = pendingFor(data, list.id, filter).length;
    const active = view === 'tasks' && selectedList === list.id;

    if (editState?.type === 'list' && editState.id === list.id) {
      return <RenameListRow key={list.id} list={list} act={act} cancel={cancelEdit} />;
    }
    if (editState?.type === 'move-list' && editState.id === list.id) {
      return <MoveListRow key={list.id} list={list} groups={data.groups} act={act} />;
    }

    return (
      <button key={list.id} className={`list-nav-item nav-list${active ? ' active' : ''}`} onClick={() => navigate('tasks', list.id, null)}>
        {list.name}
        <div className="lni-right">
          <div className="lni-actions">
            {data.groups.length > 0 && (
              <button className="lni-action mov" title="Move to group" onClick={e => {
                e.stopPropagation();
                setEditState({ type: 'move-list', id: list.id });
              }}><MoveIcon /></button>
            )}
            <button className="lni-action edt" title="Rename" onClick={e => {
              e.stopPropagation();
              setEditState({ type: 'list', id: list.id });
            }}><EditIcon /></button>
            <button className="lni-action lni-del" title="Delete" onClick={e => {
              e.stopPropagation();
              if (confirm(`Delete list "${list.name}" and all its tasks?`)) act(API.deleteList, { list: list.name });
            }}><DeleteIcon /></button>
          </div>
          {count ? <span className="lni-count">{count}</span> : null}
        </div>
      </button>
    );
  };

  return (
    <aside id="sidebar">
      <div className="sidebar-logo">
        <img src={logoUrl} />
        <p>Taskman</p>
      </div>
      <div className="sidebar-lists">
        <div id="list-nav">
          <button className={`list-nav-item nav-top${view === 'calendar' ? ' active' : ''}`} onClick={() => navigate('calendar')}>
            {MSG.calendar}
          </button>
          <button className={`list-nav-item nav-top${view === 'daysheet' ? ' active' : ''}`} onClick={() => navigate('daysheet')}>
            {MSG.daysheet}
          </button>
          <div className="nav-section">
            <button className={`list-nav-item nav-top${view === 'tasks' && selectedList === null && selectedGroup === null ? ' active' : ''}`} onClick={() => navigate('tasks')}>
              {MSG.tasks}
            </button>
            <div className="nav-section-body">
              {data && <TaskNav data={data} view={view} selectedGroup={selectedGroup} listButton={listButton} selectGroup={selectGroup} setEditState={setEditState} act={act} />}
              {editState?.type === 'new-list'
                ? <NewListRow act={act} cancel={() => setEditState(null)} />
                : <button className="new-list-btn" onClick={() => setEditState({ type: 'new-list' })}>{MSG.newList}</button>}
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}

function TaskNav({ data, view, selectedGroup, listButton, selectGroup, setEditState, act }: {
  data: StateResponse;
  view: ViewMode;
  selectedGroup: string | null;
  listButton: (list: TaskList) => ReactNode;
  selectGroup: (id: string | null) => void;
  setEditState: (state: EditState) => void;
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
          <div key={group.id} className="nav-group">
            <GroupHeader group={group} active={view === 'tasks' && selectedGroup === group.id} selectGroup={() => selectGroup(group.id)} setEditState={setEditState} act={act} />
            <div className="nav-group-lists">{lists.map(listButton)}</div>
          </div>
        );
      })}
      {sortByName(data.lists.filter(l => !seen.has(l.id))).map(listButton)}
    </>
  );
}

function GroupHeader({ group, active, selectGroup, setEditState, act }: {
  group: Group;
  active: boolean;
  selectGroup: () => void;
  setEditState: (state: EditState) => void;
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
      <div className="list-nav-item nav-group-header lni-rename-row">
        <input autoComplete="off" value={name} autoFocus onChange={e => setName(e.target.value)} onKeyDown={e => {
          if (e.key === 'Enter') save();
          if (e.key === 'Escape') setRenaming(false);
        }} />
        <div className="lni-right"><div className="lni-actions"><button className="lni-action sav" title="Save" onClick={save}><CheckIcon /></button></div></div>
      </div>
    );
  }

  return (
    <button className={`list-nav-item nav-group-header${active ? ' active' : ''}`} onClick={selectGroup}>
      {group.name}
      <div className="lni-right">
        <div className="lni-actions">
          <button className="lni-action edt" title="Rename" onClick={e => {
            e.stopPropagation();
            setRenaming(true);
          }}><EditIcon /></button>
          <button className="lni-action lni-del" title="Delete group" onClick={e => {
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
    <div className="list-nav-item nav-list lni-rename-row">
      <input autoComplete="off" value={name} autoFocus onChange={e => setName(e.target.value)} onKeyDown={e => {
        if (e.key === 'Enter') save();
        if (e.key === 'Escape') cancel();
      }} />
      <div className="lni-right"><div className="lni-actions"><button className="lni-action sav" title="Save" onClick={save}><CheckIcon /></button></div></div>
    </div>
  );
}

function MoveListRow({ list, groups, act }: { list: TaskList; groups: Group[]; act: Action }) {
  const currentGroup = groups.find(g => g.id === list.groupId);
  const [group, setGroup] = useState(currentGroup?.name || '');

  return (
    <div className="list-nav-item nav-list lni-move-row">
      <select className="lni-move-select" value={group} autoFocus onChange={e => setGroup(e.target.value)}>
        <option value="">No group</option>
        {sortByName(groups).map(g => <option key={g.id} value={g.name}>{g.name}</option>)}
      </select>
      <div className="lni-right"><div className="lni-actions"><button className="lni-action sav" title="Save" onClick={() => act(API.moveList, { list: list.name, group })}><CheckIcon /></button></div></div>
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
    <div className="new-list-input lni-rename-row list-nav-item">
      <input placeholder={MSG.listName} autoComplete="off" value={name} autoFocus onChange={e => setName(e.target.value)} onKeyDown={e => {
        if (e.key === 'Enter') save();
        if (e.key === 'Escape') cancel();
      }} />
      <div className="lni-right"><div className="lni-actions"><button className="lni-action sav" title="Add" onClick={save}><CheckIcon /></button></div></div>
    </div>
  );
}
