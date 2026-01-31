"""
Example: Mark-Based Task Generation (No Database Access)

This example demonstrates how to use the mark-based task generation endpoint.
The LLM receives marks directly from the user and generates tasks WITHOUT
accessing any database.

Perfect for:
- Teachers who manually track student marks
- Quick task generation without database setup
- External assessment integration
- Stateless, serverless task generation
"""

import asyncio
import httpx
import json


# Example 1: Generate task from student marks
async def example_1_basic_marks_to_task():
    """
    Basic example: Provide marks and get a task.
    """
    print("="*60)
    print("Example 1: Basic Mark-Based Task Generation")
    print("="*60)
    
    # Prepare the request
    request_data = {
        "marks": {
            "student_name": "Emma Wilson",
            "subject": "Algebra",
            "recent_marks": [65, 70, 68, 72],  # Recent test scores
            "total_marks": 100,
            "teacher_notes": "Student is improving but struggles with word problems"
        },
        # Let system auto-calculate difficulty and task length
        "difficulty_preference": None,
        "task_length_preference": None
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/tasks/generate-from-marks",
            json=request_data,
            timeout=30.0
        )
        
        if response.status_code == 200:
            task = response.json()
            print(f"\n✅ Task Generated Successfully!\n")
            print(f"Student: {task['student_name']}")
            print(f"Subject: {task['subject']}")
            print(f"Calculated Difficulty: {task['calculated_difficulty']}/10")
            print(f"\nTitle: {task['title']}")
            print(f"\nInstructions:\n{task['instructions']}")
            print(f"\nExpected Input:\n{task['expected_input']}")
            print(f"\nReasoning:\n{task['reasoning']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


# Example 2: High-performing student
async def example_2_high_performer():
    """
    Example with a high-performing student.
    """
    print("\n" + "="*60)
    print("Example 2: High-Performing Student")
    print("="*60)
    
    request_data = {
        "marks": {
            "student_name": "Ryan Chen",
            "subject": "Calculus",
            "recent_marks": [92, 95, 88, 94, 96],  # Consistently high scores
            "total_marks": 100,
            "teacher_notes": "Excels at derivatives, ready for advanced topics"
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/tasks/generate-from-marks",
            json=request_data,
            timeout=30.0
        )
        
        if response.status_code == 200:
            task = response.json()
            print(f"\n✅ Advanced Task Generated!\n")
            print(f"Difficulty: {task['calculated_difficulty']}/10")
            print(f"\n{task['title']}")
            print(f"\n{task['instructions'][:200]}...")
        else:
            print(f"❌ Error: {response.status_code}")


# Example 3: Struggling student
async def example_3_struggling_student():
    """
    Example with a struggling student who needs support.
    """
    print("\n" + "="*60)
    print("Example 3: Struggling Student (Supportive Task)")
    print("="*60)
    
    request_data = {
        "marks": {
            "student_name": "Sophie Martinez",
            "subject": "Fractions",
            "recent_marks": [45, 38, 42, 40],  # Low scores
            "total_marks": 100,
            "teacher_notes": "Needs foundational review and confidence building"
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/tasks/generate-from-marks",
            json=request_data,
            timeout=30.0
        )
        
        if response.status_code == 200:
            task = response.json()
            print(f"\n✅ Supportive Task Generated!\n")
            print(f"Difficulty: {task['calculated_difficulty']}/10 (Lower to build confidence)")
            print(f"\n{task['title']}")
            print(f"\nReasoning: {task['reasoning']}")
        else:
            print(f"❌ Error: {response.status_code}")


# Example 4: Manual difficulty override
async def example_4_manual_difficulty():
    """
    Example where teacher specifies exact difficulty level.
    """
    print("\n" + "="*60)
    print("Example 4: Manual Difficulty Override")
    print("="*60)
    
    request_data = {
        "marks": {
            "student_name": "Lucas Brown",
            "subject": "Geometry",
            "recent_marks": [75, 78, 80],
            "total_marks": 100
        },
        "difficulty_preference": 8.5,  # Teacher wants challenging task
        "task_length_preference": "long"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/tasks/generate-from-marks",
            json=request_data,
            timeout=30.0
        )
        
        if response.status_code == 200:
            task = response.json()
            print(f"\n✅ Custom Difficulty Task Generated!\n")
            print(f"Requested Difficulty: 8.5/10")
            print(f"Applied Difficulty: {task['calculated_difficulty']}/10")
            print(f"\n{task['title']}")
        else:
            print(f"❌ Error: {response.status_code}")


# Example 5: Batch generation for multiple students
async def example_5_batch_generation():
    """
    Generate tasks for multiple students at once.
    """
    print("\n" + "="*60)
    print("Example 5: Batch Task Generation")
    print("="*60)
    
    students = [
        {
            "student_name": "Anna Lee",
            "subject": "Chemistry",
            "recent_marks": [82, 85, 80],
            "total_marks": 100
        },
        {
            "student_name": "David Kim",
            "subject": "Chemistry",
            "recent_marks": [68, 72, 70],
            "total_marks": 100
        },
        {
            "student_name": "Olivia Johnson",
            "subject": "Chemistry",
            "recent_marks": [55, 58, 60],
            "total_marks": 100
        }
    ]
    
    async with httpx.AsyncClient() as client:
        tasks_generated = []
        
        for student_marks in students:
            request_data = {
                "marks": student_marks
            }
            
            response = await client.post(
                "http://localhost:8000/api/tasks/generate-from-marks",
                json=request_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                task = response.json()
                tasks_generated.append(task)
                print(f"✅ {student_marks['student_name']}: Difficulty {task['calculated_difficulty']}/10")
            else:
                print(f"❌ {student_marks['student_name']}: Error")
        
        print(f"\n📊 Generated {len(tasks_generated)} personalized tasks!")


async def main():
    """Run all examples."""
    print("\n🎓 MARK-BASED TASK GENERATION EXAMPLES")
    print("=" * 60)
    print("These examples show how to generate tasks WITHOUT database access.")
    print("The LLM receives marks directly and creates appropriate tasks.")
    print("=" * 60)
    
    try:
        # Run examples
        await example_1_basic_marks_to_task()
        
        # Uncomment to run other examples:
        # await example_2_high_performer()
        # await example_3_struggling_student()
        # await example_4_manual_difficulty()
        # await example_5_batch_generation()
        
        print("\n" + "="*60)
        print("✅ All examples completed!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n⚠️  Make sure the server is running:")
        print("   python main.py")


if __name__ == "__main__":
    asyncio.run(main())
