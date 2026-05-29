#!/usr/bin/env python3
"""
Local server for Apollyon Dynamics site.
Serves static files, stubs API routes, and falls back to index.html for SPA routing.
Run: python serve.py
Then open: http://localhost:3000
"""
import os
import sys
import json
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from pathlib import Path

PORT = 3000
ROOT = Path(__file__).parent

STUB_NEWS = json.dumps({
    "items": [
        {
            "title": "Apollyon Dynamics Unveils Nightshade ADX-1",
            "link": "https://apollyondynamics.com",
            "pubDate": "2025-01-01T00:00:00Z",
            "source": "Apollyon Dynamics"
        }
    ]
}).encode()


class SPAHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        path = self.path.split("?")[0].split("#")[0]

        # Stub API routes
        if path.startswith("/api/"):
            if "news" in path:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(STUB_NEWS)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                try:
                    self.wfile.write(STUB_NEWS)
                except (ConnectionResetError, BrokenPipeError):
                    pass
            else:
                self.send_response(404)
                self.end_headers()
            return

        file_path = ROOT / path.lstrip("/")
        if not file_path.is_file():
            self.path = "/index.html"

        try:
            super().do_GET()
        except (ConnectionResetError, BrokenPipeError, socket.error):
            pass

    def log_message(self, format, *args):
        print(f"  {args[1]}  {args[0]}")


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        exc = sys.exc_info()[1]
        if isinstance(exc, (ConnectionResetError, BrokenPipeError, socket.error)):
            return
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    os.chdir(ROOT)
    server = ThreadedHTTPServer(("localhost", PORT), SPAHandler)
    print(f"\n  Apollyon Dynamics — local server")
    print(f"  http://localhost:{PORT}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        sys.exit(0)
