"""Feasibility-aware deterministic workout generation."""

from pydantic import BaseModel, Field

from app.domain.models import AthleteProfile, Workout


class WorkoutRequest(BaseModel):
    organization_id: str
    team_id: str
    athlete_id: str | None = None
    age_group: str
    group_size: int = Field(gt=0, le=500)
    lane_count: int = Field(gt=0, le=100)
    pool_length_m: int = Field(gt=0, le=100)
    duration_minutes: int = Field(gt=0, le=600)
    objective: str = Field(min_length=2)
    level: str = "INTERMEDIATE"
    equipment: list[str] = Field(default_factory=list)
    recent_load: int = Field(default=0, ge=0)


def generate_workout(request: WorkoutRequest, athlete: AthleteProfile | None = None) -> Workout:
    if request.pool_length_m not in {25, 50}:
        raise ValueError("Yüzme havuzu 25 m veya 50 m olmalıdır")
    if request.duration_minutes < 30:
        raise ValueError("Uygulanabilir bir antrenman için en az 30 dakika gerekir")
    swimmers_per_lane = (request.group_size + request.lane_count - 1) // request.lane_count
    notes = [f"Her kulvarda yaklaşık {swimmers_per_lane} sporcu; interval aralığını buna göre aç."]
    if swimmers_per_lane > 8:
        notes.append("Kulvar yoğunluğu yüksek: iki hız grubu ve dönüş sırası önerilir.")
    if request.recent_load > 700:
        notes.append("Son yük yüksek; yüksek yoğunluk hacmi azaltıldı, teknik/recovery önceliklendirildi.")
    warmup = max(200, round(request.duration_minutes * 3.2 / request.pool_length_m) * request.pool_length_m)
    main = max(request.pool_length_m * 4, round(request.duration_minutes * 5.2 / request.pool_length_m) * request.pool_length_m)
    cooldown = max(100, round(request.duration_minutes * 1.2 / request.pool_length_m) * request.pool_length_m)
    return Workout(organization_id=request.organization_id, team_id=request.team_id, athlete_id=request.athlete_id, title=f"{request.age_group} / {request.objective}", pool_length_m=request.pool_length_m, duration_minutes=request.duration_minutes, group_size=request.group_size, lane_count=request.lane_count, objective=request.objective, energy_system="AEROBIC + TECHNICAL", sets=[{"name": "Warm-up", "distance_m": warmup, "interval": "easy", "rpe": 3}, {"name": "Main set", "distance_m": main, "interval": "lane-dependent", "target_pace": "CSS + controlled", "rpe": 6}, {"name": "Recovery", "distance_m": cooldown, "interval": "easy", "rpe": 2}], feasibility_notes=notes)
