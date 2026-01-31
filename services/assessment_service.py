"""
Assessment service for role-based manual student evaluation.
"""

from models.assessment import ManualAssessment, AssessmentRecord, UserRole
from models.student import SkillLevel
from services.student_service import get_student_service
from database import get_db_client
from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class AssessmentService:
    """Service for handling role-based manual assessments."""
    
    def __init__(self):
        self.db = get_db_client()
        self.student_service = get_student_service()
    
    async def submit_assessment(self, assessment: ManualAssessment) -> AssessmentRecord:
        """
        Submit a manual assessment and update student profile accordingly.
        
        This allows teachers/admins to manually adjust student difficulty
        based on their observations or external test scores.
        
        Args:
            assessment: Manual assessment data
            
        Returns:
            Assessment record with applied changes
        """
        # Get current student profile
        student = await self.student_service.get_student(assessment.student_id)
        if not student:
            raise ValueError(f"Student {assessment.student_id} not found")
        
        logger.info(
            f"{assessment.assessor_role.value} '{assessment.assessor_name}' "
            f"assessing student {assessment.student_id}"
        )
        
        # Calculate new difficulty based on assessment
        new_difficulty = self._calculate_difficulty_from_assessment(
            current_difficulty=student.current_difficulty,
            performance_score=assessment.performance_score,
            comprehension_level=assessment.comprehension_level,
            recommended_difficulty=assessment.recommended_difficulty
        )
        
        # Update skill scores if provided
        updated_skills = student.skills.copy()
        if assessment.skill_scores:
            for skill, score in assessment.skill_scores.items():
                # Convert score (0-10) to skill level
                skill_level = self._score_to_skill_level(score)
                updated_skills[skill] = skill_level.value
        
        # Determine if adjustment should be applied
        adjustment_applied = abs(new_difficulty - student.current_difficulty) > 0.1
        
        # Update student profile
        if adjustment_applied or assessment.skill_scores:
            update_data = {
                "current_difficulty": new_difficulty,
                "skills": updated_skills,
                "updated_at": datetime.utcnow().isoformat()
            }
            await self.db.update_student(assessment.student_id, update_data)
            logger.info(
                f"Updated student difficulty: {student.current_difficulty:.2f} → {new_difficulty:.2f}"
            )
        
        # Create assessment record
        record_data = {
            "student_id": assessment.student_id,
            "assessor_role": assessment.assessor_role.value,
            "assessor_name": assessment.assessor_name,
            "performance_score": assessment.performance_score,
            "comprehension_level": assessment.comprehension_level,
            "skill_scores": assessment.skill_scores,
            "notes": assessment.notes,
            "recommended_difficulty": assessment.recommended_difficulty,
            "difficulty_before": student.current_difficulty,
            "difficulty_after": new_difficulty,
            "adjustment_applied": adjustment_applied,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Save assessment to database
        result = await self.db.create_assessment(record_data)
        
        return AssessmentRecord(**result)
    
    def _calculate_difficulty_from_assessment(
        self,
        current_difficulty: float,
        performance_score: float,
        comprehension_level: float,
        recommended_difficulty: Optional[float] = None
    ) -> float:
        """
        Calculate new difficulty level based on manual assessment.
        
        If recommended_difficulty is provided, use it (with limits).
        Otherwise, calculate based on performance and comprehension scores.
        
        Args:
            current_difficulty: Current difficulty (0-10)
            performance_score: Performance score (0-10)
            comprehension_level: Comprehension score (0-10)
            recommended_difficulty: Optional explicit recommendation
            
        Returns:
            New difficulty level (0-10)
        """
        if recommended_difficulty is not None:
            # Use recommended difficulty but limit change to ±2 per assessment
            max_change = 2.0
            new_diff = max(
                current_difficulty - max_change,
                min(current_difficulty + max_change, recommended_difficulty)
            )
            return max(0.0, min(10.0, new_diff))
        
        # Calculate weighted average of performance and comprehension
        # Performance weighted more heavily (60%) than comprehension (40%)
        combined_score = (performance_score * 0.6) + (comprehension_level * 0.4)
        
        # Determine adjustment based on combined score
        if combined_score >= 8.5:
            # Excellent - increase difficulty significantly
            adjustment = 1.5
        elif combined_score >= 7.0:
            # Good - moderate increase
            adjustment = 1.0
        elif combined_score >= 5.5:
            # Average - slight increase
            adjustment = 0.5
        elif combined_score >= 4.0:
            # Below average - maintain or slight decrease
            adjustment = 0.0
        elif combined_score >= 2.5:
            # Poor - moderate decrease
            adjustment = -1.0
        else:
            # Very poor - significant decrease
            adjustment = -1.5
        
        new_difficulty = current_difficulty + adjustment
        
        # Clamp between 0 and 10
        return max(0.0, min(10.0, new_difficulty))
    
    def _score_to_skill_level(self, score: float) -> SkillLevel:
        """
        Convert numeric score (0-10) to skill level enum.
        
        Args:
            score: Numeric score 0-10
            
        Returns:
            Corresponding skill level
        """
        if score >= 8.0:
            return SkillLevel.EXPERT
        elif score >= 6.0:
            return SkillLevel.ADVANCED
        elif score >= 4.0:
            return SkillLevel.INTERMEDIATE
        else:
            return SkillLevel.BEGINNER
    
    async def get_student_assessments(
        self, 
        student_id: str, 
        limit: int = 20
    ) -> List[AssessmentRecord]:
        """
        Get assessment history for a student.
        
        Args:
            student_id: Student ID
            limit: Maximum number of records to return
            
        Returns:
            List of assessment records
        """
        results = await self.db.get_student_assessments(student_id, limit)
        return [AssessmentRecord(**r) for r in results]
    
    async def get_recent_assessment_summary(self, student_id: str) -> dict:
        """
        Get summary of recent assessments for a student.
        
        Args:
            student_id: Student ID
            
        Returns:
            Summary statistics
        """
        assessments = await self.get_student_assessments(student_id, limit=10)
        
        if not assessments:
            return {
                "total_assessments": 0,
                "average_performance": 0.0,
                "average_comprehension": 0.0,
                "total_difficulty_change": 0.0,
                "assessors": []
            }
        
        avg_performance = sum(a.performance_score for a in assessments) / len(assessments)
        avg_comprehension = sum(a.comprehension_level for a in assessments) / len(assessments)
        
        # Calculate total difficulty change
        if assessments:
            first_before = assessments[-1].difficulty_before
            last_after = assessments[0].difficulty_after
            total_change = last_after - first_before
        else:
            total_change = 0.0
        
        # Get unique assessors
        assessors = list(set(
            f"{a.assessor_role.value}: {a.assessor_name}" for a in assessments
        ))
        
        return {
            "total_assessments": len(assessments),
            "average_performance": round(avg_performance, 2),
            "average_comprehension": round(avg_comprehension, 2),
            "total_difficulty_change": round(total_change, 2),
            "assessors": assessors
        }


# Singleton instance
_assessment_service = None


def get_assessment_service() -> AssessmentService:
    """Get the singleton assessment service instance."""
    global _assessment_service
    if _assessment_service is None:
        _assessment_service = AssessmentService()
    return _assessment_service
