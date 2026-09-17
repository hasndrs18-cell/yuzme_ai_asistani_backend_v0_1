"""Async PostgreSQL repository with transaction-scoped writes and tenant checks."""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthenticatedUser, AuthorizationError
from app.db.models import Athlete, AuditEntry as DbAuditEntry, GuardianRelationship, PerformanceRecord as DbPerformance, PlanVersion as DbPlanVersion, TeamMembership, TrainingPlan as DbTrainingPlan, WellnessRecord as DbWellness, WorkoutAssignment as DbWorkoutAssignment, Workout as DbWorkout, TrainingSession as DbTrainingSession
from app.domain.models import AthleteProfile, PerformanceRecord, WellnessRecord
from app.domain.planning import PlanStatus, PlanVersion, TrainingPlan
from app.domain.race_service import RaceInput, RaceResultInput, RaceStatus, RaceView
from app.domain.summary import AthleteSummary, RecoverySummary, TrainingLoadSummary
from app.db.models import Race as DbRace


class PostgresDomainRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_athlete(self, principal: AuthenticatedUser, profile: AthleteProfile) -> AthleteProfile:
        if principal.role.value not in {"ADMIN", "COACH", "ASSISTANT_COACH", "TEAM_MANAGER"}:
            raise AuthorizationError("Athlete profile creation is restricted")
        row = Athlete(id=profile.athlete_id, organization_id=profile.organization_id, team_id=profile.team_id, display_name=profile.display_name, birth_date=profile.birth_date, height_cm=profile.height_cm, weight_kg=profile.weight_kg, swimming_age_years=profile.swimming_age_years, dominant_stroke=profile.dominant_stroke, main_event=profile.main_event, goals=profile.goals, consent_health_data=profile.consent_health_data)
        self.session.add(row)
        self.session.add(DbAuditEntry(organization_id=profile.organization_id, actor_id=principal.user_id, action="ATHLETE_CREATED", resource_type="athlete", resource_id=profile.athlete_id))
        await self.session.commit()
        return profile

    async def _athlete(self, principal: AuthenticatedUser, athlete_id: str) -> Athlete:
        row = await self.session.get(Athlete, athlete_id)
        if row is None:
            raise AuthorizationError("Athlete access denied")
        if principal.role.value == "ADMIN":
            return row

        if principal.role.value in {"ATHLETE", "STUDENT"}:
            allowed = row.id == principal.student_id and (row.user_id is None or row.user_id == principal.user_id)
        elif principal.role.value == "GUARDIAN":
            allowed = await self.session.scalar(
                select(GuardianRelationship.id).where(
                    GuardianRelationship.guardian_user_id == principal.user_id,
                    GuardianRelationship.athlete_id == row.id,
                    GuardianRelationship.status == "ACTIVE",
                )
            ) is not None
        else:
            allowed = await self.session.scalar(
                select(TeamMembership.id).where(
                    TeamMembership.user_id == principal.user_id,
                    TeamMembership.team_id == row.team_id,
                    TeamMembership.organization_id == row.organization_id,
                    TeamMembership.role == principal.role.value,
                    TeamMembership.status == "ACTIVE",
                )
            ) is not None

        if not allowed:
            raise AuthorizationError("Athlete access denied")
        return row

    async def get_athlete(self, principal: AuthenticatedUser, athlete_id: str) -> AthleteProfile:
        row = await self._athlete(principal, athlete_id)
        return AthleteProfile(athlete_id=row.id, organization_id=row.organization_id, team_id=row.team_id, display_name=row.display_name, birth_date=row.birth_date, height_cm=row.height_cm, weight_kg=row.weight_kg, swimming_age_years=row.swimming_age_years, dominant_stroke=row.dominant_stroke, main_event=row.main_event, goals=row.goals or [], consent_health_data=row.consent_health_data, created_at=row.created_at, updated_at=row.updated_at)

    async def add_performance(self, principal: AuthenticatedUser, record: PerformanceRecord) -> PerformanceRecord:
        athlete = await self._athlete(principal, record.athlete_id)
        row = DbPerformance(organization_id=athlete.organization_id, athlete_id=record.athlete_id, record_date=record.recorded_on, distance_m=record.distance_m, stroke=record.stroke, time_seconds=record.time_seconds, source=record.source.value, metrics=record.metrics.model_dump())
        self.session.add(row)
        self.session.add(DbAuditEntry(organization_id=athlete.organization_id, actor_id=principal.user_id, action="PERFORMANCE_CREATED", resource_type="performance", resource_id=record.record_id))
        await self.session.commit()
        return record

    async def add_wellness(self, principal: AuthenticatedUser, record: WellnessRecord) -> WellnessRecord:
        athlete = await self._athlete(principal, record.athlete_id)
        if not athlete.consent_health_data and principal.role.value != "ADMIN":
            raise AuthorizationError("Health data consent is required")
        self.session.add(DbWellness(organization_id=athlete.organization_id, athlete_id=record.athlete_id, record_date=record.recorded_on, payload=record.model_dump()))
        self.session.add(DbAuditEntry(organization_id=athlete.organization_id, actor_id=principal.user_id, action="HEALTH_DATA_CREATED", resource_type="wellness", resource_id=f"{record.athlete_id}:{record.recorded_on}"))
        await self.session.commit()
        return record

    async def get_performances(self, principal: AuthenticatedUser, athlete_id: str) -> list[PerformanceRecord]:
        await self._athlete(principal, athlete_id)
        rows = (await self.session.scalars(select(DbPerformance).where(DbPerformance.athlete_id == athlete_id).order_by(DbPerformance.record_date))).all()
        return [PerformanceRecord(record_id=row.id, athlete_id=row.athlete_id, recorded_on=row.record_date, distance_m=row.distance_m, stroke=row.stroke, time_seconds=row.time_seconds, source=row.source, metrics=row.metrics or {}) for row in rows]

    async def get_wellness(self, principal: AuthenticatedUser, athlete_id: str) -> list[WellnessRecord]:
        await self._athlete(principal, athlete_id)
        rows = (await self.session.scalars(select(DbWellness).where(DbWellness.athlete_id == athlete_id).order_by(DbWellness.record_date))).all()
        return [WellnessRecord(athlete_id=row.athlete_id, recorded_on=row.record_date, **{key: value for key, value in (row.payload or {}).items() if key != "athlete_id" and key != "recorded_on"}) for row in rows]

    async def get_training_load(self, principal: AuthenticatedUser, athlete_id: str) -> TrainingLoadSummary | None:
        await self._athlete(principal, athlete_id)
        today = date.today()
        rows = (await self.session.scalars(select(DbTrainingSession).where(DbTrainingSession.athlete_id == athlete_id, DbTrainingSession.session_date >= today - timedelta(days=27)).order_by(DbTrainingSession.session_date))).all()
        if not rows:
            return None
        seven = sum(row.load for row in rows if row.session_date >= today - timedelta(days=6))
        twenty_eight = sum(row.load for row in rows)
        return TrainingLoadSummary(daily=next((row.load for row in reversed(rows) if row.session_date == today), None), seven_day=seven, twenty_eight_day=twenty_eight, trend="HIGH" if seven > 700 else "MODERATE")

    async def get_active_plan(self, principal: AuthenticatedUser, athlete_id: str) -> TrainingPlan | None:
        await self._athlete(principal, athlete_id)
        row = (await self.session.scalars(select(DbTrainingPlan).where(DbTrainingPlan.athlete_id == athlete_id, DbTrainingPlan.status == PlanStatus.ACTIVE.value).order_by(DbTrainingPlan.updated_at.desc()))).first()
        return self._to_plan(row) if row else None

    async def get_next_race(self, principal: AuthenticatedUser, athlete_id: str) -> RaceView | None:
        await self._athlete(principal, athlete_id)
        row = (await self.session.scalars(select(DbRace).where(DbRace.athlete_id == athlete_id, DbRace.race_date >= date.today()).order_by(DbRace.race_date))).first()
        return self._to_race(row) if row else None

    async def get_summary(self, principal: AuthenticatedUser, athlete_id: str) -> AthleteSummary:
        athlete = await self.get_athlete(principal, athlete_id)
        wellness = await self.get_wellness(principal, athlete_id)
        training_load = await self.get_training_load(principal, athlete_id)
        readiness = None
        recovery = None
        if wellness:
            latest = wellness[-1]
            readiness = readiness_score(latest, recent_load=training_load.seven_day if training_load and training_load.seven_day is not None else 0)
            available = [name for name, value in (("Sleep", latest.sleep_hours), ("HRV", latest.hrv_ms), ("Resting HR", latest.resting_hr_bpm), ("Fatigue", latest.fatigue), ("Soreness", latest.soreness), ("Stress", latest.stress)) if value is not None]
            missing = [name for name in ("Sleep", "HRV", "Resting HR", "Fatigue", "Soreness", "Stress") if name not in available]
            recovery = RecoverySummary(score=readiness.score if len(available) >= 2 else None, latest_recorded_at=datetime.combine(latest.recorded_on, datetime.min.time(), tzinfo=timezone.utc), available_signals=available, missing_signals=missing)
        performances = await self.get_performances(principal, athlete_id)
        return AthleteSummary(athlete=athlete, readiness=readiness, recovery=recovery, training_load=training_load, performance_trend=compare_performance(performances) if performances else None, active_plan=await self.get_active_plan(principal, athlete_id), next_race=await self.get_next_race(principal, athlete_id), technical_development=None, generated_at=datetime.now(timezone.utc))

    async def get_today_workout(self, principal: AuthenticatedUser, athlete_id: str) -> dict[str, object]:
        plan = await self.get_active_plan(principal, athlete_id)
        if plan is None:
            return {"status": "NO_WORKOUT", "plan_id": None, "workout": None}
        version = (await self.get_plan_versions(principal, plan.plan_id))[-1:]
        workouts = version[0].workouts if version else []
        if not workouts:
            return {"status": "NO_WORKOUT", "plan_id": plan.plan_id, "workout": None}
        workout = workouts[0]
        workout_date = workout.get("date") or workout.get("session_date")
        if workout_date != date.today().isoformat():
            return {"status": "NO_WORKOUT", "plan_id": plan.plan_id, "workout": None}
        return {"status": "PLAN_AVAILABLE", "plan_id": plan.plan_id, "workout": workout, "coach_notes": version[0].rationale if version else []}

    async def get_performance_summary(self, principal: AuthenticatedUser, athlete_id: str) -> dict[str, object]:
        records = await self.get_performances(principal, athlete_id)
        trend = compare_performance(records) if records else None
        return {"recent": [record.model_dump(mode="json") for record in records[-5:]], "trend": trend, "PB": min((record.time_seconds for record in records), default=None), "SB": min((record.time_seconds for record in records if record.season), default=None)}

    async def get_recovery(self, principal: AuthenticatedUser, athlete_id: str) -> RecoverySummary | None:
        summary = await self.get_summary(principal, athlete_id)
        return summary.recovery

    async def create_plan(self, principal: AuthenticatedUser, plan: TrainingPlan, version: PlanVersion) -> TrainingPlan:
        if principal.role.value not in {"ADMIN", "COACH", "ASSISTANT_COACH", "TEAM_MANAGER"}:
            raise AuthorizationError("Plan creation denied")
        athlete = await self._athlete(principal, plan.athlete_id)
        if version.plan_id != plan.plan_id or version.version != 1 or plan.status is not PlanStatus.DRAFT:
            raise ValueError("New plans must begin as version 1 DRAFT")
        self.session.add(DbTrainingPlan(id=plan.plan_id, organization_id=athlete.organization_id, team_id=plan.team_id, athlete_id=plan.athlete_id, goal=plan.goal, event=plan.event, race_date=plan.race_date, status=plan.status.value, current_version=1))
        self.session.add(DbPlanVersion(id=version.version_id, plan_id=plan.plan_id, version=1, created_by=principal.user_id, status=version.status.value, rationale=version.rationale, workouts=version.workouts))
        self.session.add(DbAuditEntry(organization_id=athlete.organization_id, actor_id=principal.user_id, action="PLAN_CREATED", resource_type="plan", resource_id=plan.plan_id, metadata_json={"version": 1, "status": "DRAFT"}))
        await self.session.commit()
        return plan

    async def _plan(self, principal: AuthenticatedUser, plan_id: str) -> DbTrainingPlan:
        row = await self.session.get(DbTrainingPlan, plan_id)
        if row is None:
            raise AuthorizationError("Plan access denied")
        await self._athlete(principal, row.athlete_id)
        return row

    @staticmethod
    def _to_plan(row: DbTrainingPlan) -> TrainingPlan:
        return TrainingPlan(plan_id=row.id, organization_id=row.organization_id, team_id=row.team_id, athlete_id=row.athlete_id, goal=row.goal, event=row.event, race_date=row.race_date, status=PlanStatus(row.status), current_version=row.current_version, created_at=row.created_at, updated_at=row.updated_at)

    async def get_plan(self, principal: AuthenticatedUser, plan_id: str) -> TrainingPlan:
        return self._to_plan(await self._plan(principal, plan_id))

    async def list_plans(self, principal: AuthenticatedUser, athlete_id: str | None = None) -> list[TrainingPlan]:
        if athlete_id:
            await self._athlete(principal, athlete_id)
            rows = (await self.session.scalars(select(DbTrainingPlan).where(DbTrainingPlan.athlete_id == athlete_id).order_by(DbTrainingPlan.created_at.desc()))).all()
        elif principal.role.value == "ADMIN":
            rows = (await self.session.scalars(select(DbTrainingPlan).order_by(DbTrainingPlan.created_at.desc()))).all()
        else:
            rows = []
            for student_id in principal.authorized_student_ids | ({principal.student_id} if principal.student_id else set()):
                rows.extend((await self.session.scalars(select(DbTrainingPlan).where(DbTrainingPlan.athlete_id == student_id))).all())
        return [self._to_plan(row) for row in rows]

    async def get_plan_versions(self, principal: AuthenticatedUser, plan_id: str) -> list[PlanVersion]:
        await self._plan(principal, plan_id)
        rows = (await self.session.scalars(select(DbPlanVersion).where(DbPlanVersion.plan_id == plan_id).order_by(DbPlanVersion.version))).all()
        return [PlanVersion(version_id=row.id, plan_id=row.plan_id, version=row.version, created_by=row.created_by or "unknown", rationale=row.rationale or [], workouts=row.workouts or [], status=PlanStatus(row.status), created_at=row.created_at) for row in rows]

    async def edit_plan(self, principal: AuthenticatedUser, plan_id: str, expected_version: int, goal: str | None, event: str | None, race_date: object, rationale: list[str], workouts: list[dict[str, object]]) -> TrainingPlan:
        if principal.role.value not in {"ADMIN", "COACH", "ASSISTANT_COACH", "TEAM_MANAGER"}:
            raise AuthorizationError("Plan edit denied")
        row = await self._plan(principal, plan_id)
        if row.status in {PlanStatus.COMPLETED.value, PlanStatus.ARCHIVED.value}:
            raise ValueError("Completed or archived plans cannot be edited")
        if row.current_version != expected_version:
            raise ValueError(f"Plan version conflict: expected {expected_version}, current {row.current_version}")
        athlete = await self._athlete(principal, row.athlete_id)
        next_version = row.current_version + 1
        version = DbPlanVersion(plan_id=plan_id, version=next_version, created_by=principal.user_id, status=PlanStatus.DRAFT.value, rationale=rationale, workouts=workouts)
        if goal is not None:
            row.goal = goal
        if event is not None:
            row.event = event
        if race_date is not None:
            row.race_date = race_date
        previous_status = row.status
        row.current_version = next_version
        row.status = PlanStatus.DRAFT.value
        self.session.add(version)
        self.session.add(DbAuditEntry(organization_id=athlete.organization_id, actor_id=principal.user_id, action="PLAN_VERSION_CREATED", resource_type="plan", resource_id=plan_id, metadata_json={"previous_version": expected_version, "new_version": next_version, "previous_status": previous_status}))
        await self.session.commit()
        return self._to_plan(row)

    async def plan_version_diff(self, principal: AuthenticatedUser, plan_id: str, version_a: int, version_b: int) -> dict[str, object]:
        await self._plan(principal, plan_id)
        rows = (await self.session.scalars(select(DbPlanVersion).where(DbPlanVersion.plan_id == plan_id, DbPlanVersion.version.in_([version_a, version_b])))).all()
        by_version = {row.version: row for row in rows}
        if version_a not in by_version or version_b not in by_version:
            raise ValueError("Plan versions not found")
        left, right = by_version[version_a], by_version[version_b]
        changes = {}
        if (left.rationale or []) != (right.rationale or []):
            changes["coach_notes"] = {"from": left.rationale or [], "to": right.rationale or []}
        if (left.workouts or []) != (right.workouts or []):
            changes["workouts"] = {"from": left.workouts or [], "to": right.workouts or []}
        return {"plan_id": plan_id, "from_version": version_a, "to_version": version_b, "changes": changes}

    async def assign_workout(self, principal: AuthenticatedUser, plan_id: str, workout_id: str, athlete_id: str | None, team_id: str | None) -> dict[str, object]:
        if principal.role.value not in {"ADMIN", "COACH", "ASSISTANT_COACH", "TEAM_MANAGER"}:
            raise AuthorizationError("Workout assignment denied")
        plan = await self._plan(principal, plan_id)
        if athlete_id:
            await self._athlete(principal, athlete_id)
        workout = await self.session.get(DbWorkout, workout_id)
        if workout is None or workout.organization_id != plan.organization_id:
            raise AuthorizationError("Workout assignment denied")
        assignment = DbWorkoutAssignment(plan_id=plan_id, workout_id=workout_id, athlete_id=athlete_id, team_id=team_id, assigned_by=principal.user_id)
        self.session.add(assignment)
        await self.session.commit()
        return {"assignment_id": assignment.id, "plan_id": plan_id, "workout_id": workout_id, "athlete_id": athlete_id, "team_id": team_id}

    async def transition_plan(self, principal: AuthenticatedUser, plan_id: str, target: PlanStatus, version: int = 1, note: str | None = None) -> TrainingPlan:
        if principal.role.value not in {"ADMIN", "COACH", "TEAM_MANAGER"}:
            raise AuthorizationError("Plan transition denied")
        row = await self._plan(principal, plan_id)
        current = PlanStatus(row.status)
        if row.current_version != version:
            raise ValueError(f"Plan version conflict: expected {version}, current {row.current_version}")
        allowed = {(PlanStatus.DRAFT, PlanStatus.APPROVED), (PlanStatus.PENDING_REVIEW, PlanStatus.APPROVED), (PlanStatus.PENDING_REVIEW, PlanStatus.DRAFT), (PlanStatus.APPROVED, PlanStatus.DRAFT), (PlanStatus.APPROVED, PlanStatus.ACTIVE), (PlanStatus.DRAFT, PlanStatus.ARCHIVED), (PlanStatus.ACTIVE, PlanStatus.COMPLETED), (PlanStatus.COMPLETED, PlanStatus.ARCHIVED)}
        if (current, target) not in allowed:
            raise ValueError(f"Invalid plan transition: {current.value} -> {target.value}")
        athlete = await self._athlete(principal, row.athlete_id)
        previous = row.status
        row.status = target.value
        self.session.add(DbAuditEntry(organization_id=athlete.organization_id, actor_id=principal.user_id, action="PLAN_STATUS_CHANGED", resource_type="plan", resource_id=plan_id, metadata_json={"version": version, "previous_status": previous, "new_status": target.value, "note": note}))
        await self.session.commit()
        return self._to_plan(row)

    @staticmethod
    def _to_race(row: DbRace) -> RaceView:
        payload = row.payload or {}
        result = payload.get("result")
        return RaceView(race_id=row.id, athlete_id=row.athlete_id, name=payload.get("name", row.event), date=row.race_date, location=payload.get("location", ""), pool_type=payload.get("pool_type", ""), distance_m=payload.get("distance_m", 0), event=row.event, stroke=row.stroke, priority=row.priority, target_time=row.target_seconds, actual_time=row.actual_seconds, status=RaceStatus(payload.get("status", "PLANNED")), result=RaceResultInput(**result) if result else None)

    async def create_race(self, principal: AuthenticatedUser, race: RaceInput, athlete_id: str, organization_id: str, team_id: str) -> RaceView:
        athlete = await self._athlete(principal, athlete_id)
        if athlete.organization_id != organization_id or athlete.team_id != team_id:
            raise AuthorizationError("Race tenant scope mismatch")
        row = DbRace(id=str(uuid4()), organization_id=organization_id, athlete_id=athlete_id, race_date=race.date, event=race.event, stroke=race.stroke, priority=race.priority.value, target_seconds=race.target_time, payload={"name": race.name, "location": race.location, "pool_type": race.pool_type, "distance_m": race.distance_m, "status": race.status.value})
        self.session.add(row)
        self.session.add(DbAuditEntry(organization_id=organization_id, actor_id=principal.user_id, action="RACE_CREATED", resource_type="race", resource_id=row.id))
        await self.session.commit()
        return self._to_race(row)

    async def get_race(self, principal: AuthenticatedUser, race_id: str) -> RaceView:
        row = await self.session.get(DbRace, race_id)
        if row is None:
            raise AuthorizationError("Race access denied")
        await self._athlete(principal, row.athlete_id)
        return self._to_race(row)

    async def list_races(self, principal: AuthenticatedUser, athlete_id: str | None = None) -> list[RaceView]:
        if athlete_id:
            await self._athlete(principal, athlete_id)
            rows = (await self.session.scalars(select(DbRace).where(DbRace.athlete_id == athlete_id).order_by(DbRace.race_date))).all()
        else:
            ids = principal.authorized_student_ids | ({principal.student_id} if principal.student_id else set())
            if principal.role.value == "ADMIN":
                rows = (await self.session.scalars(select(DbRace).order_by(DbRace.race_date))).all()
            else:
                rows = (await self.session.scalars(select(DbRace).where(DbRace.athlete_id.in_(ids)).order_by(DbRace.race_date))).all()
        return [self._to_race(row) for row in rows]

    async def add_race_result(self, principal: AuthenticatedUser, race_id: str, result: RaceResultInput) -> RaceView:
        row = await self.session.get(DbRace, race_id)
        if row is None:
            raise AuthorizationError("Race access denied")
        athlete = await self._athlete(principal, row.athlete_id)
        payload = dict(row.payload or {})
        payload["result"] = result.model_dump(mode="json")
        payload["status"] = RaceStatus.COMPLETED.value
        row.payload = payload
        row.actual_seconds = result.actual_time
        self.session.add(DbAuditEntry(organization_id=athlete.organization_id, actor_id=principal.user_id, action="RACE_RESULT_CREATED", resource_type="race", resource_id=race_id))
        await self.session.commit()
        return self._to_race(row)

    async def analyze_race(self, principal: AuthenticatedUser, race_id: str) -> dict[str, object]:
        race = await self.get_race(principal, race_id)
        performances = await self.get_performances(principal, race.athlete_id)
        same = [item for item in performances if item.distance_m == race.distance_m and item.stroke.lower() == race.stroke.lower()]
        pb = min((item.time_seconds for item in same), default=None)
        sb = min((item.time_seconds for item in same if item.season), default=None)
        result = race.result
        return {"race": race.model_dump(mode="json"), "comparison": {"target": race.target_time, "PB": pb, "SB": sb, "actual": race.actual_time}, "metrics": result.model_dump(mode="json") if result else None, "notes": [] if result and result.splits else ["Split verisi mevcut değil."]}
