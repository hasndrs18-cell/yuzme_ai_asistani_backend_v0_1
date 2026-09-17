"""Tenant-scoped in-memory repository. Replace the storage adapter with Postgres without changing domain services."""

from collections import defaultdict
from datetime import datetime, timezone

from app.core.auth import AuthenticatedUser, AuthorizationError
from app.domain.models import AthleteProfile, AuditEntry, PerformanceRecord, TrainingSession, WellnessRecord, Workout
from app.domain.calculations import compare_performance, readiness_score
from app.domain.summary import AthleteSummary


class DomainRepository:
    def __init__(self) -> None:
        self.athletes: dict[str, AthleteProfile] = {}
        self.performances: dict[str, list[PerformanceRecord]] = defaultdict(list)
        self.wellness: dict[str, list[WellnessRecord]] = defaultdict(list)
        self.sessions: dict[str, list[TrainingSession]] = defaultdict(list)
        self.workouts: dict[str, Workout] = {}
        self.audit: list[AuditEntry] = []

    def _can_access(self, principal: AuthenticatedUser, athlete: AthleteProfile) -> bool:
        if principal.role.value == "ADMIN":
            return True
        return athlete.athlete_id == principal.student_id or athlete.athlete_id in principal.authorized_student_ids

    def add_athlete(self, principal: AuthenticatedUser, athlete: AthleteProfile) -> AthleteProfile:
        if principal.role.value not in {"ADMIN", "COACH", "ASSISTANT_COACH", "TEAM_MANAGER"}:
            raise AuthorizationError("Athlete profile creation is restricted")
        self.athletes[athlete.athlete_id] = athlete
        self.audit.append(AuditEntry(organization_id=athlete.organization_id, actor_id=principal.user_id, action="ATHLETE_CREATED", resource_type="athlete", resource_id=athlete.athlete_id))
        return athlete

    def get_athlete(self, principal: AuthenticatedUser, athlete_id: str) -> AthleteProfile:
        athlete = self.athletes.get(athlete_id)
        if athlete is None or not self._can_access(principal, athlete):
            raise AuthorizationError("Athlete access denied")
        return athlete

    def add_performance(self, principal: AuthenticatedUser, record: PerformanceRecord) -> PerformanceRecord:
        athlete = self.get_athlete(principal, record.athlete_id)
        if principal.role.value not in {"ADMIN", "COACH", "ASSISTANT_COACH", "TEAM_MANAGER", "ATHLETE"}:
            raise AuthorizationError("Performance write denied")
        duplicate = any(item.recorded_on == record.recorded_on and item.distance_m == record.distance_m and item.stroke == record.stroke and item.time_seconds == record.time_seconds for item in self.performances[record.athlete_id])
        if duplicate:
            raise ValueError("Duplicate performance record")
        self.performances[record.athlete_id].append(record)
        self.audit.append(AuditEntry(organization_id=athlete.organization_id, actor_id=principal.user_id, action="PERFORMANCE_CREATED", resource_type="performance", resource_id=record.record_id))
        return record

    def add_wellness(self, principal: AuthenticatedUser, record: WellnessRecord) -> WellnessRecord:
        athlete = self.get_athlete(principal, record.athlete_id)
        if not athlete.consent_health_data and principal.role.value != "ADMIN":
            raise AuthorizationError("Health data consent is required")
        self.wellness[record.athlete_id].append(record)
        self.audit.append(AuditEntry(organization_id=athlete.organization_id, actor_id=principal.user_id, action="HEALTH_DATA_CREATED", resource_type="wellness", resource_id=f"{record.athlete_id}:{record.recorded_on}"))
        return record

    def get_performances(self, principal: AuthenticatedUser, athlete_id: str) -> list[PerformanceRecord]:
        self.get_athlete(principal, athlete_id)
        return list(self.performances[athlete_id])

    def get_wellness(self, principal: AuthenticatedUser, athlete_id: str) -> list[WellnessRecord]:
        self.get_athlete(principal, athlete_id)
        return list(self.wellness[athlete_id])

    async def get_summary(self, principal: AuthenticatedUser, athlete_id: str) -> AthleteSummary:
        athlete = self.get_athlete(principal, athlete_id)
        wellness = self.get_wellness(principal, athlete_id)
        performances = self.get_performances(principal, athlete_id)
        return AthleteSummary(
            athlete=athlete,
            readiness=readiness_score(wellness[-1], 0) if wellness else None,
            recovery=None,
            training_load=None,
            performance_trend=compare_performance(performances) if performances else None,
            active_plan=None,
            next_race=None,
            technical_development=None,
            generated_at=datetime.now(timezone.utc)
        )

    async def get_today_workout(self, principal: AuthenticatedUser, athlete_id: str) -> dict[str, object]:
        self.get_athlete(principal, athlete_id)
        return {"status": "NO_WORKOUT", "plan_id": None, "workout": None}

    async def get_performance_summary(self, principal: AuthenticatedUser, athlete_id: str) -> dict[str, object]:
        records = self.get_performances(principal, athlete_id)
        return {"recent": [record.model_dump(mode="json") for record in records[-5:]], "trend": compare_performance(records) if records else None, "PB": min((record.time_seconds for record in records), default=None), "SB": min((record.time_seconds for record in records if record.season), default=None)}

    async def get_recovery(self, principal: AuthenticatedUser, athlete_id: str):
        return (await self.get_summary(principal, athlete_id)).recovery
