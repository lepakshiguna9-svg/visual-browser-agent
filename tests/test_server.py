import json
import os
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

from backend.server import EventHandler


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.database = tempfile.NamedTemporaryFile(delete=False)
        self.database.close()
        EventHandler.db_path = self.database.name
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), EventHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.connection = HTTPConnection("127.0.0.1", self.server.server_port)

    def tearDown(self):
        self.connection.close()
        self.server.shutdown()
        self.server.server_close()
        os.unlink(self.database.name)

    def request_json(self, method, path, body=None):
        encoded = json.dumps(body).encode() if body is not None else None
        self.connection.request(method, path, encoded, {"Content-Type": "application/json"} if encoded else {})
        response = self.connection.getresponse()
        return response.status, json.loads(response.read())

    def test_health_and_event_round_trip(self):
        self.assertEqual(self.request_json("GET", "/health")[0], 200)
        status, body = self.request_json("POST", "/api/events", {
            "event_type": "page_view",
            "url": "https://example.com/",
            "title": "Example",
            "timestamp": "2026-08-03T10:00:00Z",
        })
        self.assertEqual(status, 201)
        self.assertEqual(body["event"]["url"], "https://example.com/")
        status, body = self.request_json("GET", "/api/events")
        self.assertEqual(status, 200)
        self.assertEqual(body["events"][0]["title"], "Example")

    def test_invalid_event_is_rejected(self):
        status, body = self.request_json("POST", "/api/events", {"url": "https://example.com"})
        self.assertEqual(status, 400)
        self.assertIn("required strings", body["error"])


if __name__ == "__main__":
    unittest.main()
