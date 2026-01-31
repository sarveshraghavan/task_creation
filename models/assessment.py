"""
Role-based assessment models for manual student evaluation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


class UserRole(str, Enum):
    """User roles for role-based assessment."""
    TEACHER = "teacher"
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    PARENT = "parent"


class ManualAssessment(BaseModel):
    """Manual assessment from teacher/admin."""
    student_id: str
    assessor_role: UserRole
    assessor_name: str
    
    # Assessment scores
    performance_score: float = Field(ge=0.0, le=10.0, description="Overall performance (0-10)")
    comprehension_level: float = Field(ge=0.0, le=10.0, description="Understanding level (0-10)")
    
    # Optional detailed scores
    skill_scores: Optional[dict[str, float]] = Field(default=None, description="Specific skill scores")
    
    # Notes and reasoning
    notes: Optional[str] = Field(default=None, description="Assessment notes")
    recommended_difficulty: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "uuid",
                "assessor_role": "teacher",
                "assessor_name": "Ms. Johnson",
                "performance_score": 7.5,
                "comprehension_level": 8.0,
                "skill_scores": {
                    "algebra": 7.0,
                    "geometry": 8.5
                },
                "notes": "Student shows strong grasp but needs more practice",
                "recommended_difficulty": 7.5
            }
        }


class AssessmentRecord(BaseModel):
    """Record of a manual assessment."""
    id: Optional[str] = None
    student_id: str
    assessor_role: UserRole
    assessor_name: str
    performance_score: float
    comprehension_level: float
    skill_scores: Optional[dict[str, float]] = None
    notes: Optional[str] = None
    recommended_difficulty: Optional[float] = None
    created_at: Optional[datetime] = None
    
    # Impact on student profile
    difficulty_before: float
    difficulty_after: float
    adjustment_applied: bool = False
