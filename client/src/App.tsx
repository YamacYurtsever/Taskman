import { useCallback, useEffect, useState } from 'react';
import { Navigate, Route, Routes, useLocation, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import styles from './App.module.css';
import { api } from './lib/api';
import { CalendarView } from './views/CalendarView';
import { DaysheetView } from './views/DaysheetView';
import { Sidebar } from './components/Sidebar';
import { CardsView, FocusedView } from './views/TasksView';
import { Topbar } from './components/Topbar';
import type { DaysheetResponse, StateResponse, TaskFilter } from './lib/types';
import { todayStr } from './lib/utils';

type Action = (path: string, body: unknown) => Promise<void>;

function CardsRoute({ data, filter, expandedCards, setExpandedCards, act, refresh }: {
  data: StateResponse;
  filter: TaskFilter;
  expandedCards: Set<string>;
  setExpandedCards: (next: Set<string>) => void;
  act: Action;
  refresh: () => Promise<void>;
}) {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const selectedGroup = searchParams.get('group');
  return (
    <CardsView
      data={data}
      filter={filter}
      selectedGroup={selectedGroup}
      expandedCards={expandedCards}
      setExpandedCards={setExpandedCards}
      selectGroup={id => navigate(id ? `/tasks?group=${id}` : '/tasks')}
      selectList={id => navigate(`/list/${id}`)}
      act={act}
      refresh={refresh}
    />
  );
}

function FocusedRoute({ data, filter, showDone, setShowDone, act, refresh }: {
  data: StateResponse;
  filter: TaskFilter;
  showDone: Set<string>;
  setShowDone: (next: Set<string>) => void;
  act: Action;
  refresh: () => Promise<void>;
}) {
  const { listId } = useParams<{ listId: string }>();
  return (
    <FocusedView
      data={data}
      listId={listId!}
      filter={filter}
      showDone={showDone}
      setShowDone={setShowDone}
      act={act}
      refresh={refresh}
    />
  );
}

export function App() {
  const location = useLocation();
  const [filter, setFilter] = useState<TaskFilter>('all');
  const [data, setData] = useState<StateResponse | null>(null);
  const [daysheet, setDaysheet] = useState<DaysheetResponse | null>(null);
  const [daysheetDate, setDaysheetDate] = useState(todayStr());
  const [calendarUrl, setCalendarUrl] = useState('');
  const [showDone, setShowDone] = useState(new Set<string>());
  const [expandedCards, setExpandedCards] = useState(new Set<string>());

  const isDaysheet = location.pathname === '/daysheet';
  const isCalendar = location.pathname === '/calendar';

  const refresh = useCallback(async () => {
    if (isDaysheet) {
      const [nextDaysheet, nextData] = await Promise.all([api.daysheet(daysheetDate), api.state()]);
      setDaysheet(nextDaysheet);
      setData(nextData);
    } else {
      setData(await api.state());
    }
  }, [daysheetDate, isDaysheet]);

  const act = useCallback(async (path: string, body: unknown) => {
    const res = await api.post(path, body);
    if (res?.ok) {
      setData(null);
      setDaysheet(null);
      if (isDaysheet) {
        const [nextDaysheet, nextData] = await Promise.all([api.daysheet(daysheetDate), api.state()]);
        setDaysheet(nextDaysheet);
        setData(nextData);
      } else {
        setData(await api.state());
      }
    }
  }, [daysheetDate, isDaysheet]);

  useEffect(() => {
    api.config().then(cfg => {
      if (cfg?.calendarUrl) setCalendarUrl(cfg.calendarUrl);
    });
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <>
      <Sidebar data={data} filter={filter} act={act} refresh={refresh} />
      <div className={styles.content}>
        <Topbar filter={filter} setFilter={setFilter} />
        <main className={styles.main} style={{ display: isCalendar && calendarUrl ? 'none' : undefined }}>
          <Routes>
            <Route path="/" element={<Navigate to="/tasks" replace />} />
            <Route path="/calendar" element={<CalendarView calendarUrl={calendarUrl} />} />
            <Route path="/daysheet" element={
              <DaysheetView
                data={data}
                daysheet={daysheet}
                daysheetDate={daysheetDate}
                setDaysheetDate={setDaysheetDate}
                act={act}
                refresh={refresh}
              />
            } />
            <Route path="/list/:listId" element={
              data ? (
                <FocusedRoute
                  data={data}
                  filter={filter}
                  showDone={showDone}
                  setShowDone={setShowDone}
                  act={act}
                  refresh={refresh}
                />
              ) : null
            } />
            <Route path="/tasks" element={
              data ? (
                <CardsRoute
                  data={data}
                  filter={filter}
                  expandedCards={expandedCards}
                  setExpandedCards={setExpandedCards}
                  act={act}
                  refresh={refresh}
                />
              ) : null
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
