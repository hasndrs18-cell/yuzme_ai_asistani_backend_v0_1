"""Swimming performance calculators and workout prescription tools."""

from __future__ import annotations

from math import floor

from langchain_core.tools import tool


_TRAINING_ZONES = {
    "A1": (60, 70, "Aerobic recovery and technical efficiency"),
    "A2": (70, 80, "Aerobic endurance and sustainable volume"),
    "A3": (80, 85, "Aerobic power and threshold preparation"),
    "EN1": (85, 90, "Extensive endurance and CSS support"),
    "EN2": (90, 95, "Intensive endurance near CSS"),
    "EN3": (95, 100, "High-intensity endurance and lactate tolerance"),
}


def _format_pace(seconds: float) -> str:
    minutes = floor(seconds / 60)
    remaining_seconds = round(seconds - minutes * 60)
    if remaining_seconds == 60:
        minutes += 1
        remaining_seconds = 0
    return f"{minutes}:{remaining_seconds:02d} / 100 m"


@tool
def calculate_css(t_200: float, t_400: float) -> dict[str, object]:
    """Calculate Critical Swim Speed from 200 m and 400 m times in seconds.

    Returns CSS pace plus practical A1-EN3 training intensity zones. Heart-rate
    values are percentages of an athlete's measured HRmax; a personal HRmax is
    required to turn them into beats per minute.
    """
    if t_200 <= 0 or t_400 <= 0:
        raise ValueError("Süreler sıfırdan büyük saniye değerleri olmalıdır.")
    if t_400 <= t_200:
        raise ValueError("400 m süresi 200 m süresinden büyük olmalıdır.")

    css_m_per_second = 200 / (t_400 - t_200)
    css_pace_seconds = 100 / css_m_per_second
    zones = []
    for name, (lower_hr, upper_hr, purpose) in _TRAINING_ZONES.items():
        pace_factor = lower_hr / 100
        upper_factor = upper_hr / 100
        zones.append(
            {
                "zone": name,
                "heart_rate_percent_hrmax": f"{lower_hr}-{upper_hr}%",
                "pace_per_100m": {
                    "fast": _format_pace(css_pace_seconds / upper_factor),
                    "slow": _format_pace(css_pace_seconds / pace_factor),
                },
                "purpose": purpose,
            }
        )

    return {
        "t_200_seconds": t_200,
        "t_400_seconds": t_400,
        "css_m_per_second": round(css_m_per_second, 3),
        "css_pace_per_100m": _format_pace(css_pace_seconds),
        "css_pace_seconds_per_100m": round(css_pace_seconds, 2),
        "heart_rate_note": "Yüzde değerlerini bpm'e çevirmek için sporcunun ölçülmüş HRmax değeri gerekir.",
        "training_zones": zones,
    }


@tool
def generate_swim_workout(distance: int, target_zone: str, level: str) -> dict[str, object]:
    """Generate a structured swim workout for a distance, zone, and level."""
    if distance < 400:
        raise ValueError("Antrenman mesafesi en az 400 metre olmalıdır.")

    normalized_zone = target_zone.strip().upper()
    if normalized_zone not in _TRAINING_ZONES:
        raise ValueError("Hedef bölge A1, A2, A3, EN1, EN2 veya EN3 olmalıdır.")

    normalized_level = level.strip().lower()
    level_names = {"beginner": "başlangıç", "intermediate": "orta", "advanced": "ileri"}
    if normalized_level not in level_names:
        raise ValueError("Seviye beginner, intermediate veya advanced olmalıdır.")

    warmup = max(200, round(distance * 0.15 / 50) * 50)
    cooldown = max(200, round(distance * 0.15 / 50) * 50)
    main_distance = distance - warmup - cooldown
    if main_distance < 100:
        raise ValueError("Bu mesafe için ısınma ve soğuma bölümleri ayrılamıyor.")

    repetitions = 4 if normalized_level == "beginner" else 6 if normalized_level == "intermediate" else 8
    rep_distance = max(50, round((main_distance / repetitions) / 50) * 50)
    repetitions = max(1, round(main_distance / rep_distance))
    main_distance = repetitions * rep_distance
    cooldown = distance - warmup - main_distance
    if cooldown < 100:
        cooldown = 100
        main_distance = distance - warmup - cooldown
        rep_distance = max(50, round((main_distance / repetitions) / 50) * 50)
        repetitions = max(1, round(main_distance / rep_distance))
        main_distance = repetitions * rep_distance
        cooldown = distance - warmup - main_distance

    return {
        "total_distance_m": distance,
        "target_zone": normalized_zone,
        "level": level_names[normalized_level],
        "sets": [
            {"name": "Isınma", "distance_m": warmup, "zone": "A1", "detail": "Kolay yüzüş + teknik odak"},
            {
                "name": "Ana set",
                "distance_m": main_distance,
                "repetitions": repetitions,
                "rep_distance_m": rep_distance,
                "zone": normalized_zone,
                "detail": "Teknik kaliteyi koruyarak, tekrarlar arasında 20-30 sn aktif dinlenme",
            },
            {"name": "Soğuma", "distance_m": cooldown, "zone": "A1", "detail": "Rahat tempo ve nefes kontrolü"},
        ],
        "coaching_notes": [
            "Her tekrarda stroke rate ve streamline kalitesini koru.",
            "Teknik bozulursa hızı değil, dinlenmeyi ayarla.",
        ],
    }


SWIMMING_TOOLS = (calculate_css, generate_swim_workout)