import pytest

from app.core.auth import AuthenticatedUser, AuthorizationError, Role
from app.domain.plan_service import PlanService
from app.domain.planning import PlanApproval, PlanStatus, PlanVersion, TrainingPlan


def draft():
    return TrainingPlan(organization_id="org", team_id="team", athlete_id="athlete", goal="PB", event="100 freestyle"), PlanVersion(plan_id="pending", version=1, created_by="coach")


def test_plan_requires_coach_approval_before_active():
    service = PlanService()
    coach = AuthenticatedUser(user_id="coach", role=Role.COACH, authorized_student_ids=frozenset({"athlete"}))
    plan, version = draft()
    version.plan_id = plan.plan_id
    service.create_draft(coach, plan, version)
    assert plan.status is PlanStatus.DRAFT
    service.approve(coach, PlanApproval(plan_id=plan.plan_id, version=1, actor_id="coach", approved=True))
    assert service.plans[plan.plan_id].status is PlanStatus.ACTIVE


def test_athlete_cannot_approve_plan():
    service = PlanService()
    athlete = AuthenticatedUser(user_id="athlete", role=Role.ATHLETE, student_id="athlete")
    plan, version = draft()
    with pytest.raises(AuthorizationError):
        service.create_draft(athlete, plan, version)
