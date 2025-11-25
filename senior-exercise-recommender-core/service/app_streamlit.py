import typing as t
import streamlit as st

# ============================================================
# 타입 / 추천엔진 import (없어도 fake로 돌아가게 방어적 처리)
# ============================================================
try:
    from recommender.types import UserProfile, Location, WeatherInfo  # type: ignore
    HAS_TYPES = True
except ImportError:
    HAS_TYPES = False
    UserProfile = Location = WeatherInfo = t.Any  # type: ignore

try:
    from recommender.pipeline import recommend as real_recommend  # type: ignore
    HAS_REAL = True
except ImportError:
    HAS_REAL = False
    real_recommend = None


# -------------------------------
# Fake recommend (임시 추천 함수)
# -------------------------------
def fake_recommend(user_profile, location, weather_info, top_k: int = 5):
    """실제 파이프라인 없을 때 UI만 동작하게 하는 더미 추천 함수"""
    return [
        {
            "facility_name": "은평구민체육센터",
            "program_name": "실버 요가 (초급)",
            "sport_category": "yoga",
            "distance_km": 1.2,
            "intensity_level": "low",
            "is_indoor": True,
            "score": 0.86,
            "reason": "무릎 통증에 적합한 저강도 실내 운동입니다.",
        },
        {
            "facility_name": "마포노인복지관",
            "program_name": "시니어 스트레칭 & 근력",
            "sport_category": "stretch",
            "distance_km": 2.3,
            "intensity_level": "low-mid",
            "is_indoor": True,
            "score": 0.81,
            "reason": "허리 부담을 줄이며 근력 향상에 도움이 됩니다.",
        },
    ]


def get_recommend_func():
    """실제 recommend가 있으면 그걸 쓰고, 없으면 fake 사용"""
    if HAS_REAL and real_recommend:
        return real_recommend, False
    return fake_recommend, True


# ============================================================
# 세션 상태 초기화 / 온보딩 단계 이동
# ============================================================
def init_onboarding_state():
    if "onboarding_step" not in st.session_state:
        st.session_state["onboarding_step"] = 0
    if "profile" not in st.session_state:
        st.session_state["profile"] = {
            "age_group": None,
            "gender": None,
            "health_issues": [],
            "goals": [],
            "preference_env": None,
        }


def next_step():
    st.session_state["onboarding_step"] += 1
    st.rerun()


def prev_step():
    if st.session_state["onboarding_step"] > 0:
        st.session_state["onboarding_step"] -= 1
    st.rerun()


