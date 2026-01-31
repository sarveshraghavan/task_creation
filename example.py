"""
Simple example showing how to use the Adaptive Learning System.
"""

import asyncio
from models import (
    StudentCreate, 
    TaskGenerationParams, 
    TaskSubmission,
    TaskLength,
    RepetitionLevel,
    SkillLevel
)
from services import get_student_service, get_task_service


async def example_workflow():
    """Example workflow demonstrating the adaptive learning flow."""
    
    student_service = get_student_service()
    task_service = get_task_service()
    
    # 1. Create a new student
    print("Creating student...")
    new_student = StudentCreate(
        name="Alice Smith",
        email="alice.smith@example.com",
        initial_skill="mathematics",
        initial_level=SkillLevel.BEGINNER
    )
    student = await student_service.create_student(new_student)
    print(f"Student created: {student.name} (ID: {student.id})")
    
    # 2. Generate first task with specific parameters
    print("\nGenerating first task...")
    task1 = await task_service.generate_task(
        TaskGenerationParams(
            student_id=student.id,
            skill="mathematics",
            difficulty=2.0,
            task_length=TaskLength.SHORT,
            repetition=RepetitionLevel.MEDIUM
        )
    )
    print(f"Task: {task1.title}")
    print(f"Instructions: {task1.instructions}")
    
    # 3. Simulate student completing the task
    print("\nSubmitting task...")
    score1 = await task_service.submit_task(
        TaskSubmission(
            task_id=task1.id,
            student_id=student.id,
            answer="Student's answer here...",
            time_spent_minutes=8.0
        )
    )
    print(f"Score: {score1.score}/100")
    print(f"Feedback: {score1.feedback}")
    
    # 4. Generate next task - system automatically adapts
    print("\nGenerating adaptive task...")
    next_params = await task_service.get_next_task_params(
        student.id, 
        "mathematics"
    )
    print(f"Next task difficulty: {next_params.difficulty}")
    print(f"Next task length: {next_params.task_length}")
    
    task2 = await task_service.generate_task(next_params)
    print(f"New task: {task2.title}")
    
    # 5. Check updated student profile
    updated_student = await student_service.get_student(student.id)
    print(f"\nStudent progress:")
    print(f"  Tasks completed: {updated_student.total_tasks_completed}")
    print(f"  Success rate: {updated_student.success_rate:.1%}")
    print(f"  Current difficulty: {updated_student.current_difficulty}")


async def simple_task_generation():
    """Simplest example - just generate a task."""
    
    task_service = get_task_service()
    
    # Assuming you already have a student_id
    student_id = "your-student-id-here"
    
    # Auto-generate optimal task
    task = await task_service.generate_task(
        await task_service.get_next_task_params(student_id, "algebra")
    )
    
    print(f"Task: {task.title}")
    print(task.instructions)


if __name__ == "__main__":
    print("Running example workflow...\n")
    asyncio.run(example_workflow())
