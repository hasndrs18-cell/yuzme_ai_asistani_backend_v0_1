from datetime import date
from inspect import isawaitable

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from app.core.auth import AuthenticatedUser, AuthorizationError, LocalTokenVerifier
from app.core.config import get_settings
from app.domain.calculations import calculate_css, compare_performance, create_css_test, readiness_score, session_rpe_load
from app.domain.models import AthleteProfile, PerformanceRecord, ReadinessResult, WellnessRecord
from app.domain.planning import PlanStatus, PlanVersion, TrainingPlan
from app.domain.race_service import RaceInput, RaceResultInput, RaceView
from app.domain.summary import AthleteSummary
from app.domain.repository_factory import get_domain_repository
from app.domain.workout_engine import WorkoutRequest, generate_workout

router = APIRouter(prefix="/domain", tags=["performance-domain"])
_bearer = HTTPBearer(auto_error=False)
_settings = get_settings()
_verifier = LocalTokenVerifier(_settings.auth_secret, _settings.auth_issuer, _settings.auth_audience, _settings.auth_token_lifetime_seconds)

async def repository_call(repository: object, method: str, *args: object) -> object:
    result = getattr(repository, method)(*args)
    return await result if isawaitable(result) else result


async def principal(credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        return _verifier.verify_bearer_token(f"Bearer {credentials.credentials}")
    except Exception as error:
        raise HTTPException(status_code=401, detail="Authentication failed") from error


class AthleteCreateRequest(BaseModel):
    organization_id: str
    team_id: str
    display_name: str
    age: int | None = Field(default=None, ge=1, le=120)
    height_cm: float | None = Field(default=None, gt=0)
    weight_kg: float | None = Field(default=None, gt=0)
    swimming_age_years: float | None = Field(default=None, ge=0)
    dominant_stroke: str | None = None
    main_event: str | None = None
    goals: list[str] = []
    consent_health_data: bool = False


class CssRequest(BaseModel):
    athlete_id: str
    tested_on: date
    pool_length_m: int = Field(gt=0, le=100)
    time_200_seconds: float = Field(gt=0)
    time_400_seconds: float = Field(gt=0)


class LoadRequest(BaseModel):
    duration_minutes: int = Field(gt=0)
    rpe: int = Field(ge=0, le=10)


class PerformanceCreateRequest(BaseModel):
    athlete_id: str
    recorded_on: date
    distance_m: int = Field(gt=0)
    stroke: str
    time_seconds: float = Field(gt=0)


class WellnessCreateRequest(BaseModel):
    athlete_id: str
    recorded_on: date
    heart_rate_bpm: float | None = Field(default=None, ge=20, le=240)
    hrmax_bpm: float | None = Field(default=None, ge=80, le=250)
    resting_hr_bpm: float | None = Field(default=None, ge=20, le=150)
    hrv_ms: float | None = Field(default=None, ge=1, le=300)
    sleep_hours: float | None = Field(default=None, ge=0, le=24)
    fatigue: int | None = Field(default=None, ge=0, le=10)
    soreness: int | None = Field(default=None, ge=0, le=10)
    stress: int | None = Field(default=None, ge=0, le=10)
    mood: int | None = Field(default=None, ge=0, le=10)
    rpe: int | None = Field(default=None, ge=0, le=10)


class PlanCreateRequest(BaseModel):
    organization_id: str
    team_id: str
    athlete_id: str
    goal: str
    event: str
    race_date: date | None = None
    rationale: list[str] = []
    workouts: list[dict[str, object]] = []


class PlanTransitionRequest(BaseModel):
    version: int = Field(default=1, ge=1)
    note: str | None = None


class PlanPatchRequest(BaseModel):
    expected_version: int = Field(ge=1)
    goal: str | None = None
    event: str | None = None
    race_date: date | None = None
    rationale: list[str] = []
    workouts: list[dict[str, object]] = []


class RaceCreateRequest(RaceInput):
    athlete_id: str
    organization_id: str
    team_id: str


@router.post("/athletes", response_model=AthleteProfile, status_code=201)
async def create_athlete(payload: AthleteCreateRequest, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> AthleteProfile:
    athlete = AthleteProfile(**payload.model_dump())
    try:
        return await repository_call(repository, "add_athlete", user, athlete)
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Athlete profile creation is restricted") from error


@router.get("/athletes/{athlete_id}", response_model=AthleteProfile)
async def get_athlete(athlete_id: str, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> AthleteProfile:
    try:
        return await repository_call(repository, "get_athlete", user, athlete_id)
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Athlete access denied") from error


@router.get("/athletes/{athlete_id}/summary", response_model=AthleteSummary)
async def athlete_summary(athlete_id: str, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> AthleteSummary:
    try:
        return await repository_call(repository, "get_summary", user, athlete_id)
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Athlete summary access denied") from error


@router.get("/athletes/{athlete_id}/training-load")
async def athlete_training_load(athlete_id: str, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> object:
    try:
        return await repository_call(repository, "get_training_load", user, athlete_id)
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Training load access denied") from error


@router.get("/athletes/{athlete_id}/today-workout")
async def today_workout(athlete_id: str, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> object:
    try:
        return await repository_call(repository, "get_today_workout", user, athlete_id)
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Workout access denied") from error


@router.get("/athletes/{athlete_id}/performance/summary")
async def performance_summary(athlete_id: str, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> object:
    try:
        return await repository_call(repository, "get_performance_summary", user, athlete_id)
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Performance access denied") from error


@router.get("/athletes/{athlete_id}/recovery")
async def recovery_summary(athlete_id: str, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> object:
    try:
        return await repository_call(repository, "get_recovery", user, athlete_id)
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Recovery access denied") from error


@router.post("/css/calculate")
async def css_calculate(payload: CssRequest, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> dict[str, object]:
    try:
        await repository_call(repository, "get_athlete", user, payload.athlete_id)
        test = create_css_test(**payload.model_dump())
        result = calculate_css(payload.time_200_seconds, payload.time_400_seconds)
        return {"test": test.model_dump(mode="json"), "result": {"css_pace_100m": result.pace_100_seconds, "css_pace_50m": result.pace_50_seconds, "EN1": result.en1_seconds, "EN2": result.en2_seconds, "EN3": result.en3_seconds}, "note": test.scientific_note}
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Athlete access denied") from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post("/performance", response_model=PerformanceRecord, status_code=201)
async def add_performance(payload: PerformanceCreateRequest, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> PerformanceRecord:
    try:
        return await repository_call(repository, "add_performance", user, PerformanceRecord(**payload.model_dump()))
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Athlete access denied") from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post("/wellness", response_model=WellnessRecord, status_code=201)
async def add_wellness(payload: WellnessCreateRequest, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> WellnessRecord:
    try:
        return await repository_call(repository, "add_wellness", user, WellnessRecord(**payload.model_dump()))
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Health data access denied") from error


@router.post("/load/session")
async def calculate_load(payload: LoadRequest, _: AuthenticatedUser = Depends(principal)) -> dict[str, int]:
    return {"session_rpe_load": session_rpe_load(payload.duration_minutes, payload.rpe)}


@router.post("/workouts/generate")
async def generate_team_workout(payload: WorkoutRequest, user: AuthenticatedUser = Depends(principal)) -> dict[str, object]:
    if user.role.value not in {"ADMIN", "COACH", "ASSISTANT_COACH", "TEAM_MANAGER"}:
        raise HTTPException(status_code=403, detail="Workout generation is restricted to coaching roles")
    try:
        workout = generate_workout(payload)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return workout.model_dump(mode="json")


@router.post("/readiness/{athlete_id}", response_model=ReadinessResult)
async def readiness(athlete_id: str, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> ReadinessResult:
    try:
        await repository_call(repository, "get_athlete", user, athlete_id)
        wellness = await repository_call(repository, "get_wellness", user, athlete_id)
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Athlete access denied") from error
    if not wellness:
        raise HTTPException(status_code=422, detail="Readiness için wellness verisi yetersiz")
    return readiness_score(wellness[-1], recent_load=0)


@router.get("/readiness/{athlete_id}", response_model=ReadinessResult)
async def readiness_get(athlete_id: str, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> ReadinessResult:
    return await readiness(athlete_id, user, repository)


@router.get("/performance/{athlete_id}/timeline")
async def performance_timeline(athlete_id: str, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> dict[str, object]:
    try:
        records = await repository_call(repository, "get_performances", user, athlete_id)
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Athlete access denied") from error
    return compare_performance(records)


@router.post("/plans", response_model=TrainingPlan, status_code=201)
async def create_plan(payload: PlanCreateRequest, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> TrainingPlan:
    plan = TrainingPlan(**payload.model_dump(exclude={"rationale", "workouts"}))
    version = PlanVersion(plan_id=plan.plan_id, version=1, created_by=user.user_id, rationale=payload.rationale, workouts=payload.workouts)
    try:
        return await repository_call(repository, "create_plan", user, plan, version)
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Plan creation denied") from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get("/plans", response_model=list[TrainingPlan])
async def list_plans(athlete_id: str | None = None, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> list[TrainingPlan]:
    try:
        return await repository_call(repository, "list_plans", user, athlete_id)
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Plan access denied") from error


@router.get("/plans/{plan_id}", response_model=TrainingPlan)
async def get_plan(plan_id: str, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> TrainingPlan:
    try:
        return await repository_call(repository, "get_plan", user, plan_id)
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Plan access denied") from error


@router.get("/plans/{plan_id}/versions", response_model=list[PlanVersion])
async def get_plan_versions(plan_id: str, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> list[PlanVersion]:
    try:
        return await repository_call(repository, "get_plan_versions", user, plan_id)
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Plan access denied") from error


@router.patch("/plans/{plan_id}", response_model=TrainingPlan)
async def edit_plan(plan_id: str, payload: PlanPatchRequest, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> TrainingPlan:
    try:
        return await repository_call(repository, "edit_plan", user, plan_id, payload.expected_version, payload.goal, payload.event, payload.race_date, payload.rationale, payload.workouts)
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Plan edit denied") from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("/plans/{plan_id}/versions/{version_a}/diff/{version_b}")
async def diff_plan_versions(plan_id: str, version_a: int, version_b: int, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> dict[str, object]:
    try:
        return await repository_call(repository, "plan_version_diff", user, plan_id, version_a, version_b)
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Plan access denied") from error
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/plans/{plan_id}/approve", response_model=TrainingPlan)
async def approve_plan(plan_id: str, payload: PlanTransitionRequest, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> TrainingPlan:
    try:
        return await repository_call(repository, "transition_plan", user, plan_id, PlanStatus.APPROVED, payload.version, payload.note)
    except (AuthorizationError, ValueError) as error:
        raise HTTPException(status_code=403 if isinstance(error, AuthorizationError) else 422, detail=str(error)) from error


@router.post("/plans/{plan_id}/activate", response_model=TrainingPlan)
async def activate_plan(plan_id: str, payload: PlanTransitionRequest, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> TrainingPlan:
    try:
        return await repository_call(repository, "transition_plan", user, plan_id, PlanStatus.ACTIVE, payload.version, payload.note)
    except (AuthorizationError, ValueError) as error:
        raise HTTPException(status_code=403 if isinstance(error, AuthorizationError) else 422, detail=str(error)) from error


@router.post("/plans/{plan_id}/reject", response_model=TrainingPlan)
async def reject_plan(plan_id: str, payload: PlanTransitionRequest, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> TrainingPlan:
    try:
        return await repository_call(repository, "transition_plan", user, plan_id, PlanStatus.DRAFT, payload.version, payload.note)
    except (AuthorizationError, ValueError) as error:
        raise HTTPException(status_code=403 if isinstance(error, AuthorizationError) else 422, detail=str(error)) from error


@router.post("/plans/{plan_id}/complete", response_model=TrainingPlan)
async def complete_plan(plan_id: str, payload: PlanTransitionRequest, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> TrainingPlan:
    try:
        return await repository_call(repository, "transition_plan", user, plan_id, PlanStatus.COMPLETED, payload.version, payload.note)
    except (AuthorizationError, ValueError) as error:
        raise HTTPException(status_code=403 if isinstance(error, AuthorizationError) else 422, detail=str(error)) from error


@router.post("/plans/{plan_id}/archive", response_model=TrainingPlan)
async def archive_plan(plan_id: str, payload: PlanTransitionRequest, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> TrainingPlan:
    try:
        return await repository_call(repository, "transition_plan", user, plan_id, PlanStatus.ARCHIVED, payload.version, payload.note)
    except (AuthorizationError, ValueError) as error:
        raise HTTPException(status_code=403 if isinstance(error, AuthorizationError) else 422, detail=str(error)) from error


@router.post("/races", response_model=RaceView, status_code=201)
async def create_race(payload: RaceCreateRequest, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> RaceView:
    try:
        return await repository_call(repository, "create_race", user, RaceInput(**payload.model_dump(exclude={"athlete_id", "organization_id", "team_id"})), payload.athlete_id, payload.organization_id, payload.team_id)
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Race access denied") from error


@router.get("/races", response_model=list[RaceView])
async def list_races(athlete_id: str | None = None, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> list[RaceView]:
    try:
        return await repository_call(repository, "list_races", user, athlete_id)
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Race access denied") from error


@router.get("/races/{race_id}", response_model=RaceView)
async def get_race(race_id: str, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> RaceView:
    try:
        return await repository_call(repository, "get_race", user, race_id)
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Race access denied") from error


@router.post("/races/{race_id}/result", response_model=RaceView)
async def add_race_result(race_id: str, payload: RaceResultInput, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> RaceView:
    try:
        return await repository_call(repository, "add_race_result", user, race_id, payload)
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Race access denied") from error


@router.get("/races/{race_id}/analysis")
async def analyze_race(race_id: str, user: AuthenticatedUser = Depends(principal), repository: object = Depends(get_domain_repository)) -> dict[str, object]:
    try:
        return await repository_call(repository, "analyze_race", user, race_id)
    except AuthorizationError as error:
        raise HTTPException(status_code=403, detail="Race access denied") from error
