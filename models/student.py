"""
Student data models.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from enum import Enum


class SkillLevel(str, Enum):
    """Student skill proficiency levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class StudentProfile(BaseModel):
    """Student profile model."""
    id: Optional[str] = None
    name: str
    email: str
    skills: Dict[str, SkillLevel] = Field(default_factory=dict)
    current_difficulty: float = Field(default=1.0, ge=0.0, le=10.0)
    total_tasks_completed: int = 0
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "skills": {
                    "algebra": "beginner",
                    "geometry": "intermediate"
                },
                "current_difficulty": 2.5
            }
        }


class StudentCreate(BaseModel):
    """Model for creating a new student."""
    name: str
    email: str
    initial_skill: Optional[str] = None
    initial_level: Optional[SkillLevel] = SkillLevel.BEGINNER


class StudentUpdate(BaseModel):
    """Model for updating student profile."""
    name: Optional[str] = None
    skills: Optional[Dict[str, SkillLevel]] = None
    current_difficulty: Optional[float] = None
