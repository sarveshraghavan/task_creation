"""
Test script to demonstrate the Adaptive Learning System.

This script shows the complete flow:
1. Create student profile
2. Generate task
3. Submit task
4. See profile update
"""

import asyncio
from models import StudentCreate, TaskGenerationParams, TaskSubmission, TaskLength, RepetitionLevel
from services import get_student_service, get_task_service


async def main():
    """Run the demonstration."""
    
    print("=" * 80)
    print("ADAPTIVE LEARNING SYSTEM - DEMONSTRATION")
    print("=" * 80)
    print()
    
    student_service = get_student_service()
    task_service = get_task_service()
    
    # Step 1: Create a student
    print("Step 1: Creating student profile...")
    student_data = StudentCreate(
        name="Test Student",
        email=f"test_{asyncio.get_event_loop().time()}@example.com",
        initial_skill="algebra",
        initial_level="beginner"
    )
    
    student = await student_service.create_student(student_data)
    print(f"✓ Student created: {student.name} (ID: {student.id})")
    print(f"  Initial difficulty: {student.current_difficulty}")
    print(f"  Skills: {student.skills}")
    print()
    
    # Step 2: Generate a task
    print("Step 2: Generating task...")
    task_params = TaskGenerationParams(
        student_id=student.id,
        skill="algebra",
        difficulty=student.current_difficulty,
        task_length=TaskLength.SHORT,
        repetition=RepetitionLevel.MEDIUM
    )
    
    task = await task_service.generate_task(task_params)
    print(f"✓ Task generated: {task.title}")
    print(f"  Skill: {task.skill}")
    print(f"  Difficulty: {task.difficulty}")
    print()
    print("TASK INSTRUCTIONS:")
    print("-" * 80)
    print(task.instructions)
    print("-" * 80)
    print()
    print(f"EXPECTED INPUT: {task.expected_input}")
    print()
    
    # Step 3: Submit the task (simulated answer)
    print("Step 3: Submitting task...")
    print("(Using a sample answer for demonstration)")
    
    submission = TaskSubmission(
        task_id=task.id,
        student_id=student.id,
        answer="Sample student answer: x = 5",
        time_spent_minutes=10.0
    )
    
    score = await task_service.submit_task(submission)
    print(f"✓ Task scored: {score.score}/100")
    print(f"  Correct: {score.correct}")
    print()
    print("FEEDBACK:")
    print("-" * 80)
    print(score.feedback)
    print("-" * 80)
    
    if score.areas_for_improvement:
        print()
        print("AREAS FOR IMPROVEMENT:")
        for area in score.areas_for_improvement:
            print(f"  • {area}")
    print()
    
    # Step 4: View updated profile
    print("Step 4: Viewing updated student profile...")
    updated_student = await student_service.get_student(student.id)
    print(f"✓ Profile updated:")
    print(f"  New difficulty: {updated_student.current_difficulty}")
    print(f"  Tasks completed: {updated_student.total_tasks_completed}")
    print(f"  Success rate: {updated_student.success_rate:.2%}")
    print(f"  Skills: {updated_student.skills}")
    print()
    
    # Step 5: Get next task params (adaptive)
    print("Step 5: Getting adaptive task parameters for next task...")
    next_params = await task_service.get_next_task_params(student.id, "algebra")
    print(f"✓ Next task should be:")
    print(f"  Difficulty: {next_params.difficulty}")
    print(f"  Length: {next_params.task_length.value}")
    print(f"  Repetition: {next_params.repetition.value}")
    print()
    
    print("=" * 80)
    print("DEMONSTRATION COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
