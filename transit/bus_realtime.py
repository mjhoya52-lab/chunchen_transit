import time

from datetime import datetime, timedelta

import requests

from bus_timetable import SEOUL_TZ


CHUNCHEON_BIS_ARRIVAL_URL = (
    "https://ccbus.chuncheon.go.kr/"
    "rest/api/v1/rbs/predict/arrival"
)


class RealtimeApiError(RuntimeError):
    """춘천버스GO 실시간 도착정보 조회 또는 응답 해석 오류."""


def _to_int(value, default=None):
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def _to_float(value, default=None):
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


class ChuncheonBisRealtimeClient:
    """춘천버스GO BIS의 정류소별 실시간 도착예정정보를 조회한다."""

    def __init__(
        self,
        timeout_seconds: float = 8,
        cache_ttl_seconds: float = 30,
    ) -> None:
        self.timeout_seconds = float(timeout_seconds)
        self.cache_ttl_seconds = max(float(cache_ttl_seconds), 0)
        self._station_arrival_cache = {}
        self._station_arrival_cache_times = {}

    @property
    def is_configured(self) -> bool:
        return True

    def get_stop_arrivals(self, node_id: str) -> list[dict]:
        """정류소의 전체 도착정보를 한 번만 조회해 노선별로 재사용한다."""
        station_id = str(node_id)
        cached_at = self._station_arrival_cache_times.get(station_id)
        if (
            station_id in self._station_arrival_cache
            and cached_at is not None
            and time.monotonic() - cached_at <= self.cache_ttl_seconds
        ):
            return self._station_arrival_cache[station_id]

        try:
            response = requests.get(
                CHUNCHEON_BIS_ARRIVAL_URL,
                params={"entity.stationId": station_id},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as error:
            raise RealtimeApiError(
                f"춘천버스GO BIS 요청 실패: {error}"
            ) from error

        if not isinstance(payload, list):
            raise RealtimeApiError(
                "춘천버스GO BIS 도착정보 응답 형식이 올바르지 않습니다."
            )

        self._station_arrival_cache[station_id] = payload
        self._station_arrival_cache_times[station_id] = time.monotonic()
        return payload

    def get_route_arrivals(
        self,
        node_id: str,
        route_id: str,
    ) -> list[dict]:
        results = []
        for item in self.get_stop_arrivals(node_id):
            if not isinstance(item, dict):
                continue
            item_route_id = str(item.get("entityId", "")).strip()
            if item_route_id != str(route_id):
                continue

            predict_minute = _to_float(item.get("predictMinute"))
            if predict_minute is None or predict_minute < 0:
                continue

            results.append({
                "node_id": str(node_id),
                "node_name": str(item.get("stationName", "")).strip(),
                "route_id": item_route_id,
                "route_number": str(item.get("routeName", "")).strip(),
                "route_type": str(item.get("routeTypeName", "")).strip(),
                "arrival_seconds": round(predict_minute * 60),
                "remaining_stop_count": _to_int(item.get("leftStationCount")),
                "vehicle_type": str(item.get("cityRouteTypeCode", "")).strip() or None,
                "vehicle_number": str(item.get("plateNumber", "")).strip() or None,
                "destination_name": str(item.get("finalArrivalStation", "")).strip() or None,
                "source": "CHUNCHEON_BIS",
            })

        results.sort(key=lambda item: item["arrival_seconds"])
        return results

    def build_realtime_predictions(
        self,
        node_id: str,
        route_id: str,
        query_datetime: datetime,
        in_vehicle_seconds: float,
        count: int = 2,
        earliest_boarding_datetime: datetime | None = None,
    ) -> dict:
        if query_datetime.tzinfo is None:
            query_datetime = query_datetime.replace(tzinfo=SEOUL_TZ)
        else:
            query_datetime = query_datetime.astimezone(SEOUL_TZ)

        if (
            earliest_boarding_datetime is not None
            and earliest_boarding_datetime.tzinfo is None
        ):
            earliest_boarding_datetime = earliest_boarding_datetime.replace(
                tzinfo=SEOUL_TZ
            )

        arrivals = self.get_route_arrivals(node_id, route_id)
        predictions = []
        for item in arrivals:
            boarding_arrival = query_datetime + timedelta(
                seconds=item["arrival_seconds"]
            )
            if (
                earliest_boarding_datetime is not None
                and boarding_arrival < earliest_boarding_datetime
            ):
                continue

            predictions.append({
                **item,
                "source": "CHUNCHEON_BIS_REALTIME_ARRIVAL_API",
                "query_datetime": query_datetime,
                "boarding_arrival_datetime": boarding_arrival,
                "alighting_estimated_datetime": boarding_arrival + timedelta(
                    seconds=float(in_vehicle_seconds)
                ),
                "gps_location_available": False,
            })
            if len(predictions) >= count:
                break

        return {
            "available": bool(predictions),
            "predictions": predictions,
            "gps_location_available": False,
            "raw_arrival_count": len(arrivals),
        }
