"""
Task generation and scoring service.
"""

from models.task import (
    GeneratedTask, TaskGenerationParams, TaskSubmission, 
    TaskScore, TaskStatus
)
from services.llm_service import get_llm_service
from services.student_service import get_student_service
from database import get_db_client
from prompts import get_task_generation_prompt, get_task_scoring_prompt
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TaskService:
    """Service for task generation and scoring."""
    
    def __init__(self):
        self.db = get_db_client()
        self.llm = get_llm_service()
        self.student_service = get_student_service()
    
    async def generate_task(self, params: TaskGenerationParams) -> GeneratedTask:
        """
        Generate a new task for a student.
        
        Args:
            params: Task generation parameters
            
        Returns:
            Generated task
        """
        # Get student profile to verify existence
        student = await self.student_service.get_student(params.student_id)
        if not student:
            raise ValueError(f"Student {params.student_id} not found")
        
        # Generate prompt
        prompt = get_task_generation_prompt(
            skill=params.skill,
            difficulty=params.difficulty,
            task_length=params.task_length.value,
            repetition=params.repetition.value
        )
        
        logger.info(f"Generating task for student {params.student_id}, skill: {params.skill}")
        
        # Call LLM to generate task
        task_content = await self.llm.generate_task(prompt)
        
        # Create task object
        task_data = {
            "student_id": params.student_id,
            "skill": params.skill,
            "difficulty": params.difficulty,
            "task_length": params.task_length.value,
            "repetition": params.repetition.value,
            "title": task_content["title"],
            "instructions": task_content["instructions"],
            "expected_input": task_content["expected_input"],
            "status": TaskStatus.PENDING.value,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Save to database
        result = await self.db.create_task(task_data)
        
        logger.info(f"Task created with ID: {result.get('id')}")
        
        return GeneratedTask(**result)
    
    async def get_task(self, task_id: str) -> Optional[GeneratedTask]:
        """
        Get task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task or None if not found
        """
        result = await self.db.get_task(task_id)
        return GeneratedTask(**result) if result else None
    
    async def submit_task(self, submission: TaskSubmission) -> TaskScore:
        """
        Submit and score a completed task.
        
        Automatically generates supplementary content if score drops.
        
        Args:
            submission: Student's task submission
            
        Returns:
            Task score and feedback
        """
        # Get the task
        task = await self.get_task(submission.task_id)
        if not task:
            raise ValueError(f"Task {submission.task_id} not found")
        
        # Verify student matches
        if task.student_id != submission.student_id:
            raise ValueError("Task does not belong to this student")
        
        # Get previous task for comparison
        recent_tasks = await self.db.get_student_tasks(submission.student_id, limit=2)
        previous_score = None
        if len(recent_tasks) > 0:
            # Get the most recent scored task (excluding current one)
            for prev_task in recent_tasks:
                if prev_task.get('id') != submission.task_id and prev_task.get('score') is not None:
                    previous_score = prev_task.get('score')
                    break
        
        # Generate scoring prompt
        prompt = get_task_scoring_prompt(
            task_instructions=task.instructions,
            student_answer=submission.answer,
            skill=task.skill
        )
        
        logger.info(f"Scoring task {submission.task_id} for student {submission.student_id}")
        
        # Call LLM to score the task
        score, is_correct, feedback, areas = await self.llm.score_task(prompt)
        
        # Update task status
        task_update = {
            "status": TaskStatus.SCORED.value,
            "submitted_at": datetime.utcnow().isoformat(),
            "score": score,
            "feedback": feedback
        }
        await self.db.update_task(submission.task_id, task_update)
        
        # Check if score dropped - trigger supplementary content generation
        supplementary_content_id = None
        if previous_score is not None and score < previous_score:
            score_drop = previous_score - score
            logger.info(f"Score drop detected: {previous_score} → {score} (-{score_drop})")
            
            # Generate supplementary content
            try:
                supplementary_content_id = await self._generate_supplementary_content(
                    student_id=submission.student_id,
                    task_id=submission.task_id,
                    skill=task.skill,
                    topic=task.title,
                    current_score=score,
                    previous_score=previous_score,
                    areas_of_difficulty=areas
                )
                logger.info(f"Generated supplementary content: {supplementary_content_id}")
            except Exception as e:
                logger.error(f"Failed to generate supplementary content: {e}")
        
        # Update student profile
        await self.student_service.update_after_task(
            student_id=submission.student_id,
            skill=task.skill,
            score=score,
            was_correct=is_correct
        )
        
        logger.info(f"Task scored: {score}/100, correct: {is_correct}")
        
        task_score = TaskScore(
            task_id=submission.task_id,
            score=score,
            feedback=feedback,
            correct=is_correct,
            areas_for_improvement=areas
        )
        
        # Add supplementary content ID if generated
        if supplementary_content_id:
            task_score.supplementary_content_id = supplementary_content_id
        
        return task_score
    
    async def _generate_supplementary_content(
        self,
        student_id: str,
        task_id: str,
        skill: str,
        topic: str,
        current_score: float,
        previous_score: float,
        areas_of_difficulty: list
    ) -> str:
        """
        Generate supplementary learning content for a student.
        
        Triggered when score drops below previous performance.
        
        Args:
            student_id: Student ID
            task_id: Current task ID
            skill: Skill being practiced
            topic: Specific topic/concept
            current_score: Current task score
            previous_score: Previous task score
            areas_of_difficulty: Areas where student struggled
            
        Returns:
            Supplementary content ID
        """
        from prompts import get_supplementary_content_prompt
        
        # Generate the prompt
        prompt = get_supplementary_content_prompt(
            skill=skill,
            topic=topic,
            current_score=current_score,
            previous_score=previous_score,
            areas_of_difficulty=areas_of_difficulty
        )
        
        # Call LLM to generate content
        content_data = await self.llm.generate_supplementary_content(prompt)
        
        # Save to database
        supplementary_data = {
            "student_id": student_id,
            "task_id": task_id,
            "skill": skill,
            "current_score": current_score,
            "previous_score": previous_score,
            "score_drop": previous_score - current_score,
            "concept_review": content_data.get("concept_review", ""),
            "key_points": content_data.get("key_points", []),
            "worked_example": content_data.get("worked_example", ""),
            "practice_tips": content_data.get("practice_tips", []),
            "common_mistakes": content_data.get("common_mistakes", []),
            "created_at": datetime.utcnow().isoformat(),
            "viewed": False
        }
        
        result = await self.db.create_supplementary_content(supplementary_data)
        return result.get("id")
    
    async def get_next_task_params(self, student_id: str, skill: str) -> TaskGenerationParams:
        """
        Derive optimal task parameters for a student's next task.
        
        Args:
            student_id: Student ID
            skill: Skill to practice
            
        Returns:
            Recommended task generation parameters
        """
        # Get student profile
        student = await self.student_service.get_student(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")
        
        # Get recent tasks to analyze patterns
        recent_tasks = await self.db.get_student_tasks(student_id, limit=5)
        
        # Determine task length based on success rate
        if student.success_rate >= 0.8:
            from models.task import TaskLength
            task_length = TaskLength.LONG
        elif student.success_rate >= 0.5:
            from models.task import TaskLength
            task_length = TaskLength.MEDIUM
        else:
            from models.task import TaskLength
            task_length = TaskLength.SHORT
        
        # Determine repetition based on recent performance
        if len(recent_tasks) >= 2:
            recent_scores = [t.get('score', 0) for t in recent_tasks[:2]]
            avg_recent = sum(recent_scores) / len(recent_scores)
            
            from models.task import RepetitionLevel
            if avg_recent < 60:
                repetition = RepetitionLevel.HIGH
            elif avg_recent < 80:
                repetition = RepetitionLevel.MEDIUM
            else:
                repetition = RepetitionLevel.LOW
        else:
            from models.task import RepetitionLevel
            repetition = RepetitionLevel.MEDIUM
        
        return TaskGenerationParams(
            student_id=student_id,
            skill=skill,
            difficulty=student.current_difficulty,
            task_length=task_length,
            repetition=repetition
        )


# Singleton instance
_task_service = None


def get_task_service() -> TaskService:
    """Get the singleton task service instance."""
    global _task_service
    if _task_service is None:
        _task_service = TaskService()
    return _task_service
