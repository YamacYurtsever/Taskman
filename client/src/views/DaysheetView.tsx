import { useState } from 'react';
import { API } from '../lib/api';
import { CheckIcon, ChevronLeftIcon, ChevronRightIcon, DeleteIcon, EditIcon, PlusIcon } from '../components/icons';
import type { DaysheetEntry, DaysheetResponse, StateResponse } from '../lib/types';
import { MSG, sortByName, todayStr } from '../lib/utils';

type Action = (path: string, body: unknown) => Promise<void>;

export function DaysheetView({ data, daysheet, daysheetDate, setDaysheetDate, act, refresh }: {
  data: StateResponse | null;
  daysheet: DaysheetResponse | null;
  daysheetDate: string;
  setDaysheetDate: (date: string) => void;
  act: Action;
  refresh: () => Promise<void>;
}) {
  const entries = daysheet?.entries || [];
  const lists = data?.lists || [];

  const shiftDay = (delta: number) => {
    const d = new Date(`${daysheetDate}T12:00:00`);
    d.setDate(d.getDate() + delta);
    setDaysheetDate(d.toISOString().slice(0, 10));
  };

  return (
    <div className="daysheet-view">
      <div className="daysheet-header">
        <h1 className="daysheet-title">{MSG.daysheet}</h1>
        <div className="date-nav">
          <button className="date-nav-btn" onClick={() => shiftDay(-1)}><ChevronLeftIcon /></button>
          <span className="date-nav-label">{dateLabel(daysheetDate)}</span>
          <button className="date-nav-btn" onClick={() => shiftDay(1)}><ChevronRightIcon /></button>
        </div>
      </div>
      <Timeline entries={entries} act={act} refresh={refresh} />
      {lists.length > 0 && <LogForm lists={lists} act={act} />}
    </div>
  );
}

function dateLabel(str: string) {
  const today = todayStr();
  if (str === today) return MSG.today;
  const yest = new Date();
  yest.setDate(yest.getDate() - 1);
  if (str === yest.toISOString().slice(0, 10)) return MSG.yesterday;
  return new Date(`${str}T12:00:00`).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

function Timeline({ entries, act, refresh }: { entries: DaysheetEntry[]; act: Action; refresh: () => Promise<void> }) {
  if (!entries.length) {
    return <div className="timeline"><div className="empty">{MSG.noEntries}</div></div>;
  }

  const bySection = new Map<string, { name: string; inGroup: boolean; items: DaysheetEntry[] }>();
  for (const entry of entries) {
    if (!bySection.has(entry.sectionId)) {
      bySection.set(entry.sectionId, { name: entry.sectionName, inGroup: entry.inGroup, items: [] });
    }
    bySection.get(entry.sectionId)?.items.push(entry);
  }

  return (
    <div className="timeline">
      {sortByName([...bySection.values()]).map(section => (
        <div key={section.name} className="timeline-group">
          <div className="timeline-group-name">{section.name}</div>
          {section.items.map(entry => <TimelineEntry key={entry.id} entry={entry} inGroup={section.inGroup} act={act} refresh={refresh} />)}
        </div>
      ))}
    </div>
  );
}

function TimelineEntry({ entry, inGroup, act, refresh }: {
  entry: DaysheetEntry;
  inGroup: boolean;
  act: Action;
  refresh: () => Promise<void>;
}) {
  const [editing, setEditing] = useState(false);
  const [text, setText] = useState(entry.text);
  const prefix = entry.type === 'done' ? 'Finished ' : entry.type === 'continue' ? 'Continued ' : '';

  const save = async () => {
    const newText = text.trim();
    if (!newText) return;
    await act(API.daysheetEdit, { id: entry.id, text: newText });
  };

  if (editing) {
    return (
      <div className="timeline-entry timeline-edit-row">
        <span className="timeline-time">{entry.datetime.slice(11, 16)}</span>
        <input className="timeline-edit-input" autoComplete="off" value={text} autoFocus onChange={e => setText(e.target.value)} onKeyDown={e => {
          if (e.key === 'Enter') save();
          if (e.key === 'Escape') refresh();
        }} />
        <div className="timeline-actions">
          <button className="task-btn sav timeline-del" title="Save" onClick={save}><CheckIcon /></button>
        </div>
      </div>
    );
  }

  return (
    <div className="timeline-entry">
      <span className="timeline-time">{entry.datetime.slice(11, 16)}</span>
      <span className="timeline-text">
        {prefix + entry.text}
        {inGroup && <span className="timeline-list-tag">{entry.listName}</span>}
      </span>
      <div className="timeline-actions">
        {entry.type === 'log' && <button className="task-btn edt timeline-del" title="Edit" onClick={() => setEditing(true)}><EditIcon /></button>}
        <button className="task-btn del timeline-del" title="Delete" onClick={() => act(API.daysheetDelete, { id: entry.id })}><DeleteIcon /></button>
      </div>
    </div>
  );
}

function LogForm({ lists, act }: { lists: StateResponse['lists']; act: Action }) {
  const sorted = sortByName(lists);
  const [listName, setListName] = useState(sorted[0]?.name || '');
  const [text, setText] = useState('');

  const submit = () => {
    const trimmed = text.trim();
    if (!trimmed) return;
    act(API.log, { list: listName, text: trimmed });
    setText('');
  };

  return (
    <div className="log-form">
      <select value={listName} onChange={e => setListName(e.target.value)}>
        {sorted.map(list => <option key={list.id} value={list.name}>{list.name}</option>)}
      </select>
      <input type="text" placeholder={MSG.entryText} autoComplete="off" value={text} onChange={e => setText(e.target.value)} onKeyDown={e => e.key === 'Enter' && submit()} />
      <button className="log-form-btn" onClick={submit}><PlusIcon /></button>
    </div>
  );
}
