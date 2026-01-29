@echo off
cd /d "%~dp0"
echo Installing dependencies...
pip install streamlit google-genai feedparser requests python-dotenv -q
echo.
echo Starting News Chatbot...
streamlit run app.py
