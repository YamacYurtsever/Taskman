import { useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import {
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
  useSearchParams,
} from 'react-router-dom';

import styles from './App.module.css';
import { Sidebar } from './components/Sidebar/Sidebar';
import { Topbar } from './components/Topbar';
import { useAppData } from './hooks/useAppData';
import { useIsMobile } from './hooks/useIsMobile';
import type { StateResponse, TaskFilter } from './lib/types';
import { CalendarView } from './views/CalendarView';
import { CardsView } from './views/CardsView';
import { DaysheetView } from './views/DaysheetView';
import { FocusedView } from './views/FocusedView';

type Action = (path: string, body: unknown) => Promise<void>;

type RouteProps = {
  data: StateResponse;
  filter: TaskFilter;
  act: Action;
};

type RequireDataProps = {
  data: StateResponse | null;
  children: (data: StateResponse) => ReactNode;
};

const RequireData = ({ data, children }: RequireDataProps) => {
  if (!data) return <p>Loading...</p>;
  return children(data);
};

const TasksRoute = ({ data, filter, act }: RouteProps) => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  return (
    <CardsView
      data={data}
      filter={filter}
      selectedGroup={searchParams.get('group')}
      selectGroup={id => navigate(id ? `/tasks?group=${id}` : '/tasks')}
      selectList={id => navigate(`/list/${id}`)}
      act={act}
    />
  );
};

const ListRoute = ({ data, filter, act }: RouteProps) => {
  const { listId } = useParams<{ listId: string }>();

  if (!listId) {
    return <Navigate to="/tasks" replace />;
  }

  return <FocusedView data={data} listId={listId} filter={filter} act={act} />;
};

const App = () => {
  const [filter, setFilter] = useState<TaskFilter>('all');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { data, calendarUrl, act, refresh } = useAppData();
  const isMobile = useIsMobile();

  const { pathname } = useLocation();
  const showingCalendar = pathname === '/calendar' && calendarUrl;
  const activeCalendarUrl = isMobile
    ? calendarUrl.replace('mode=WEEK', 'mode=AGENDA')
    : calendarUrl;

  useEffect(() => {
    if (!isMobile) {
      setSidebarOpen(false);
    }
  }, [isMobile]);

  useEffect(() => {
    setSidebarOpen(false);
  }, [pathname]);

  return (
    <>
      <Sidebar
        data={data}
        filter={filter}
        act={act}
        refresh={refresh}
        isMobile={isMobile}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />
      {isMobile && sidebarOpen && (
        <button
          aria-label="Close navigation"
          className={styles.sidebarBackdrop}
          onClick={() => setSidebarOpen(false)}
        />
      )}
      <div className={styles.content}>

        <Topbar
          filter={filter}
          setFilter={setFilter}
          showMenuButton={isMobile}
          onMenuClick={() => setSidebarOpen(true)}
        />
        <main className={styles.main}>

          <div hidden={!!showingCalendar}>
            <Routes>
              <Route path="/" element={<Navigate to="/tasks" replace />} />
              <Route path="/calendar" element={<CalendarView calendarUrl={calendarUrl} />} />
              <Route path="/daysheet" element={<DaysheetView data={data} act={act} refresh={refresh} />} />
              <Route
                path="/tasks"
                element={
                  <RequireData data={data}>
                    {data => <TasksRoute data={data} filter={filter} act={act} />}
                  </RequireData>
                }
              />
              <Route
                path="/list/:listId"
                element={
                  <RequireData data={data}>
                    {data => <ListRoute data={data} filter={filter} act={act} />}
                  </RequireData>
                }
              />
            </Routes>
          </div>

          {calendarUrl && (
            <iframe
              hidden={!showingCalendar}
              className={styles.calendarFrame}
              src={activeCalendarUrl}
              title="Calendar"
            />
          )}
        </main>
      </div>
    </>
  );
};

export type { Action };
export { App };
