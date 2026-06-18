import streamlit as st
from naver_search import collect_titles
from analyzer import analyze_and_generate
from datetime import datetime

st.set_page_config(page_title="블로그 제목 생성기", page_icon="📝")

# 비밀번호 확인
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    pw = st.text_input("🔒 비밀번호 입력", type="password")
    if pw == "757687*":
        st.session_state.authenticated = True
        st.rerun()
    elif pw:
        st.error("비밀번호가 틀립니다.")
    st.stop()

st.title("📝 네이버 블로그 제목 생성기")
st.caption("키워드를 입력하면 네이버 상위 제목을 분석하고 최적화된 제목을 만들어줍니다.")

keyword = st.text_input("🔎 키워드 입력", placeholder="예: 선불폰, 바로유심, 앤텔레콤")

if st.button("제목 생성", type="primary", disabled=not keyword):
    with st.spinner("네이버 검색 중..."):
        data = collect_titles(keyword, display=30)
        blog_titles = [r["title"] for r in data["blog"]][:10]
        cafe_titles = [r["title"] for r in data["cafe"]][:10]

    if not blog_titles and not cafe_titles:
        st.error(f"'{keyword}' 검색 결과가 없습니다.")
    else:
        with st.spinner("AI가 패턴 분석 + 제목 생성 중..."):
            result = analyze_and_generate(keyword, blog_titles, cafe_titles)

        if result is None:
            st.error("AI 분석에 실패했습니다. 다시 시도해주세요.")
        else:
            # 패턴 분석
            analysis = result.get("analysis", {})

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📋 블로그 상위 제목")
                for i, t in enumerate(blog_titles, 1):
                    st.text(f"{i:2d}. {t}")

            with col2:
                st.subheader("📋 카페 상위 제목")
                for i, t in enumerate(cafe_titles, 1):
                    st.text(f"{i:2d}. {t}")

            st.divider()
            st.subheader("📊 패턴 분석")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("평균 길이", f"{analysis.get('avg_length', '?')}자")
            c2.metric("주요 유형", analysis.get("top_type", "?"))
            c3.metric("시점 표기", analysis.get("timestamp_ratio", "?"))
            c4.metric("반복 키워드", ", ".join(analysis.get("top_keywords", [])[:3]))
            st.info(f"**공통 패턴:** {analysis.get('common_pattern', '?')}")

            st.divider()

            col3, col4 = st.columns(2)

            with col3:
                st.subheader("📝 블로그용 제목")
                for i, t in enumerate(result.get("blog_titles", []), 1):
                    with st.container(border=True):
                        st.markdown(f"**{t.get('title', '')}**")
                        st.caption(f"📎 참고: {t.get('reference', '')}")
                        st.caption(f"💡 이유: {t.get('reason', '')}")
                        if st.button(f"복사", key=f"blog_{i}"):
                            st.toast(f"제목을 복사했습니다: {t.get('title', '')}")

            with col4:
                st.subheader("💬 카페용 제목")
                for i, t in enumerate(result.get("cafe_titles", []), 1):
                    with st.container(border=True):
                        st.markdown(f"**{t.get('title', '')}**")
                        st.caption(f"📎 참고: {t.get('reference', '')}")
                        st.caption(f"💡 이유: {t.get('reason', '')}")
                        if st.button(f"복사", key=f"cafe_{i}"):
                            st.toast(f"제목을 복사했습니다: {t.get('title', '')}")

            # 자동 저장
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            filename = f"result_{keyword}.txt"
            lines = [f"\n[{now}]", f"키워드: {keyword}", "\n블로그용:"]
            for t in result.get("blog_titles", []):
                lines.append(f"  - {t.get('title', '')}")
            lines.append("\n카페용:")
            for t in result.get("cafe_titles", []):
                lines.append(f"  - {t.get('title', '')}")
            with open(filename, "a", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n\n")
