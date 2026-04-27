import { useState } from 'react';
import type { ReactNode } from 'react';
import { API } from './api';
import { CheckIcon, ChevronLeftIcon, ChevronRightIcon, ContinueIcon, DeleteIcon, EditIcon, MoveIcon } from './icons';
import { InlineAdd } from './InlineAdd';
import type { StateResponse, Task, TaskFilter, TaskList } from './types';
import { doneFor, formatDue, MSG, pendingFor, sortByName } from './utils';

type Action = (path: string, body: unknown) => Promise<void>;

type TaskRowProps = {
  data: StateResponse;
  task: Task;
  listName: string;
  act: Action;
  refresh: () => Promise<void>;
};

function TaskRow({ data, task, listName, act, refresh }: TaskRowProps) {
  const [mode, setMode] = useState<'view' | 'edit' | 'move'>('view');
  const [name, setName] = useState(task.name);
  const [due, setDue] = useState(task.due || '');
  const [newList, setNewList] = useState(listName);
  const dueInfo = task.due ? formatDue(task.due, data.today) : null;

  const saveEdit = async () => {
    const newName = name.trim();
    if (!newName) return;
    await act(API.edit, { list: listName, name: task.name, newName, due: due || null });
  };

  if (mode === 'edit') {
    return (
      <div className="task-row task-edit-row">
        <div className="task-left" />
        <div className="task-edit-body">
          <input className="task-edit-name" autoComplete="off" value={name} autoFocus onChange={e => setName(e.target.value)} onKeyDown={e => {
            if (e.key === 'Enter') saveEdit();
            if (e.key === 'Escape') refresh();
          }} />
          <input className="task-edit-due" type="date" value={due} onChange={e => setDue(e.target.value)} />
        </div>
        <div className="task-right">
          <button className="task-btn sav" title="Save" onClick={saveEdit}><CheckIcon /></button>
        </div>
      </div>
    );
  }

  if (mode === 'move') {
    return (
      <div className="task-row task-move-row">
        <select className="task-move-select" value={newList} autoFocus onChange={e => setNewList(e.target.value)}>
          {sortByName(data.lists).map(l => <option key={l.id} value={l.name}>{l.name}</option>)}
        </select>
        <div className="task-right">
          <button className="task-btn sav" title="Save" onClick={() => {
            if (newList && newList !== listName) act(API.moveTask, { list: listName, name: task.name, newList });
            else refresh();
          }}><CheckIcon /></button>
        </div>
      </div>
    );
  }

  return (
    <div className={`task-row${task.done ? ' done' : ''}`}>
      <div className="task-left">
        <div
          className="task-check"
          title={task.done ? 'Mark pending' : 'Mark done'}
          onClick={() => task.done ? act(API.undo, { list: listName, name: task.name }) : act(API.done, { list: listName, name: task.name })}
        >
          <svg className="task-check-svg" width="9" height="9" viewBox="0 0 16 16" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 8.5l3 3L13 5" />
          </svg>
        </div>
        {!task.done && (
          <button className="task-btn cnt" title="Log continue" onClick={() => act(API.continue, { list: listName, task: task.name })}>
            <ContinueIcon />
          </button>
        )}
      </div>
      <div className="task-body">
        <span className="task-name">{task.name}</span>
        {dueInfo && <span className={`task-due${dueInfo.cls ? ` ${dueInfo.cls}` : ''}`}>{dueInfo.label}</span>}
      </div>
      <div className="task-right">
        <div className="task-edit-actions">
          <button className="task-btn mov" title="Move to list" onClick={() => setMode('move')}><MoveIcon /></button>
          <button className="task-btn edt" title="Rename" onClick={() => setMode('edit')}><EditIcon /></button>
        </div>
        <button className="task-btn del" title="Delete" onClick={() => {
          if (confirm(`Delete "${task.name}"?`)) act(API.delete, { list: listName, name: task.name });
        }}><DeleteIcon /></button>
      </div>
    </div>
  );
}

const CARD_LIMIT = 10;

function Card({ data, list, filter, expanded, toggleExpanded, act, refresh, openList }: {
  data: StateResponse;
  list: TaskList;
  filter: TaskFilter;
  expanded: boolean;
  toggleExpanded: () => void;
  act: Action;
  refresh: () => Promise<void>;
  openList: () => void;
}) {
  const pending = pendingFor(data, list.id, filter);
  if (!pending.length) return null;

  const overflow = pending.length > CARD_LIMIT;
  const visible = overflow && !expanded ? pending.slice(0, CARD_LIMIT) : pending;

  return (
    <div className="card">
      <div className="card-header" onClick={openList}>
        <span className="card-title">{list.name}</span>
        <span className="card-count">{pending.length}</span>
      </div>
      <div className="card-body">
        {visible.map(t => <TaskRow key={t.id} data={data} task={t} listName={list.name} act={act} refresh={refresh} />)}
      </div>
      {overflow && (
        <button className="card-overflow-toggle" onClick={toggleExpanded}>
          {expanded ? <ChevronLeftIcon /> : <ChevronRightIcon />}
          {expanded ? ` hide ${pending.length - CARD_LIMIT}` : ` ${pending.length - CARD_LIMIT} more`}
        </button>
      )}
    </div>
  );
}

