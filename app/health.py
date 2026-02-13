# filename: app/health.py

from __future__ import annotations
from typing import Dict
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading


def health_check() -> Dict[str, str]:
    """
    Simple health check for tests and monitoring.
    """
    return {"status": "ok"}


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            payload = json.dumps(health_check()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_response(404)
            self.end_headers()


def start_health_server(port: int = 8080) -> None:
    """
    Starts a background HTTP server exposing /health.
    """
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
