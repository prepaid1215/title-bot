import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

HEADERS = {
    "X-Naver-Client-Id": NAVER_CLIENT_ID,
    "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
}


def clean_title(title: str) -> str:
    """HTML 태그 제거 + 공백 정리"""
    title = re.sub(r"<.*?>", "", title)
    title = title.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    title = title.replace("&quot;", '"').replace("&#39;", "'")
    return title.strip()


def search_naver(query: str, category: str = "blog", display: int = 30, sort: str = "sim") -> list[dict]:
    """
    네이버 검색 API 호출
    category: 'blog' 또는 'cafearticle'
    sort: 'sim'(정확도순) 또는 'date'(최신순)
    """
    url = f"https://openapi.naver.com/v1/search/{category}"
    params = {
        "query": query,
        "display": display,
        "sort": sort,
    }

    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        print(f"[오류] 네이버 API 응답 코드: {response.status_code}")
        print(response.text)
        return []

    data = response.json()
    items = data.get("items", [])

    results = []
    for item in items:
        results.append({
            "title": clean_title(item.get("title", "")),
            "link": item.get("link", ""),
            "description": clean_title(item.get("description", "")),
        })

    return results


def collect_titles(query: str, display: int = 15) -> dict:
    """블로그 + 카페 상위 제목을 한번에 수집"""
    print(f"\n🔍 '{query}' 키워드로 네이버 검색 중...\n")

    blog_results = search_naver(query, category="blog", display=display)
    cafe_results = search_naver(query, category="cafearticle", display=display)

    print(f"  📋 블로그 제목 {len(blog_results)}개 수집")
    print(f"  📋 카페 제목 {len(cafe_results)}개 수집")

    # 중복 제목 제거
    seen = set()
    unique_blog = []
    for r in blog_results:
        if r["title"] not in seen:
            seen.add(r["title"])
            unique_blog.append(r)

    unique_cafe = []
    for r in cafe_results:
        if r["title"] not in seen:
            seen.add(r["title"])
            unique_cafe.append(r)

    print(f"  ✅ 중복 제거 후: 블로그 {len(unique_blog)}개 + 카페 {len(unique_cafe)}개\n")

    return {
        "blog": unique_blog,
        "cafe": unique_cafe,
    }


if __name__ == "__main__":
    # 단독 테스트용
    result = collect_titles("선불폰")
    print("=== 블로그 상위 제목 ===")
    for i, r in enumerate(result["blog"][:10], 1):
        print(f"  {i}. {r['title']}")
    print("\n=== 카페 상위 제목 ===")
    for i, r in enumerate(result["cafe"][:10], 1):
        print(f"  {i}. {r['title']}")
