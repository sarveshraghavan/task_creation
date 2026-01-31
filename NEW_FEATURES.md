# New Features Guide

## Overview

This guide explains the two major new features added to the Adaptive Learning System:

1. **Automatic Supplementary Content Generation** - When scores drop
2. **Role-Based Manual Assessments** - Teacher/admin can adjust difficulty

---

## Feature 1: Automatic Supplementary Content Generation

### What It Does

When a student's score **drops below their previous score**, the system automatically:
1. Detects the score decrease
2. Generates supplementary learning content using Gemini LLM
3. Provides extra help to improve understanding

### How It Works

```
Student submits task
        ↓
System scores task (e.g., 65/100)
        ↓
System checks previous score (e.g., 80/100)
        ↓
Score dropped by 15 points! 🚨
        ↓
Gemini generates supplementary content:
    - Concept Review
    - Key Points
    - Worked Example
    - Practice Tips
    - Common Mistakes to Avoid
        ↓
Content saved and linked to task
```

### Supplementary Content Structure

The LLM generates structured content:

```
CONCEPT REVIEW:
A clear explanation of the core concept the student struggled with.

KEY POINTS:
- Main point 1
- Main point 2
- Main point 3

WORKED EXAMPLE:
Step-by-step demonstration showing how to solve a similar problem.

PRACTICE TIPS:
- Tip 1: How to approach this type of problem
- Tip 2: What to watch out for
- Tip 3: Practice strategies

COMMON MISTAKES TO AVOID:
- Mistake 1: Why it's wrong
- Mistake 2: How to avoid it
```

### API Usage

#### Submit a Task (Automatic)

```bash
curl -X POST "http://localhost:8000/api/tasks/submit" \\
  -H "Content-Type: application/json" \\
  -d '{
    "task_id": "task-uuid",
    "student_id": "student-uuid",
    "answer": "student answer"
  }'
```

**Response** (if score dropped):
```json
{
  "task_id": "task-uuid",
  "score": 65.0,
  "feedback": "Good attempt, but...",
  "correct": false,
  "areas_for_improvement": ["area1", "area2"],
  "supplementary_content_id": "content-uuid"  // ← Extra content generated!
}
```

#### Get Supplementary Content

```bash
curl "http://localhost:8000/api/supplementary/content-uuid"
```

**Response**:
```json
{
  "id": "content-uuid",
  "student_id": "student-uuid",
  "task_id": "task-uuid",
  "skill": "algebra",
  "current_score": 65.0,
  "previous_score": 80.0,
  "score_drop": 15.0,
  "concept_review": "Let's review the concept of...",
  "key_points": [
    "Point 1",
    "Point 2",
    "Point 3"
  ],
  "worked_example": "Step-by-step solution...",
  "practice_tips": [
    "Tip 1",
    "Tip 2"
  ],
  "common_mistakes": [
    "Mistake 1",
    "Mistake 2"
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "viewed": false
}
```

#### List All Supplementary Content for Student

```bash
curl "http://localhost:8000/api/students/student-uuid/supplementary"
```

---

## Feature 2: Role-Based Manual Assessments

### What It Does

Allows **teachers, admins, supervisors, or parents** to:
1. Manually evaluate student performance
2. Input scores based on external assessments
3. Automatically adjust student difficulty
4. Override or supplement automated adjustments

### When to Use

- After parent-teacher conferences
- Following external standardized tests
- Based on in-class observations
- When automated system doesn't reflect true ability

### How It Works

```
Teacher observes student
        ↓
Teacher submits assessment:
    - Performance Score: 7.5/10
    - Comprehension Level: 8.0/10
    - Optional: Skill-specific scores
    - Optional: Recommended difficulty
    - Notes about student
        ↓
System calculates difficulty adjustment:
    - High scores (8.5+) → Increase +1.5
    - Good scores (7-8.5) → Increase +1.0
    - Average (5.5-7) → Increase +0.5
    - Below average (4-5.5) → No change
    - Poor (<4) → Decrease difficulty
        ↓
Student profile updated automatically
        ↓
Next tasks use new difficulty
```

### Assessor Roles

- **teacher**: Classroom teachers
- **admin**: School administrators
- **supervisor**: Department heads
- **parent**: Parents with educator access

### API Usage

#### Submit Manual Assessment

