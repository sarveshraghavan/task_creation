# Mark-Based Task Generation 🎓

**Generate educational tasks from student marks WITHOUT database access!**

## Quick Overview

This feature allows the LLM to generate personalized educational tasks based purely on user-provided marks, without requiring any database setup.

### The Problem We Solved
Traditional approach: Database → LLM queries DB → Task generated  
**Our approach**: User provides marks → LLM generates task

### Key Benefits
- ✅ **No database required** - Completely stateless
- ✅ **Simple integration** - Just 3 files needed
- ✅ **Privacy-focused** - No data storage
- ✅ **Automatic difficulty** - Calculated from marks

## Quick Start

### 1. Install Dependencies
```bash
pip install google-generativeai pydantic pydantic-settings fastapi uvicorn
```

### 2. Set Environment Variables
```bash
export GEMINI_API_KEY=your_api_key_here
export GEMINI_MODEL=gemini-2.0-flash-exp
```

### 3. Start Server
```bash
python main.py
```

### 4. Test It
```bash
python demo_mark_based.py
```

## API Usage

### Endpoint
```
POST /api/tasks/generate-from-marks
```

### Request Example
```json
{
  "marks": {
    "student_name": "Alice Johnson",
    "subject": "Algebra",
    "recent_marks": [75, 82, 78, 85],
    "total_marks": 100,
    "teacher_notes": "Shows improvement"
  }
}
```

### Response Example
```json
{
  "student_name": "Alice Johnson",
  "subject": "Algebra",
  "calculated_difficulty": 8.0,
  "title": "Advanced Quadratic Equations",
  "instructions": "Solve the following problems...",
  "expected_input": "Show all work...",
  "reasoning": "Strong performance (80%) with improving trend..."
}
```

## How It Works

```
User provides marks: [75, 82, 78, 85]
         ↓
System calculates: avg=80%, trend=improving
         ↓
Difficulty: 8.0/10 (auto-calculated)
         ↓
LLM receives ALL context in prompt (no DB lookup!)
         ↓
Task generated with matched difficulty
```

## Files Overview

### Core Implementation
- **`services/mark_based_service.py`** - Main service (stateless, no database)
- **`services/llm_service.py`** - LLM wrapper
- **`config.py`** - Configuration

### Examples & Tests
- **`example_mark_based.py`** - API usage examples
- **`demo_mark_based.py`** - Standalone demo (no dependencies)
- **`test_mark_based.py`** - Unit tests

### Documentation
- **`MARK_BASED_INTEGRATION_QUICK_START.txt`** - Complete integration guide

## Difficulty Mapping

| Average Marks | Difficulty | Task Type |
|--------------|-----------|-----------|
| 90%+ | 9.0 | Expert level |
| 80-89% | 7.5 | Advanced |
| 70-79% | 6.0 | Intermediate |
| 60-69% | 5.0 | Medium |
| 50-59% | 4.0 | Below average |
| <40% | 2.0 | Supportive |

**Trend Adjustments:**
- Improving marks: +0.5 difficulty
- Declining marks: -0.5 difficulty

## Integration

### For Python Projects
```python
from services.mark_based_service import (
    get_mark_based_service,
    StudentMarks,
    MarkBasedTaskRequest
)

service = get_mark_based_service()
marks = StudentMarks(
    student_name="Alice",
    subject="Math",
    recent_marks=[75, 82, 78]
)
request = MarkBasedTaskRequest(marks=marks)
task = await service.generate_task_from_marks(request)
```

### Via REST API (Any Language)
```bash
curl -X POST http://localhost:8000/api/tasks/generate-from-marks \
  -H "Content-Type: application/json" \
  -d '{"marks": {"student_name": "Alice", "subject": "Math", "recent_marks": [75, 82, 78]}}'
```

## What You Need

**Required:**
- Python 3.10+
- Gemini API key
- Dependencies (see requirements.txt)

**Not Required:**
- ❌ Database (Supabase, PostgreSQL, etc.)
- ❌ Database credentials
- ❌ Student data storage
- ❌ ORM configuration

## Examples

Run the demos:
```bash
# Simple demonstration
python demo_mark_based.py

# Full API examples
python example_mark_based.py
```

## API Documentation

Interactive docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Complete Guide

See **`MARK_BASED_INTEGRATION_QUICK_START.txt`** for:
- Detailed integration instructions
- Code examples
- Troubleshooting
- Customization guide

## Repository

**GitHub**: https://github.com/sarveshraghavan/task_creation

## License

MIT License - See LICENSE file for details

---

**Built with ❤️ for teachers who want AI assistance without database complexity**
