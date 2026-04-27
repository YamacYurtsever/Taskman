import type { MouseEvent } from 'react';
import type { StateResponse, Task, TaskFilter } from './types';

const MS_PER_DAY = 86_400_000;
const OTHERS_RE = /^others?$/i;

const MSG = {
  noTasks: 'No tasks',
  noEntries: 'No entries',
  addTask: 'Add task...',
  entryText: 'Entry text...',
  listName: 'List name...',
  newList: '+ New List',
  today: 'Today',
  yesterday: 'Yesterday',
  daysheet: 'Daysheet',
  tasks: 'Tasks',
  others: 'Others',
  calendar: 'Calendar',
  noCalUrl: 'No calendars configured. Add a "calendars" array and "calendarTimezone" to ~/.taskman/config.json.',
} as const;

const todayStr = () =>
  new Date().toISOString().slice(0, 10);

const byName = <T extends { name: string }>(a: T, b: T) =>
  a.name.localeCompare(b.name);

const byDueThenName = (a: Task, b: Task) =>
  (a.due ?? '').localeCompare(b.due ?? '') || byName(a, b);

const sortByName = <T extends { name: string }>(arr: T[]) =>
  [...arr].sort((a, b) => {
    if (OTHERS_RE.test(a.name)) return 1;
    if (OTHERS_RE.test(b.name)) return -1;
    return byName(a, b);
  });

const cx = (...classes: Array<string | false | null | undefined>) =>
  classes.filter(Boolean).join(' ');

const stop = (fn: () => void) => (e: MouseEvent) => {
  e.stopPropagation();
  fn();
};

const pendingFor = (data: StateResponse, listId: string, filter: TaskFilter) => {
  const today = new Date(data.today);
  const pending = data.tasks.filter(t => t.listId === listId && !t.done);

  if (filter === 'day') {
    return pending
      .filter(t => t.due && new Date(t.due) <= today)
      .sort(byDueThenName);
  }

  if (filter === 'week') {
    const cut = new Date(today);
    cut.setDate(cut.getDate() + 7);

    return pending
      .filter(t => t.due && new Date(t.due) <= cut)
      .sort(byDueThenName);
  }

  return [
    ...pending.filter(t => t.due).sort(byDueThenName),
    ...pending.filter(t => !t.due).sort(byName),
  ];
};

const doneFor = (data: StateResponse, listId: string) =>
  data.tasks
    .filter(t => t.listId === listId && t.done)
    .sort((a, b) => (b.done ?? '').localeCompare(a.done ?? ''));

const formatDue = (due: string, today: string) => {
  const dueDate = new Date(due);
  const todayDate = new Date(today);
  const days = Math.round((dueDate.getTime() - todayDate.getTime()) / MS_PER_DAY);

  if (days < 0) {
    return {
      label: dueDate.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
      cls: 'overdue',
    };
  }

  if (days === 0) return { label: 'today', cls: 'today-due' };
  if (days === 1) return { label: 'tomorrow', cls: 'soon' };

  if (days < 7) {
    return {
      label: dueDate.toLocaleDateString(undefined, { weekday: 'short' }).toLowerCase(),
      cls: '',
    };
  }

  return {
    label: dueDate.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
    cls: '',
  };
};

export {
  MSG,
  cx,
  todayStr,
  sortByName,
  stop,
  pendingFor,
  doneFor,
  formatDue,
};
