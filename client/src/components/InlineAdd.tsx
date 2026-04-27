import { useState } from 'react';
import { PlusIcon } from './icons';
import { MSG } from '../lib/utils';

type InlineAddProps = {
  listName: string;
  variant: 'card' | 'focused';
  onAdd: (listName: string, name: string, due: string | null) => Promise<void>;
};

export function InlineAdd({ listName, variant, onAdd }: InlineAddProps) {
  const [name, setName] = useState('');
  const [due, setDue] = useState('');

  const submit = async () => {
    const trimmed = name.trim();
    if (!trimmed) return;
    await onAdd(listName, trimmed, due || null);
    setName('');
    setDue('');
  };

  const controls = (
    <>
      <input type="text" placeholder={MSG.addTask} value={name} onChange={e => setName(e.target.value)} onKeyDown={e => e.key === 'Enter' && submit()} />
      <input type="date" value={due} onChange={e => setDue(e.target.value)} />
      <button className={variant === 'focused' ? 'focused-add-btn' : 'task-btn sav'} onClick={submit}>
        <PlusIcon />
      </button>
    </>
  );

  if (variant === 'focused') {
    return <div className="focused-add">{controls}</div>;
  }

  return <div className="focused-add">{controls}</div>;
}
