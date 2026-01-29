"""
Vercel 서버리스: 뉴스 수집 API. API 키는 환경변수에서만 사용됩니다.
"""
import json
import os
from http.server import BaseHTTPRequestHandler

# 프로젝트 루트에서 모듈 로드 (Vercel 실행 시 cwd = 루트)
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from news_fetcher import fetch_google_news


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
            if not keyword:
                _send_json(self, 400, {"ok": False, "error": "키워드를 입력하세요."})
                return
            articles = fetch_google_news(keyword, max_articles=10)
            _send_json(self, 200, {"ok": True, "articles": articles})
        except Exception as e:
            _send_json(self, 500, {"ok": False, "error": str(e)})
