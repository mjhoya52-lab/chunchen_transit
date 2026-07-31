"""Streamlit version of the Bomnaeum program discovery service."""

from __future__ import annotations

from html import escape
import importlib.util
from pathlib import Path
import sys

import streamlit as st

from app import find_student, program_rows


PROJECT_ROOT = Path(__file__).resolve().parent
TRANSIT_WEB_APP = PROJECT_ROOT / "transit" / "web" / "app.py"


@st.cache_resource
def load_transit_module():
    """Load the existing Chuncheon Bus GO route engine without changing it."""
    spec = importlib.util.spec_from_file_location("bomnae_transit_web", TRANSIT_WEB_APP)
    if spec is None or spec.loader is None:
        raise RuntimeError("교통 경로 모듈을 불러올 수 없습니다.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

st.set_page_config(
    page_title="봄내티움 | 프로그램 찾기",
    page_icon="🌱",
    layout="wide",
)

st.markdown(
    """
    <style>
      :root { --green:#238b45; --dark:#173e2d; --paper:#fffefa; --line:#e3e9e3; }
      .stApp { background:#f7f7f2; color:#202522; }
      #MainMenu, footer, header { visibility:hidden; }
      .block-container { max-width:1720px; padding:18px 5vw 70px !important; }
      div[data-testid="stImage"] img { width:158px !important; }
      div.stButton > button { min-height:44px; border:0; border-radius:12px; background:var(--green); color:#fff; font-weight:800; }
      div.stButton > button:hover { background:#166c35; color:#fff; border:0; }
      div[data-testid="stRadio"] div[role="radiogroup"] { gap:9px; flex-wrap:wrap; }
      div[data-testid="stRadio"] label { border:1px solid #dfe5df; border-radius:999px; padding:8px 14px; background:var(--paper); font-weight:800; }
      .hero { margin:15px 0 46px; min-height:265px; padding:48px 55px; border-radius:26px; background:linear-gradient(120deg,#eff8e9 0%,#fffbe6 62%,#fff4dc 100%); display:grid; grid-template-columns:1.2fr .8fr; overflow:hidden; position:relative; }
      .eyebrow { margin:0 0 12px; color:var(--green); font-size:11px; font-weight:900; letter-spacing:1.8px; }
      .hero h1 { margin:0; font-size:clamp(32px,4vw,51px); letter-spacing:-2.5px; line-height:1.16; }.hero h1 em { color:var(--green); font-style:normal; }.hero p:last-child { color:#667069; margin:18px 0 0; }
      .garden-art { position:relative; }.sun { position:absolute; right:15%; top:6%; width:72px; height:72px; border-radius:50%; background:#ffd965; box-shadow:0 0 0 16px rgba(255,217,101,.2); }.hill { position:absolute; border-radius:50% 50% 0 0; bottom:-70px; }.hill-a { right:-38px; width:370px; height:220px; background:#a9d792; }.hill-b { right:140px; width:300px; height:170px; bottom:-90px; background:#63aa69; }.seed { position:absolute; right:28%; bottom:43px; font-size:67px; filter:drop-shadow(0 10px 9px rgba(40,80,40,.18)); }
      .section-head { margin:0 0 10px; }.section-head h2 { margin:0; font-size:28px; letter-spacing:-1px; }
      .program-card { position:relative; min-height:340px; margin:12px 0; padding:22px; border:1px solid var(--line); border-radius:18px; background:var(--paper); box-shadow:0 8px 26px rgba(44,70,50,.06); overflow:hidden; }.program-card:before { content:""; position:absolute; left:0; top:0; bottom:0; width:5px; background:var(--green); }.program-top { display:flex; justify-content:space-between; gap:10px; }.badge { display:inline-block; padding:5px 8px; margin-right:4px; border-radius:999px; background:#edf7ed; color:#176c35; font-size:10px; font-weight:900; }.badge.ai { background:#e7f0ff; color:#3868ad; }.badge.bio { background:#fff1dd; color:#b66a15; }.status { color:#758078; font-size:11px; white-space:nowrap; }.program-card h3 { margin:22px 0 8px; color:var(--dark); font-size:20px; letter-spacing:-.8px; }.provider { color:#31734a; font-size:12px; font-weight:800; }.summary { min-height:61px; color:#747d77; font-size:12px; line-height:1.65; }.facts { margin-top:15px; padding-top:13px; border-top:1px solid var(--line); color:#68726b; font-size:11px; line-height:1.85; }.facts b { color:#354139; }
      .profile-box { padding:26px; border:1px solid var(--line); border-radius:20px; background:var(--paper); }.growth { display:grid; place-items:center; min-height:240px; border-radius:18px; background:linear-gradient(145deg,#eff8e9,#fffbe8); text-align:center; }.growth .emoji { font-size:84px; }.growth h3 { margin:8px 0 0; color:var(--green); }.login-note { color:#738078; font-size:12px; }
      @media(max-width:700px) { .block-container { padding:10px 14px 45px !important; }.hero { grid-template-columns:1fr; min-height:250px; padding:35px 26px; }.hero h1 { font-size:34px; }.garden-art { position:absolute; right:-45px; bottom:-30px; width:250px; height:160px; opacity:.42; }.program-card { min-height:auto; }.summary { min-height:auto; } }
    </style>
    """,
    unsafe_allow_html=True,
)


CATEGORY_DEFINITIONS = [
    ("전체", None),
    ("SW", {"is_sw"}),
    ("AI", {"is_ai"}),
    ("바이오", {"is_bio"}),
    ("AI·SW 융합", {"is_ai", "is_sw"}),
    ("AI·바이오 융합", {"is_ai", "is_bio"}),
    ("SW·바이오 융합", {"is_sw", "is_bio"}),
    ("AI·SW·바이오 융합", {"is_ai", "is_sw", "is_bio"}),
]


st.markdown(
    """
    <style>
      .transit-hero { margin: 12px 0 30px; padding: 42px 48px; border-radius: 26px; background:linear-gradient(120deg,#eff8e9,#fffbe6 62%,#fff4dc); }
      .transit-hero h2 { margin:0; font-size:clamp(30px,4vw,48px); letter-spacing:-2px; }.transit-hero em { color:#238b45; font-style:normal; }
      .transit-hero p { color:#667069; margin:16px 0 0; }.route-card { position:relative; min-height:345px; padding:22px; margin:12px 0; overflow:hidden; border:1px solid #e3e9e3; border-radius:18px; background:#fffefa; box-shadow:0 8px 26px rgba(44,70,50,.06); }.route-card:before { content:''; position:absolute; inset:0 auto 0 0; width:5px; background:#238b45; }
      .route-top { display:flex; justify-content:space-between; gap:12px; align-items:flex-start; }.route-title { display:flex; gap:11px; align-items:center; }.route-rank { display:grid; place-items:center; width:30px; height:30px; border-radius:10px; background:#eaf5eb; color:#238b45; font-size:13px; font-weight:900; }.route-time { font-size:25px; font-weight:900; letter-spacing:-1px; line-height:1.15; }.route-type,.route-arrival small { color:#89908b; font-size:10px; }.route-arrival { text-align:right; white-space:nowrap; }.route-arrival strong { display:block; margin-top:3px; color:#166c35; font-size:16px; }
      .route-tags { display:flex; flex-wrap:wrap; gap:6px; margin:17px 0 12px; }.route-tag { display:inline-block; padding:5px 8px; border-radius:999px; background:#edf7ed; color:#166c35; font-size:10px; font-weight:800; }.route-tag:nth-child(even) { background:#fff2df; color:#b66a15; }.route-walks { display:flex; flex-wrap:wrap; gap:7px; margin-bottom:13px; }.route-walks span { padding:6px 9px; border-radius:9px; background:#f1f4ef; color:#69716b; font-size:10px; }.route-walks b { color:#202522; }
      .route-journey { display:grid; gap:10px; padding:13px; border-radius:13px; background:#f8faf7; }.route-segment { display:grid; grid-template-columns:58px 1fr; gap:10px; }.bus-number { display:grid; place-items:center; min-height:31px; padding:4px; border-radius:8px; background:#238b45; color:#fff; font-size:10px; font-weight:900; text-align:center; overflow-wrap:anywhere; }.route-segment strong { display:block; font-size:12px; }.route-segment small { color:#858d87; font-size:10px; }.realtime { color:#d9342b; font-weight:900; }.route-stats { display:grid; grid-template-columns:repeat(3,1fr); margin-top:15px; padding-top:13px; border-top:1px solid #e3e9e3; }.route-stats div { padding:0 7px; border-right:1px solid #e3e9e3; }.route-stats div:last-child { border:0; }.route-stats small { display:block; color:#919892; font-size:9px; }.route-stats b { font-size:12px; }
      div[data-testid='stExpander'] { border:1px solid #e3e9e3; border-radius:12px; background:#fbfcfa; margin:-5px 0 14px; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=30, show_spinner=False)
def calculate_transit_routes(origin_key: str, destination_key: str) -> dict:
    transit = load_transit_module()
    return transit.calculate_routes(transit.PLACES[origin_key], transit.PLACES[destination_key])


def render_transit_route(route: dict) -> None:
    tags = "".join(f'<span class="route-tag">{escape(tag)}</span>' for tag in route.get("tags", []))
    segments_html = ""
    for segment in route["segments"]:
        realtime = segment.get("realtime_arrivals", [])
        wait = ""
        if realtime:
            first = realtime[0]
            minutes = max(round(first["arrival_seconds"] / 60), 1)
            remaining = first.get("remaining_stop_count")
            remaining_text = f" · {remaining}정거장 남음" if remaining is not None else ""
            wait = f'<span class="realtime"> · 실시간 약 {minutes}분 후{remaining_text}</span>'
        elif segment.get("bus_options"):
            wait = f' · {escape(segment["bus_options"][0].get("wait_text") or "시간표 확인")}'
        segments_html += f'''<div class="route-segment"><span class="bus-number">{escape(', '.join(segment['route_numbers']))}</span><span><strong>{escape(segment['boarding_stop'])} → {escape(segment['alighting_stop'])}</strong><small>정류장 {segment['stop_count']}개 · 버스 탑승 {escape(segment['in_vehicle_text'])}{wait}</small></span></div>'''
    st.markdown(
        f'''<article class="route-card"><div class="route-top"><div class="route-title"><span class="route-rank">{route.get('rank', '-')}</span><div><div class="route-time">{escape(route['in_vehicle_text'])}</div><div class="route-type">환승 {route['transfer_count']}회 경로</div></div></div><div class="route-arrival"><small>목적지 도착</small><strong>{escape(route.get('arrival_time') or '시간표 확인 중')}</strong></div></div><div class="route-tags">{tags}</div><div class="route-walks"><span>출발 도보 <b>{round(route['origin_walking_distance_m'])}m</b></span><span>도착 도보 <b>{round(route['destination_walking_distance_m'])}m</b></span></div><div class="route-journey">{segments_html}</div><div class="route-stats"><div><small>총 소요</small><b>{escape(route['elapsed_text'])}</b></div><div><small>버스 탑승</small><b>{escape(route['in_vehicle_text'])}</b></div><div><small>총 도보</small><b>{round(route['walking_distance_m'])}m</b></div></div></article>''',
        unsafe_allow_html=True,
    )
    for segment in route["segments"]:
        route_numbers = ", ".join(segment["route_numbers"])
        realtime = segment.get("realtime_arrivals", [])
        if realtime:
            first = realtime[0]
            arrival_text = f"실시간 약 {max(round(first['arrival_seconds'] / 60), 1)}분 후"
            if first.get("remaining_stop_count") is not None:
                arrival_text += f" · {first['remaining_stop_count']}정거장 남음"
        else:
            arrival_text = segment.get("boarding_time") or "시간표 정보 없음"
        with st.expander(f"{route_numbers}번 · {segment['boarding_stop']} → {segment['alighting_stop']}"):
            st.write(f"탑승 예정: {arrival_text}")
            st.write(f"정류장 {segment['stop_count']}개 · 버스 이동 {segment['in_vehicle_text']}")
            stops = " → ".join(stop["name"] for stop in segment.get("stops", []))
            if stops:
                st.caption(stops)


@st.cache_data(show_spinner=False)
def load_programs() -> list[dict]:
    return program_rows()


def program_fields(program: dict) -> set[str]:
    return {
        field
        for field in ("is_sw", "is_ai", "is_bio")
        if program.get(field) == "1"
    }


def program_matches(program: dict, wanted: set[str] | None) -> bool:
    return wanted is None or program_fields(program) == wanted


def program_badges(program: dict) -> str:
    labels = {"is_sw": "SW", "is_ai": "AI", "is_bio": "바이오"}
    css = {"is_sw": "sw", "is_ai": "ai", "is_bio": "bio"}
    return "".join(
        f'<span class="badge {css[field]}">{labels[field]}</span>'
        for field in ("is_sw", "is_ai", "is_bio")
        if field in program_fields(program)
    )


@st.dialog("프로그램 상세")
def show_program_detail(program: dict) -> None:
    st.subheader(program["title"])
    st.caption(program.get("provider") or "제공 기관 정보 없음")
    st.write(program.get("summary") or "상세 설명이 없습니다.")
    st.write(f"대상: {program.get('grade_label') or '확인 필요'}")
    st.write(f"기간: {program.get('start_date') or '확인 필요'} ~ {program.get('end_date') or '확인 필요'}")
    st.write(f"장소: {'온라인' if program.get('is_online') == '1' else program.get('place_name') or '확인 필요'}")
    if program.get("detail_url"):
        st.link_button("프로그램 상세 페이지 열기", program["detail_url"], use_container_width=True)


def render_program(program: dict) -> None:
    location = "온라인" if program.get("is_online") == "1" else (program.get("place_name") or "확인 필요")
    st.markdown(
        f"""
        <article class="program-card">
          <div class="program-top"><div>{program_badges(program)}</div><span class="status">{escape(program.get('status_label') or '일정 확인')}</span></div>
          <h3>{escape(program['title'])}</h3>
          <p class="provider">{escape(program.get('provider') or '제공 기관 확인')}</p>
          <p class="summary">{escape(program.get('summary') or '프로그램 상세 페이지에서 교육 내용을 확인해보세요.')}</p>
          <div class="facts"><b>대상</b> {escape(program.get('grade_label') or '확인 필요')}<br><b>기간</b> {escape(program.get('start_date') or '확인 필요')} ~ {escape(program.get('end_date') or '확인 필요')}<br><b>장소</b> {escape(location)}</div>
        </article>
        """,
        unsafe_allow_html=True,
    )


logo_column, login_column = st.columns([5, 1])
with logo_column:
    st.image(str(PROJECT_ROOT / "public" / "bomnae-logo-transparent-v3.png"))
with login_column:
    if st.button("학생 로그인", use_container_width=True):
        st.session_state["show_login"] = True

st.markdown(
    """<section class="hero"><div><p class="eyebrow">BOMNAE-TIUM PROGRAMS</p>
    <h1>나에게 맞는 배움,<br><em>봄내티움에서 찾아보세요.</em></h1>
    <p>SW·AI·바이오 프로그램을 분야와 관심사에 맞게 추천합니다.</p></div>
    <div class="garden-art"><span class="sun"></span><span class="hill hill-a"></span><span class="hill hill-b"></span><span class="seed">🌱</span></div></section>""",
    unsafe_allow_html=True,
)

program_tab, growth_tab, transit_tab = st.tabs(
    ["프로그램 찾기", "나의 성장 정원", "🚌 참여 경로 확인"]
)

with program_tab:
    st.markdown('<div class="section-head"><p class="eyebrow">PROGRAMS</p><h2>지금 인기 있는 프로그램</h2></div>', unsafe_allow_html=True)
    selected_name = st.radio(
        "분야 선택",
        [name for name, _ in CATEGORY_DEFINITIONS],
        horizontal=True,
        label_visibility="collapsed",
    )
    selected_fields = dict(CATEGORY_DEFINITIONS)[selected_name]
    programs = [program for program in load_programs() if program_matches(program, selected_fields)]
    if not programs:
        st.info("해당 분야의 프로그램이 없습니다.")
    else:
        visible = programs[:12]
        columns = st.columns(3)
        for index, program in enumerate(visible):
            with columns[index % 3]:
                render_program(program)
                if st.button("자세히 보기 →", key=f"program-{program['program_id']}", use_container_width=True):
                    show_program_detail(program)

with growth_tab:
    st.markdown('<div class="section-head"><p class="eyebrow">MY GROWTH</p><h2>나의 성장 정원</h2></div>', unsafe_allow_html=True)
    if st.session_state.get("student"):
        student = st.session_state["student"]
        fertilizer = st.session_state.get("fertilizer", 0)
        stages = [(0, "씨앗", "🌰"), (2, "새싹", "🌱"), (6, "본잎", "🌿"), (12, "꽃", "🌸"), (20, "열매", "🍎")]
        current = max((stage for stage in stages if fertilizer >= stage[0]), key=lambda stage: stage[0])
        left, right = st.columns([1, 1.4])
        with left:
            st.markdown(f'<div class="growth"><div class="emoji">{current[2]}</div><h3>{escape(student["stu_name"])}님의 {current[1]}</h3><p>비료 {fertilizer}개</p></div>', unsafe_allow_html=True)
        with right:
            st.subheader("성장시키기")
            st.progress(min(fertilizer / 20, 1.0))
            st.write("프로그램 활동을 통해 비료를 모아 성장 단계를 올려보세요.")
            if st.button("비료 주기", use_container_width=True) and fertilizer < 20:
                st.session_state["fertilizer"] = fertilizer + 1
                st.rerun()
    else:
        st.info("학생 로그인 후 나의 성장 정원을 이용할 수 있습니다.")

with transit_tab:
    st.markdown(
        """<section class="transit-hero"><p class="eyebrow">PROGRAM ACCESS GUIDE</p>
        <h2>내게 맞는 프로그램,<br><em>직접 참여할 수 있을까요?</em></h2>
        <p>춘천버스GO 실시간 도착 정보와 시간표를 바탕으로 참여 경로를 확인합니다.</p></section>""",
        unsafe_allow_html=True,
    )
    try:
        transit = load_transit_module()
    except Exception as error:
        st.error("교통 경로 기능을 준비하지 못했습니다.")
        st.exception(error)
    else:
        place_keys = list(transit.PLACES)

        def transit_place_label(key: str) -> str:
            place = transit.PLACES[key]
            return f"{place['name']} · {place['description']}"

        left, right = st.columns(2)
        with left:
            origin_key = st.selectbox(
                "나의 출발 위치", place_keys, format_func=transit_place_label,
                index=place_keys.index("bio_center"), key="transit-origin",
            )
        with right:
            destination_key = st.selectbox(
                "선택한 프로그램 장소", place_keys, format_func=transit_place_label,
                index=place_keys.index("youth_library"), key="transit-destination",
            )

        if st.button("참여 경로 확인", key="find-transit-route", type="primary", use_container_width=True):
            if origin_key == destination_key:
                st.warning("출발지와 도착지는 서로 다르게 선택해주세요.")
            else:
                with st.spinner("직행·환승 경로와 춘천버스GO 실시간 정보를 계산하고 있습니다..."):
                    try:
                        st.session_state["transit_result"] = calculate_transit_routes(origin_key, destination_key)
                    except Exception as error:
                        st.error("경로를 계산하지 못했습니다. 잠시 후 다시 시도해주세요.")
                        st.exception(error)

        result = st.session_state.get("transit_result")
        if result:
            st.markdown('<div class="section-head"><p class="eyebrow">PROGRAM ACCESS</p><h2>이 프로그램에 갈 수 있는 경로</h2></div>', unsafe_allow_html=True)
            st.caption(f"{result['queried_at']} 기준 · 빨간 글씨는 춘천버스GO 실시간 도착 정보입니다.")
            categories = result["categories"]
            category_tabs = st.tabs([category["label"] for category in categories.values()])
            for category_tab, category in zip(category_tabs, categories.values()):
                with category_tab:
                    routes = category["routes"]
                    if not routes:
                        st.info("표시할 경로가 없습니다.")
                        continue
                    columns = st.columns(min(3, len(routes)))
                    for index, route in enumerate(routes):
                        with columns[index % len(columns)]:
                            render_transit_route(route)
        else:
            st.info("출발 위치와 프로그램 장소를 선택한 뒤 참여 경로 확인을 눌러주세요.")

if st.session_state.get("show_login"):
    with st.sidebar:
        st.subheader("학생 로그인")
        st.caption("기존 학생 계정으로 로그인할 수 있습니다.")
        with st.form("student-login"):
            login_id = st.text_input("아이디")
            login_password = st.text_input("비밀번호", type="password")
            submitted = st.form_submit_button("로그인", use_container_width=True)
        if submitted:
            student = find_student(login_id, login_password)
            if student:
                st.session_state["student"] = student
                st.session_state.setdefault("fertilizer", 0)
                st.session_state["show_login"] = False
                st.success(f"{student['stu_name']}님, 환영합니다!")
            else:
                st.error("아이디 또는 비밀번호를 확인해주세요.")
