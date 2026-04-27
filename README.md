# Taskman

A minimal web-based task manager for personal daily use. Tasks live in lists, lists can be grouped, and everything is stored in a flat JSON file at `~/.taskman/db.json`.

---

## Setup

```bash
pip install flask
```

```bash
cd client && npm install && npm run build
```

---

## Running

```bash
python -m server
```

Opens `http://127.0.0.1:5050`.

```bash
python -m server --port 8080 --debug
```

For frontend development, run both in parallel:

```bash
python -m server
cd client && npm run dev
```

---

## Calendar Config

Create `~/.taskman/config.json` to configure which calendars appear in the embedded Google Calendar view:

```json
{
  "calendars": [
    { "id": "you@gmail.com", "color": "#B39DDB" },
    { "id": "other@group.calendar.google.com", "color": "#E67C73" }
  ],
  "calendarTimezone": "America/Sydney"
}
```

Available colors: `#E67C73` Flamingo · `#33B679` Sage · `#B39DDB` Wisteria · `#039BE5` Peacock · `#3F51B5` Blueberry · `#7986CB` Lavender · `#8E24AA` Grape · `#F6BF26` Banana · `#F4511E` Tangerine · `#0B8043` Basil · `#D50000` Tomato · `#616161` Graphite
