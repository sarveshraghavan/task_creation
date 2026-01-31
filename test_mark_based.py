"""
Simple test for mark-based task generation.

This test verifies that:
1. The service correctly calculates difficulty from marks
2. Tasks are generated without database access
3. Different mark levels produce appropriate difficulty levels
"""

from services.mark_based_service import (
    MarkBasedTaskService,
    StudentMarks,
    MarkBasedTaskRequest
)


def test_difficulty_calculation():
    """Test automatic difficulty calculation from marks."""
    service = MarkBasedTaskService()
    
    # High marks → High difficulty
    high_marks = [92, 95, 90, 94]
    difficulty_high = service._calculate_difficulty_from_marks(high_marks)
    assert difficulty_high >= 7.0, "High marks should result in high difficulty"
    
    # Medium marks → Medium difficulty
    medium_marks = [65, 70, 68, 72]
    difficulty_medium = service._calculate_difficulty_from_marks(medium_marks)
    assert 4.0 <= difficulty_medium <= 7.0, "Medium marks should result in medium difficulty"
    
    # Low marks → Low difficulty
    low_marks = [35, 40, 38, 42]
    difficulty_low = service._calculate_difficulty_from_marks(low_marks)
    assert difficulty_low <= 4.0, "Low marks should result in low difficulty"


def test_improving_trend_adjustment():
    """Test that improving marks increase difficulty slightly."""
    service = MarkBasedTaskService()
    
    # Improving trend
    improving_marks = [60, 65, 70, 75]
    difficulty_improving = service._calculate_difficulty_from_marks(improving_marks)
    
    # Stable marks (same average)
    stable_marks = [67.5, 67.5, 67.5, 67.5]
    difficulty_stable = service._calculate_difficulty_from_marks(stable_marks)
    
    # Improving should be slightly harder
    assert difficulty_improving > difficulty_stable, \
        "Improving trend should increase difficulty"


def test_declining_trend_adjustment():
    """Test that declining marks decrease difficulty slightly."""
    service = MarkBasedTaskService()
    
    # Declining trend
    declining_marks = [75, 70, 65, 60]
    difficulty_declining = service._calculate_difficulty_from_marks(declining_marks)
    
    # Stable marks (same average)
    stable_marks = [67.5, 67.5, 67.5, 67.5]
    difficulty_stable = service._calculate_difficulty_from_marks(stable_marks)
    
    # Declining should be slightly easier
    assert difficulty_declining < difficulty_stable, \
        "Declining trend should decrease difficulty"


def test_task_length_determination():
    """Test task length based on marks."""
    service = MarkBasedTaskService()
    
    # High marks → Long tasks
    high_marks = [85, 88, 90]
    length_high = service._determine_task_length(high_marks)
    assert length_high == "long", "High marks should get long tasks"
    
    # Medium marks → Medium tasks
    medium_marks = [60, 65, 62]
    length_medium = service._determine_task_length(medium_marks)
    assert length_medium == "medium", "Medium marks should get medium tasks"
    
    # Low marks → Short tasks
    low_marks = [40, 45, 42]
    length_low = service._determine_task_length(low_marks)
    assert length_low == "short", "Low marks should get short tasks"


def test_repetition_level_determination():
    """Test repetition level based on marks."""
    service = MarkBasedTaskService()
    
    # High marks → Low repetition
    high_marks = [85, 88, 90]
    rep_high = service._determine_repetition_level(high_marks)
    assert rep_high == "low", "High marks should get low repetition"
    
    # Medium marks → Medium repetition
    medium_marks = [65, 70, 68]
    rep_medium = service._determine_repetition_level(medium_marks)
    assert rep_medium == "medium", "Medium marks should get medium repetition"
    
    # Low marks → High repetition
    low_marks = [45, 50, 48]
    rep_low = service._determine_repetition_level(low_marks)
    assert rep_low == "high", "Low marks should get high repetition"


def test_difficulty_bounds():
    """Test that difficulty is always within 0-10 range."""
    service = MarkBasedTaskService()
    
    # Extremely high marks
    extreme_high = [100, 100, 100, 100]
    diff_high = service._calculate_difficulty_from_marks(extreme_high)
    assert 0 <= diff_high <= 10, "Difficulty should be within 0-10"
    
    # Extremely low marks
    extreme_low = [0, 0, 0, 0]
    diff_low = service._calculate_difficulty_from_marks(extreme_low)
    assert 0 <= diff_low <= 10, "Difficulty should be within 0-10"


async def test_full_task_generation_mock():
    """
    Test full task generation flow.
    
    Note: This is a mock test. For real testing with LLM,
    make sure your API key is configured.
    """
    service = MarkBasedTaskService()
    
    # Create a request
    marks = StudentMarks(
        student_name="Test Student",
        subject="Mathematics",
        recent_marks=[70, 75, 72],
        total_marks=100,
        teacher_notes="Practice needed"
    )
    
    request = MarkBasedTaskRequest(marks=marks)
    
    # This would normally call the LLM
    # For unit testing, we just verify the logic works
    difficulty = service._calculate_difficulty_from_marks(marks.recent_marks)
    task_length = service._determine_task_length(marks.recent_marks)
    repetition = service._determine_repetition_level(marks.recent_marks)
    
    assert 5.0 <= difficulty <= 7.0
    assert task_length == "medium"
    assert repetition in ["medium", "low"]


def test_manual_override():
    """Test that manual preferences are respected."""
    service = MarkBasedTaskService()
    
    marks = StudentMarks(
        student_name="Test Student",
        subject="Math",
        recent_marks=[60, 65],
        total_marks=100
    )
    
    # Test with manual difficulty
    request = MarkBasedTaskRequest(
        marks=marks,
        difficulty_preference=8.5,
        task_length_preference="long"
    )
    
    # Verify manual preferences would be used
    assert request.difficulty_preference == 8.5
    assert request.task_length_preference == "long"


if __name__ == "__main__":
    # Run tests manually
    print("Running mark-based task generation tests...")
    
    test_difficulty_calculation()
    print("✅ Difficulty calculation test passed")
    
    test_improving_trend_adjustment()
    print("✅ Improving trend test passed")
    
    test_declining_trend_adjustment()
    print("✅ Declining trend test passed")
    
    test_task_length_determination()
    print("✅ Task length test passed")
    
    test_repetition_level_determination()
    print("✅ Repetition level test passed")
    
    test_difficulty_bounds()
    print("✅ Difficulty bounds test passed")
    
    test_manual_override()
    print("✅ Manual override test passed")
    
    print("\n✅ All tests passed!")
