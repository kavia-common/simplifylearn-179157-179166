from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class Level(str, Enum):
    """Difficulty level for explanations."""
    ELI5 = "ELI5"
    ELI15 = "ELI15"
    EXPERT = "EXPERT"


# Topic Schemas

class TopicBase(BaseModel):
    title: str = Field(..., description="Short title for the topic", max_length=255)
    content: str = Field(..., description="Full content or description of the topic")


class TopicCreate(TopicBase):
    """Payload to create a Topic."""
    pass


class TopicRead(TopicBase):
    """Returned representation of a Topic."""
    id: int = Field(..., description="Unique identifier of the topic")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


# Explanation Schemas

class ExplanationBase(BaseModel):
    level: Level = Field(..., description="Difficulty level of the explanation")
    text: str = Field(..., description="Explanation text for the topic")


class ExplanationCreate(ExplanationBase):
    """Payload to create an Explanation."""
    topic_id: int = Field(..., description="Associated topic ID")


class ExplanationRead(ExplanationBase):
    """Returned representation of an Explanation."""
    id: int = Field(..., description="Unique identifier of the explanation")
    topic_id: int = Field(..., description="Associated topic ID")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class TopicWithExplanations(TopicRead):
    """Topic with nested explanations."""
    explanations: List[ExplanationRead] = Field(default_factory=list, description="Related explanations")
