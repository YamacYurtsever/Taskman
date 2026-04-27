import type { ApiResult, ConfigResponse, DaysheetResponse, StateResponse } from './types';

export const API = {
  config: '/api/config',
  state: '/api/state',
  daysheet: '/api/daysheet',
  add: '/api/add',
  addList: '/api/add-list',
  moveTask: '/api/move-task',
  moveList: '/api/move-list',
  renameList: '/api/rename-list',
  deleteList: '/api/delete-list',
  renameGroup: '/api/rename-group',
  deleteGroup: '/api/delete-group',
  done: '/api/done',
  undo: '/api/undo',
  delete: '/api/delete',
  continue: '/api/continue',
  edit: '/api/edit',
  log: '/api/log',
  daysheetDelete: '/api/daysheet/delete',
  daysheetEdit: '/api/daysheet/edit',
};

export async function request<T>(method: string, path: string, body?: unknown): Promise<T | null> {
  const opts: RequestInit = { method };
  if (body !== undefined) {
    opts.headers = { 'Content-Type': 'application/json' };
    opts.body = JSON.stringify(body);
  }

  try {
    const res = await fetch(path, opts);
    const json = await res.json();
    if (!res.ok) {
      console.log(json.message || json.error || 'Request failed');
      return null;
    }
    return json as T;
  } catch {
    console.log('Request failed');
    return null;
  }
}

export const api = {
  config: () => request<ConfigResponse>('GET', API.config),
  state: () => request<StateResponse>('GET', API.state),
  daysheet: (date: string) => request<DaysheetResponse>('GET', `${API.daysheet}?date=${date}`),
  post: (path: string, body: unknown) => request<ApiResult>('POST', path, body),
};
