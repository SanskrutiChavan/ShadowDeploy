from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        print(f"Request: {args}", flush=True)

print("=== Auth Service starting on port 5000 ===", flush=True)

# App listens on 5000, but K8s probe checks 8080 → probe fails

HTTPServer(("", 5000), Handler).serve_forever()

