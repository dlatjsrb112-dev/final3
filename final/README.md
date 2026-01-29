# 뉴스 챗봇

키워드를 입력하면 **Google 뉴스 10건**을 수집하고, **Gemini 3 Flash**로 요약한 뒤, 요약된 뉴스에 대해 대화할 수 있는 챗봇입니다.

## 기능

1. **뉴스 수집**: 검색 키워드로 Google News RSS에서 최대 10건 수집
2. **요약**: Gemini 3 Flash로 수집한 뉴스를 2~3문단으로 요약
3. **대화**: 요약 내용을 바탕으로 질문·답변

## 설치

- **Vercel 배포**: `requirements.txt`는 API용 최소 의존성만 포함 (250MB 제한 대응).
- **로컬 실행 (Flask/Streamlit)**:
```bash
cd final
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements-full.txt
```

## API 키 설정 (유출 금지)

**API 키는 코드/저장소에 넣지 마세요.** 환경변수로만 사용합니다.

- **로컬 실행**: 프로젝트 루트에 `.env` 파일을 만들고 `GEMINI_API_KEY=여기에_API_키` 추가 (`.env`는 `.gitignore`에 포함되어 커밋되지 않음)
- **Vercel 배포**: Vercel 대시보드 → 프로젝트 → Settings → Environment Variables 에서 `GEMINI_API_KEY` 추가 (값은 코드/저장소에 포함하지 않음)

API 키 발급: [Google AI Studio](https://aistudio.google.com/apikey)

## 실행

### 웹 앱 (권장)

브라우저에서 사용하는 웹 버전입니다.

```bash
python app_web.py
```

또는 **`run_web.bat`** 더블클릭 (Windows). 브라우저에서 **http://127.0.0.1:5000** 을 열면 됩니다.

### Streamlit 버전

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 이 열립니다.

## 사용 방법 (웹)

1. 키워드 입력 (예: 인공지능, 삼성전자)
2. **뉴스 수집 (10건)** 클릭
3. **요약하기** 클릭
4. 하단 채팅창에서 뉴스에 대해 질문

## 사용 기술

- **뉴스 수집**: Google News RSS (feedparser)
- **요약·챗**: Gemini 3 Flash (`gemini-3-flash-preview`)
- **웹**: Flask + HTML/CSS/JS (단일 페이지)
- **대안 UI**: Streamlit (`app.py`)

## Vercel 배포 (웹)

1. 저장소를 Vercel에 연결
2. **Settings → Environment Variables** 에서 `GEMINI_API_KEY` 추가 (API 키는 여기서만 설정, 코드/저장소에 넣지 않음)
3. 배포 시 자동으로 `api/` 서버리스 함수와 `index.html`이 배포됨

API는 서버에서만 환경변수를 읽으며, 클라이언트/프론트엔드에는 API 키가 노출되지 않습니다.

**250MB 초과 오류 시**: 저장소 루트에 `pyproject.toml` 또는 `uv.lock` 이 있으면 제거하세요. Vercel이 `requirements.txt`(API용 최소 의존성)만 사용하도록 해야 합니다.

## 기타 배포 (Render, Railway 등)

- **환경변수**: `GEMINI_API_KEY`, `SECRET_KEY` 설정
- **시작 명령**: `gunicorn app_web:app --bind 0.0.0.0:$PORT` (또는 Procfile 사용)
