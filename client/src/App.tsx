import { useCallback, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { Navigate, Route, Routes, useLocation, useNavigate, useParams, useSearchParams } from 'react-router-dom';

import styles from './App.module.css';
import { api } from './lib/api';
import type { StateResponse, TaskFilter } from './lib/types';

import { Sidebar } from './components/Sidebar';
import { Topbar } from './components/Topbar';
import { CalendarView } from './views/CalendarView';
import { DaysheetView } from './views/DaysheetView';
import { CardsView, FocusedView } from './views/TasksView';

export type Action = (path: string, body: unknown) => Promise<void>;

type RouteProps = {
  data: StateResponse;
  filter: TaskFilter;
  act: Action;
  refresh: () => Promise<void>;
};

function TasksRoute({ data, filter, act, refresh }: RouteProps) {
  const [sp] = useSearchParams();
  const nav = useNavigate();
  return (
    <CardsView
      data={data}
      filter={filter}
      selectedGroup={sp.get('group')}
      selectGroup={id => nav(id ? `/tasks?group=${id}` : '/tasks')}
      selectList={id => nav(`/list/${id}`)}
      act={act}
      refresh={refresh}
    />
  );
}

function ListRoute({ data, filter, act, refresh }: RouteProps) {
  const { listId } = useParams<{ listId: string }>();
  if (!listId) return <Navigate to="/tasks" replace />;
  return <FocusedView data={data} listId={listId} filter={filter} act={act} refresh={refresh} />;
}

function RequireData({ data, children }: {
  data: StateResponse | null;
  children: (data: StateResponse) => ReactNode;
}) {
  if (!data) return <p>Loading...</p>;
  return children(data);
}

function useAppData() {
  const [data, setData] = useState<StateResponse | null>(null);
  const [calendarUrl, setCalendarUrl] = useState('');

  const refresh = useCallback(async () => setData(await api.state()), []);
  const act = useCallback(async (path: string, body: unknown) => {
    const res = await api.post(path, body);
    if (res?.ok) setData(await api.state());
  }, []);

  useEffect(() => { api.config().then(c => c?.calendarUrl && setCalendarUrl(c.calendarUrl)); }, []);
  useEffect(() => { refresh(); }, [refresh]);

  return { data, calendarUrl, act, refresh };
}

export function App() {
  const [filter, setFilter] = useState<TaskFilter>('all');
  const { data, calendarUrl, act, refresh } = useAppData();

  const location = useLocation();
  const isCalendar = location.pathname === '/calendar';

  return (
    <>
      <Sidebar data={data} filter={filter} act={act} refresh={refresh} />

      <div className={styles.content}>
        <Topbar filter={filter} setFilter={setFilter} />

        <main
          className={styles.main}
          style={{ display: isCalendar && calendarUrl ? 'none' : undefined }}
        >
          <Routes>
            <Route path="/" element={<Navigate to="/tasks" replace />} />
            <Route path="/calendar" element={<CalendarView calendarUrl={calendarUrl} />} />
            <Route path="/daysheet" element={<DaysheetView data={data} act={act} refresh={refresh} />} />
            <Route path="/tasks" element={
              <RequireData data={data}>
                {data => <TasksRoute data={data} filter={filter} act={act} refresh={refresh} />}
              </RequireData>
            } />
            <Route path="/list/:listId" element={
              <RequireData data={data}>
                {data => <ListRoute data={data} filter={filter} act={act} refresh={refresh} />}
              </RequireData>
            } />
          </Routes>
        </main>

        {calendarUrl && (
          <iframe
            className={styles.calendarFrame}
            src={calendarUrl}
            style={{ display: isCalendar ? 'block' : 'none' }}
          />
        )}
      </div>
    </>
  );
}
