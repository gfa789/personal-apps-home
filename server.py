"""Owner-only, loopback homepage behind Tailscale Serve."""
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

class Server(ThreadingHTTPServer):
    daemon_threads = True
    def __init__(self, port=8880, owner=None):
        self.owner = owner or os.environ["TAILSCALE_OWNER"]
        super().__init__(("127.0.0.1", port), Handler)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass
    def do_GET(self):
        if self.headers.get_all("Tailscale-User-Login", []) != [self.server.owner]:
            status, body = 403, b""
        elif urlsplit(self.path).path != "/":
            status, body = 404, b""
        else:
            status, body = 200, Path(__file__).with_name("index.html").read_bytes()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)
    do_HEAD = do_GET

if __name__ == "__main__":
    with Server() as server:
        server.serve_forever()
