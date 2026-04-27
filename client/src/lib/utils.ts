import type { StateResponse, Task, TaskFilter } from './types';

export const MSG = {
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
};

export function todayStr() {
  return new Date().toISOString().slice(0, 10);
}

export function sortByName<T extends { name: string }>(arr: T[]) {
  return [...arr].sort((a, b) => {
    if (/^others?$/i.test(a.name)) return 1;
    if (/^others?$/i.test(b.name)) return -1;
    return a.name.localeCompare(b.name);
  });
}

export function pendingFor(data: StateResponse, listId: string, filter: TaskFilter) {
  const today = new Date(data.today);
  const pending = data.tasks.filter(t => t.listId === listId && !t.done);
  const byDueThenName = (a: Task, b: Task) => (a.due || '').localeCompare(b.due || '') || a.name.localeCompare(b.name);

  if (filter === 'day') {
    return pending.filter(t => t.due && new Date(t.due) <= today).sort(byDueThenName);
  }
  if (filter === 'week') {
    const cut = new Date(today);
    cut.setDate(cut.getDate() + 7);
    return pending.filter(t => t.due && new Date(t.due) <= cut).sort(byDueThenName);
  }
  return [
    ...pending.filter(t => t.due).sort(byDueThenName),
    ...pending.filter(t => !t.due).sort((a, b) => a.name.localeCompare(b.name)),
  ];
}

export function doneFor(data: StateResponse, listId: string) {
  return data.tasks
    .filter(t => t.listId === listId && t.done)
    .sort((a, b) => (b.done || '').localeCompare(a.done || ''));
}

export function formatDue(due: string, today: string) {
  const dueD = new Date(due);
  const todayD = new Date(today);
  const days = Math.round((dueD.getTime() - todayD.getTime()) / 86400000);
  if (days < 0) return { label: dueD.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }), cls: 'overdue' };
  if (days === 0) return { label: 'today', cls: 'today-due' };
  if (days === 1) return { label: 'tomorrow', cls: 'soon' };
  if (days < 7) return { label: dueD.toLocaleDateString(undefined, { weekday: 'short' }).toLowerCase(), cls: '' };
  return { label: dueD.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }), cls: '' };
}
