from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


class LevelEnum(str, Enum):
    """Explanation difficulty levels."""
    ELI5 = "ELI5"
    ELI15 = "ELI15"
    EXPERT = "EXPERT"


class Topic(Base):
    """Topic entity representing a submitted complex topic/text."""
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationship to explanations
    explanations: Mapped[list["Explanation"]] = relationship(
        "Explanation",
        back_populates="topic",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Explanation(Base):
    """Explanation entity for a topic at a particular difficulty level."""
    __tablename__ = "explanations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True
    )
    level: Mapped[LevelEnum] = mapped_column(SAEnum(LevelEnum), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    topic: Mapped[Topic] = relationship("Topic", back_populates="explanations")
