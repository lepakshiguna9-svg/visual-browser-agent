CREATE TABLE IF NOT EXISTS browser_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    url TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    timestamp TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'extension',
    received_at TEXT NOT NULL DEFAULT (datetime('now'))
);
