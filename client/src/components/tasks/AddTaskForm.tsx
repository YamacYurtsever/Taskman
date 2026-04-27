import { useState } from 'react';
import { PlusIcon } from '../icons';
import { API } from '../../lib/api';
import { MSG } from '../../lib/utils';
import styles from './Tasks.module.css';
import type { Action } from './Tasks.shared';

type AddTaskFormProps = {
  listName: string;
  act: Action;
};

export const AddTaskForm = ({ listName, act }: AddTaskFormProps) => {
  const [name, setName] = useState('');
  const [due, setDue] = useState('');

  const submit = async () => {
    const trimmed = name.trim();
    if (!trimmed) return;

    await act(API.add, { list: listName, name: trimmed, due: due || null });
    setName('');
    setDue('');
  };

  return (
    <div className={styles.inlineAdd}>
      <input
        type="text"
        placeholder={MSG.addTask}
        value={name}
        onChange={e => setName(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && submit()}
      />
      <input type="date" value={due} onChange={e => setDue(e.target.value)} />
      <button className={styles.inlineAddBtn} onClick={submit}>
        <PlusIcon />
      </button>
    </div>
  );
};
