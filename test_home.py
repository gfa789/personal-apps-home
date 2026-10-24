import http.client
import threading
import unittest
from server import Server

class HomeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = Server(0, "owner@example.com")
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
    def request(self, path="/", owner="owner@example.com", method="GET"):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        conn.request(method, path, headers={"Tailscale-User-Login": owner} if owner else {})
        r = conn.getresponse()
        result = r.status, r.read(), dict(r.getheaders())
        conn.close()
        return result
    def test_home_links_and_security_headers(self):
        status, body, headers = self.request()
        self.assertEqual(status, 200)
        self.assertIn(b'href="/running/"', body)
        self.assertIn(b'href="/chess/"', body)
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        self.assertEqual(headers["Cache-Control"], "no-store")
    def test_identity_guard_and_loopback(self):
        self.assertEqual(self.server.server_address[0], "127.0.0.1")
        for owner in (None, "other@example.com"):
            self.assertEqual(self.request(owner=owner)[0], 403)
    def test_head_and_unknown_paths(self):
        self.assertEqual(self.request(method="HEAD")[:2], (200, b""))
        self.assertEqual(self.request("/server.py")[0], 404)

if __name__ == "__main__":
    unittest.main()
