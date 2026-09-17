"""Deterministic swimming calculations. LLMs never own these decisions."""

from dataclasses import dataclass
from datetime import date

from app.domain.models import Confidence, CssTest, PerformanceRecord, ReadinessResult, WellnessRecord


@dataclass(frozen=True)
class CssResult:
    speed_m_per_second: float
    pace_100_seconds: float
    pace_50_seconds: float
    en1_seconds: float
    en2_seconds: float
    en3_seconds: float


def calculate_css(time_200_seconds: float, time_400_seconds: float) -> CssResult:
    if time_200_seconds <= 0 or time_400_seconds <= time_200_seconds:
        raise ValueError("400 m süresi 200 m süresinden büyük ve süreler pozitif olmalıdır")
    speed = 200 / (time_400_seconds - time_200_seconds)
    pace = 100 / speed
    return CssResult(speed, pace, pace / 2, pace + 8, pace + 2, max(1.0, pace - 3))


def create_css_test(athlete_id: str, tested_on: date, pool_length_m: int, time_200_seconds: float, time_400_seconds: float) -> CssTest:
    result = calculate_css(time_200_seconds, time_400_seconds)
    return CssTest(athlete_id=athlete_id, tested_on=tested_on, pool_length_m=pool_length_m, time_200_seconds=time_200_seconds, time_400_seconds=time_400_seconds, css_m_per_second=round(result.speed_m_per_second, 3), css_pace_seconds_per_100m=round(result.pace_100_seconds, 2))


def session_rpe_load(duration_minutes: int, rpe: int) -> int:
    if duration_minutes <= 0 or not 0 <= rpe <= 10:
        raise ValueError("Süre pozitif, RPE 0-10 arasında olmalıdır")
    return duration_minutes * rpe


def hr_zones(hrmax_bpm: int, resting_hr_bpm: int | None = None) -> dict[str, tuple[int, int]]:
    if not 80 <= hrmax_bpm <= 250:
        raise ValueError("HRmax 80-250 bpm arasında olmalıdır")
    base = resting_hr_bpm or 0
    reserve = hrmax_bpm - base if resting_hr_bpm else hrmax_bpm
    return {f"Z{index}": (round(base + reserve * low), round(base + reserve * high)) for index, (low, high) in enumerate(((0.60, 0.70), (0.70, 0.80), (0.80, 0.90), (0.90, 0.95), (0.95, 1.0)), 1)}


def readiness_score(wellness: WellnessRecord, recent_load: float, performance_signal: float | None = None) -> ReadinessResult:
    values = [wellness.sleep_hours is not None, wellness.hrv_ms is not None, wellness.resting_hr_bpm is not None, wellness.rpe is not None, wellness.mood is not None]
    completeness = sum(values) / len(values)
    components: list[tuple[str, float | None]] = [
        ("Sleep", None if wellness.sleep_hours is None else min(100, wellness.sleep_hours / 8 * 100)),
        ("HRV", None if wellness.hrv_ms is None else min(100, wellness.hrv_ms / 80 * 100)),
        ("Resting HR", None if wellness.resting_hr_bpm is None else max(0, 100 - wellness.resting_hr_bpm)),
        ("RPE", None if wellness.rpe is None else max(0, 100 - wellness.rpe * 10)),
        ("Wellness", None if wellness.mood is None else wellness.mood * 10),
        ("Load", max(0, 100 - min(100, recent_load / 1000 * 100))),
        ("Performance", performance_signal),
    ]
    present = [value for _, value in components if value is not None]
    score = round(sum(present) / len(present)) if present else 0
    reasons = [name for name, value in components if value is not None and value < 60]
    confidence = Confidence.HIGH if completeness >= 0.8 and len(present) >= 5 else Confidence.MEDIUM if completeness >= 0.5 else Confidence.LOW
    status = "HIGH ATTENTION" if score < 55 else "MONITOR" if score < 75 else "NORMAL"
    return ReadinessResult(score=score, status=status, reasons=reasons or ["Belirgin negatif sinyal yok"], data_completeness=completeness, confidence=confidence)


def detect_performance_anomaly(previous: PerformanceRecord, current: PerformanceRecord) -> bool:
    if previous.athlete_id != current.athlete_id or previous.distance_m != current.distance_m or previous.stroke != current.stroke:
        return False
    return current.time_seconds < previous.time_seconds * 0.8 or current.time_seconds > previous.time_seconds * 1.3


def compare_performance(records: list[PerformanceRecord]) -> dict[str, object]:
    ordered = sorted(records, key=lambda item: item.recorded_on)
    if not ordered:
        return {"count": 0, "trend": "INSUFFICIENT_DATA", "records": []}
    first, latest = ordered[0], ordered[-1]
    change_percent = round((latest.time_seconds - first.time_seconds) / first.time_seconds * 100, 2) if first.time_seconds else 0
    return {"count": len(ordered), "trend": "IMPROVING" if change_percent < 0 else "REGRESSING" if change_percent > 0 else "STABLE", "change_percent": change_percent, "records": [record.model_dump(mode="json") for record in ordered]}
