import { useCallback, useEffect, useState } from 'react';
import { api } from './api';
import { CalendarView } from './CalendarView';
import { DaysheetView } from './DaysheetView';
import { Sidebar } from './Sidebar';
import { CardsView, FocusedView } from './TasksView';
import { Topbar } from './Topbar';
import type { DaysheetResponse, StateResponse, TaskFilter, ViewMode } from './types';
import { todayStr } from './utils';

export function App() {
  const [view, setView] = useState<ViewMode>('tasks');
  const [filter, setFilter] = useState<TaskFilter>('all');
  const [selectedList, setSelectedList] = useState<string | null>(null);
  const [selectedGroup, setSelectedGroup] = useState<string | null>(null);
  const [data, setData] = useState<StateResponse | null>(null);
  const [daysheet, setDaysheet] = useState<DaysheetResponse | null>(null);
  const [daysheetDate, setDaysheetDate] = useState(todayStr());
  const [calendarUrl, setCalendarUrl] = useState('');
  const [showDone, setShowDone] = useState(new Set<string>());
  const [expandedCards, setExpandedCards] = useState(new Set<string>());

  const refresh = useCallback(async () => {
    if (view === 'daysheet') {
      const [nextDaysheet, nextData] = await Promise.all([
        api.daysheet(daysheetDate),
        api.state(),
      ]);
      setDaysheet(nextDaysheet);
      setData(nextData);
    } else {
      setData(await api.state());
    }
  }, [daysheetDate, view]);

  const act = useCallback(async (path: string, body: unknown) => {
    const res = await api.post(path, body);
    if (res?.ok) {
      setData(null);
      setDaysheet(null);
      if (view === 'daysheet') {
        const [nextDaysheet, nextData] = await Promise.all([api.daysheet(daysheetDate), api.state()]);
        setDaysheet(nextDaysheet);
        setData(nextData);
      } else {
        setData(await api.state());
      }
    }
  }, [daysheetDate, view]);

  useEffect(() => {
    api.config().then(cfg => {
      if (cfg?.calendarUrl) setCalendarUrl(cfg.calendarUrl);
    });
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const selectList = (id: string | null) => {
    setSelectedList(id);
    if (id) setSelectedGroup(null);
    setView('tasks');
  };

  const selectGroup = (id: string | null) => {
    setSelectedGroup(id);
    if (id) setSelectedList(null);
    setView('tasks');
  };

  const isCalendar = view === 'calendar';

  return (
    <>
      <Sidebar
        data={data}
        view={view}
        filter={filter}
        selectedList={selectedList}
        selectedGroup={selectedGroup}
        setView={setView}
        selectList={selectList}
        selectGroup={selectGroup}
        act={act}
        refresh={refresh}
      />
      <div id="content">
        <Topbar view={view} filter={filter} setFilter={setFilter} />
        <main id="main" style={{ display: isCalendar && calendarUrl ? 'none' : undefined }}>
          {view === 'calendar' && <CalendarView calendarUrl={calendarUrl} />}
          {view === 'daysheet' && (
            <DaysheetView
              data={data}
              daysheet={daysheet}
              daysheetDate={daysheetDate}
              setDaysheetDate={setDaysheetDate}
              act={act}
              refresh={refresh}
            />
          )}
          {view === 'tasks' && data && selectedList && (
            <FocusedView
              data={data}
              listId={selectedList}
              filter={filter}
              showDone={showDone}
              setShowDone={setShowDone}
              act={act}
              refresh={refresh}
            />
          )}
          {view === 'tasks' && data && !selectedList && (
            <CardsView
              data={data}
              filter={filter}
              selectedGroup={selectedGroup}
              expandedCards={expandedCards}
              setExpandedCards={setExpandedCards}
              selectGroup={selectGroup}
              selectList={selectList}
              act={act}
              refresh={refresh}
            />
          )}
        </main>
        {calendarUrl && (
          <iframe
            id="calendar-frame"
            className="calendar-frame"
            src={calendarUrl}
            frameBorder="0"
            scrolling="no"
            style={{ display: isCalendar ? 'block' : 'none' }}
          />
        )}
      </div>
    </>
  );
}
