"""
Mark-based task generation service.

This service generates tasks purely based on user-provided marks,
without accessing any database. The LLM receives marks directly
and creates appropriate tasks.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from services.llm_service import get_llm_service
from models.task import TaskLength, RepetitionLevel
import logging

logger = logging.getLogger(__name__)


class StudentMarks(BaseModel):
    """User-provided student marks/scores."""
    student_name: str = Field(..., description="Student's name")
    subject: str = Field(..., description="Subject or skill area")
    recent_marks: List[float] = Field(..., description="List of recent marks (0-100)")
    total_marks: float = Field(100, description="Total marks possible")
    teacher_notes: Optional[str] = Field(None, description="Optional teacher observations")


class MarkBasedTaskRequest(BaseModel):
    """Request for generating a task based on marks."""
    marks: StudentMarks
    difficulty_preference: Optional[float] = Field(
        None, 
        ge=0, 
        le=10,
        description="Optional difficulty level (0-10). If not provided, calculated from marks"
    )
    task_length_preference: Optional[str] = Field(
        None,
        description="Optional task length: 'short', 'medium', or 'long'"
    )


class GeneratedTaskResponse(BaseModel):
    """Task generated based on marks."""
    student_name: str
    subject: str
    calculated_difficulty: float
    title: str
    instructions: str
    expected_input: str
    reasoning: str = Field(..., description="Why this difficulty was chosen")


class MarkBasedTaskService:
    """
    Service for generating tasks based purely on user-provided marks.
    
    This service is STATELESS and does NOT access any database.
    All information is provided by the user, and the LLM generates
    tasks based solely on that information.
    """
    
    def __init__(self):
        self.llm = get_llm_service()
    
    def _calculate_difficulty_from_marks(
        self, 
        recent_marks: List[float],
        total_marks: float = 100
    ) -> float:
        """
        Calculate appropriate difficulty level based on marks.
        
        Args:
            recent_marks: List of recent marks (0-100)
            total_marks: Maximum marks possible
            
        Returns:
            Difficulty level (0-10)
        """
        if not recent_marks:
            return 5.0  # Default medium difficulty
        
        # Calculate percentage
        avg_mark = sum(recent_marks) / len(recent_marks)
        percentage = (avg_mark / total_marks) * 100
        
        # Map percentage to difficulty (0-10)
        # Higher marks = higher difficulty
        if percentage >= 90:
            difficulty = 9.0
        elif percentage >= 80:
            difficulty = 7.5
        elif percentage >= 70:
            difficulty = 6.0
        elif percentage >= 60:
            difficulty = 5.0
        elif percentage >= 50:
            difficulty = 4.0
        elif percentage >= 40:
            difficulty = 3.0
        else:
            difficulty = 2.0
        
        # Adjust based on consistency
        if len(recent_marks) >= 2:
            # If marks are improving, slightly increase difficulty
            if recent_marks[-1] > recent_marks[0]:
                difficulty += 0.5
            # If marks are declining, decrease difficulty
            elif recent_marks[-1] < recent_marks[0]:
                difficulty -= 0.5
        
        return max(0.0, min(10.0, difficulty))
    
    def _determine_task_length(self, recent_marks: List[float]) -> str:
        """
        Determine task length based on marks.
        
        Args:
            recent_marks: List of recent marks
            
        Returns:
            Task length: 'short', 'medium', or 'long'
        """
        if not recent_marks:
            return "medium"
        
        avg_mark = sum(recent_marks) / len(recent_marks)
        
        if avg_mark >= 75:
            return "long"  # Strong students get comprehensive tasks
        elif avg_mark >= 50:
            return "medium"
        else:
            return "short"  # Struggling students get focused tasks
    
    def _determine_repetition_level(self, recent_marks: List[float]) -> str:
        """
        Determine repetition level based on marks.
        
        Args:
            recent_marks: List of recent marks
            
        Returns:
            Repetition level: 'low', 'medium', or 'high'
        """
        if not recent_marks:
            return "medium"
        
        avg_mark = sum(recent_marks) / len(recent_marks)
        
        if avg_mark >= 80:
            return "low"  # Minimal repetition for strong students
        elif avg_mark >= 60:
            return "medium"
        else:
            return "high"  # High repetition for struggling students
    
    async def generate_task_from_marks(
        self, 
        request: MarkBasedTaskRequest
    ) -> GeneratedTaskResponse:
        """
        Generate a task based purely on user-provided marks.
        
        NO DATABASE ACCESS. All information comes from the request.
        
        Args:
            request: Task request with student marks
            
        Returns:
            Generated task with reasoning
        """
        marks = request.marks
        
        # Calculate difficulty from marks if not provided
        difficulty = request.difficulty_preference
        if difficulty is None:
            difficulty = self._calculate_difficulty_from_marks(
                marks.recent_marks,
                marks.total_marks
            )
        
        # Determine task length
        task_length = request.task_length_preference
        if task_length is None:
            task_length = self._determine_task_length(marks.recent_marks)
        
        # Determine repetition level
        repetition = self._determine_repetition_level(marks.recent_marks)
        
        # Build context for LLM
        avg_mark = sum(marks.recent_marks) / len(marks.recent_marks) if marks.recent_marks else 0
        percentage = (avg_mark / marks.total_marks) * 100
        
        # Check for improvement or decline
        trend = "stable"
        if len(marks.recent_marks) >= 2:
            if marks.recent_marks[-1] > marks.recent_marks[0]:
                trend = "improving"
            elif marks.recent_marks[-1] < marks.recent_marks[0]:
                trend = "declining"
        
        # Generate prompt for LLM
        prompt = self._build_task_generation_prompt(
            student_name=marks.student_name,
            subject=marks.subject,
            recent_marks=marks.recent_marks,
            average_percentage=percentage,
            trend=trend,
            difficulty=difficulty,
            task_length=task_length,
            repetition=repetition,
            teacher_notes=marks.teacher_notes
        )
        
        logger.info(
            f"Generating task for {marks.student_name} in {marks.subject} "
            f"(avg: {percentage:.1f}%, difficulty: {difficulty})"
        )
        
        # Call LLM to generate task
        task_content = await self.llm.generate_task(prompt)
        
        # Build reasoning
        reasoning = self._build_reasoning(
            avg_percentage=percentage,
            trend=trend,
            difficulty=difficulty,
            task_length=task_length,
            repetition=repetition
        )
        
        return GeneratedTaskResponse(
            student_name=marks.student_name,
            subject=marks.subject,
            calculated_difficulty=difficulty,
            title=task_content["title"],
            instructions=task_content["instructions"],
            expected_input=task_content["expected_input"],
            reasoning=reasoning
        )
    
    def _build_task_generation_prompt(
        self,
        student_name: str,
        subject: str,
        recent_marks: List[float],
        average_percentage: float,
        trend: str,
        difficulty: float,
        task_length: str,
        repetition: str,
        teacher_notes: Optional[str]
    ) -> str:
        """Build the LLM prompt for task generation."""
        
        marks_str = ", ".join([f"{m:.1f}" for m in recent_marks])
        
        prompt = f"""You are an educational task generator creating personalized learning tasks.

