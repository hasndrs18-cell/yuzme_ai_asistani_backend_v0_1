from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.domain import principal
from app.core.auth import AuthenticatedUser, Role
from app.db.database import get_db_session
from app.db.models import AcademyContent, AcademyLesson, LearningProgress, SavedContent, Source

router = APIRouter(prefix="/academy", tags=["academy"])


class SourceResponse(BaseModel):
    id: str
    title: str
    author: str | None
    publication_year: int | None
    publisher: str | None
    journal: str | None
    doi: str | None
    url: str | None
    source_type: str
    evidence_level: str
    last_checked: object | None
    rights_notes: str | None


class ContentResponse(BaseModel):
    id: str
    content_type: str
    title: str
    slug: str
    summary: str
    body: str
    language: str
    level: str
    category: str
    status: str
    source_id: str | None
    source: SourceResponse | None
    lesson: dict[str, object] | None


class LessonCreate(BaseModel):
    objective: str = Field(min_length=1)
    prerequisites: list[str] = []
    estimated_duration_minutes: int | None = Field(default=None, gt=0)
    sequence: int = Field(default=1, ge=1)
    difficulty: str = Field(min_length=1, max_length=32)


class ContentCreate(BaseModel):
    content_type: str = Field(min_length=1, max_length=40)
    title: str = Field(min_length=1, max_length=240)
    slug: str = Field(min_length=1, max_length=240)
    summary: str = Field(min_length=1)
    body: str = Field(min_length=1)
    language: str = Field(default="tr", min_length=2, max_length=12)
    level: str = Field(min_length=1, max_length=32)
    category: str = Field(min_length=1, max_length=48)
    source_id: str | None = None
    lesson: LessonCreate | None = None


class ProgressPatch(BaseModel):
    status: Literal["NOT_STARTED", "IN_PROGRESS", "COMPLETED"]
    progress_percent: int = Field(ge=0, le=100)
    last_position: int | None = Field(default=None, ge=0)


class ProgressResponse(BaseModel):
    id: str
    content_id: str
    status: str
    progress_percent: int
    last_position: int | None
    started_at: datetime | None
    completed_at: datetime | None


def _source_response(source: Source | None) -> SourceResponse | None:
    return SourceResponse.model_validate(source, from_attributes=True) if source else None


def _content_response(content: AcademyContent, source: Source | None = None, lesson: AcademyLesson | None = None) -> ContentResponse:
    return ContentResponse(
        id=content.id,
        content_type=content.content_type,
        title=content.title,
        slug=content.slug,
        summary=content.summary,
        body=content.body,
        language=content.language,
        level=content.level,
        category=content.category,
        status=content.status,
        source_id=content.source_id,
        source=_source_response(source),
        lesson={
            "objective": lesson.objective,
            "prerequisites": lesson.prerequisites,
            "estimated_duration_minutes": lesson.estimated_duration_minutes,
            "sequence": lesson.sequence,
            "difficulty": lesson.difficulty,
        } if lesson else None,
    )


async def _published_content(session: AsyncSession, identifier: str) -> tuple[AcademyContent, Source | None, AcademyLesson | None]:
    content = (await session.scalars(select(AcademyContent).where(or_(AcademyContent.id == identifier, AcademyContent.slug == identifier), AcademyContent.status == "PUBLISHED", AcademyContent.organization_id.is_(None)))).first()
    if content is None:
        raise HTTPException(status_code=404, detail="Academy content not found")
    source = await session.get(Source, content.source_id) if content.source_id else None
    lesson = (await session.scalars(select(AcademyLesson).where(AcademyLesson.content_id == content.id))).first()
    return content, source, lesson


@router.get("/categories")
async def academy_categories(session: AsyncSession = Depends(get_db_session)) -> list[str]:
    values = await session.scalars(select(AcademyContent.category).where(AcademyContent.status == "PUBLISHED", AcademyContent.organization_id.is_(None)).distinct().order_by(AcademyContent.category))
    return list(values)


@router.get("/sources", response_model=list[SourceResponse])
async def academy_sources(session: AsyncSession = Depends(get_db_session)) -> list[SourceResponse]:
    source_ids = select(AcademyContent.source_id).where(AcademyContent.status == "PUBLISHED", AcademyContent.organization_id.is_(None), AcademyContent.source_id.is_not(None))
    sources = (await session.scalars(select(Source).where(Source.id.in_(source_ids)).order_by(Source.last_checked.desc().nullslast(), Source.title))).all()
    return [SourceResponse.model_validate(source, from_attributes=True) for source in sources]


@router.get("", response_model=list[ContentResponse])
async def list_academy_content(
    category: str | None = None,
    level: str | None = None,
    language: str = Query(default="tr", min_length=2, max_length=12),
    query: str | None = Query(default=None, min_length=1, max_length=120),
    session: AsyncSession = Depends(get_db_session),
) -> list[ContentResponse]:
    statement = select(AcademyContent).where(AcademyContent.status == "PUBLISHED", AcademyContent.organization_id.is_(None), AcademyContent.language == language)
    if category:
        statement = statement.where(AcademyContent.category == category)
    if level:
        statement = statement.where(AcademyContent.level == level)
    if query:
        pattern = f"%{query}%"
        statement = statement.where(or_(AcademyContent.title.ilike(pattern), AcademyContent.summary.ilike(pattern)))
    contents = (await session.scalars(statement.order_by(AcademyContent.updated_at.desc()))).all()
    return [_content_response(content) for content in contents]


