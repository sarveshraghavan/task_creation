# Setup Guide - Adaptive Learning System

## Prerequisites

- Python 3.10 or higher
- Supabase account (free tier works)
- Google Gemini API key

## Step-by-Step Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Supabase

#### 2.1 Create a Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Wait for the project to be ready

#### 2.2 Run Database Schema

1. Open the Supabase SQL Editor
2. Copy the contents of `database/schema.sql`
3. Paste and run the SQL script
4. Verify tables are created: `students` and `tasks`

#### 2.3 Get API Credentials

1. Go to Project Settings > API
2. Copy your project URL
3. Copy your `anon` public key (or `service_role` key for backend use)

### 3. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Save it securely

### 4. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-or-service-key

# Gemini API Configuration
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.0-flash-exp

# Application Configuration
APP_ENV=development
LOG_LEVEL=INFO
```

### 5. Run the Application

#### Option A: Run API Server

```bash
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

#### Option B: Run Demo Script

```bash
python test_demo.py
```

This will demonstrate the complete workflow.

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution**: Make sure you've installed all dependencies:
```bash
pip install -r requirements.txt
```

### Issue: "Supabase authentication failed"

**Solution**: 
1. Check your `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
2. Ensure the database schema has been created
3. Verify RLS policies allow access

### Issue: "Gemini API error"

**Solution**:
1. Verify your `GEMINI_API_KEY` is correct
2. Check you have API quota remaining
3. Try a different model if `gemini-2.0-flash-exp` is not available

### Issue: "Database table not found"

**Solution**:
1. Go to Supabase SQL Editor
2. Run the `database/schema.sql` script
3. Verify tables exist in the Table Editor

## Testing the API

### 1. Create a Student

```bash
curl -X POST "http://localhost:8000/api/students" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "initial_skill": "algebra",
    "initial_level": "beginner"
  }'
```

### 2. Generate a Task (Auto-Adaptive)

```bash
curl -X POST "http://localhost:8000/api/tasks/generate/auto?student_id=YOUR_STUDENT_ID&skill=algebra"
```

### 3. Submit a Task

```bash
curl -X POST "http://localhost:8000/api/tasks/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "YOUR_TASK_ID",
    "student_id": "YOUR_STUDENT_ID",
    "answer": "x = 5"
  }'
```

## Next Steps

- Integrate with a frontend application
- Add more skills and subjects
- Implement user authentication
- Add analytics and progress tracking
- Deploy to production (Vercel, Railway, etc.)

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review the logs for error messages
3. Verify all environment variables are set correctly
