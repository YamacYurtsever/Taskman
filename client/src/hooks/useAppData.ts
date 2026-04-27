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
    api.config().then(config => {
      if (config?.calendarUrl) {
        setCalendarUrl(config.calendarUrl);
      }
    });
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data, calendarUrl, act, refresh };
};
