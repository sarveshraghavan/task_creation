# Adaptive Learning System

An intelligent educational task generator that adapts to student performance using **Google Gemini LLM**.

## 🌟 Key Features

### Core Features
- ✅ **AI-Powered Task Generation** - Gemini LLM creates personalized learning tasks
- ✅ **Automated Scoring** - Objective evaluation with constructive feedback
- ✅ **Adaptive Difficulty** - Automatically adjusts based on student performance
- ✅ **Skill Progression** - Tracks and upgrades skill levels (beginner → expert)

### 🆕 Advanced Features
- ✅ **Automatic Supplementary Content** - Generates extra help when scores drop
- ✅ **Role-Based Assessments** - Teachers/admins can manually adjust difficulty
- ✅ **Score Drop Detection** - Monitors performance trends
- ✅ **Profile Management** - Comprehensive student data persistence

## 🏗️ Architecture Flow

```
Student Profile (Supabase)
        ↓
FastAPI derives task controls ← OR → Teacher submits assessment
        ↓                                      ↓
LLM generates TASK                    Manual difficulty adjustment
        ↓                                      ↓
Student completes task                         │
        ↓                                      │
FastAPI scores task ←──────────────────────────┘
        ↓
Score dropped? → Generate extra content
        ↓
Profile updated
        ↓
Next task adapts automatically
```

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup Supabase (run database/schema.sql)

# 3. Configure environment
cp .env.example .env
# Edit .env with your keys

# 4. Run the application
uvicorn main:app --reload

# 5. Visit http://localhost:8000/docs
```

See **[QUICKSTART.md](QUICKSTART.md)** for detailed setup.

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | 5-minute setup guide |
| [NEW_FEATURES.md](NEW_FEATURES.md) | Guide for new features  |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Complete implementation summary |
| [API.md](API.md) | Full API reference |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design & diagrams |
| [SETUP.md](SETUP.md) | Detailed setup & troubleshooting |

## 🔌 API Endpoints

### Students
- `POST /api/students` - Create student profile
- `GET /api/students/{id}` - Get student details
- `PATCH /api/students/{id}` - Update profile

### Tasks
- `POST /api/tasks/generate` - Generate task with custom parameters
- `POST /api/tasks/generate/auto` - Auto-adaptive task generation
- `POST /api/tasks/submit` - Submit & score (auto-generates content if score drops)
- `GET /api/tasks/{id}` - Get task details

### Supplementary Content 🆕
- `GET /api/supplementary/{id}` - Get extra learning content
- `GET /api/students/{id}/supplementary` - List all for student

### Manual Assessments 🆕
- `POST /api/assessments` - Teacher/admin submits evaluation
- `GET /api/students/{id}/assessments` - Get assessment history
- `GET /api/students/{id}/assessment-summary` - Get summary stats

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.10+)
- **Database**: Supabase (PostgreSQL)
- **LLM**: Google Gemini API
- **Validation**: Pydantic
- **Architecture**: Clean service-oriented design

## 📂 Project Structure

```
.
├── main.py                 # FastAPI application
├── config.py              # Configuration
├── models/                # Data models
│   ├── student.py
│   ├── task.py
│   ├── assessment.py     # 🆕
│   └── supplementary.py  # 🆕
├── services/              # Business logic
│   ├── llm_service.py
│   ├── task_service.py
│   ├── student_service.py
│   └── assessment_service.py  # 🆕
├── database/              # Data layer
│   ├── schema.sql        # 4 tables
│   └── supabase_client.py
└── prompts/              # LLM prompts
    ├── task_generator.py
    └── supplementary_content.py  # 🆕
```

## 🎯 How It Works

### 1. Automatic Adaptation
```python
# Student takes tasks
score = 85/100  # High score
→ Difficulty increases (+0.3)
→ Skill level may upgrade
→ Next task automatically harder
```

### 2. Score Drop Detection 🆕
```python
# Student's score drops
previous_score = 80
current_score = 60  # Dropped!
→ Gemini generates extra content:
   - Concept review
   - Worked examples
   - Practice tips
   - Common mistakes
→ Content linked to task
```

### 3. Manual Assessment 🆕
```python
# Teacher inputs scores
performance = 7.5/10
comprehension = 8.0/10
→ System calculates adjustment
→ Student difficulty updated
→ Assessment recorded
```

## 💡 Example Usage

See [example.py](example.py) and [test_demo.py](test_demo.py) for complete examples.

## 🔐 Environment

Required environment variables:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.0-flash-exp
```

## 📊 Features in Detail

### Adaptive Difficulty
- Automatically adjusts 0-10 scale
- Based on performance metrics
- Smooth progression

### Skill Progression  
- Four levels: beginner → intermediate → advanced → expert
- Auto-upgrades at 85%+ scores
- Tracks multiple skills independently

### Supplementary Content 🆕
- Auto-generated when performance drops
- Personalized to student's weak areas
- Structured learning materials

### Role-Based Assessment 🆕
- Teacher/admin manual evaluation
- Performance-based adjustments
- Complete audit trail

## 🎓 Built For

- Online learning platforms
- Tutoring applications
- Corporate training
- Self-study tools
- Educational games
- Assessment systems

---

**Built with ❤️ using FastAPI and Google Gemini**

Start learning adaptively! 🚀
