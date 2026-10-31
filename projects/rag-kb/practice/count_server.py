from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        self.rfile.read(length)  # 先把请求体读完，避免客户端收到连接重置
        print("收到一次请求", flush=True)
        body = b'{"error": {"message": "boom", "type": "server_error"}}'
        self.send_response(500)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass  # 关掉默认访问日志，只保留上面那行


HTTPServer(("127.0.0.1", 9999), Handler).serve_forever()
