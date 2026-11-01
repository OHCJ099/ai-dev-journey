"""假上游：按 MODE 返回指定状态码，或干脆不回（用来造超时）。只做测量，不是练习。"""

import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

MODE = os.getenv("MODE", "401")  # 401 / 402 / 429 / timeout / empty / nousage

ERROR_BODY = b'{"error": {"message": "fake", "type": "fake_error", "code": "fake"}}'


def reply_body() -> bytes:
    if MODE not in ("empty", "nousage"):
        return ERROR_BODY
    usage = (
        ""
        if MODE == "nousage"
        else ', "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}'
    )
    return (
        '{"id": "chatcmpl-fake", "object": "chat.completion", "created": 1,'
        ' "model": "fake", "choices": [{"index": 0, "message":'
        ' {"role": "assistant", "content": ""}, "finish_reason": "stop"}]' + usage + "}"
    ).encode()


class H(BaseHTTPRequestHandler):
    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if MODE == "timeout":
            time.sleep(70)  # 客户端 60 秒读超时，会先放弃
            return
        body = reply_body()
        self.send_response(200 if MODE in ("empty", "nousage") else int(MODE))
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        pass


print("fake upstream on 127.0.0.1:9998, mode =", MODE, flush=True)
HTTPServer(("127.0.0.1", 9998), H).serve_forever()