```bash
curl -X POST "http://localhost:8000/api/assessments" \\
  -H "Content-Type: application/json" \\
  -d '{
    "student_id": "student-uuid",
    "assessor_role": "teacher",
    "assessor_name": "Ms. Johnson",
    "performance_score": 7.5,
    "comprehension_level": 8.0,
    "skill_scores": {
      "algebra": 7.0,
      "geometry": 8.5
    },
    "notes": "Student shows strong grasp but needs more practice with word problems",
    "recommended_difficulty": 7.5
  }'
```

**Response**:
```json
{
  "id": "assessment-uuid",
  "student_id": "student-uuid",
  "assessor_role": "teacher",
  "assessor_name": "Ms. Johnson",
  "performance_score": 7.5,
  "comprehension_level": 8.0,
  "skill_scores": {
    "algebra": 7.0,
    "geometry": 8.5
  },
  "notes": "Student shows strong grasp...",
  "recommended_difficulty": 7.5,
  "difficulty_before": 5.0,
  "difficulty_after": 7.0,  // ← Adjusted!
  "adjustment_applied": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Get Student Assessments

```bash
curl "http://localhost:8000/api/students/student-uuid/assessments"
```

#### Get Assessment Summary

```bash
curl "http://localhost:8000/api/students/student-uuid/assessment-summary"
```

**Response**:
```json
{
  "total_assessments": 5,
  "average_performance": 7.8,
  "average_comprehension": 8.2,
  "total_difficulty_change": 2.5,
  "assessors": [
    "teacher: Ms. Johnson",
    "admin: Dr. Smith",
    "parent: Mr. Doe"
  ]
}
```

---

## Combined Workflow Example

### Scenario: Student Struggling After Teacher Assessment

```
Day 1: Teacher Assessment
    Teacher submits low scores (4.5/10)
    → Difficulty automatically decreased to 3.0

Day 2: Student Attempts Task at Difficulty 3.0
    Scores 55/100 (lower than previous 70)
    → Supplementary content auto-generated
    → Student reviews extra material

Day 3: Student Tries Again
    Scores 75/100 (improvement!)
    → Difficulty adjusts back up to 3.5
    → No supplementary content needed

Day 4: Teacher Reassesses
    Performance improved to 6.5/10
    → Difficulty increases to 5.0
```

---

## Database Schema

### supplementary_content Table

```sql
- id: UUID
- student_id: UUID (FK)
- task_id: UUID (FK)
- skill: TEXT
- current_score: FLOAT
- previous_score: FLOAT
- score_drop: FLOAT
- concept_review: TEXT
- key_points: JSONB
- worked_example: TEXT
- practice_tips: JSONB
- common_mistakes: JSONB
- created_at: TIMESTAMP
- viewed: BOOLEAN
```

### assessments Table

```sql
- id: UUID
- student_id: UUID (FK)
- assessor_role: TEXT
- assessor_name: TEXT  
- performance_score: FLOAT (0-10)
- comprehension_level: FLOAT (0-10)
- skill_scores: JSONB
- notes: TEXT
- recommended_difficulty: FLOAT
- difficulty_before: FLOAT
- difficulty_after: FLOAT
- adjustment_applied: BOOLEAN
- created_at: TIMESTAMP
```

---

## Benefits

### Automatic Supplementary Content
✅ Immediate help when students struggle  
✅ Personalized to specific weaknesses  
✅ No manual intervention required  
✅ Encourages self-paced learning  

### Role-Based Assessments
✅ Incorporates human expertise  
✅ Handles non-digital assessments  
✅ Provides oversight and control  
✅ Builds comprehensive student profile  

---

## Setup

Both features are automatically enabled. Just:

1. **Run the updated database schema**:
   ```sql
   -- Execute database/schema.sql in Supabase
   ```

2. **Restart your server**:
   ```bash
   uvicorn main:app --reload
   ```

3. **Start using**:
   - Submit tasks → Auto-generates content if scores drop
   - Submit assessments → Manual control for educators

---

## Future Enhancements

Potential additions:
- Email notifications when supplementary content is generated
- Interactive exercises in supplementary content
- Video explanations via gen AI
- Parent portal for viewing assessments
- Bulk assessment imports from CSV
- Analytics dashboard for teachers

---

## Summary

🎯 **Score drops?** → Extra content auto-generated  
👨‍🏫 **Teacher input?** → Manual difficulty adjustment  
🔄 **Combined?** → Powerful adaptive learning system!
