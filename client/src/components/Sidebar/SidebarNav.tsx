import { API } from '../../lib/api';
import type { StateResponse, TaskFilter, TaskList } from '../../lib/types';
import { pendingFor, sortByName } from '../../lib/utils';
import styles from './Sidebar.module.css';
import { SidebarGroupRow } from './SidebarGroupRow';
import { SidebarListRow } from './SidebarListRow';
import type { Action, EditState } from './Sidebar.shared';

type SidebarNavProps = {
  data: StateResponse;
  filter: TaskFilter;
  selectedGroup: string | null;
  selectedList: string | null;
  editState: EditState;
  setEditState: (state: EditState) => void;
  selectGroup: (id: string) => void;
  selectList: (id: string) => void;
  act: Action;
  cancelEdit: () => void;
};

const SidebarNav = ({
  data,
  filter,
  selectedGroup,
  selectedList,
  editState,
  setEditState,
  selectGroup,
  selectList,
  act,
  cancelEdit,
}: SidebarNavProps) => {
  const groups = sortByName(data.groups).map(group => ({
    group,
    lists: sortByName(data.lists.filter(list => list.groupId === group.id)),
  }));

  const groupedIds = new Set(groups.flatMap(({ lists }) => lists.map(list => list.id)));
  const ungrouped = sortByName(data.lists.filter(list => !groupedIds.has(list.id)));

  const renderList = (list: TaskList) => (
    <SidebarListRow
      key={list.id}
      list={list}
      dataGroups={data.groups}
      filterCount={pendingFor(data, list.id, filter).length}
      isActive={selectedList === list.id}
      isEditing={editState?.type === 'list' && editState.id === list.id}
      isMoving={editState?.type === 'move-list' && editState.id === list.id}
      onSelect={() => selectList(list.id)}
      onEdit={() => setEditState({ type: 'list', id: list.id })}
      onMove={() => setEditState({ type: 'move-list', id: list.id })}
      onDelete={() => {
        if (confirm(`Delete list "${list.name}" and all its tasks?`)) {
          act(API.deleteList, { list: list.name });
        }
      }}
      act={act}
      cancel={cancelEdit}
    />
  );

  return (
    <>
      {groups.map(({ group, lists }) => (
        <div key={group.id} className={styles.navGroup}>
          <SidebarGroupRow
            group={group}
            active={selectedGroup === group.id}
            selectGroup={() => selectGroup(group.id)}
            act={act}
          />
          <div className={styles.navGroupLists}>{lists.map(renderList)}</div>
        </div>
      ))}

      {ungrouped.map(renderList)}
    </>
  );
};

export { SidebarNav };
