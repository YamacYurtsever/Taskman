import { useCallback, useEffect, useState } from 'react';
import { api } from '../lib/api';
import type { StateResponse } from '../lib/types';


export const useAppData = () => {
  const [data, setData] = useState<StateResponse | null>(null);
  const [calendarUrl, setCalendarUrl] = useState('');

  const refresh = useCallback(async () => {
    setData(await api.state());
  }, []);

  const act = useCallback(async (path: string, body: unknown) => {
    const res = await api.post(path, body);

    if (res?.ok) {
      setData(await api.state());
    }
  }, []);

  useEffect(() => {
    const syncConfig = async () => {
      const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      let config = await api.config();
      if (!config) return;

      if (browserTimezone && browserTimezone !== config.calendarTimezone) {
        const res = await api.setTimezone(browserTimezone);
        if (res?.ok) {
          config = await api.config();
          if (!config) return;
        }
      }

      setCalendarUrl(config.calendarUrl || '');
      setData(await api.state());
    };

    syncConfig();
  }, []);

  const logout = useCallback(async () => {
    await api.logout();
  }, []);

  return { data, calendarUrl, act, refresh, logout };
};
