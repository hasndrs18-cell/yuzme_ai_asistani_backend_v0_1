from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from app.core.auth import AuthenticatedUser, LocalTokenVerifier
from app.core.config import get_settings
from app.db.database import get_db_session
from app.db.models import OnboardingState as DbOnboarding
from app.domain.onboarding import OnboardingRole, OnboardingState
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/onboarding", tags=["onboarding"])
_bearer = HTTPBearer(auto_error=False)
_settings = get_settings()
_verifier = LocalTokenVerifier(_settings.auth_secret, _settings.auth_issuer, _settings.auth_audience, _settings.auth_token_lifetime_seconds)


async def principal(credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        return _verifier.verify_bearer_token(f"Bearer {credentials.credentials}")
    except Exception as error:
        raise HTTPException(status_code=401, detail="Authentication failed") from error


class StepPayload(BaseModel):
    role: OnboardingRole | None = None
    current_step: str = Field(min_length=1, max_length=64)
    data: dict[str, object] = {}
    complete_step: bool = True


async def _state(session: AsyncSession, user_id: str) -> DbOnboarding:
    row = await session.get(DbOnboarding, user_id)
    if row is None:
        row = DbOnboarding(user_id=user_id)
        session.add(row)
        await session.flush()
    return row


def _view(row: DbOnboarding) -> OnboardingState:
    return OnboardingState(user_id=row.user_id, role=row.role, current_step=row.current_step, completed_steps=row.completed_steps or [], completion_status=row.completion_status, data=row.data or {}, started_at=row.started_at, completed_at=row.completed_at)


@router.get("/state", response_model=OnboardingState)
async def get_state(user: AuthenticatedUser = Depends(principal), session: AsyncSession = Depends(get_db_session)) -> OnboardingState:
    return _view(await _state(session, user.user_id))


@router.put("/step", response_model=OnboardingState)
async def save_step(payload: StepPayload, user: AuthenticatedUser = Depends(principal), session: AsyncSession = Depends(get_db_session)) -> OnboardingState:
    row = await _state(session, user.user_id)
    if row.completion_status == "COMPLETED":
        return _view(row)
    row.role = payload.role.value if payload.role else row.role
    row.current_step = payload.current_step
    row.data = {**(row.data or {}), **payload.data}
    completed = list(row.completed_steps or [])
    if payload.complete_step and payload.current_step not in completed:
        completed.append(payload.current_step)
    row.completed_steps = completed
    await session.commit()
    return _view(row)


@router.post("/complete", response_model=OnboardingState)
async def complete(user: AuthenticatedUser = Depends(principal), session: AsyncSession = Depends(get_db_session)) -> OnboardingState:
    row = await _state(session, user.user_id)
    if not row.role:
        raise HTTPException(status_code=422, detail="Role selection is required before completion")
    row.completion_status = "COMPLETED"
    row.completed_at = datetime.now(timezone.utc)
    await session.commit()
    return _view(row)
