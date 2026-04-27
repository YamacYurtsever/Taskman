import type { StateResponse, Task, TaskFilter, TaskList } from '../../lib/types';

export type Action = (path: string, body: unknown) => Promise<void>;

export type TaskRowProps = {
  data: StateResponse;
  task: Task;
  listName: string;
  act: Action;
};

export type TaskCardProps = {
  data: StateResponse;
  list: TaskList;
  filter: TaskFilter;
  expanded: boolean;
  toggleExpanded: () => void;
  openList: () => void;
  act: Action;
};

export type CardsViewProps = {
  data: StateResponse;
  filter: TaskFilter;
  selectedGroup: string | null;
  selectGroup: (id: string | null) => void;
  selectList: (id: string | null) => void;
  act: Action;
};

export type FocusedViewProps = {
  data: StateResponse;
  listId: string;
  filter: TaskFilter;
  act: Action;
};
