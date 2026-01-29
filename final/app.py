"""
뉴스 챗봇: 키워드로 Google 뉴스 10건 수집 → Gemini로 요약 → 대화
"""
import streamlit as st
from news_fetcher import fetch_google_news
from gemini_service import summarize_news, chat_with_news


st.set_page_config(
    page_title="뉴스 챗봇",
    page_icon="📰",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 세션 상태 초기화
if "articles" not in st.session_state:
    st.session_state.articles = []
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "keyword" not in st.session_state:
    st.session_state.keyword = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def main():
    st.title("📰 뉴스 챗봇")
    st.caption("키워드를 입력하면 Google에서 뉴스 10건을 수집하고, Gemini로 요약·대화할 수 있습니다.")

    # 키워드 입력
    keyword = st.text_input(
        "검색 키워드",
        placeholder="예: 인공지능, 삼성전자, 부동산",
        value=st.session_state.keyword,
    ).strip()

    fetch_clicked = st.button("🔍 뉴스 수집 (10건)")

    # 뉴스 수집
    if fetch_clicked and keyword:
        st.session_state.keyword = keyword
        with st.spinner("Google 뉴스를 수집하는 중..."):
            try:
                st.session_state.articles = fetch_google_news(keyword, max_articles=10)
                st.session_state.chat_history = []
                st.session_state.summary = ""
            except Exception as e:
                st.error(f"뉴스 수집 실패: {e}")
                st.session_state.articles = []

    # 수집 결과 표시
    if st.session_state.articles:
        st.subheader(f"수집된 뉴스 ({len(st.session_state.articles)}건)")
        for i, a in enumerate(st.session_state.articles, 1):
            with st.expander(f"{i}. {a.get('title', '(제목 없음)')}"):
                if a.get("summary"):
                    st.write(a["summary"])
                st.caption(f"출처: {a.get('source', '')} | {a.get('published', '')}")
                if a.get("link"):
                    st.markdown(f"[기사 보기]({a['link']})")

        # 요약하기 (아직 요약이 없을 때만 버튼 표시)
        if not st.session_state.summary and st.button("✨ 요약하기"):
            with st.spinner("Gemini로 요약 중..."):
                try:
                    st.session_state.summary = summarize_news(
                        st.session_state.keyword,
                        st.session_state.articles,
                    )
                except Exception as e:
                    st.error(f"요약 실패: {e}")

        # 이미 요약이 있거나 요약 버튼 실행 후
        if st.session_state.summary:
            st.subheader("📋 뉴스 요약")
            st.info(st.session_state.summary)

            st.divider()
            st.subheader("💬 뉴스에 대해 질문하기")

            # 채팅 영역: 이전 대화 표시
            for turn in st.session_state.chat_history:
                role = turn.get("role", "")
                text = ""
                if turn.get("parts"):
                    text = turn["parts"][0].get("text", "")
                else:
                    text = turn.get("text", "")
                if role == "user":
                    st.chat_message("user").write(text)
                elif role == "model":
                    st.chat_message("assistant").write(text)

            # 새 메시지 입력
            if prompt := st.chat_input("요약된 뉴스에 대해 궁금한 것을 물어보세요."):
                st.session_state.chat_history.append({
                    "role": "user",
                    "parts": [{"text": prompt}],
                })
                st.chat_message("user").write(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("답변 생성 중..."):
                        try:
                            reply = chat_with_news(
                                user_message=prompt,
                                keyword=st.session_state.keyword,
                                summary=st.session_state.summary,
                                chat_history=st.session_state.chat_history[:-1],
                            )
                            st.write(reply)
                            st.session_state.chat_history.append({
                                "role": "model",
                                "parts": [{"text": reply}],
                            })
                        except Exception as e:
                            st.error(f"오류: {e}")

    elif fetch_clicked and not keyword:
        st.warning("검색 키워드를 입력한 뒤 '뉴스 수집'을 눌러 주세요.")


if __name__ == "__main__":
    main()
