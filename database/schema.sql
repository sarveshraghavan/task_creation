-- Adaptive Learning System Database Schema
-- Run this in your Supabase SQL Editor

-- ============================================================================
-- STUDENTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    skills JSONB DEFAULT '{}'::jsonb,
    current_difficulty FLOAT DEFAULT 1.0 CHECK (current_difficulty >= 0 AND current_difficulty <= 10),
    total_tasks_completed INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0 CHECK (success_rate >= 0 AND success_rate <= 1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_students_email ON students(email);

-- Create index on created_at for sorting
CREATE INDEX IF NOT EXISTS idx_students_created_at ON students(created_at DESC);


-- ============================================================================
-- TASKS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    skill TEXT NOT NULL,
    difficulty FLOAT NOT NULL CHECK (difficulty >= 0 AND difficulty <= 10),
    task_length TEXT NOT NULL CHECK (task_length IN ('short', 'medium', 'long')),
    repetition TEXT NOT NULL CHECK (repetition IN ('low', 'medium', 'high')),
    
    -- Task content
    title TEXT NOT NULL,
    instructions TEXT NOT NULL,
    expected_input TEXT NOT NULL,
    
    -- Status and results
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'submitted', 'scored')),
    score FLOAT CHECK (score >= 0 AND score <= 100),
    feedback TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    submitted_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_tasks_student_id ON tasks(student_id);
CREATE INDEX IF NOT EXISTS idx_tasks_skill ON tasks(skill);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);

-- Composite index for student's recent tasks
CREATE INDEX IF NOT EXISTS idx_tasks_student_created ON tasks(student_id, created_at DESC);


-- ============================================================================
-- SUPPLEMENTARY_CONTENT TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS supplementary_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    skill TEXT NOT NULL,
    
    -- Score drop trigger
    current_score FLOAT NOT NULL,
    previous_score FLOAT NOT NULL,
    score_drop FLOAT NOT NULL,
    
    -- Generated content
    concept_review TEXT NOT NULL,
    key_points JSONB DEFAULT '[]'::jsonb,
    worked_example TEXT NOT NULL,
    practice_tips JSONB DEFAULT '[]'::jsonb,
    common_mistakes JSONB DEFAULT '[]'::jsonb,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    viewed BOOLEAN DEFAULT FALSE,
    helpful BOOLEAN
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_supplementary_student_id ON supplementary_content(student_id);
CREATE INDEX IF NOT EXISTS idx_supplementary_task_id ON supplementary_content(task_id);
CREATE INDEX IF NOT EXISTS idx_supplementary_created_at ON supplementary_content(created_at DESC);


-- ============================================================================
-- ASSESSMENTS TABLE (Role-based manual assessments)
-- ============================================================================

CREATE TABLE IF NOT EXISTS assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    
    -- Assessor information
    assessor_role TEXT NOT NULL CHECK (assessor_role IN ('teacher', 'admin', 'supervisor', 'parent')),
    assessor_name TEXT NOT NULL,
    
    -- Assessment scores
    performance_score FLOAT NOT NULL CHECK (performance_score >= 0 AND performance_score <= 10),
    comprehension_level FLOAT NOT NULL CHECK (comprehension_level >= 0 AND comprehension_level <= 10),
    skill_scores JSONB,
    
    -- Notes and recommendations
    notes TEXT,
    recommended_difficulty FLOAT CHECK (recommended_difficulty >= 0 AND recommended_difficulty <= 10),
    
    -- Impact tracking
    difficulty_before FLOAT NOT NULL,
    difficulty_after FLOAT NOT NULL,
    adjustment_applied BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_assessments_student_id ON assessments(student_id);
CREATE INDEX IF NOT EXISTS idx_assessments_created_at ON assessments(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_assessments_role ON assessments(assessor_role);


-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at on students table
DROP TRIGGER IF EXISTS update_students_updated_at ON students;
CREATE TRIGGER update_students_updated_at
    BEFORE UPDATE ON students
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE supplementary_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all operations for service role
CREATE POLICY "Service role has full access to students"
    ON students
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role has full access to tasks"
    ON tasks
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role has full access to supplementary_content"
    ON supplementary_content
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role has full access to assessments"
    ON assessments
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Policy: Allow authenticated users to read their own data
CREATE POLICY "Users can view their own student profile"
    ON students
    FOR SELECT
    TO authenticated
    USING (auth.uid()::text = id::text);

CREATE POLICY "Users can view their own tasks"
    ON tasks
    FOR SELECT
    TO authenticated
    USING (student_id::text = auth.uid()::text);

CREATE POLICY "Users can view their own supplementary content"
    ON supplementary_content
    FOR SELECT
    TO authenticated
    USING (student_id::text = auth.uid()::text);

CREATE POLICY "Users can view their own assessments"
    ON assessments
    FOR SELECT
    TO authenticated
    USING (student_id::text = auth.uid()::text);



-- ============================================================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================================================

-- Uncomment to insert sample data
/*
INSERT INTO students (name, email, skills, current_difficulty) VALUES
    ('Alice Johnson', 'alice@example.com', '{"algebra": "beginner", "geometry": "intermediate"}', 2.5),
    ('Bob Smith', 'bob@example.com', '{"calculus": "advanced"}', 6.0);
*/
