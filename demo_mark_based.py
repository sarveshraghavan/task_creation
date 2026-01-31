"""
Simple demonstration of mark-based task generation logic.

This shows how the system calculates difficulty from marks
WITHOUT any database access.
"""


def calculate_difficulty_from_marks(recent_marks, total_marks=100):
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
    
    # Adjust based on trend
    if len(recent_marks) >= 2:
        if recent_marks[-1] > recent_marks[0]:
            difficulty += 0.5  # Improving
        elif recent_marks[-1] < recent_marks[0]:
            difficulty -= 0.5  # Declining
    
    return max(0.0, min(10.0, difficulty))


def main():
    """Demonstrate the mark-based difficulty calculation."""
    
    print("="*60)
    print("MARK-BASED TASK GENERATION DEMONSTRATION")
    print("="*60)
    print("\nThis shows how difficulty is calculated from marks")
    print("WITHOUT accessing any database.\n")
    
    # Test cases
    test_cases = [
        {
            "name": "High Performer",
            "marks": [92, 95, 88, 94],
            "description": "Consistently high marks"
        },
        {
            "name": "Improving Student",
            "marks": [60, 65, 70, 75],
            "description": "Marks are improving"
        },
        {
            "name": "Declining Student",
            "marks": [75, 70, 65, 60],
            "description": "Marks are declining"
        },
        {
            "name": "Average Student",
            "marks": [65, 70, 68, 72],
            "description": "Medium performance"
        },
        {
            "name": "Struggling Student",
            "marks": [45, 38, 42, 40],
            "description": "Needs support"
        }
    ]
    
    for case in test_cases:
        marks = case["marks"]
        avg = sum(marks) / len(marks)
        difficulty = calculate_difficulty_from_marks(marks)
        
        print(f"{case['name']}:")
        print(f"  Description: {case['description']}")
        print(f"  Recent Marks: {marks}")
        print(f"  Average: {avg:.1f}%")
        print(f"  ⭐ Calculated Difficulty: {difficulty:.1f}/10")
        print()
    
    print("="*60)
    print("KEY CONCEPTS")
    print("="*60)
    print()
    print("1. ❌ NO DATABASE ACCESS")
    print("   - User provides marks directly")
    print("   - System calculates difficulty from marks")
    print("   - LLM receives marks in prompt")
    print()
    print("2. ✅ AUTOMATIC DIFFICULTY ADJUSTMENT")
    print("   - High marks (90%+) → Difficulty 9.0")
    print("   - Medium marks (60-80%) → Difficulty 5.0-7.5")
    print("   - Low marks (<40%) → Difficulty 2.0")
    print()
    print("3. 📈 TREND DETECTION")
    print("   - Improving marks → +0.5 difficulty")
    print("   - Declining marks → -0.5 difficulty")
    print()
    print("4. 🎯 TASK PARAMETERS")
    print("   - Task length: Short/Medium/Long based on performance")
    print("   - Repetition: High repetition for struggling students")
    print("   - Content: LLM generates appropriate tasks")
    print()
    print("="*60)
    print("USAGE")
    print("="*60)
    print()
    print("To use this feature:")
    print("1. Start the server: python main.py")
    print("2. POST to: /api/tasks/generate-from-marks")
    print("3. Provide marks in JSON:")
    print('''
{
  "marks": {
    "student_name": "Alice",
    "subject": "Math",
    "recent_marks": [75, 80, 78],
    "total_marks": 100
  }
}
    ''')
    print()
    print("4. Receive generated task with difficulty matched to marks")
    print()
    print("="*60)
    print("✅ This approach is STATELESS and requires NO DATABASE!")
    print("="*60)


if __name__ == "__main__":
    main()
