"""Streamlit entry point for the Chuncheon bus route recommender."""

from pathlib import Path
import sys

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
      .stApp { background: #f8faf5; }
      .route-card {
        background: white; border: 1px solid #dce6dc; border-radius: 16px;
        padding: 18px; min-height: 230px; margin-bottom: 14px;
      }
      .route-card h4 { color: #17412d; margin: 0 0 8px; }
      .tag { display: inline-block; background: #e6f5e8; color: #17733b;
        border-radius: 999px; padding: 3px 8px; font-size: 0.8rem; margin-right: 4px; }
      .muted { color: #65726a; font-size: 0.9rem; }
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


def render_route(route: dict) -> None:
    tags = "".join(
        f'<span class="tag">{tag}</span>' for tag in route.get("tags", [])
    )
    st.markdown(
        f"""
        <div class="route-card">
          <h4>{route.get('rank', '-')}. {route['in_vehicle_text']} 버스 이동</h4>
          <div>{tags}</div>
          <p><b>예상 도착</b> {route.get('arrival_time') or '시간표 확인 중'}</p>
          <p class="muted">총 소요 {route['elapsed_text']} · 도보 {round(route['walking_distance_m'])}m · 환승 {route['transfer_count']}회</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for segment in route["segments"]:
        bus_numbers = ", ".join(segment["route_numbers"])
        realtime = segment.get("realtime_arrivals", [])
        if realtime:
            first = realtime[0]
            arrival_text = (
                f"실시간 약 {max(round(first['arrival_seconds'] / 60), 1)}분 후"
            )
        else:
            arrival_text = segment.get("boarding_time") or "시간표 정보 없음"
        with st.expander(
            f"{bus_numbers}번 · {segment['boarding_stop']} → {segment['alighting_stop']}"
        ):
            st.write(f"탑승 예정: {arrival_text}")
            st.write(f"정류장 {segment['stop_count']}개 · 버스 이동 {segment['in_vehicle_text']}")
            stops = " → ".join(stop["name"] for stop in segment.get("stops", []))
            if stops:
                st.caption(stops)


st.title("🚌 봄내티움 참여 경로 확인")
st.write("관심 프로그램 장소까지의 버스 경로를 시간표와 실시간 도착정보로 안내합니다.")

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
    st.caption(f"{result['queried_at']} 기준")
    categories = result["categories"]
    tabs = st.tabs([category["label"] for category in categories.values()])
    for tab, category in zip(tabs, categories.values()):
        with tab:
            routes = category["routes"]
            if not routes:
                st.info("표시할 경로가 없습니다.")
                continue
            for route in routes:
                render_route(route)
else:
    st.info("출발지와 프로그램 장소를 선택한 뒤 참여 경로 확인을 눌러주세요.")
