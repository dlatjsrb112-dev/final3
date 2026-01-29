@echo off
cd /d "%~dp0"
echo Installing dependencies...
pip install flask google-genai feedparser requests python-dotenv -q
echo.
echo Starting News Chatbot (Web)...
echo Open in browser: http://127.0.0.1:5000
echo.
python app_web.py
