"""
Google News RSS를 통해 키워드로 뉴스 10건을 수집합니다.
"""
import re
import feedparser
from urllib.parse import quote_plus
from typing import List, Dict


def fetch_google_news(keyword: str, max_articles: int = 10) -> List[Dict[str, str]]:
    """
    키워드로 Google News RSS에서 뉴스를 수집합니다.
    
    Args:
        keyword: 검색 키워드
        max_articles: 수집할 최대 기사 수 (기본 10)
    
    Returns:
        [{"title", "link", "published", "summary", "source"}] 형태의 리스트
    """
    encoded_keyword = quote_plus(keyword)
    # Google News RSS 검색 URL (한국어)
    url = (
        f"https://news.google.com/rss/search?"
        f"q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
    )
    
    feed = feedparser.parse(url)
    articles = []
    
    for i, entry in enumerate(feed.entries):
        if i >= max_articles:
            break
        # summary가 없을 수 있음
        summary = getattr(entry, "summary", "") or ""
        # HTML 태그 제거
        if summary:
            summary = re.sub(r"<[^>]+>", "", summary)
        source = ""
        if hasattr(entry, "source") and entry.source:
            source = getattr(entry.source, "title", "") or str(entry.source)
        articles.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
            "summary": summary.strip(),
            "source": source,
        })
    
    return articles
