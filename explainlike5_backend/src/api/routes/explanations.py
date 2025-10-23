from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from src.api.schemas import (
    ErrorMessage,
    ExplanationRequest,
    ExplanationResponse,
    HistoryItem,
    HistoryResponse,
    RegenerateResponse,
)
from src.db.models import Explanation, LevelEnum, Topic
from src.db.schemas import ExplanationRead, Level, TopicWithExplanations
from src.db.session import get_db
from src.services import deterministic_simplify

router = APIRouter(tags=["explanations"])


def _level_to_enum(level: Level) -> LevelEnum:
    return LevelEnum[level.value]


# PUBLIC_INTERFACE
@router.post(
    "/explanations",
    response_model=ExplanationResponse,
    summary="Generate explanations for a topic",
    description="Creates a Topic and generates simplified explanations for the requested levels.",
    responses={400: {"model": ErrorMessage}},
)
def create_explanations(payload: ExplanationRequest, db: Session = Depends(get_db)):
    """Create a Topic and deterministic explanations across levels."""
    # Validate levels are unique
    unique_levels = []
    for lv in payload.levels:
        if lv not in unique_levels:
            unique_levels.append(lv)
    if not unique_levels:
        raise HTTPException(status_code=400, detail="At least one level must be provided.")

    # Create Topic
    topic = Topic(title=payload.topic_title, content=payload.topic_content)
    db.add(topic)
    db.flush()  # obtain topic.id without commit

    # Generate explanations deterministically
    explanations: List[Explanation] = []
    for lv in unique_levels:
        enum_lv = _level_to_enum(lv)
        text = deterministic_simplify(payload.topic_title, payload.topic_content, enum_lv)
        exp = Explanation(topic_id=topic.id, level=enum_lv, text=text)
        db.add(exp)
        explanations.append(exp)

    db.commit()
    db.refresh(topic)
    for exp in explanations:
        db.refresh(exp)

    # Prepare response
    explanations_read = [
        ExplanationRead.model_validate(
            {
                "id": e.id,
                "topic_id": e.topic_id,
                "level": Level(e.level.value),
                "text": e.text,
                "created_at": e.created_at,
            }
        )
        for e in explanations
    ]
    return ExplanationResponse(
        topic={"id": topic.id, "title": topic.title, "content": topic.content, "created_at": topic.created_at},
        explanations=explanations_read,
    )


# PUBLIC_INTERFACE
@router.get(
    "/topics/{topic_id}",
    response_model=TopicWithExplanations,
    summary="Fetch a topic with its explanations",
    description="Returns topic details and all explanations across levels.",
    responses={404: {"model": ErrorMessage}},
    tags=["topics"],
)
def get_topic(topic_id: int, db: Session = Depends(get_db)):
    """Fetch a single topic with nested explanations."""
    stmt = (
        select(Topic)
        .options(joinedload(Topic.explanations))
        .where(Topic.id == topic_id)
        .limit(1)
    )
    topic = db.execute(stmt).scalars().first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Convert to Pydantic
    explanations = [
        {
            "id": e.id,
            "topic_id": e.topic_id,
            "level": e.level.value,
            "text": e.text,
            "created_at": e.created_at,
        }
        for e in sorted(topic.explanations, key=lambda x: (x.created_at, x.id))
    ]
    return TopicWithExplanations(
        id=topic.id,
        title=topic.title,
        content=topic.content,
        created_at=topic.created_at,
        explanations=explanations,
    )


# PUBLIC_INTERFACE
@router.get(
    "/history",
    response_model=HistoryResponse,
    summary="List topic history",
    description="Paginated list of topics with counts of explanations.",
    tags=["topics"],
)
def get_history(
    limit: int = Query(10, ge=1, le=100, description="Max items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    db: Session = Depends(get_db),
):
    """Return paginated topics for history view."""
    total = db.scalar(select(func.count(Topic.id))) or 0

    # Fetch items
    # Use a subquery to count explanations for each topic for performance
    exp_counts_sub = (
        select(Explanation.topic_id, func.count(Explanation.id).label("cnt"))
        .group_by(Explanation.topic_id)
        .subquery()
    )

    stmt = (
        select(
            Topic.id,
            Topic.title,
            Topic.created_at,
            func.coalesce(exp_counts_sub.c.cnt, 0).label("explanations_count"),
        )
        .outerjoin(exp_counts_sub, exp_counts_sub.c.topic_id == Topic.id)
        .order_by(Topic.created_at.desc(), Topic.id.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = db.execute(stmt).all()
    items: List[HistoryItem] = [
        HistoryItem(
            id=r.id, title=r.title, created_at=r.created_at, explanations_count=r.explanations_count
        )
        for r in rows
    ]
    return HistoryResponse(items=items, total=total, limit=limit, offset=offset)


# PUBLIC_INTERFACE
@router.post(
    "/explanations/{topic_id}/regenerate",
    response_model=RegenerateResponse,
    summary="Regenerate explanation for a topic",
    description="Creates a new Explanation row for the given topic at the requested level.",
    responses={404: {"model": ErrorMessage}, 400: {"model": ErrorMessage}},
)
def regenerate_explanation(
    topic_id: int,
    level: Level = Query(..., description="Level to regenerate"),
    db: Session = Depends(get_db),
):
    """Regenerate an explanation at the given level; stores a new row."""
    topic = db.get(Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    enum_lv = _level_to_enum(level)
    text = deterministic_simplify(topic.title, topic.content, enum_lv)
    exp = Explanation(topic_id=topic.id, level=enum_lv, text=text)
    db.add(exp)
    db.commit()
    db.refresh(exp)

    return RegenerateResponse(
        topic_id=topic.id,
        explanation=ExplanationRead.model_validate(
            {
                "id": exp.id,
                "topic_id": exp.topic_id,
                "level": level,
                "text": exp.text,
                "created_at": exp.created_at,
            }
        ),
    )
