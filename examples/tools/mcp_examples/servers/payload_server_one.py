from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class PayloadHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        payload = {
            "function_name": "get_crypto_price",
            "server_url": "http://0.0.0.0:8000/sse",
            "payload": {"coin_id": "bitcoin"},
        }
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 9000), PayloadHandler).serve_forever()
