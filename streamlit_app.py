"""Streamlit entry point for the Chuncheon bus route recommender."""

from pathlib import Path
import sys
from html import escape

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
WEB_ROOT = PROJECT_ROOT / "transit" / "web"
sys.path.insert(0, str(WEB_ROOT))

from app import CATEGORY_LABELS, PLACES, calculate_routes  # noqa: E402


st.set_page_config(
    page_title="봄내티움 | 참여 경로 확인",
    page_icon="🚌",
    layout="wide",
)

st.markdown(
    """
    <style>
      :root { --green: #238b45; --green-dark: #166c35; --paper: #fffefa; --ink: #202522; --line: #e3e9e3; }
      .stApp { background: #f7f7f2; color: var(--ink); }
      #MainMenu, footer, header { visibility: hidden; }
      .block-container { max-width: 1720px; padding: 0 5vw 70px !important; }
      div[data-testid="stVerticalBlock"] { gap: 0.85rem; }
      div[data-testid="stImage"] img { width: 158px !important; }
      div[data-testid="stSelectbox"] > label { color: #8a918c; font-size: 0.76rem; font-weight: 700; }
      div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        min-height: 58px; border: 1px solid var(--line); border-radius: 14px;
        background: #fbfcfa; box-shadow: none;
      }
      div[data-testid="stSelectbox"] div[data-baseweb="select"] span { color: var(--ink); font-weight: 800; }
      div.stButton > button {
        min-height: 58px; border: 0; border-radius: 14px; background: var(--green);
        color: #fff; font-weight: 850; font-size: 1rem; box-shadow: 0 8px 18px rgba(35,139,69,.2);
      }
      div.stButton > button:hover { background: var(--green-dark); color: #fff; border: 0; transform: translateY(-1px); }
      button[data-baseweb="tab"] { border: 1px solid #dfe5df !important; border-radius: 999px !important;
        padding: 9px 17px !important; background: var(--paper) !important; color: #636a65 !important; font-weight: 800 !important; }
      button[data-baseweb="tab"][aria-selected="true"] { background: var(--green) !important; color: white !important;
        border-color: var(--green) !important; box-shadow: 0 7px 15px rgba(35,139,69,.18); }
      div[data-baseweb="tab-list"] { gap: 8px; border-bottom: 0; }
      div[data-baseweb="tab-highlight"] { display: none; }
      .top-spacer { height: 12px; }
      .hero {
        min-height: 282px; padding: 48px 56px; border-radius: 26px;
        background: linear-gradient(120deg,#eff8e9 0%,#fffbe6 62%,#fff4dc 100%);
        display: grid; grid-template-columns: 1.2fr .8fr; overflow: hidden; position: relative;
      }
      .eyebrow { margin: 0 0 12px; color: var(--green); font-size: 11px; font-weight: 900; letter-spacing: 1.8px; }
      .hero h1 { margin: 0; font-size: clamp(32px,4vw,50px); line-height: 1.18; letter-spacing: -2.3px; }
      .hero h1 em { color: var(--green); font-style: normal; }
      .hero p:not(.eyebrow) { margin: 20px 0 0; color: #667069; font-size: 15px; }
      .hero-art { position: relative; min-height: 180px; }
      .sun { position:absolute; width:72px; height:72px; border-radius:50%; background:#ffd965; right:12%; top:8%; box-shadow:0 0 0 16px rgba(255,217,101,.2); }
      .hill { position:absolute; border-radius:50% 50% 0 0; bottom:-70px; }
      .hill-one { width:360px;height:220px;background:#a9d792;right:-30px; }
      .hill-two { width:300px;height:170px;background:#63aa69;right:140px;bottom:-90px; }
      .bus { position:absolute; z-index:2; right:24%; bottom:18px; width:116px; height:61px; border-radius:18px 18px 10px 10px; background:#fff; border:7px solid #ec8a1b; color:#ec8a1b; display:grid; place-items:center; font-weight:900; letter-spacing:2px; box-shadow:0 12px 20px rgba(45,75,45,.18); }
      .bus:before,.bus:after { content:""; position:absolute; width:17px;height:17px;border-radius:50%;background:#34463a;bottom:-15px; }
      .bus:before { left:15px; }.bus:after { right:15px; }
      .search-hint { color: #667069; font-size: .86rem; margin: 18px 0 2px; }
      .section-title { margin: 58px 0 6px; }
      .section-title h2 { font-size: 28px; letter-spacing: -1px; margin: 0; }
      .queried { color: #89908b; font-size: 12px; text-align: right; margin: 12px 0; }
      .route-card {
        position: relative; overflow: hidden; background: var(--paper); border: 1px solid var(--line);
        border-radius: 18px; padding: 24px; min-height: 405px; margin: 14px 0 0; box-shadow: 0 8px 26px rgba(44,70,50,.06);
      }
      .route-card:before { content:""; position:absolute; left:0; top:0; bottom:0; width:5px; background:var(--green); }
      .route-top { display:flex; justify-content:space-between; gap:12px; align-items:flex-start; }
      .route-title { display:flex; gap:11px; align-items:center; }
      .rank { display:grid; place-items:center; width:30px; height:30px; border-radius:10px; background:#eaf5eb; color:var(--green); font-size:13px; font-weight:900; }
      .time { font-size:29px; font-weight:900; letter-spacing:-1px; line-height:1.15; }
      .type, .arrival small { color:#89908b; font-size:11px; }
      .arrival { text-align:right; white-space:nowrap; }.arrival strong { display:block; color:var(--green-dark); font-size:18px; margin-top:4px; }
      .tags { margin:17px 0 12px; display:flex; flex-wrap:wrap; gap:6px; }
      .tag { display:inline-block; border-radius:999px; padding:5px 8px; background:#edf7ed; color:var(--green-dark); font-size:10px; font-weight:800; }
      .tag:nth-child(even) { background:#fff2df; color:#b66a15; }
      .walks { display:flex; gap:7px; flex-wrap:wrap; margin-bottom:14px; }.walks span { padding:7px 10px; border-radius:9px; background:#f1f4ef; color:#69716b; font-size:11px; }.walks b { color:var(--ink); }
      .journey { padding:15px; background:#f8faf7; border-radius:13px; display:grid; gap:12px; }
      .segment { display:grid; grid-template-columns:64px 1fr; gap:11px; }.bus-number { display:grid; place-items:center; min-height:48px; padding:5px; border-radius:9px; background:var(--green); color:#fff; font-size:11px; font-weight:900; text-align:center; overflow:hidden; }.segment strong { display:block; font-size:13px; }.segment small { color:#858d87; font-size:11px; line-height:1.55; }.realtime { color:#d9342b; font-weight:900; }
      .stats { display:grid; grid-template-columns:repeat(3,1fr); margin-top:17px; padding-top:14px; border-top:1px solid var(--line); }.stats div { padding:0 9px; border-right:1px solid var(--line); }.stats div:last-child { border:0; }.stats small { display:block; color:#919892; font-size:10px; margin-bottom:4px; }.stats b { font-size:13px; }
      div[data-testid="stExpander"] { border: 1px solid var(--line); border-radius: 12px; background: #fbfcfa; margin: -5px 0 14px; }
      div[data-testid="stButton"] button[kind="secondary"] { min-height: 42px; border: 1px solid #b9ddc1; background: #fffefa; color: var(--green-dark); box-shadow: none; font-size: .88rem; }
      div[data-testid="stDialog"] div[role="dialog"] { width: min(720px, calc(100vw - 28px)); }
      .detail-head { display:flex; justify-content:space-between; align-items:end; gap:12px; margin:8px 0 20px; }.detail-head h2 { margin:0; font-size:39px; letter-spacing:-2px; }.detail-head b { color:var(--green-dark); font-size:14px; text-align:right; }
      .timeline { margin:12px 0; }.timeline-item { position:relative; padding:0 0 25px 58px; min-height:64px; }.timeline-item:before { content:""; position:absolute; left:17px; top:35px; bottom:0; width:3px; background:#dfe4df; }.timeline-item:last-child:before { display:none; }.timeline-dot { position:absolute; left:5px; top:3px; width:27px; height:27px; border:5px solid #7e8580; border-radius:50%; background:white; }.timeline-item.bus .timeline-dot { border-color:#344d8c; border-radius:9px; }.timeline-item.destination .timeline-dot { border-color:#e34d3f; }.timeline-item b { display:block; font-size:17px; }.timeline-item p { margin:4px 0; color:#818a84; font-size:12px; }.bus-box { margin-top:12px; padding:13px 15px; border:1px solid var(--line); border-radius:14px; background:#fbfcfa; }.bus-option { display:flex; align-items:center; gap:9px; padding:6px 0; font-size:13px; }.bus-option span { min-width:48px; padding:5px 7px; border-radius:7px; background:#4f9f2f; color:white; text-align:center; font-size:11px; font-weight:900; }.stop-list { margin-top:10px; padding:13px 16px; border-radius:12px; background:#f1f4ef; }.stop-list strong { display:block; margin-bottom:8px; }.stop-list ol { margin:0; padding-left:24px; }.stop-list li { padding:4px 0; color:#49534b; font-size:12px; }
      @media (max-width: 700px) { .block-container { padding: 0 14px 48px !important; }.hero { padding:34px 25px; grid-template-columns:1fr; min-height:260px; }.hero-art { position:absolute; right:-45px; bottom:-25px; width:260px; height:150px; opacity:.45; }.hero h1 { font-size:34px; }.route-card { min-height:auto; }.time { font-size:22px; } }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=30, show_spinner=False)
def calculate_routes_cached(origin_key: str, destination_key: str) -> dict:
    """Cache identical searches briefly without changing route ranking."""
    return calculate_routes(PLACES[origin_key], PLACES[destination_key])


def place_label(key: str) -> str:
    place = PLACES[key]
    return f"{place['name']} · {place['description']}"


def short_bus_number(number: str) -> str:
    return number.split("(", 1)[0].strip()


def render_route(route: dict) -> None:
    tags = "".join(f'<span class="tag">{escape(tag)}</span>' for tag in route.get("tags", []))
    segments_html = ""
    for segment in route["segments"]:
        realtime = segment.get("realtime_arrivals", [])
        wait = ""
        if realtime:
            wait = f'<span class="realtime"> · 실시간 약 {max(round(realtime[0]["arrival_seconds"] / 60), 1)}분 후</span>'
        elif segment.get("bus_options"):
            wait = f' · {escape(segment["bus_options"][0].get("wait_text") or "시간표 확인")}'
        route_numbers = segment["route_numbers"]
        primary_number = short_bus_number(route_numbers[0])
        alternatives = f" · 같은 경로 {len(route_numbers)}대" if len(route_numbers) > 1 else ""
        segments_html += f"""
          <div class="segment"><span class="bus-number">{escape(primary_number)}</span>
          <span><strong>{escape(segment['boarding_stop'])} → {escape(segment['alighting_stop'])}</strong>
          <small>정류장 {segment['stop_count']}개 · 버스 탑승 {escape(segment['in_vehicle_text'])}{alternatives}{wait}</small></span></div>"""
    st.markdown(
        f"""
        <div class="route-card">
          <div class="route-top"><div class="route-title"><span class="rank">{route.get('rank', '-')}</span><div><div class="time">{escape(route['in_vehicle_text'])}</div><div class="type">환승 {route['transfer_count']}회 경로</div></div></div>
          <div class="arrival"><small>목적지 도착</small><strong>{escape(route.get('arrival_time') or '시간표 확인 중')}</strong></div></div>
          <div class="tags">{tags}</div>
          <div class="walks"><span>출발 도보 <b>{round(route['origin_walking_distance_m'])}m</b></span><span>도착 도보 <b>{round(route['destination_walking_distance_m'])}m</b></span></div>
          <div class="journey">{segments_html}</div>
          <div class="stats"><div><small>총 소요</small><b>{escape(route['elapsed_text'])}</b></div><div><small>버스 탑승</small><b>{escape(route['in_vehicle_text'])}</b></div><div><small>총 도보</small><b>{round(route['walking_distance_m'])}m</b></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.dialog("상세 경로")
def show_route_detail(route: dict, origin: dict, destination: dict) -> None:
    tags = "".join(f'<span class="tag">{escape(tag)}</span>' for tag in route.get("tags", []))
    timeline = f"""
      <div class="timeline"><div class="timeline-item"><span class="timeline-dot"></span>
      <b>{escape(origin['name'])}</b><p>{escape(origin['description'])}</p></div>
      <div class="timeline-item"><span class="timeline-dot"></span><b>도보 {round(route['origin_walking_distance_m'])}m</b><p>{max(round(route['origin_walking_minutes']), 1)}분 예상</p></div>"""
    for segment in route["segments"]:
        options = segment.get("bus_options", []) or [{"route_number": number} for number in segment["route_numbers"]]
        option_html = "".join(
            f'<div class="bus-option"><span>{escape(short_bus_number(option["route_number"]))}</span>{escape(option.get("wait_text") or option.get("boarding_time") or "도착정보 확인 중")}</div>'
            for option in options[:4]
        )
        stops = segment.get("stops", [])
        stops_html = "".join(f'<li>{escape(stop["name"])} <small>{escape(str(stop.get("number") or ""))}</small></li>' for stop in stops)
        timeline += f"""
          <div class="timeline-item bus"><span class="timeline-dot"></span><b>{escape(segment['boarding_stop'])}</b><p>{escape(segment['alighting_stop'])}에서 하차</p>
          <div class="bus-box">{option_html}</div>
          <div class="stop-list"><strong>{segment['stop_count']}개 정류장 · {escape(segment['in_vehicle_text'])}</strong><ol>{stops_html}</ol></div></div>"""
        if segment is not route["segments"][-1]:
            timeline += '<div class="timeline-item"><span class="timeline-dot"></span><b>환승 도보</b><p>다음 버스 탑승 정류장으로 이동</p></div>'
    timeline += f"""<div class="timeline-item"><span class="timeline-dot"></span><b>도보 {round(route['destination_walking_distance_m'])}m</b><p>{max(round(route['destination_walking_minutes']), 1)}분 예상</p></div>
      <div class="timeline-item destination"><span class="timeline-dot"></span><b>{escape(destination['name'])}</b><p>{escape(destination['description'])}</p></div></div>"""
    st.markdown(
        f'<div class="detail-head"><h2>{escape(route["in_vehicle_text"])}</h2><b>{escape(route.get("arrival_time") or "시간표 확인 중")} 도착 예정</b></div><div class="tags">{tags}</div>{timeline}',
        unsafe_allow_html=True,
    )


st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)
logo_column, action_column = st.columns([5, 1])
with logo_column:
    st.image(str(PROJECT_ROOT / "transit" / "web" / "static" / "logo.svg"))
