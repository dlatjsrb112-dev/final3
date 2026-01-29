"""
Gemini 3 Flash를 사용해 뉴스 요약 및 대화 기능을 제공합니다.
API 키는 반드시 환경변수 GEMINI_API_KEY로만 주입합니다. (코드/로그에 노출 금지)
"""
import os
from typing import List, Dict, Optional

# API 키: 환경변수에서만 읽음. 배포 시 Vercel 등에서 환경변수로 설정.
# 로컬 개발 시에만 키가 없을 때 .env 시도 (Vercel에서는 사용 안 함)
def _get_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    try:
        from dotenv import load_dotenv
        load_dotenv()
        key = os.environ.get("GEMINI_API_KEY")
    except Exception:
        key = ""
    return key or ""


def get_client():
    """Gemini API 클라이언트를 반환합니다. API 키는 환경변수에서만 사용합니다."""
    from google import genai
    api_key = _get_api_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다. 배포 환경의 환경변수를 확인하세요.")
    return genai.Client(api_key=api_key)


MODEL_ID = "gemini-3-flash-preview"


def summarize_news(keyword: str, articles: List[Dict[str, str]]) -> str:
    """
    수집한 뉴스 목록을 Gemini로 요약합니다.
    
    Args:
        keyword: 검색 키워드
        articles: news_fetcher에서 반환한 기사 리스트
    
    Returns:
        요약 텍스트
    """
    if not articles:
        return "수집된 뉴스가 없습니다."
    
    client = get_client()
    
    news_text = ""
    for i, a in enumerate(articles, 1):
        news_text += f"\n[기사 {i}] {a.get('title', '')}\n"
        if a.get("summary"):
            news_text += f"요약: {a['summary']}\n"
        if a.get("source"):
            news_text += f"출처: {a['source']}\n"
    
    prompt = f"""다음은 '{keyword}' 키워드로 수집한 뉴스 기사들입니다.
각 기사의 제목·요약·출처를 바탕으로 전체를 2~3문단으로 요약해 주세요.
핵심 이슈와 흐름을 담아 읽기 쉽게 작성해 주세요.

{news_text}

위 뉴스 요약 (한국어):"""
    
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
    )
    return getattr(response, "text", "") or str(response)


def chat_with_news(
    user_message: str,
    keyword: str,
    summary: str,
    chat_history: List[Dict[str, str]],
) -> str:
    """
    뉴스 요약을 컨텍스트로 삼아 사용자 메시지에 답합니다.
    
    Args:
        user_message: 사용자 입력
        keyword: 검색 키워드
        summary: 뉴스 요약
        chat_history: [{"role": "user"|"model", "parts": [{"text": "..."}]}] 형식의 이전 대화 (선택)
    
    Returns:
        모델 응답 텍스트
    """
    client = get_client()
    
    system_context = f"""당신은 '{keyword}' 관련 최신 뉴스를 요약·설명해 주는 뉴스 챗봇입니다.
아래는 해당 키워드로 수집한 뉴스의 요약입니다. 이 내용을 바탕으로만 답변하세요.
요약에 없는 내용은 "제공된 뉴스 요약에는 해당 정보가 없습니다"라고 답하세요.

[뉴스 요약]
{summary}
"""
    
    # google-genai는 대화형으로 contents에 이전 대화 + 새 메시지를 넣을 수 있음
    contents = [system_context]
    for turn in chat_history:
        role = turn.get("role", "")
        text = turn.get("parts", [{}])[0].get("text", "") if turn.get("parts") else turn.get("text", "")
        if role == "user":
            contents.append({"role": "user", "parts": [{"text": text}]})
        elif role == "model":
            contents.append({"role": "model", "parts": [{"text": text}]})
    
    contents.append({"role": "user", "parts": [{"text": user_message}]})
    
    # SDK에 따라 generate_content에 history를 넘기는 방식이 다를 수 있음
    # 간단히 마지막 사용자 메시지와 시스템 컨텍스트만 보내는 방식으로 시도
    try:
        # 채팅 API가 있다면 사용, 없으면 단일 요청으로 처리
        full_prompt = system_context
        for turn in chat_history:
            role = turn.get("role", "")
            text = (turn.get("parts", [{}])[0].get("text", "") if turn.get("parts") else turn.get("text", "")) or ""
            if role == "user":
                full_prompt += f"\n\n[사용자]\n{text}"
            elif role == "model":
                full_prompt += f"\n\n[챗봇]\n{text}"
        full_prompt += f"\n\n[사용자]\n{user_message}\n\n[챗봇]\n"
        
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=full_prompt,
        )
        return getattr(response, "text", "") or str(response)
    except Exception as e:
        return f"응답 생성 중 오류가 발생했습니다: {e}"
