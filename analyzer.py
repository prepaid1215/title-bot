import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.5-flash"

with open("prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()


def analyze_and_generate(keyword: str, blog_titles: list[str], cafe_titles: list[str]) -> dict:
    """
    수집된 제목을 분석하고 새 제목을 생성
    """
    titles_text = "## 블로그 상위 제목\n"
    for i, t in enumerate(blog_titles, 1):
        titles_text += f"{i}. {t}\n"

    titles_text += "\n## 카페 상위 제목\n"
    for i, t in enumerate(cafe_titles, 1):
        titles_text += f"{i}. {t}\n"

    user_prompt = f"""키워드: "{keyword}"

아래는 이 키워드로 네이버 검색 상위에 노출된 실제 제목들입니다.

{titles_text}

다음 작업을 수행하세요:

### 작업 1: 패턴 분석
위 제목들을 분석해서 다음을 알려주세요:
- 평균 제목 길이 (글자 수)
- 가장 많은 제목 유형 (경험/후기형, 비교형, 가이드형, 질문형 등)과 비율
- 자주 반복되는 키워드 TOP 5
- 시점 표기 비율
- 상위 제목들의 공통 구조 패턴
- 메인 키워드의 제목 내 위치 (앞/중간/뒤 비율)

### 작업 2: 블로그용 제목 생성
블로그 상위 제목들의 실제 구조와 톤을 참고해서 블로그에 올릴 제목 3개를 만들어주세요.
상위 제목과 비슷한 길이와 구조를 유지하되 약간의 차별점만 넣을 것.


### 작업 3: 카페용 제목 생성
카페 상위 제목들의 실제 구조와 톤을 참고해서 카페에 올릴 제목 3개를 만들어주세요.
카페 특유의 질문형, 후기 공유형 톤을 살릴 것.

반드시 아래 JSON 형식으로만 응답하세요. 마크다운 백틱, 설명, 번호 매기기 없이 순수 JSON만 출력하세요. JSON 외의 텍스트가 한 글자라도 있으면 실패입니다.

{{
  "analysis": {{
    "avg_length": 숫자,
    "top_type": "유형명 (비율%)",
    "top_keywords": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"],
    "timestamp_ratio": "비율%",
    "common_pattern": "공통 구조 설명"
  }},
  "blog_titles": [
    {{
      "title": "생성된 제목",
      "reference": "참고한 상위 제목 또는 패턴",
      "reason": "네이버에서 유리한 이유"
    }}
  ],
  "cafe_titles": [
    {{
      "title": "생성된 제목",
      "reference": "참고한 상위 제목 또는 패턴",
      "reason": "네이버에서 유리한 이유"
    }}
  ]
}}"""

    response = client.models.generate_content(
        model=MODEL,
        contents=SYSTEM_PROMPT + "\n\n" + user_prompt,
        config={
            "temperature": 0.8,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        },
    )

    text = response.text.strip()
    # JSON 파싱 (백틱 제거)
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(text)
        return result
    except json.JSONDecodeError:
        print("[오류] Gemini 응답 JSON 파싱 실패")
        print("원본 응답:")
        print(text)
        return None


def format_result(keyword: str, data: dict, blog_titles: list[str], cafe_titles: list[str]) -> str:
    """결과를 보기 좋게 포맷"""
    lines = []
    lines.append("=" * 56)
    lines.append(f"  🔍 키워드: {keyword}")
    lines.append("=" * 56)

    # 상위 제목 표시
    lines.append("\n📋 네이버 상위 제목 (블로그)")
    lines.append("-" * 40)
    for i, t in enumerate(blog_titles[:10], 1):
        lines.append(f"  {i:2d}. {t}")

    lines.append("\n📋 네이버 상위 제목 (카페)")
    lines.append("-" * 40)
    for i, t in enumerate(cafe_titles[:10], 1):
        lines.append(f"  {i:2d}. {t}")

    # 패턴 분석
    analysis = data.get("analysis", {})
    lines.append("\n📊 패턴 분석")
    lines.append("-" * 40)
    lines.append(f"  평균 제목 길이: {analysis.get('avg_length', '?')}자")
    lines.append(f"  주요 유형: {analysis.get('top_type', '?')}")
    lines.append(f"  반복 키워드: {', '.join(analysis.get('top_keywords', []))}")
    lines.append(f"  시점 표기 비율: {analysis.get('timestamp_ratio', '?')}")
    lines.append(f"  공통 패턴: {analysis.get('common_pattern', '?')}")

    # 블로그용 제목
    blog = data.get("blog_titles", [])
    lines.append(f"\n📝 블로그용 제목 ({len(blog)}개)")
    lines.append("-" * 40)
    for i, t in enumerate(blog, 1):
        lines.append(f"\n  [{i}] {t.get('title', '')}")
        lines.append(f"      📎 참고: {t.get('reference', '')}")
        lines.append(f"      💡 이유: {t.get('reason', '')}")

    # 카페용 제목
    cafe = data.get("cafe_titles", [])
    lines.append(f"\n💬 카페용 제목 ({len(cafe)}개)")
    lines.append("-" * 40)
    for i, t in enumerate(cafe, 1):
        lines.append(f"\n  [{i}] {t.get('title', '')}")
        lines.append(f"      📎 참고: {t.get('reference', '')}")
        lines.append(f"      💡 이유: {t.get('reason', '')}")
    lines.append("\n" + "=" * 56)
    return "\n".join(lines)

if __name__ == "__main__":
    # 단독 테스트
    test_blog = ["선불폰 개통 후기", "바로유심 편의점 구매 방법", "신불자 선불폰 추천"]
    test_cafe = ["선불폰 어디서 개통하나요", "바로유심 vs 모두의원칩 비교"]
    result = analyze_and_generate("선불폰", test_blog, test_cafe)
    if result:
        print(format_result("선불폰", result, test_blog, test_cafe))
