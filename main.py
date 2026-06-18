"""
네이버 블로그 제목 생성기
========================
네이버 상위 노출 제목을 분석하고, AI가 최적화된 제목을 만들어줍니다.

사용법:
  python main.py                     # 대화형 모드
  python main.py 선불폰              # 키워드 직접 입력
  python main.py 선불폰 바로유심     # 여러 키워드 순차 실행
"""

import sys
from naver_search import collect_titles
from analyzer import analyze_and_generate, format_result


def run(keyword: str):
    """키워드 하나에 대해 전체 파이프라인 실행"""

    # 1. 네이버에서 제목 수집
    data = collect_titles(keyword, display=30)

    blog_titles = [r["title"] for r in data["blog"]][:10]
    cafe_titles = [r["title"] for r in data["cafe"]][:10]

    if not blog_titles and not cafe_titles:
        print(f"\n⚠️  '{keyword}' 검색 결과가 없습니다. 키워드를 확인해주세요.\n")
        return

    # 2. Gemini로 분석 + 제목 생성
    print("🤖 AI가 패턴 분석 + 제목 생성 중...\n")
    result = analyze_and_generate(keyword, blog_titles, cafe_titles)

    if result is None:
        print("⚠️  AI 분석에 실패했습니다. 다시 시도해주세요.\n")
        return

    # 3. 결과 출력
    output = format_result(keyword, result, blog_titles, cafe_titles)
    print(output)
   
    # 4. 결과 저장
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    filename = f"result_{keyword}.txt"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"\n[{now}]\n")
        f.write(output)
        f.write("\n\n")
    print(f"  💾 저장 완료: {filename}")

def interactive_mode():
    """대화형 모드"""
    print()
    print("╔══════════════════════════════════════╗")
    print("║   📝 네이버 블로그 제목 생성기       ║")
    print("║   상위 노출 패턴 분석 + AI 제목 생성 ║")
    print("╚══════════════════════════════════════╝")
    print()
    print("  키워드를 입력하면 네이버 상위 제목을 분석하고")
    print("  최적화된 블로그 제목을 만들어줍니다.")
    print("  종료: q 또는 Ctrl+C")
    print()

    while True:
        try:
            keyword = input("🔎 키워드 입력: ").strip()

            if not keyword:
                continue
            if keyword.lower() in ("q", "quit", "exit", "종료"):
                print("\n👋 종료합니다.\n")
                break

            run(keyword)
            print()

        except KeyboardInterrupt:
            print("\n\n👋 종료합니다.\n")
            break


def main():
    if len(sys.argv) > 1:
        # 커맨드라인 인자로 키워드 전달
        keywords = sys.argv[1:]
        for keyword in keywords:
            run(keyword)
            print()
    else:
        # 대화형 모드
        interactive_mode()


if __name__ == "__main__":
    main()
