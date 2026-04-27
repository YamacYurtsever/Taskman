# Taskman

A minimal web-based task manager for personal daily use. Tasks live in lists, lists can be grouped, and everything is stored in a flat JSON file at `~/.taskman/db.json`.

---

## Setup

Install Python dependencies:

```bash
pip install flask
```

Build the frontend once before serving:

```bash
cd client
npm install
npm run build
```

---

## Running

```bash
python -m server
```

Opens a local web interface at `http://127.0.0.1:5050` with:

- Cards view of all lists and groups with pending tasks
- Focused view per list with pending + completed tasks
- Daysheet view with date navigation and log entry form
- Google Calendar embed (week view, multi-calendar support)
- Filter pills: All / Week / Day
- Inline task add, mark done, delete, rename, move, and continue
- Light/dark mode

```bash
python -m server --port 8080 --debug
```

For frontend development, run Flask for the API and Vite for the React app in parallel:

```bash
python -m server
cd client && npm run dev
```

---

### Calendar Config

Create `~/.taskman/config.json` to configure which calendars appear:

```json
{
  "calendars": [
    { "id": "you@gmail.com", "color": "#B39DDB" },
    { "id": "other@group.calendar.google.com", "color": "#E67C73" }
  ],
  "calendarTimezone": "America/Sydney"
}
```
