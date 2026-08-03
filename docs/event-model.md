# Event Model

The API accepts JSON objects shaped like this:

```json
{
  "event_type": "page_view",
  "url": "https://example.com/",
  "title": "Example",
  "timestamp": "2026-08-03T10:00:00Z",
  "source": "tabs.onUpdated"
}
```

The backend adds an auto-incrementing `id` and a server-side `received_at` value. The schema is duplicated in `backend/schema.sql` so it can be migrated to another SQLite-compatible workflow later.