export function CardsView({ data, filter, selectedGroup, expandedCards, setExpandedCards, selectGroup, selectList, act, refresh }: {
  data: StateResponse;
  filter: TaskFilter;
  selectedGroup: string | null;
  expandedCards: Set<string>;
  setExpandedCards: (next: Set<string>) => void;
  selectGroup: (id: string | null) => void;
  selectList: (id: string | null) => void;
  act: Action;
  refresh: () => Promise<void>;
}) {
  const toggleExpanded = (id: string) => {
    const next = new Set(expandedCards);
    next.has(id) ? next.delete(id) : next.add(id);
    setExpandedCards(next);
  };

  const renderCards = (lists: TaskList[]) => lists
    .filter(list => pendingFor(data, list.id, filter).length > 0)
    .map(list => (
      <Card
        key={list.id}
        data={data}
        list={list}
        filter={filter}
        expanded={expandedCards.has(list.id)}
        toggleExpanded={() => toggleExpanded(list.id)}
        openList={() => selectList(list.id)}
        act={act}
        refresh={refresh}
      />
    ));

  if (selectedGroup) {
    const group = data.groups.find(g => g.id === selectedGroup);
    if (!group) return null;
    const cards = renderCards(sortByName(data.lists.filter(l => l.groupId === group.id)));
    return (
      <>
        <div className="section-label">{group.name}</div>
        {cards.length ? <div className="cards-grid">{cards}</div> : <div className="empty">{MSG.noTasks}</div>}
      </>
    );
  }

  const sections: ReactNode[] = [];
  const seen = new Set<string>();
  for (const group of sortByName(data.groups)) {
    const lists = sortByName(data.lists.filter(l => l.groupId === group.id));
    const cards = renderCards(lists);
    if (cards.length) {
      sections.push(<div key={`${group.id}-label`} className="section-label section-label-link" onClick={() => selectGroup(group.id)}>{group.name}</div>);
      sections.push(<div key={group.id} className="cards-grid">{cards}</div>);
    }
    lists.forEach(l => seen.add(l.id));
  }

  const ungrouped = sortByName(data.lists.filter(l => !seen.has(l.id)));
  const ungroupedCards = renderCards(ungrouped);
  if (ungroupedCards.length) {
    const hasGroups = data.groups.some(g => data.lists.some(l => l.groupId === g.id));
    if (hasGroups) sections.push(<div key="others-label" className="section-label">{MSG.others}</div>);
    sections.push(<div key="others" className="cards-grid">{ungroupedCards}</div>);
  }

  return <>{sections.length ? sections : <div className="empty">{MSG.noTasks}</div>}</>;
}

export function FocusedView({ data, listId, filter, showDone, setShowDone, act, refresh }: {
  data: StateResponse;
  listId: string;
  filter: TaskFilter;
  showDone: Set<string>;
  setShowDone: (next: Set<string>) => void;
  act: Action;
  refresh: () => Promise<void>;
}) {
  const list = data.lists.find(l => l.id === listId);
  if (!list) return <div className="empty">{MSG.noTasks}</div>;

  const pending = pendingFor(data, listId, filter);
  const done = doneFor(data, listId);
  const open = showDone.has(listId);
  const toggleDone = () => {
    const next = new Set(showDone);
    open ? next.delete(listId) : next.add(listId);
    setShowDone(next);
  };

  return (
    <div className="focused-view">
      <div className="focused-header">
        <h1 className="focused-title">{list.name}</h1>
        <span className="focused-meta">{pending.length}</span>
      </div>
      <div className="focused-tasks">
        {pending.length
          ? pending.map(t => <TaskRow key={t.id} data={data} task={t} listName={list.name} act={act} refresh={refresh} />)
          : <div className="empty">{MSG.noTasks}</div>}
      </div>
      <InlineAdd listName={list.name} variant="focused" onAdd={(listName, name, due) => act(API.add, { list: listName, name, due })} />
      {done.length > 0 && (
        <div className="done-wrapper">
          <button className="done-toggle" onClick={toggleDone}>
            {open ? <ChevronLeftIcon /> : <ChevronRightIcon />}
            {` ${open ? 'hide' : 'show'} done (${done.length})`}
          </button>
          <div className="done-section">
            {open && done.map(t => <TaskRow key={t.id} data={data} task={t} listName={list.name} act={act} refresh={refresh} />)}
          </div>
        </div>
      )}
    </div>
  );
}
