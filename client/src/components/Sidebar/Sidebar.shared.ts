import type { Group, TaskList } from '../../lib/types';

type Action = (path: string, body: unknown) => Promise<void>;

type EditState =
  | { type: 'list'; id: string }
  | { type: 'group'; id: string }
  | { type: 'move-list'; id: string }
  | { type: 'new-list' }
  | null;

type ListRowProps = {
  dataGroups: Group[];
  filterCount: number;
  isActive: boolean;
  isEditing: boolean;
  isMoving: boolean;
  list: TaskList;
  onDelete: () => void;
  onEdit: () => void;
  onMove: () => void;
  onSelect: () => void;
  act: Action;
  cancel: () => void;
};

export type {
  Action,
  EditState,
  ListRowProps,
};
