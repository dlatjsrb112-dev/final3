"""
뉴스 챗봇 웹 앱: Flask 백엔드 + API
"""
import os
import json
from flask import Flask, render_template, request, jsonify, session

from news_fetcher import fetch_google_news
from gemini_service import summarize_news, chat_with_news

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "news-chatbot-secret-change-in-production")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/news", methods=["POST"])
def api_news():
    data = request.get_json() or {}
    keyword = (data.get("keyword") or "").strip()
    if not keyword:
        return jsonify({"ok": False, "error": "키워드를 입력하세요."}), 400
    try:
        articles = fetch_google_news(keyword, max_articles=10)
        session["keyword"] = keyword
        session["articles"] = articles
        session["summary"] = ""
        return jsonify({"ok": True, "articles": articles})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/summarize", methods=["POST"])
def api_summarize():
    keyword = session.get("keyword", "")
    articles = session.get("articles", [])
    if not articles:
        return jsonify({"ok": False, "error": "먼저 뉴스를 수집하세요."}), 400
    try:
        summary = summarize_news(keyword, articles)
        session["summary"] = summary
        return jsonify({"ok": True, "summary": summary})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json() or {}
    message = (data.get("message") or "").strip()
    history = data.get("history") or []
    summary = session.get("summary", "")
    keyword = session.get("keyword", "")
    if not summary:
        return jsonify({"ok": False, "error": "먼저 뉴스를 수집하고 요약하세요."}), 400
    if not message:
        return jsonify({"ok": False, "error": "메시지를 입력하세요."}), 400
    # history: [ { "role": "user"|"model", "text": "..." } ]
    chat_history = [
        {"role": h.get("role"), "parts": [{"text": h.get("text", "")}]}
        for h in history
        if h.get("role") in ("user", "model")
    ]
    try:
        reply = chat_with_news(message, keyword, summary, chat_history)
        return jsonify({"ok": True, "reply": reply})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