# ============================================================
# 온보딩 화면 (질문 5개 → 프로필 구성)
# ============================================================
def onboarding():
    init_onboarding_state()
    step = st.session_state["onboarding_step"]
    profile = st.session_state["profile"]

    labels = ["연령대", "성별", "건강 상태", "운동 목표", "운동 환경"]

    # ----------------------- 상단 헤더 카드 -----------------------
    st.markdown(
        f"""
        <div class="header-card">
            <h1 class="big-title">시니어 맞춤 운동 추천</h1>
            <p class="body-text">
                간단한 질문 몇 가지에 답하면<br/>
                더 잘 맞는 운동을 추천해 드립니다.
            </p>
            <p class="step-indicator">
                단계 {step+1} / {len(labels)} · <b>{labels[step]}</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<hr/>", unsafe_allow_html=True)

    # =====================================================
    # STEP 0 — 연령대
    # =====================================================
    if step == 0:
        st.markdown(
            '<h2 class="question-title">연령대를 선택해 주세요.</h2>',
            unsafe_allow_html=True,
        )

        age_list = ["60-64", "65-69", "70-74", "75-79", "80+"]

        # 위 2개, 가운데 2개, 아래 1개 (정사각형 버튼 느낌)
        row1 = st.columns(2, gap="large")
        row2 = st.columns(2, gap="large")
        row3 = st.columns([1, 1, 1], gap="large")

        layout = [
            (row1[0], age_list[0]),
            (row1[1], age_list[1]),
            (row2[0], age_list[2]),
            (row2[1], age_list[3]),
            (row3[1], age_list[4]),
        ]

        for col, age in layout:
            with col:
                if st.button(age, use_container_width=True):
                    profile["age_group"] = age
                    st.session_state["profile"] = profile
                    next_step()

    # =====================================================
    # STEP 1 — 성별
    # =====================================================
    elif step == 1:
        st.markdown(
            '<h2 class="question-title">성별을 선택해 주세요.</h2>',
            unsafe_allow_html=True,
        )

        cols = st.columns(3, gap="large")
        gender_opts = [("남성", "남성"), ("여성", "여성"), ("기타", "기타/응답하지 않음")]

        for i, (label, value) in enumerate(gender_opts):
            with cols[i]:
                if st.button(label, use_container_width=True):
                    profile["gender"] = value
                    st.session_state["profile"] = profile
                    next_step()

        st.button("⬅️ 이전", on_click=prev_step)

    # =====================================================
    # STEP 2 — 건강 상태
    # =====================================================
    elif step == 2:
        st.markdown(
            """
            <h2 class="question-title">건강 상태를 선택해 주세요.</h2>
            <p class="body-text" style="margin-top:0.5rem;">
                해당되는 항목을 모두 체크해 주세요.
            </p>
            """,
            unsafe_allow_html=True,
        )

        options = [
            ("무릎 통증", "knee_pain"),
            ("허리 통증", "back_pain"),
            ("고혈압", "hypertension"),
            ("당뇨", "diabetes"),
            ("심혈관 질환 위험", "cardio_risk"),
            ("특별한 질환 없음", "none"),
        ]

        selected = profile.get("health_issues", [])

        # 온보딩 영역 래퍼 (체크박스 스타일 범위 제한용)
        st.markdown("<div class='onboard-area'><div class='center-box'>",
                    unsafe_allow_html=True)

        new_selected: list[str] = []
        for label, code in options:
            checked = st.checkbox(
                label,
                value=(code in selected),
                key=f"hi_{code}",
            )
            if checked:
                new_selected.append(code)

        st.markdown("</div></div>", unsafe_allow_html=True)

        profile["health_issues"] = new_selected or ["none"]
        st.session_state["profile"] = profile

        col_prev, col_next = st.columns([1, 1])
        with col_prev:
            st.button("⬅️ 이전", on_click=prev_step, use_container_width=True)
        with col_next:
            st.button("다음 ➡️", on_click=next_step, use_container_width=True)

    # =====================================================
    # STEP 3 — 운동 목표
    # =====================================================
    elif step == 3:
        st.markdown(
            '<h2 class="question-title">운동의 목표는 무엇인가요?</h2>',
            unsafe_allow_html=True,
        )

        options = [
            ("혈압 관리", "blood_pressure"),
            ("체중 관리", "weight"),
            ("근력 향상", "strength"),
            ("유연성 향상", "flexibility"),
            ("균형감 향상", "balance"),
            ("사회적 교류", "social"),
        ]

        chosen: list[str] = []
        st.markdown("<div class='onboard-area'><div class='center-box'>",
                    unsafe_allow_html=True)

        for label, code in options:
            checked = st.checkbox(
                label,
                value=(code in profile.get("goals", [])),
                key=f"goal_{code}",
            )
            if checked:
                chosen.append(code)

        st.markdown("</div></div>", unsafe_allow_html=True)

        profile["goals"] = chosen
        st.session_state["profile"] = profile

        col1, col2 = st.columns(2)
        col1.button("⬅️ 이전", on_click=prev_step, use_container_width=True)
        col2.button("다음 ➡️", on_click=next_step, use_container_width=True)

    # =====================================================
    # STEP 4 — 운동 환경
    # =====================================================
    elif step == 4:
        st.markdown(
            '<h2 class="question-title">선호하는 운동 환경을 골라 주세요.</h2>',
            unsafe_allow_html=True,
        )

        env_opts = [("상관 없음", "any"), ("실내 위주", "indoor"), ("야외 위주", "outdoor")]
        cols = st.columns(3, gap="large")

        for i, (label, code) in enumerate(env_opts):
            with cols[i]:
                if st.button(label, use_container_width=True):
                    profile["preference_env"] = code
                    st.session_state["profile"] = profile
                    st.session_state["profile_confirmed"] = True
                    st.rerun()

        st.button("⬅️ 이전", on_click=prev_step)


# ============================================================
# 메인 추천 화면
# ============================================================
def main():
    st.set_page_config(page_title="시니어 운동 추천", layout="wide")

    # ----------------------
    #  전체 스타일 (색, 폰트, 카드 레이아웃 등)
    # ----------------------
    st.markdown(
        """
        <style>
        /* 전체 배경 */
        [data-testid="stAppViewContainer"] {
            background-color: #f7f2e8;
        }

        /* 사이드바 톤 */
        [data-testid="stSidebar"] {
            background-color: #f3ebdd;
        }

        /* 상단 헤더 카드 */
        .header-card {
            max-width: 640px;
            margin: 1.8rem auto 1.2rem auto;
            padding: 1.6rem 1.8rem;
            background-color: #ffffff;
            border-radius: 1.2rem;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
            text-align: center;
        }

        /* 메인 화면 큰 카드 */
        .main-card {
            max-width: 800px;
            margin: 2rem auto;
            padding: 2rem 2.4rem;
            background-color: #ffffff;
            border-radius: 1.2rem;
            box-shadow: 0 10px 24px rgba(0, 0, 0, 0.10);
            text-align: center;
        }

        /* 추천 결과 카드 */
        .result-card {
            max-width: 800px;
            margin: 1.2rem auto;
            padding: 1.6rem 2rem;
            background-color: #ffffff;
            border-radius: 1rem;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
        }

        /* 큰 타이틀 */
        .big-title {
            font-size: 3rem;
            font-weight: 700;
            color: #00003c !important;
            margin: 0;
        }

        /* 질문 제목 */
        .question-title {
            font-size: 2.4rem;
            font-weight: 700;
            color: #00003c !important;
            text-align: center;
            margin-top: 2rem;
        }

        /* 본문 설명 */
        .body-text {
            font-size: 1.3rem !important;
            color: #222;
            text-align: center;
        }

        /* 단계 표시 */
        .step-indicator {
            font-size: 1.2rem !important;
            color: #444;
            margin-top: 0.6rem;
        }

        /* 온보딩 버튼 (연령/성별/환경) 크게 */
        .stButton > button {
            font-size: 5rem !important;   /* 전체 높이 기준 */
            background-color: #00003c !important;
            color: #ffffff !important;
            padding-top: 1.2rem !important;
            padding-bottom: 1.2rem !important;
            border-radius: 1rem !important;
            min-width: 130px;
            min-height: 160px;
        }
        .stButton > button > div {
            font-size: 2rem !important;   /* 버튼 안 텍스트 크기 */
            font-weight: 500 !important;
        }

        /* 건강 상태 / 운동 목표 체크박스들을 가운데로 정렬하는 래퍼 */
        .center-box {
            display: flex;
            flex-direction: column;
            align-items: flex-start;  /* 왼쪽 정렬이 보기 좋으면 center→flex-start로 */
            margin-top: 1rem;
        }

        /* 온보딩 영역 안에 있는 체크박스만 네이비 블록 + 흰 글씨 */
        .onboard-area [data-testid="stCheckbox"] {
            margin: 0.7rem 0 !important;
        }

        .onboard-area [data-testid="stCheckbox"] label {
            background-color: #00003c;
            color: #ffffff !important;
            padding: 0.6rem 1.6rem;
            border-radius: 0.8rem;
            display: inline-block;
            min-width: 260px;
            text-align: center;
            font-size: 1.8rem !important;
            font-weight: 600 !important;
        }

        /* 체크박스 안의 텍스트 span도 강제로 흰색/큰 글자 */
        .onboard-area [data-testid="stCheckbox"] label span {
            color: #ffffff !important;
            font-size: 1.8rem !important;
            font-weight: 600 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 온보딩이 끝나지 않았으면 먼저 프로필 수집
    if not st.session_state.get("profile_confirmed"):
        onboarding()
        return

    # -------------------------------
    # 사용자 프로필 / 추천 함수 준비
    # -------------------------------
    profile = st.session_state["profile"]
    recommend_func, _ = get_recommend_func()

    # -------------------------------
    # 메인 설명 카드
    # -------------------------------
    st.markdown(
        """
        <div class="main-card">
            <h1 class="big-title">🏃‍♀️ 오늘은 어떤 운동이 좋을까요?</h1>
            <p class="body-text">
                왼쪽에서 조건을 조정한 뒤,<br/>
                아래 추천 버튼을 눌러 주변 운동 프로그램을 확인해 보세요!
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -------------------------------
    # 사이드바 입력 폼
    # -------------------------------
    with st.sidebar:
        st.header("🧑‍🦳 사용자 프로필")

        # 연령대
        age_options = ["60-64", "65-69", "70-74", "75-79", "80+"]
        age_default = profile.get("age_group") or "65-69"
        if age_default not in age_options:
            age_default = "65-69"

        age_group = st.selectbox(
            "연령대",
            age_options,
            index=age_options.index(age_default),
        )

        # 성별
        gender_options = ["남성", "여성", "기타/응답하지 않음"]
        gender_default = profile.get("gender") or "여성"
        if gender_default not in gender_options:
            gender_default = "여성"

        gender = st.radio(
            "성별",
            gender_options,
            index=gender_options.index(gender_default),
        )

        # 건강 상태
        health_all = [
            "knee_pain",
            "back_pain",
            "hypertension",
            "diabetes",
            "cardio_risk",
            "none",
        ]
        health_default = profile.get("health_issues") or ["none"]
        health = st.multiselect(
            "건강 상태",
            health_all,
            default=[x for x in health_default if x in health_all] or ["none"],
        )

        # 운동 목표
        goals_all = [
            "blood_pressure",
            "weight",
            "strength",
            "flexibility",
            "balance",
            "social",
        ]
        goals_default = profile.get("goals") or []
        goals = st.multiselect(
            "운동 목표",
            goals_all,
            default=[g for g in goals_default if g in goals_all],
        )

        # 환경
        env_options = ["any", "indoor", "outdoor"]
        env_default = profile.get("preference_env") or "any"
        if env_default not in env_options:
            env_default = "any"

        env = st.radio(
            "선호 운동 환경",
            env_options,
            index=env_options.index(env_default),
            format_func=lambda x: {
                "any": "상관 없음",
                "indoor": "실내 위주",
                "outdoor": "야외 위주",
            }[x],
        )

        st.markdown("---")
        lat = st.number_input("위도", value=37.5665)
        lon = st.number_input("경도", value=126.9780)

        st.markdown("---")
        top_k = st.slider("추천 개수", 1, 10, 5)

        submit = st.button("🔍 추천 받기", use_container_width=True)

        if st.button("⚙️ 기본 정보 다시 설정하기", use_container_width=True):
            st.session_state["profile_confirmed"] = False
            st.session_state["onboarding_step"] = 0
            st.rerun()

    # -------------------------------
    # 추천 결과 영역
    # -------------------------------
    if submit:
        user_profile = {
            "age_group": age_group,
            "gender": gender,
            "health_issues": health or ["none"],
            "goals": goals,
            "preference_env": env,
        }
        loc = {"lat": lat, "lon": lon}
        weather = {"temp": 12.0, "rain_prob": 0.2, "pm10": 40.0, "is_daytime": True}

        # 세션 프로필도 업데이트 (다음에 들어왔을 때 기본값으로 쓰려고)
        profile.update(user_profile)
        st.session_state["profile"] = profile

        recs = recommend_func(user_profile, loc, weather, top_k=top_k)

        st.subheader("추천 결과")

        if not recs:
            st.warning("조건에 맞는 프로그램이 없습니다.")
        else:
            for idx, rec in enumerate(recs, start=1):
                st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                st.markdown(f"### {idx}. {rec['facility_name']}")
                st.write(rec["program_name"])
                st.caption(
                    f"{rec['sport_category']} · 거리 {rec['distance_km']} km "
                    f"· 강도 {rec['intensity_level']} · "
                    f"{'실내' if rec['is_indoor'] else '야외'}"
                )
                st.write(f"🟩 추천 이유: {rec['reason']}")
                st.metric("적합도 점수", f"{rec['score']:.2f}")
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("왼쪽에서 조건을 선택한 뒤 **‘추천 받기’** 버튼을 눌러 주세요.")


if __name__ == "__main__":
    main()
