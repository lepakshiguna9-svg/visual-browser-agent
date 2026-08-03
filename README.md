# Visual Browser Agent

A minimal Chrome Manifest V3 prototype that records browser navigation metadata and posts it to a local SQLite-backed HTTP API.

## What it tracks

The extension records a basic `page_view` event with:

- `url`
- `title`
- ISO 8601 `timestamp`
- event `source`

It listens to completed tab navigations and tab activation. It does not capture screenshots, keystrokes, page contents, passwords, or form fields.

## Permissions

- `tabs`: read the active tab's URL and title when a navigation or activation event fires.
- `storage`: save the backend URL and tracking toggle.
- `http://localhost:8787/*`: send events to the local development API.

The extension is intentionally scoped to a local backend by default. Change the backend URL from the extension's options page if you deploy the API elsewhere, and update `host_permissions` in `extension/manifest.json` for production.

## Run the backend

Python 3.10+ is enough; no third-party packages are required.

```bash
cd backend
python3 server.py
```

The API listens on `http://127.0.0.1:8787` and stores data in `events.sqlite3`. Set `VISUAL_AGENT_DB=/path/to/events.sqlite3` to choose another database file.

Endpoints:

- `GET /health`
- `POST /api/events`
- `GET /api/events` (latest 100 events)

## Load the Chrome extension

1. Open `chrome://extensions`.
2. Enable **Developer mode**.
3. Select **Load unpacked**.
4. Choose this project's `extension` directory.
5. Open the extension's **Details → Extension options** if you need to change the backend URL or disable tracking.

## Test

From the project root:

```bash
python3 -m unittest discover -s tests -v
```

Manual smoke test:

1. Start the backend.
2. Load the unpacked extension.
3. Visit two normal web pages in Chrome.
4. Query `http://127.0.0.1:8787/api/events` and confirm the URL, title, and timestamp are present.

## Development history

This repository intentionally keeps multiple focused commits rather than squashing the implementation history.
