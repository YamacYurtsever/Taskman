# Taskman

A minimal web-based task manager built for personal daily use. Tasks are organized into lists, and lists can be optionally grouped. Each task has a name, a parent list, and an optional due date. Data is stored in a flat JSON file at `~/.taskman/db.json`.

---

### Agent Workflow

After completing each milestone item:

- Add unit tests for any new API endpoints or service logic
- Run `python -m pytest server/ -v` and confirm all pass
- Run `python -m vulture server --min-confidence 80` and confirm it has no findings
- Check off the item in the milestones section
- Run `git add . && git commit -m "<description>"`

After changes to `server/` or `server/config.py`, advise the user to restart the web server:

```bash
python -m server
```

After changes to the frontend source, advise the user to rebuild:

```bash
cd client && npm run build
```

Then hard-refresh with Cmd+Shift+R.

---

### Project Structure

```
taskman/
  server/               Flask app and all backend logic
    __init__.py         App factory and API routes
    __main__.py         Entry point for python -m server
    services/           Business logic called by routes
      daysheet.py       Log and continue entry operations
      tasks.py          Task CRUD operations
      utils.py          Shared helpers (find, require, db mutations)
    db.py               JSON persistence (~/.taskman/db.json)
    config.py           Config loader (~/.taskman/config.json)
    constants.py        Shared constants and DaysheetEntryType
    tests/              Pytest test suite
      test_api.py       Flask route tests
      test_daysheet.py  Daysheet service tests
      test_tasks.py     Task service tests
      test_utils.py     Utility function tests
      helpers.py        Shared test fixtures
    pytest.ini          Pytest config (pythonpath, testpaths)
  client/               Vite + React + TypeScript frontend
    src/
      App.tsx           Root component and state
      views/            CalendarView, DaysheetView, TasksView
      components/       Sidebar, Topbar, ThemeToggle, InlineAdd, icons
      lib/              api.ts, types.ts, utils.ts
    static/             Static assets (logo, etc.)
    index.html
    vite.config.ts
    tsconfig.json
    package.json
```

---

### Implementation Notes

- The Flask server exposes a REST API; some endpoints delegate to service functions, others mutate the DB directly for complex operations.
- Service functions in `server/services/` use a CLI-style `args` list interface and raise `SystemExit` on error — the `_run()` helper in `server/__init__.py` captures both.
- There is no schema migration layer. Any new task fields must be backward-compatible with existing JSON records.
- The frontend is built with Vite and served as static files from `client/dist/`. In dev mode, Vite proxies `/api` to the Flask server on port 5050.

---

### Database Schema

```json
{
  "groups": [{ "id": "uuid", "name": "UNSW" }],
  "lists":  [{ "id": "uuid", "name": "COMP3131", "groupId": "uuid | null" }],
  "tasks":  [{ "id": "uuid", "name": "Finish Assignment 5", "listId": "uuid", "due": "2026-04-30 | null", "done": "2026-04-26 | null" }],
  "daysheet": [{ "id": "uuid", "datetime": "2026-04-26T14:32:05", "listId": "uuid", "type": "log | continue | done", "text": "Talked with Baba" }]
}
```

---

### Tech Stack

- **Backend:** Python, Flask
- **Frontend:** Vite + React + TypeScript
- **Storage:** JSON flat file (`~/.taskman/db.json`)
- **Tests:** `python -m pytest server/ -v`
- **Frontend build:** `cd client && npm run build`
- **Dead code check:** `python -m vulture server --min-confidence 80`
- **CI:** `.github/workflows/ci.yml` — installs deps, builds frontend, runs tests and Vulture

---

### Milestones

##### Milestone 1 — Server

- [x] Flask server with REST API in `server/__init__.py`
- [x] Service layer in `server/services/`
- [x] JSON persistence in `server/db.py`
- [x] Config loader in `server/config.py`

##### Milestone 2 — Client

- [x] Cards view: all lists/groups with pending tasks, 4-column responsive grid
- [x] Focused view: single list with pending + completed tasks
- [x] Daysheet view: day sheet with date navigation
- [x] Filter pills: All / Week / Day
- [x] Sidebar: Calendar + Daysheet + Tasks nav, groups, lists, alphabetical with Others last
- [x] Add / mark done / undo / delete / rename / move tasks
- [x] Create / rename / delete lists and groups
- [x] Move list to group / ungroup
- [x] Add / edit / delete daysheet log entries
- [x] Continue task (logs to daysheet)
- [x] Light/dark mode toggle (persisted to `localStorage`)

##### Milestone 3 — Google Calendar

- [x] Google Calendar iframe embedded (week view by default)
- [x] Multi-calendar support via `~/.taskman/config.json`
- [x] Per-calendar color override via embed `color` param
- [x] iframe kept in DOM — switching views shows/hides it instantly

###### Calendar Config (`~/.taskman/config.json`)

```json
{
  "calendars": [
    { "id": "you@gmail.com", "color": "#B39DDB" },
    { "id": "other@group.calendar.google.com", "color": "#E67C73" }
  ],
  "calendarTimezone": "America/Sydney"
}
```

Google Calendar embed colors: `#E67C73` Flamingo · `#33B679` Sage · `#B39DDB` Wisteria · `#039BE5` Peacock · `#3F51B5` Blueberry · `#7986CB` Lavender · `#8E24AA` Grape · `#F6BF26` Banana · `#F4511E` Tangerine · `#0B8043` Basil · `#D50000` Tomato · `#616161` Graphite

##### Milestone 4 — Responsiveness

- [ ] Sidebar collapses to a full-page overlay from a burger icon
- [ ] Focused view and daysheet fill full width on mobile
- [ ] Calendar iframe scales to viewport width, day view on mobile

##### Milestone 5 — Task Descriptions

- [ ] Add `description` field to task schema (backward-compatible)
- [ ] API endpoint to read/write a task description
- [ ] Small icon on task rows when a description exists
- [ ] Task detail panel: name, list, due date at top; editable textarea below; debounced save; Escape closes
- [ ] Opens as side panel when wide enough, replaces main content on mobile
- [ ] Raw URLs in descriptions rendered as clickable links

##### Milestone 6 — Authentication

- [ ] User/account model supporting local single-user and future hosted deployment
- [ ] Web auth flow: login, logout, session handling
- [ ] All API endpoints protected when auth is enabled
- [ ] Auth config: mode, secrets, redirect URLs (no committed secrets)
- [ ] OAuth provider support with token refresh
- [ ] Google OAuth: pull the user's calendars automatically, replacing the manual `config.json` calendar list
- [ ] Account/settings UI for managing connected providers and calendar selection
- [ ] Persistence boundaries ready for a deployed database
