from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from src.db.schemas import ExplanationRead, Level, TopicRead


# PUBLIC_INTERFACE
class ExplanationRequest(BaseModel):
    """Request payload for generating simplified explanations from a topic."""
    topic_title: str = Field(..., description="Short title for the topic", max_length=255)
    topic_content: str = Field(..., description="Full content of the topic to simplify")
    levels: List[Level] = Field(
        default_factory=lambda: [Level.ELI5, Level.ELI15, Level.EXPERT],
        description="List of difficulty levels to generate"
    )


# PUBLIC_INTERFACE
class ExplanationResponse(BaseModel):
    """Response containing the created Topic and its generated explanations."""
    topic: TopicRead = Field(..., description="Created topic")
    explanations: List[ExplanationRead] = Field(..., description="Generated explanations for the topic")


# PUBLIC_INTERFACE
class RegenerateResponse(BaseModel):
    """Response for a regenerated explanation for a given topic and level."""
    topic_id: int = Field(..., description="Topic ID")
    explanation: ExplanationRead = Field(..., description="Regenerated explanation row")


# PUBLIC_INTERFACE
class HistoryItem(BaseModel):
    """Historical topic item with metadata but without full content to keep list concise."""
    id: int = Field(..., description="Topic unique identifier")
    title: str = Field(..., description="Topic title")
    created_at: datetime = Field(..., description="Creation timestamp")
    explanations_count: int = Field(..., description="Number of explanations available")


# PUBLIC_INTERFACE
class HistoryResponse(BaseModel):
    """Paginated response for topics history."""
    items: List[HistoryItem] = Field(default_factory=list, description="Page items")
    total: int = Field(..., description="Total number of topics across all pages")
    limit: int = Field(..., description="Limit used for pagination")
    offset: int = Field(..., description="Offset used for pagination")


# PUBLIC_INTERFACE
class ErrorMessage(BaseModel):
    """Standard error message payload."""
    detail: str = Field(..., description="Error detail message")
