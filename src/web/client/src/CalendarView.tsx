import { MSG } from './utils';

export function CalendarView({ calendarUrl }: { calendarUrl: string }) {
  if (!calendarUrl) {
    return <div className="empty">{MSG.noCalUrl}</div>;
  }
  return null;
}
