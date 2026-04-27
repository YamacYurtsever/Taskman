export type ViewMode = 'tasks' | 'daysheet' | 'calendar';
export type TaskFilter = 'all' | 'week' | 'day';

export type Group = {
  id: string;
  name: string;
};

export type TaskList = {
  id: string;
  name: string;
  groupId: string | null;
};

export type Task = {
  id: string;
  name: string;
  listId: string;
  due: string | null;
  done: string | null;
};

export type StateResponse = {
  groups: Group[];
  lists: TaskList[];
  tasks: Task[];
  today: string;
};

export type ConfigResponse = {
  calendarUrl: string;
};

export type DaysheetEntry = {
  id: string;
  datetime: string;
  listId: string;
  type: 'log' | 'continue' | 'done';
  text: string;
  listName: string;
  sectionId: string;
  sectionName: string;
  inGroup: boolean;
};

export type DaysheetResponse = {
  date: string;
  entries: DaysheetEntry[];
};

export type ApiResult = {
  ok: boolean;
  message: string;
};
