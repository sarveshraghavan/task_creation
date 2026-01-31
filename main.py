"""
FastAPI application for Adaptive Learning System.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from models import (
    StudentCreate, StudentProfile, StudentUpdate,
    TaskGenerationParams, GeneratedTask, TaskSubmission, TaskScore,
    ManualAssessment, AssessmentRecord
)
from models.supplementary import SupplementaryContent
from services import get_student_service, get_task_service
from services.assessment_service import get_assessment_service
from services.mark_based_service import (
    get_mark_based_service, 
    MarkBasedTaskRequest, 
    GeneratedTaskResponse
)
from database import get_db_client
from typing import List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Adaptive Learning System",
    description="AI-powered educational task generator using Gemini LLM",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# STUDENT ENDPOINTS
# ============================================================================

@app.post("/api/students", response_model=StudentProfile, status_code=status.HTTP_201_CREATED)
async def create_student(student: StudentCreate):
    """
    Create a new student profile.
    
    Args:
        student: Student creation data
        
    Returns:
        Created student profile
    """
    try:
        student_service = get_student_service()
        result = await student_service.create_student(student)
        logger.info(f"Created student: {result.id}")
        return result
    except Exception as e:
        logger.error(f"Error creating student: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/students/{student_id}", response_model=StudentProfile)
async def get_student(student_id: str):
    """
    Get student profile by ID.
    
    Args:
        student_id: Student ID
        
    Returns:
        Student profile
    """
    try:
        student_service = get_student_service()
        student = await student_service.get_student(student_id)
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return student
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting student: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/students/{student_id}", response_model=StudentProfile)
async def update_student(student_id: str, update_data: StudentUpdate):
    """
    Update student profile.
    
    Args:
        student_id: Student ID
        update_data: Fields to update
        
    Returns:
        Updated student profile
    """
    try:
        student_service = get_student_service()
        result = await student_service.update_student(student_id, update_data)
        logger.info(f"Updated student: {student_id}")
        return result
    except Exception as e:
        logger.error(f"Error updating student: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TASK ENDPOINTS
# ============================================================================

@app.post("/api/tasks/generate", response_model=GeneratedTask, status_code=status.HTTP_201_CREATED)
async def generate_task(params: TaskGenerationParams):
    """
    Generate a new learning task for a student.
    
    The task difficulty and parameters are adapted based on the student's profile.
    
    Args:
        params: Task generation parameters
        
    Returns:
        Generated task
    """
    try:
        task_service = get_task_service()
        task = await task_service.generate_task(params)
        logger.info(f"Generated task {task.id} for student {params.student_id}")
        return task
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tasks/generate/auto", response_model=GeneratedTask, status_code=status.HTTP_201_CREATED)
async def generate_adaptive_task(student_id: str, skill: str):
    """
    Generate a task with automatically derived parameters based on student profile.
    
    This endpoint analyzes the student's history and performance to determine
    optimal task difficulty, length, and repetition level.
    
    Args:
        student_id: Student ID
        skill: Skill to practice
        
    Returns:
        Generated task
    """
    try:
        task_service = get_task_service()
        
        # Get optimal parameters for next task
        params = await task_service.get_next_task_params(student_id, skill)
        
        # Generate task with those parameters
        task = await task_service.generate_task(params)
        
        logger.info(f"Auto-generated task {task.id} for student {student_id}")
        return task
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error auto-generating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/{task_id}", response_model=GeneratedTask)
async def get_task(task_id: str):
    """
    Get task details by ID.
    
    Args:
        task_id: Task ID
        
    Returns:
        Task details
    """
    try:
        task_service = get_task_service()
        task = await task_service.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tasks/submit", response_model=TaskScore)
async def submit_task(submission: TaskSubmission):
    """
    Submit a completed task for scoring.
    
    This will:
    1. Score the task using Gemini LLM
    2. Update the task status
    3. Update the student's profile and difficulty
    
    Args:
        submission: Task submission data
        
    Returns:
        Task score and feedback
    """
    try:
        task_service = get_task_service()
        score = await task_service.submit_task(submission)
        logger.info(f"Scored task {submission.task_id}: {score.score}/100")
        return score
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SUPPLEMENTARY CONTENT ENDPOINTS
# ============================================================================

@app.get("/api/supplementary/{content_id}", response_model=SupplementaryContent)
async def get_supplementary_content(content_id: str):
    """
    Get supplementary learning content by ID.
    
    This content is automatically generated when a student's score drops.
    
    Args:
        content_id: Supplementary content ID
        
    Returns:
        Supplementary learning content
    """
    try:
        db = get_db_client()
        content = await db.get_supplementary_content(content_id)
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        return SupplementaryContent(**content)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting supplementary content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/students/{student_id}/supplementary", response_model=List[SupplementaryContent])
async def get_student_supplementary_content(student_id: str, limit: int = 10):
    """
    Get all supplementary content generated for a student.
    
    Args:
        student_id: Student ID
        limit: Maximum number of items to return
        
    Returns:
        List of supplementary content
    """
    try:
        db = get_db_client()
        content_list = await db.get_student_supplementary_content(student_id, limit)
        return [SupplementaryContent(**c) for c in content_list]
    except Exception as e:
        logger.error(f"Error getting student supplementary content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ASSESSMENT ENDPOINTS (Role-based manual evaluation)
# ============================================================================

@app.post("/api/assessments", response_model=AssessmentRecord, status_code=status.HTTP_201_CREATED)
async def submit_assessment(assessment: ManualAssessment):
    """
    Submit a manual assessment from a teacher/admin.
    
    This allows educators to manually adjust student difficulty based on:
    - Direct observation
    - External test scores
    - Overall performance evaluation
    
    The system will:
    1. Calculate appropriate difficulty adjustment
    2. Update student profile
    3. Record the assessment
    
    Args:
        assessment: Manual assessment data
        
    Returns:
        Assessment record with applied changes
    """
    try:
        assessment_service = get_assessment_service()
        result = await assessment_service.submit_assessment(assessment)
        logger.info(
            f"Assessment submitted by {assessment.assessor_role.value} "
            f"'{assessment.assessor_name}' for student {assessment.student_id}"
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/students/{student_id}/assessments", response_model=List[AssessmentRecord])
async def get_student_assessments(student_id: str, limit: int = 20):
    """
    Get all manual assessments for a student.
    
    Args:
        student_id: Student ID
        limit: Maximum number of records to return
        
    Returns:
        List of assessment records
    """
    try:
        assessment_service = get_assessment_service()
        assessments = await assessment_service.get_student_assessments(student_id, limit)
        return assessments
    except Exception as e:
        logger.error(f"Error getting student assessments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/students/{student_id}/assessment-summary")
async def get_assessment_summary(student_id: str):
    """
    Get summary statistics of manual assessments for a student.
    
    Args:
        student_id: Student ID
        
    Returns:
        Summary statistics
    """
    try:
        assessment_service = get_assessment_service()
        summary = await assessment_service.get_recent_assessment_summary(student_id)
        return summary
    except Exception as e:
        logger.error(f"Error getting assessment summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MARK-BASED TASK GENERATION (No Database Access)
# ============================================================================

@app.post("/api/tasks/generate-from-marks", response_model=GeneratedTaskResponse)
async def generate_task_from_marks(request: MarkBasedTaskRequest):
    """
    Generate a task based purely on user-provided marks.
    
    **THIS ENDPOINT DOES NOT ACCESS ANY DATABASE.**
    
    Instead, the user (teacher/admin) provides:
    - Student name and subject
    - Recent marks/scores
    - Optional teacher notes
    
    The LLM then generates an appropriate task based ONLY on this information.
    
    This is ideal for:
    - Teachers who manually track student progress
    - Quick task generation without database setup
    - External assessment integration
    - Stateless task generation
    
    Args:
        request: Student marks and task preferences
        
    Returns:
        Generated task with reasoning
        
    Example Request:
        ```json
        {
            "marks": {
                "student_name": "Alice Johnson",
                "subject": "Algebra",
                "recent_marks": [75, 82, 78, 85],
                "total_marks": 100,
                "teacher_notes": "Shows improvement in quadratic equations"
            },
            "difficulty_preference": null,  # Auto-calculate from marks
            "task_length_preference": null  # Auto-determine
        }
        ```
    """
    try:
        mark_service = get_mark_based_service()
        task = await mark_service.generate_task_from_marks(request)
        
        logger.info(
            f"Generated mark-based task for {request.marks.student_name} "
            f"in {request.marks.subject} (difficulty: {task.calculated_difficulty})"
        )
        
        return task
    except Exception as e:
        logger.error(f"Error generating task from marks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Adaptive Learning System",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Adaptive Learning System API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "students": {
                "create": "POST /api/students",
                "get": "GET /api/students/{student_id}",
                "update": "PATCH /api/students/{student_id}"
            },
            "tasks": {
                "generate": "POST /api/tasks/generate",
                "generate_auto": "POST /api/tasks/generate/auto?student_id=X&skill=Y",
                "generate_from_marks": "POST /api/tasks/generate-from-marks (NO DATABASE - provide marks directly)",
                "get": "GET /api/tasks/{task_id}",
                "submit": "POST /api/tasks/submit (auto-generates extra content if score drops)"
            },
            "supplementary_content": {
                "get": "GET /api/supplementary/{content_id}",
                "list": "GET /api/students/{student_id}/supplementary"
            },
            "assessments": {
                "submit": "POST /api/assessments (role-based manual evaluation)",
                "list": "GET /api/students/{student_id}/assessments",
                "summary": "GET /api/students/{student_id}/assessment-summary"
            }
        },
        "features": {
            "automatic_difficulty_adaptation": "Adjusts based on performance",
            "supplementary_content_generation": "Auto-generates when scores drop",
            "role_based_assessment": "Teachers can manually adjust difficulty",
            "score_drop_detection": "LLM provides extra content to help improvement",
            "mark_based_generation": "Generate tasks from marks without database (stateless)",
            "no_database_llm": "LLM receives marks directly from user, no database access"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