STUDENT CONTEXT:
- Student Name: {student_name}
- Subject: {subject}
- Recent Marks: {marks_str}
- Average Score: {average_percentage:.1f}%
- Performance Trend: {trend}
{f"- Teacher Notes: {teacher_notes}" if teacher_notes else ""}

TASK REQUIREMENTS:
- Difficulty Level: {difficulty}/10
- Task Length: {task_length}
- Repetition Level: {repetition}

Based on the student's marks and performance trend, generate an appropriate learning task.

IMPORTANT RULES:
1. Output ONLY the task in the specified format below
2. No storytelling or conversational text
3. The task should match the {difficulty}/10 difficulty level
4. Consider the performance trend when designing the task
5. If marks are declining, provide supportive and encouraging tasks
6. If marks are improving, challenge the student appropriately

OUTPUT FORMAT:
TITLE: [Clear, engaging title for the task]

INSTRUCTIONS:
[Detailed, clear instructions for the student. 
- For 'short' tasks: 1-2 problems/questions
- For 'medium' tasks: 3-4 problems/questions  
- For 'long' tasks: 5-7 problems/questions
- For 'high' repetition: Include similar practice problems
- For 'low' repetition: Include varied problem types]

EXPECTED INPUT:
[Description of what the student should submit]

Generate the task now:"""
        
        return prompt
    
    def _build_reasoning(
        self,
        avg_percentage: float,
        trend: str,
        difficulty: float,
        task_length: str,
        repetition: str
    ) -> str:
        """Build reasoning for why this task was generated."""
        
        reasoning_parts = []
        
        # Performance-based reasoning
        if avg_percentage >= 80:
            reasoning_parts.append(
                f"Strong performance ({avg_percentage:.1f}%) indicates readiness for "
                f"challenging material at difficulty {difficulty}/10."
            )
        elif avg_percentage >= 60:
            reasoning_parts.append(
                f"Moderate performance ({avg_percentage:.1f}%) suggests balanced "
                f"difficulty at {difficulty}/10 with {repetition} repetition."
            )
        else:
            reasoning_parts.append(
                f"Lower performance ({avg_percentage:.1f}%) requires supportive "
                f"difficulty at {difficulty}/10 with {repetition} repetition for mastery."
            )
        
        # Trend-based reasoning
        if trend == "improving":
            reasoning_parts.append(
                "Positive trend detected - slightly increased challenge to maintain momentum."
            )
        elif trend == "declining":
            reasoning_parts.append(
                "Declining trend detected - adjusted difficulty to rebuild confidence."
            )
        
        # Task parameters
        reasoning_parts.append(
            f"Task length is '{task_length}' to {'maximize learning' if task_length == 'long' else 'maintain focus'}."
        )
        
        return " ".join(reasoning_parts)


# Singleton instance
_mark_based_service = None


def get_mark_based_service() -> MarkBasedTaskService:
    """Get the singleton mark-based task service instance."""
    global _mark_based_service
    if _mark_based_service is None:
        _mark_based_service = MarkBasedTaskService()
    return _mark_based_service
