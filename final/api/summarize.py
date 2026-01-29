"""
Vercel 서버리스: 뉴스 요약 API. API 키는 환경변수에서만 사용됩니다.
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gemini_service import summarize_news


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
            data = _read_json_body(self)
            keyword = (data.get("keyword") or "").strip()
            articles = data.get("articles") or []
            if not articles:
                _send_json(self, 400, {"ok": False, "error": "먼저 뉴스를 수집하세요."})
                return
            summary = summarize_news(keyword, articles)
            _send_json(self, 200, {"ok": True, "summary": summary})
        except Exception as e:
            _send_json(self, 500, {"ok": False, "error": str(e)})
