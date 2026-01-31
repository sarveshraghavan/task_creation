"""
Student management service.
"""

from models.student import StudentProfile, StudentCreate, StudentUpdate, SkillLevel
from database import get_db_client
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class StudentService:
    """Service for managing student profiles."""
    
    def __init__(self):
        self.db = get_db_client()
    
    async def create_student(self, student_data: StudentCreate) -> StudentProfile:
        """
        Create a new student profile.
        
        Args:
            student_data: Student creation data
            
        Returns:
            Created student profile
        """
        # Prepare student data
        profile_data = {
            "name": student_data.name,
            "email": student_data.email,
            "skills": {},
            "current_difficulty": 1.0,
            "total_tasks_completed": 0,
            "success_rate": 0.0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Add initial skill if provided
        if student_data.initial_skill:
            profile_data["skills"] = {
                student_data.initial_skill: student_data.initial_level.value
            }
        
        # Create in database
        result = await self.db.create_student(profile_data)
        return StudentProfile(**result)
    
    async def get_student(self, student_id: str) -> Optional[StudentProfile]:
        """
        Get student profile by ID.
        
        Args:
            student_id: Student ID
            
        Returns:
            Student profile or None if not found
        """
        result = await self.db.get_student(student_id)
        return StudentProfile(**result) if result else None
    
    async def update_student(self, student_id: str, update_data: StudentUpdate) -> StudentProfile:
        """
        Update student profile.
        
        Args:
            student_id: Student ID
            update_data: Fields to update
            
        Returns:
            Updated student profile
        """
        # Prepare update data
        data = update_data.model_dump(exclude_unset=True)
        data["updated_at"] = datetime.utcnow().isoformat()
        
        # Update in database
        result = await self.db.update_student(student_id, data)
        return StudentProfile(**result)
    
    async def update_after_task(
        self, 
        student_id: str, 
        skill: str, 
        score: float, 
        was_correct: bool
    ) -> StudentProfile:
        """
        Update student profile after task completion.
        Adjusts difficulty and success rate.
        
        Args:
            student_id: Student ID
            skill: Skill that was practiced
            score: Task score (0-100)
            was_correct: Whether task was completed correctly
            
        Returns:
            Updated student profile
        """
        # Get current profile
        student = await self.get_student(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")
        
        # Update skill level based on performance
        current_skills = student.skills.copy()
        skill_level = current_skills.get(skill, SkillLevel.BEGINNER.value)
        
        # Upgrade skill level if performing well
        if score >= 85 and was_correct:
            if skill_level == SkillLevel.BEGINNER.value:
                current_skills[skill] = SkillLevel.INTERMEDIATE.value
            elif skill_level == SkillLevel.INTERMEDIATE.value:
                current_skills[skill] = SkillLevel.ADVANCED.value
            elif skill_level == SkillLevel.ADVANCED.value:
                current_skills[skill] = SkillLevel.EXPERT.value
        
        # Calculate new success rate
        total_tasks = student.total_tasks_completed
        current_success_rate = student.success_rate
        new_success = 1.0 if was_correct else 0.0
        updated_success_rate = (
            (current_success_rate * total_tasks + new_success) / (total_tasks + 1)
        )
        
        # Adjust difficulty
        new_difficulty = self._calculate_new_difficulty(
            student.current_difficulty,
            score,
            was_correct
        )
        
        # Update student
        update = StudentUpdate(
            skills=current_skills,
            current_difficulty=new_difficulty
        )
        
        update_dict = {
            "skills": current_skills,
            "current_difficulty": new_difficulty,
            "total_tasks_completed": total_tasks + 1,
            "success_rate": updated_success_rate,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = await self.db.update_student(student_id, update_dict)
        return StudentProfile(**result)
    
    def _calculate_new_difficulty(
        self, 
        current_difficulty: float, 
        score: float, 
        was_correct: bool
    ) -> float:
        """
        Calculate new difficulty based on performance.
        
        Args:
            current_difficulty: Current difficulty level (0-10)
            score: Task score (0-100)
            was_correct: Whether task was completed correctly
            
        Returns:
            New difficulty level (0-10)
        """
        # If score is very high, increase difficulty
        if score >= 90 and was_correct:
            adjustment = 0.5
        elif score >= 75 and was_correct:
            adjustment = 0.3
        elif score >= 60:
            adjustment = 0.0
        elif score >= 40:
            adjustment = -0.3
        else:
            adjustment = -0.5
        
        new_difficulty = current_difficulty + adjustment
        
        # Clamp between 0 and 10
        return max(0.0, min(10.0, new_difficulty))


# Singleton instance
_student_service = None


def get_student_service() -> StudentService:
    """Get the singleton student service instance."""
    global _student_service
    if _student_service is None:
        _student_service = StudentService()
    return _student_service
