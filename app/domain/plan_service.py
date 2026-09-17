from app.core.auth import AuthenticatedUser, AuthorizationError
from app.domain.planning import PlanApproval, PlanStatus, PlanVersion, TrainingPlan


class PlanService:
    def __init__(self) -> None:
        self.plans: dict[str, TrainingPlan] = {}
        self.versions: dict[str, list[PlanVersion]] = {}

    def create_draft(self, principal: AuthenticatedUser, plan: TrainingPlan, version: PlanVersion) -> TrainingPlan:
        if principal.role.value not in {"COACH", "ASSISTANT_COACH", "TEAM_MANAGER", "ADMIN"}:
            raise AuthorizationError("Only coaching roles can create plans")
        if version.status is not PlanStatus.DRAFT or plan.status is not PlanStatus.DRAFT:
            raise ValueError("AI plan must start as DRAFT")
        self.plans[plan.plan_id] = plan
        self.versions[plan.plan_id] = [version]
        return plan

    def approve(self, principal: AuthenticatedUser, approval: PlanApproval) -> TrainingPlan:
        if principal.role.value not in {"COACH", "TEAM_MANAGER", "ADMIN"}:
            raise AuthorizationError("Only coach roles can approve plans")
        plan = self.plans.get(approval.plan_id)
        if plan is None:
            raise ValueError("Plan not found")
        version = next((item for item in self.versions[plan.plan_id] if item.version == approval.version), None)
        if version is None:
            raise ValueError("Plan version not found")
        if not approval.approved:
            plan.status = PlanStatus.DRAFT
            version.status = PlanStatus.DRAFT
            return plan
        plan.status = PlanStatus.ACTIVE
        plan.current_version = version.version
        version.status = PlanStatus.APPROVED
        return plan

    def revise(self, principal: AuthenticatedUser, plan_id: str, rationale: list[str], workouts: list[dict[str, object]]) -> PlanVersion:
        if principal.role.value not in {"COACH", "ASSISTANT_COACH", "TEAM_MANAGER", "ADMIN"}:
            raise AuthorizationError("Plan revision denied")
        if plan_id not in self.plans:
            raise ValueError("Plan not found")
        version = PlanVersion(plan_id=plan_id, version=len(self.versions[plan_id]) + 1, created_by=principal.user_id, rationale=rationale, workouts=workouts)
        self.versions[plan_id].append(version)
        self.plans[plan_id].status = PlanStatus.DRAFT
        self.plans[plan_id].current_version = version.version
        return version
