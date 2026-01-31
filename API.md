# API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API uses Supabase service role authentication through environment variables. Future versions will support user-level authentication.

---

## Endpoints

### Health Check

#### `GET /health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "Adaptive Learning System",
  "version": "1.0.0"
}
```

---

## Student Endpoints

### Create Student

#### `POST /api/students`

Create a new student profile.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "initial_skill": "algebra",
  "initial_level": "beginner"
}
```

**Fields:**
- `name` (required): Student's full name
- `email` (required): Unique email address
- `initial_skill` (optional): First skill to learn
- `initial_level` (optional): One of: `beginner`, `intermediate`, `advanced`, `expert`

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "skills": {
    "algebra": "beginner"
  },
  "current_difficulty": 1.0,
  "total_tasks_completed": 0,
  "success_rate": 0.0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

### Get Student

#### `GET /api/students/{student_id}`

Retrieve student profile by ID.

**Parameters:**
- `student_id` (path): Student UUID

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "skills": {
    "algebra": "intermediate"
  },
  "current_difficulty": 3.5,
  "total_tasks_completed": 10,
  "success_rate": 0.85,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T00:00:00Z"
}
```

---

### Update Student

#### `PATCH /api/students/{student_id}`

Update student profile.

**Request Body:**
```json
{
  "name": "John Smith",
  "skills": {
    "algebra": "advanced",
    "geometry": "beginner"
  },
  "current_difficulty": 5.0
}
```

**Response:** `200 OK` - Returns updated student profile

---

## Task Endpoints

### Generate Task

#### `POST /api/tasks/generate`

Generate a new task with specific parameters.

**Request Body:**
```json
{
  "student_id": "uuid",
  "skill": "algebra",
  "difficulty": 3.5,
  "task_length": "medium",
  "repetition": "medium"
}
```

**Fields:**
- `student_id` (required): Student UUID
- `skill` (required): Skill to practice
- `difficulty` (required): 0.0 to 10.0
- `task_length` (required): `short`, `medium`, or `long`
- `repetition` (required): `low`, `medium`, or `high`

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "student_id": "uuid",
  "skill": "algebra",
  "difficulty": 3.5,
  "task_length": "medium",
  "repetition": "medium",
  "title": "Solving Linear Equations",
  "instructions": "Solve the following equation for x...",
  "expected_input": "The value of x as a number or expression",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### Generate Adaptive Task

#### `POST /api/tasks/generate/auto`

Generate a task with automatically calculated optimal parameters.

**Query Parameters:**
- `student_id` (required): Student UUID
- `skill` (required): Skill to practice

**Example:**
```
POST /api/tasks/generate/auto?student_id=123e4567-e89b-12d3-a456-426614174000&skill=algebra
```

**Response:** `201 Created` - Same as Generate Task

**How it works:**
1. Analyzes student's recent performance
2. Calculates optimal difficulty based on success rate
3. Determines task length based on proficiency
4. Sets repetition level based on recent scores
5. Generates task with those parameters

---

### Get Task

#### `GET /api/tasks/{task_id}`

Retrieve task details by ID.

**Parameters:**
- `task_id` (path): Task UUID

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "student_id": "uuid",
  "skill": "algebra",
  "difficulty": 3.5,
  "task_length": "medium",
  "repetition": "medium",
  "title": "Solving Linear Equations",
  "instructions": "Solve the following equation...",
  "expected_input": "The value of x",
  "status": "scored",
  "score": 85.0,
  "feedback": "Good work! Minor calculation error in step 2.",
  "created_at": "2024-01-01T00:00:00Z",
  "submitted_at": "2024-01-01T00:15:00Z"
}
```

---

### Submit Task

#### `POST /api/tasks/submit`

Submit a completed task for scoring.

**Request Body:**
```json
{
  "task_id": "uuid",
  "student_id": "uuid",
  "answer": "x = 5",
  "time_spent_minutes": 10.5
}
```

**Fields:**
- `task_id` (required): Task UUID
- `student_id` (required): Student UUID
- `answer` (required): Student's answer/solution
- `time_spent_minutes` (optional): Time taken

**Response:** `200 OK`
```json
{
  "task_id": "uuid",
  "score": 85.0,
  "feedback": "Great work! You correctly solved the equation. Small calculation error in step 2.",
  "correct": true,
  "areas_for_improvement": [
    "Double-check arithmetic in multi-step problems",
    "Show all work for partial credit"
  ]
}
```

**Side Effects:**
- Task status updated to `scored`
- Student profile updated:
  - `total_tasks_completed` incremented
  - `success_rate` recalculated
  - `current_difficulty` adjusted
  - Skill level may be upgraded

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 404 Not Found
```json
{
  "detail": "Student not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error message describing the issue"
}
```

---

## Workflow Example

### Complete Learning Cycle

```bash
# 1. Create student
curl -X POST http://localhost:8000/api/students \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice",
    "email": "alice@example.com",
    "initial_skill": "algebra"
  }'
# Returns: {"id": "student-uuid", ...}

# 2. Generate adaptive task
curl -X POST "http://localhost:8000/api/tasks/generate/auto?student_id=student-uuid&skill=algebra"
# Returns: {"id": "task-uuid", "title": "...", "instructions": "...", ...}

# 3. Submit answer
curl -X POST http://localhost:8000/api/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "task-uuid",
    "student_id": "student-uuid",
    "answer": "x = 7"
  }'
# Returns: {"score": 90, "feedback": "...", ...}

# 4. Check updated profile
curl http://localhost:8000/api/students/student-uuid
# Returns updated difficulty and stats

# 5. Generate next task (automatically harder/easier based on performance)
curl -X POST "http://localhost:8000/api/tasks/generate/auto?student_id=student-uuid&skill=algebra"
```

---

## Interactive Documentation

Visit `http://localhost:8000/docs` for interactive Swagger documentation where you can test all endpoints.
