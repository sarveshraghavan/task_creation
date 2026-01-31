"""
Task generation prompt template for Gemini LLM.
"""


def get_task_generation_prompt(skill: str, difficulty: float, task_length: str, repetition: str) -> str:
    """
    Generate the prompt for task creation.
    
    Args:
        skill: The skill focus area
        difficulty: Difficulty level (0-10)
        task_length: short, medium, or long
        repetition: low, medium, or high
        
    Returns:
        Formatted prompt string
    """
    return f"""You are an educational task generator.

Generate ONE learning task.

Task Parameters:
- Skill focus: {skill}
- Difficulty: {difficulty}/10
- Task length: {task_length}
- Repetition level: {repetition}

Rules:
- Output ONLY the task
- No storytelling
- No feedback
- No encouragement
- No scoring
- Clear and simple instructions
- One task at a time

Task Format:
- Task title
- Instructions
- Input expected from student

Generate the task now in this exact format:

TITLE: [task title]

INSTRUCTIONS:
[clear step-by-step instructions]

EXPECTED INPUT:
[what the student should provide]"""


def get_task_scoring_prompt(task_instructions: str, student_answer: str, skill: str) -> str:
    """
    Generate the prompt for scoring a submitted task.
    
    Args:
        task_instructions: The original task instructions
        student_answer: Student's submitted answer
        skill: The skill being tested
        
    Returns:
        Formatted scoring prompt
    """
    return f"""You are an educational task evaluator.

Evaluate the student's answer objectively.

TASK INSTRUCTIONS:
{task_instructions}

STUDENT ANSWER:
{student_answer}

SKILL BEING TESTED: {skill}

Rules:
- Be objective and fair
- Score from 0 to 100
- Identify specific areas for improvement
- No encouragement or discouragement
- Focus on accuracy and completeness

Provide your evaluation in this exact format:

SCORE: [0-100]

CORRECT: [yes/no]

FEEDBACK:
[specific, constructive feedback]

AREAS FOR IMPROVEMENT:
- [area 1]
- [area 2]
- [area 3]"""