with action_column:
    st.button("← 프로그램 지도", use_container_width=True)

st.markdown(
    """<section class="hero"><div><p class="eyebrow">PROGRAM ACCESS GUIDE</p>
    <h1>내게 맞는 프로그램,<br><em>직접 참여할 수 있을까요?</em></h1>
    <p>관심 프로그램을 찾았다면 버스로 갈 수 있는 경로를 확인해보세요.</p></div>
    <div class="hero-art"><span class="sun"></span><span class="hill hill-one"></span><span class="hill hill-two"></span><span class="bus">BUS</span></div></section>""",
    unsafe_allow_html=True,
)
st.markdown('<p class="search-hint">출발 위치와 프로그램 장소를 선택해주세요.</p>', unsafe_allow_html=True)

place_keys = list(PLACES)
left, right = st.columns(2)
with left:
    origin_key = st.selectbox(
        "나의 출발 위치",
        place_keys,
        format_func=place_label,
        index=place_keys.index("bio_center"),
    )
with right:
    destination_key = st.selectbox(
        "선택한 프로그램 장소",
        place_keys,
        format_func=place_label,
        index=place_keys.index("youth_library"),
    )

if origin_key == destination_key:
    st.warning("출발지와 도착지는 서로 다르게 선택해주세요.")

if st.button("참여 경로 확인", type="primary", use_container_width=True):
    if origin_key == destination_key:
        st.stop()
    with st.spinner("직행·환승 경로와 도착 정보를 계산하고 있습니다..."):
        try:
            result = calculate_routes_cached(origin_key, destination_key)
        except Exception as error:
            st.error("경로를 계산하지 못했습니다. 잠시 후 다시 시도해주세요.")
            st.exception(error)
        else:
            st.session_state["route_result"] = result

result = st.session_state.get("route_result")
if result:
    st.markdown('<div class="section-title"><p class="eyebrow">PROGRAM ACCESS</p><h2>이 프로그램에 갈 수 있는 경로</h2></div>', unsafe_allow_html=True)
    st.markdown(f'<p class="queried">{result["queried_at"]} 기준</p>', unsafe_allow_html=True)
    categories = result["categories"]
    tabs = st.tabs([category["label"] for category in categories.values()])
    for tab, category in zip(tabs, categories.values()):
        with tab:
            routes = category["routes"]
            if not routes:
                st.info("표시할 경로가 없습니다.")
                continue
            columns = st.columns(min(3, len(routes)))
            for index, route in enumerate(routes):
                with columns[index % len(columns)]:
                    render_route(route)
                    if st.button(
                        "상세 경로 보기 →",
                        key=f"route-detail-{category['label']}-{index}-{route['id']}",
                        use_container_width=True,
                    ):
                        show_route_detail(
                            route,
                            PLACES[origin_key],
                            PLACES[destination_key],
                        )
else:
    st.info("출발지와 프로그램 장소를 선택한 뒤 참여 경로 확인을 눌러주세요.")
