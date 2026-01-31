"""
Supplementary content generation prompts for struggling students.
"""


def get_supplementary_content_prompt(
    skill: str,
    topic: str,
    current_score: float,
    previous_score: float,
    areas_of_difficulty: list[str]
) -> str:
    """
    Generate prompt for creating supplementary learning content.
    
    This is triggered when a student's score decreases.
    
    Args:
        skill: The skill being learned
        topic: Specific topic/concept
        current_score: Current task score
        previous_score: Previous task score
        areas_of_difficulty: Identified problem areas
        
    Returns:
        Formatted prompt for supplementary content
    """
    return f"""You are an educational content creator.

The student is struggling with {skill} - {topic}.

PERFORMANCE TREND:
- Previous score: {previous_score}/100
- Current score: {current_score}/100
- Score decreased by: {previous_score - current_score} points

AREAS OF DIFFICULTY:
{chr(10).join(f'- {area}' for area in areas_of_difficulty)}

Generate SUPPLEMENTARY LEARNING CONTENT to help this student improve.

Rules:
- Focus on the specific areas of difficulty
- Provide clear explanations with examples
- Include step-by-step breakdowns
- Add practice tips
- Keep it concise and actionable
- No discouragement

Content Format:

CONCEPT REVIEW:
[Brief review of the core concept]

KEY POINTS:
- [Point 1]
- [Point 2]
- [Point 3]

WORKED EXAMPLE:
[Step-by-step example demonstrating the concept]

PRACTICE TIPS:
- [Tip 1]
- [Tip 2]
- [Tip 3]

COMMON MISTAKES TO AVOID:
- [Mistake 1]
- [Mistake 2]
"""


def get_remedial_task_prompt(
    skill: str,
    difficulty: float,
    weak_areas: list[str]
) -> str:
    """
    Generate prompt for a remedial practice task.
    
    Args:
        skill: The skill to practice
        difficulty: Difficulty level (usually lower than current)
        weak_areas: Specific areas to focus on
        
    Returns:
        Formatted prompt for remedial task
    """
    return f"""You are an educational task generator.

Generate a REMEDIAL PRACTICE task for review.

Task Parameters:
- Skill: {skill}
- Difficulty: {difficulty}/10 (simplified for review)
- Focus areas: {', '.join(weak_areas)}

Rules:
- Make it EASIER than standard tasks
- Focus on foundational concepts
- Break down into smaller steps
- Include hints or guidance
- Build confidence through achievable challenges

Task Format:
- Task title
- Step-by-step instructions with guidance
- Expected input from student
- Helpful hints

Generate the remedial task now:

TITLE: [task title]

INSTRUCTIONS:
[clear, guided instructions with hints]

EXPECTED INPUT:
[what the student should provide]

HELPFUL HINTS:
- [Hint 1]
- [Hint 2]"""
