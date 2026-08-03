#!/usr/bin/env python3
"""Small dependency-free HTTP API for browser activity events."""

from __future__ import annotations

import json
import os
import sqlite3
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_DB_PATH = os.environ.get("VISUAL_AGENT_DB", "events.sqlite3")
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def connect_database(path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS browser_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            url TEXT NOT NULL,
            title TEXT NOT NULL DEFAULT '',
            timestamp TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'extension',
            received_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    connection.commit()
    return connection


def validate_event(payload: object) -> dict[str, str]:
    if not isinstance(payload, dict):
        raise ValueError("JSON body must be an object")
    required = ("event_type", "url", "timestamp")
    if any(not isinstance(payload.get(key), str) or not payload[key].strip() for key in required):
        raise ValueError("event_type, url, and timestamp are required strings")
    return {
        "event_type": payload["event_type"].strip(),
        "url": payload["url"].strip(),
        "title": str(payload.get("title", ""))[:500],
        "timestamp": payload["timestamp"].strip(),
        "source": str(payload.get("source", "extension"))[:100],
    }


class EventHandler(BaseHTTPRequestHandler):
    db_path = DEFAULT_DB_PATH

    def _send_json(self, status: HTTPStatus, body: dict[str, object]) -> None:
        encoded = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(encoded)

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in {"/", "/dashboard"}:
            dashboard = (PROJECT_ROOT / "dashboard.html").read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(dashboard)))
            self.end_headers()
            self.wfile.write(dashboard)
            return
        if path == "/health":
            self._send_json(HTTPStatus.OK, {"status": "ok"})
            return
        if path == "/api/events":
            with connect_database(self.db_path) as connection:
                rows = connection.execute(
                    "SELECT id, event_type, url, title, timestamp, source, received_at "
                    "FROM browser_events ORDER BY id DESC LIMIT 100"
                ).fetchall()
            self._send_json(HTTPStatus.OK, {"events": [dict(row) for row in rows]})
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/events":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 32_768:
                raise ValueError("request body is too large")
            payload = json.loads(self.rfile.read(length))
            event = validate_event(payload)
            with connect_database(self.db_path) as connection:
                cursor = connection.execute(
                    "INSERT INTO browser_events (event_type, url, title, timestamp, source) "
                    "VALUES (:event_type, :url, :title, :timestamp, :source)", event
                )
                connection.commit()
            self._send_json(HTTPStatus.CREATED, {"id": cursor.lastrowid, "event": event})
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})

    def log_message(self, format: str, *args: object) -> None:
        return


def run(host: str = "127.0.0.1", port: int = 8787, db_path: str = DEFAULT_DB_PATH) -> None:
    EventHandler.db_path = db_path
    server = ThreadingHTTPServer((host, port), EventHandler)
    print(f"Visual Browser Agent API listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