@router.get("/content/{identifier}", response_model=ContentResponse)
async def get_academy_content(identifier: str, session: AsyncSession = Depends(get_db_session)) -> ContentResponse:
    content, source, lesson = await _published_content(session, identifier)
    return _content_response(content, source, lesson)


@router.post("/content", response_model=ContentResponse, status_code=201)
async def create_academy_content(payload: ContentCreate, user: AuthenticatedUser = Depends(principal), session: AsyncSession = Depends(get_db_session)) -> ContentResponse:
    if user.role is not Role.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can create Academy content")
    if payload.source_id and await session.get(Source, payload.source_id) is None:
        raise HTTPException(status_code=422, detail="Source not found")
    content = AcademyContent(**payload.model_dump(exclude={"lesson"}), author_id=user.user_id, status="AI_DRAFT")
    session.add(content)
    await session.flush()
    if payload.lesson:
        session.add(AcademyLesson(content_id=content.id, **payload.lesson.model_dump()))
    await session.commit()
    return _content_response(content, await session.get(Source, content.source_id), (await session.scalars(select(AcademyLesson).where(AcademyLesson.content_id == content.id))).first())


@router.post("/content/{content_id}/submit-review", response_model=ContentResponse)
async def submit_academy_review(content_id: str, user: AuthenticatedUser = Depends(principal), session: AsyncSession = Depends(get_db_session)) -> ContentResponse:
    if user.role not in {Role.ADMIN, Role.COACH, Role.ASSISTANT_COACH}:
        raise HTTPException(status_code=403, detail="Content review permission required")
    content = await session.get(AcademyContent, content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Academy content not found")
    if content.status not in {"AI_DRAFT", "DRAFT"}:
        raise HTTPException(status_code=409, detail="Content is not ready for review")
    content.status = "REVIEW"
    content.reviewer_id = user.user_id
    await session.commit()
    return _content_response(content, await session.get(Source, content.source_id))


@router.post("/content/{content_id}/publish", response_model=ContentResponse)
async def publish_academy_content(content_id: str, user: AuthenticatedUser = Depends(principal), session: AsyncSession = Depends(get_db_session)) -> ContentResponse:
    if user.role is not Role.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can publish Academy content")
    content = await session.get(AcademyContent, content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Academy content not found")
    if content.status != "REVIEW" or content.source_id is None:
        raise HTTPException(status_code=409, detail="Content requires review and a source before publishing")
    content.status = "PUBLISHED"
    content.reviewer_id = user.user_id
    content.published_at = datetime.now(timezone.utc)
    await session.commit()
    return _content_response(content, await session.get(Source, content.source_id))


@router.get("/progress", response_model=list[ProgressResponse])
async def list_progress(user: AuthenticatedUser = Depends(principal), session: AsyncSession = Depends(get_db_session)) -> list[ProgressResponse]:
    rows = (await session.scalars(select(LearningProgress).where(LearningProgress.user_id == user.user_id).order_by(LearningProgress.updated_at.desc()))).all()
    return [ProgressResponse.model_validate(row, from_attributes=True) for row in rows]


@router.patch("/progress/{content_id}", response_model=ProgressResponse)
async def update_progress(content_id: str, payload: ProgressPatch, user: AuthenticatedUser = Depends(principal), session: AsyncSession = Depends(get_db_session)) -> ProgressResponse:
    content, _, _ = await _published_content(session, content_id)
    row = (await session.scalars(select(LearningProgress).where(LearningProgress.user_id == user.user_id, LearningProgress.content_id == content.id))).first()
    now = datetime.now(timezone.utc)
    if row is None:
        row = LearningProgress(user_id=user.user_id, content_id=content.id)
        session.add(row)
    row.status = payload.status
    row.progress_percent = payload.progress_percent
    row.last_position = payload.last_position
    row.started_at = row.started_at or now
    row.completed_at = now if payload.status == "COMPLETED" else None
    await session.commit()
    return ProgressResponse.model_validate(row, from_attributes=True)


@router.get("/saved", response_model=list[str])
async def list_saved(user: AuthenticatedUser = Depends(principal), session: AsyncSession = Depends(get_db_session)) -> list[str]:
    return list(await session.scalars(select(SavedContent.content_id).where(SavedContent.user_id == user.user_id)))


@router.post("/saved/{content_id}", status_code=201)
async def save_content(content_id: str, user: AuthenticatedUser = Depends(principal), session: AsyncSession = Depends(get_db_session)) -> dict[str, str]:
    content, _, _ = await _published_content(session, content_id)
    existing = (await session.scalars(select(SavedContent).where(SavedContent.user_id == user.user_id, SavedContent.content_id == content.id))).first()
    if existing is None:
        session.add(SavedContent(user_id=user.user_id, content_id=content.id))
        await session.commit()
    return {"content_id": content.id, "status": "saved"}


@router.delete("/saved/{content_id}", status_code=204)
async def unsave_content(content_id: str, user: AuthenticatedUser = Depends(principal), session: AsyncSession = Depends(get_db_session)) -> None:
    content, _, _ = await _published_content(session, content_id)
    await session.execute(delete(SavedContent).where(SavedContent.user_id == user.user_id, SavedContent.content_id == content.id))
    await session.commit()


@router.get("/{identifier}", response_model=ContentResponse)
async def get_academy_content_by_id(identifier: str, session: AsyncSession = Depends(get_db_session)) -> ContentResponse:
    content, source, lesson = await _published_content(session, identifier)
    return _content_response(content, source, lesson)
