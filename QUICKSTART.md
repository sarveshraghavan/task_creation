# 🚀 Quick Start Guide

Get your Adaptive Learning System running in 5 minutes!

## Prerequisites

- Python 3.10+
- Supabase account (free)
- Gemini API key (free)

## 1. Install Dependencies ⚙️

```bash
pip install -r requirements.txt
```

## 2. Setup Supabase 🗄️

### A. Create Project
1. Go to [supabase.com](https://supabase.com) and create a project
2. Wait for it to initialize

### B. Create Database Tables
1. Open SQL Editor in Supabase
2. Copy and run `database/schema.sql`

### C. Get Credentials
1. Go to Settings → API
2. Copy **Project URL** and **anon public** key

## 3. Get Gemini API Key 🤖

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key

## 4. Configure Environment 🔧

```bash
# Create .env file from template
cp .env.example .env
```

Edit `.env`:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key
GEMINI_API_KEY=your-gemini-key
```

## 5. Run! 🎉

### Option A: Run the Demo

```bash
python test_demo.py
```

This will show you the complete flow in action!

### Option B: Start the API Server

```bash
uvicorn main:app --reload
```

Then visit:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## Try It Out! 🧪

### Using the API

```bash
# 1. Create a student
curl -X POST http://localhost:8000/api/students \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@test.com", "initial_skill": "math"}'

# 2. Generate a task (auto-adaptive)
curl -X POST "http://localhost:8000/api/tasks/generate/auto?student_id=YOUR_ID&skill=math"

# 3. Submit an answer
curl -X POST http://localhost:8000/api/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{"task_id": "TASK_ID", "student_id": "STUDENT_ID", "answer": "x = 5"}'
```

### Using Python

```python
import asyncio
from services import get_student_service, get_task_service
from models import StudentCreate, TaskLength, RepetitionLevel

async def quick_start():
    # Create student
    student_service = get_student_service()
    student = await student_service.create_student(
        StudentCreate(name="Test", email="test@example.com")
    )
    
    # Generate adaptive task
    task_service = get_task_service()
    params = await task_service.get_next_task_params(student.id, "algebra")
    task = await task_service.generate_task(params)
    
    print(f"Task: {task.title}")
    print(task.instructions)

asyncio.run(quick_start())
```

## Understanding the Flow 🔄

```
1. Student Profile Created
   ↓
2. System Analyzes Profile
   ↓
3. Gemini Generates Task
   ↓
4. Student Completes Task
   ↓
5. Gemini Scores Task
   ↓
6. Profile Auto-Updates
   ↓
7. Next Task Adapts Automatically
```

## What Happens Behind the Scenes? 🔍

When you submit a task:

1. **LLM scores** your answer (0-100)
2. **Success rate** updates automatically
3. **Difficulty adjusts**:
   - Score 90+? → Difficulty +0.5
   - Score 75+? → Difficulty +0.3
   - Score <40? → Difficulty -0.5
4. **Skill level upgrades** at 85%+ scores
5. **Next task** uses new difficulty

## File Structure 📁

```
.
├── main.py              ← FastAPI server
├── config.py            ← Environment config
├── models/              ← Data models
│   ├── student.py
│   └── task.py
├── services/            ← Business logic
│   ├── llm_service.py   ← Gemini integration
│   ├── task_service.py  ← Task generation
│   └── student_service.py
├── database/
│   ├── schema.sql       ← Run this in Supabase
│   └── supabase_client.py
└── prompts/
    └── task_generator.py ← LLM prompts
```

## Next Steps 📚

- See `SETUP.md` for detailed setup
- See `API.md` for complete API reference
- See `ARCHITECTURE.md` for system design
- See `example.py` for code examples

## Troubleshooting 🔧

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Supabase error"
- Check `.env` has correct URL and key
- Verify you ran `schema.sql` in Supabase

### "Gemini API error"
- Verify API key is correct
- Check you have quota remaining
- Try model `gemini-1.5-flash` if current model unavailable

## Support 💬

- Check `/docs` endpoint for API playground
- Review logs for error details
- Ensure all `.env` variables are set

---

**That's it! You're ready to build adaptive learning experiences! 🎓**
