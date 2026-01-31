"""
Task data models.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TaskLength(str, Enum):
    """Task duration categories."""
    SHORT = "short"      # 5-10 minutes
    MEDIUM = "medium"    # 10-20 minutes
    LONG = "long"        # 20+ minutes


class RepetitionLevel(str, Enum):
    """How much repetition/practice the task includes."""
    LOW = "low"          # New concepts
    MEDIUM = "medium"    # Some practice
    HIGH = "high"        # Heavy practice


class TaskStatus(str, Enum):
    """Task completion status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    SCORED = "scored"


class TaskGenerationParams(BaseModel):
    """Parameters for generating a task."""
    student_id: str
    skill: str
    difficulty: float = Field(ge=0.0, le=10.0)
    task_length: TaskLength = TaskLength.MEDIUM
    repetition: RepetitionLevel = RepetitionLevel.MEDIUM
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "123",
                "skill": "algebra",
                "difficulty": 3.5,
                "task_length": "medium",
                "repetition": "medium"
            }
        }


class GeneratedTask(BaseModel):
    """A generated learning task."""
    id: Optional[str] = None
    student_id: str
    skill: str
    difficulty: float
    task_length: TaskLength
    repetition: RepetitionLevel
    
    # Task content
    title: str
    instructions: str
    expected_input: str
    
    # Metadata
    status: TaskStatus = TaskStatus.PENDING
    created_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    score: Optional[float] = None
    feedback: Optional[str] = None


class TaskSubmission(BaseModel):
    """Student's task submission."""
    task_id: str
    student_id: str
    answer: str
    time_spent_minutes: Optional[float] = None


class TaskScore(BaseModel):
    """Task scoring result."""
    task_id: str
    score: float = Field(ge=0.0, le=100.0)
    feedback: str
    correct: bool
    areas_for_improvement: list[str] = Field(default_factory=list)
    supplementary_content_id: Optional[str] = Field(default=None, description="ID of extra content if score dropped")
