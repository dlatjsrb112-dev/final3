"""
Vercel 서버리스: 뉴스 챗 API. API 키는 환경변수에서만 사용됩니다.
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)


def _read_json_body(handler: BaseHTTPRequestHandler):
    length = int(handler.headers.get("Content-Length", 0))
    if length == 0:
        return {}
    raw = handler.rfile.read(length)
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return {}


def _send_json(handler: BaseHTTPRequestHandler, status: int, data: dict):
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        try:
            from gemini_service import chat_with_news
        except Exception as e:
            _send_json(self, 500, {"ok": False, "error": "모듈 로드 실패: " + str(e)})
            return
        try:
            data = _read_json_body(self)
            message = (data.get("message") or "").strip()
            history = data.get("history") or []
            summary = (data.get("summary") or "").strip()
            keyword = (data.get("keyword") or "").strip()
            if not summary:
                _send_json(self, 400, {"ok": False, "error": "먼저 뉴스를 수집하고 요약하세요."})
                return
            if not message:
                _send_json(self, 400, {"ok": False, "error": "메시지를 입력하세요."})
                return
            chat_history = [
                {"role": h.get("role"), "parts": [{"text": h.get("text", "")}]}
                for h in history
                if h.get("role") in ("user", "model")
            ]
            reply = chat_with_news(message, keyword, summary, chat_history)
            _send_json(self, 200, {"ok": True, "reply": reply})
        except Exception as e:
            _send_json(self, 500, {"ok": False, "error": str(e)})
