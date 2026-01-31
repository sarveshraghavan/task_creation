"""
Supplementary learning content models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SupplementaryContent(BaseModel):
    """Supplementary learning content for struggling students."""
    id: Optional[str] = None
    student_id: str
    task_id: str
    skill: str
    
    # Trigger information
    current_score: float
    previous_score: float
    score_drop: float
    
    # Generated content
    concept_review: str
    key_points: List[str]
    worked_example: str
    practice_tips: List[str]
    common_mistakes: List[str]
    
    # Metadata
    created_at: Optional[datetime] = None
    viewed: bool = False
    helpful: Optional[bool] = None


class SupplementaryContentResponse(BaseModel):
    """Response containing supplementary content."""
    content: SupplementaryContent
    message: str = "Your score decreased. Here's extra content to help you improve."
    
    
class ContentGenerationTrigger(BaseModel):
    """Trigger for generating supplementary content."""
    student_id: str
    task_id: str
    skill: str
    topic: str
    current_score: float
    previous_score: float
    areas_of_difficulty: List[str]
