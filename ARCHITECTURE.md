# Architecture Overview

## System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      ADAPTIVE LEARNING SYSTEM                    │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  Student Profile │  ← Stored in Supabase
│   (Supabase)     │     - Skills & levels
└────────┬─────────┘     - Current difficulty
         │               - Success rate
         │               - Task history
         ↓
┌────────────────────────────────┐
│    FastAPI Backend             │
│  ┌──────────────────────────┐  │
│  │  Task Parameter          │  │  ← Analyzes student data
│  │  Derivation              │  │  ← Calculates optimal:
│  │                          │  │     • Difficulty
│  │  • Success rate → Diff   │  │     • Task length
│  │  • Recent scores → Rep   │  │     • Repetition level
│  │  • Profile → Length      │  │
│  └──────────┬───────────────┘  │
│             ↓                   │
│  ┌──────────────────────────┐  │
│  │  Prompt Construction     │  │
│  │                          │  │  ← Builds LLM prompt with:
│  │  Template + Parameters   │  │     • Skill focus
│  └──────────┬───────────────┘  │     • Difficulty level
└─────────────┼───────────────────┘     • Task length
              ↓                         • Repetition level
┌──────────────────────────┐
│   Gemini LLM             │
│                          │  ← Generates task with:
│  You are an educational  │     • Title
│  task generator...       │     • Instructions
│                          │     • Expected input
│  Rules:                  │
│  - Output ONLY the task  │  ← Follows strict format
│  - No storytelling       │  ← No extra content
│  - Clear instructions    │
└──────────┬───────────────┘
           │
           ↓
┌────────────────────────┐
│   Generated TASK       │
│                        │
│  TITLE: [title]        │
│  INSTRUCTIONS: [...]   │  ← Presented to student
│  EXPECTED INPUT: [.]   │
└────────┬───────────────┘
         │
         │ Student completes task
         ↓
┌────────────────────────┐
│  Task Submission       │
│                        │  ← Student provides answer
│  { answer: "x = 5" }   │
└────────┬───────────────┘
         │
         ↓
┌──────────────────────────┐
│   Gemini LLM (Scoring)   │
│                          │  ← Evaluates submission:
│  Evaluate objectively    │     • Scores 0-100
│  SCORE: [0-100]          │     • Correct yes/no
│  CORRECT: [yes/no]       │     • Detailed feedback
│  FEEDBACK: [...]         │     • Areas to improve
│  AREAS: [...]            │
└──────────┬───────────────┘
           │
           ↓
┌────────────────────────────────┐
│    FastAPI Updates             │
│                                │
│  1. Update Task Status         │
│     status = "scored"          │
│     score = 85.0               │
│                                │
│  2. Update Student Profile     │  ← Adaptive adjustments
│     • total_tasks++            │
│     • success_rate updated     │
│     • difficulty adjusted      │
│     • skill level upgraded?    │
└────────┬───────────────────────┘
         │
         ↓
┌────────────────────────┐
│  Updated Profile       │
│                        │  ← Profile adapts to 
│  difficulty: 4.0 → 4.3 │     student performance
│  success_rate: 0.85    │
│  skills: {             │  ← Skill levels auto-upgrade
│    algebra: advanced   │     based on scores
│  }                     │
└────────┬───────────────┘
         │
         │ Cycle repeats
         ↓
┌────────────────────────┐
│  Next Task Generation  │  ← Automatically uses
│                        │     updated difficulty
│  New difficulty: 4.3   │     and parameters
│  Adapted to student    │
└────────────────────────┘
```

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                             │
│                    FastAPI Application                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Student    │  │     Task     │  │    Health    │     │
│  │  Endpoints   │  │  Endpoints   │  │    Check     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘     │
└─────────┼──────────────────┼─────────────────────────────┘
          │                  │
          ↓                  ↓
┌─────────────────────────────────────────────────────────────┐
│                        services/                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐ │
│  │ student_service │  │  task_service   │  │llm_service │ │
│  │                 │  │                 │  │            │ │
│  │ • Create        │  │ • Generate      │  │• Generate  │ │
│  │ • Update        │  │ • Score         │  │• Score     │ │
│  │ • Adapt profile │  │ • Get params    │  │• Parse     │ │
│  └────────┬────────┘  └────────┬────────┘  └─────┬──────┘ │
└───────────┼────────────────────┼──────────────────┼────────┘
            │                    │                  │
            ↓                    ↓                  ↓
┌─────────────────────┐  ┌─────────────┐  ┌────────────────┐
│    database/        │  │  prompts/   │  │  Gemini API    │
│  supabase_client    │  │             │  │                │
│                     │  │ • Generator │  │ google.        │
│ • CRUD operations   │  │ • Scorer    │  │ generativeai   │
│ • Students table    │  └─────────────┘  └────────────────┘
│ • Tasks table       │
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│   Supabase          │
│   PostgreSQL        │
│                     │
│ ┌─────────────────┐ │
│ │ students table  │ │
│ ├─────────────────┤ │
│ │ tasks table     │ │
│ └─────────────────┘ │
└─────────────────────┘
```

## Key Features

### 1. **Adaptive Difficulty**
- Automatically increases difficulty when student scores 75%+
- Decreases difficulty when scores drop below 60%
- Smooth progression prevents frustration or boredom

### 2. **Skill Level Progression**
- Beginner → Intermediate → Advanced → Expert
- Auto-upgrades when consistently scoring 85%+
- Tracks multiple skills independently

### 3. **Intelligent Task Parameters**
- **Task Length**: Short for struggling students, long for proficient ones
- **Repetition**: High repetition for low scores, low for mastery
- Analyzes recent performance trends

### 4. **LLM Integration**
- Uses Gemini with strict prompt templates
- Generates focused, educational tasks
- Provides objective, constructive feedback

### 5. **Data Persistence**
- All data stored in Supabase
- Complete audit trail of tasks and progress
- Row-level security for data protection

## Technologies Used

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | FastAPI | High-performance API framework |
| Database | Supabase (PostgreSQL) | Student profiles and task history |
| LLM | Google Gemini | Task generation and scoring |
| Language | Python 3.10+ | Core application logic |
| Validation | Pydantic | Data validation and serialization |

## Deployment Options

1. **Local Development**
   - `uvicorn main:app --reload`
   
2. **Production**
   - Railway, Render, or Fly.io
   - Docker container
   - Cloud Run or Lambda functions

3. **Database**
   - Supabase (managed PostgreSQL)
   - Automatic backups
   - Global CDN
