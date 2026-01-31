"""
Supabase database client.
"""

from supabase import create_client, Client
from config import get_settings
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Client for interacting with Supabase database."""
    
    def __init__(self):
        """Initialize Supabase client."""
        settings = get_settings()
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    
    # Student operations
    async def create_student(self, student_data: Dict) -> Dict:
        """Create a new student profile."""
        try:
            result = self.client.table('students').insert(student_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating student: {e}")
            raise
    
    async def get_student(self, student_id: str) -> Optional[Dict]:
        """Get student profile by ID."""
        try:
            result = self.client.table('students').select('*').eq('id', student_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting student: {e}")
            raise
    
    async def update_student(self, student_id: str, update_data: Dict) -> Dict:
        """Update student profile."""
        try:
            result = self.client.table('students').update(update_data).eq('id', student_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error updating student: {e}")
            raise
    
    async def list_students(self, limit: int = 100) -> List[Dict]:
        """List all students."""
        try:
            result = self.client.table('students').select('*').limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error listing students: {e}")
            raise
    
    # Task operations
    async def create_task(self, task_data: Dict) -> Dict:
        """Create a new task."""
        try:
            result = self.client.table('tasks').insert(task_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise
    
    async def get_task(self, task_id: str) -> Optional[Dict]:
        """Get task by ID."""
        try:
            result = self.client.table('tasks').select('*').eq('id', task_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting task: {e}")
            raise
    
    async def update_task(self, task_id: str, update_data: Dict) -> Dict:
        """Update task."""
        try:
            result = self.client.table('tasks').update(update_data).eq('id', task_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            raise
    
    async def get_student_tasks(self, student_id: str, limit: int = 50) -> List[Dict]:
        """Get all tasks for a student."""
        try:
            result = (
                self.client.table('tasks')
                .select('*')
                .eq('student_id', student_id)
                .order('created_at', desc=True)
                .limit(limit)
                .execute()
            )
            return result.data
        except Exception as e:
            logger.error(f"Error getting student tasks: {e}")
            raise
    
    # Supplementary content operations
    async def create_supplementary_content(self, content_data: Dict) -> Dict:
        """Create supplementary learning content."""
        try:
            result = self.client.table('supplementary_content').insert(content_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating supplementary content: {e}")
            raise
    
    async def get_supplementary_content(self, content_id: str) -> Optional[Dict]:
        """Get supplementary content by ID."""
        try:
            result = self.client.table('supplementary_content').select('*').eq('id', content_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting supplementary content: {e}")
            raise
    
    async def get_student_supplementary_content(self, student_id: str, limit: int = 10) -> List[Dict]:
        """Get all supplementary content for a student."""
        try:
            result = (
                self.client.table('supplementary_content')
                .select('*')
                .eq('student_id', student_id)
                .order('created_at', desc=True)
                .limit(limit)
                .execute()
            )
            return result.data
        except Exception as e:
            logger.error(f"Error getting student supplementary content: {e}")
            raise
    
    # Assessment operations
    async def create_assessment(self, assessment_data: Dict) -> Dict:
        """Create a manual assessment record."""
        try:
            result = self.client.table('assessments').insert(assessment_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating assessment: {e}")
            raise
    
    async def get_student_assessments(self, student_id: str, limit: int = 20) -> List[Dict]:
        """Get all assessments for a student."""
        try:
            result = (
                self.client.table('assessments')
                .select('*')
                .eq('student_id', student_id)
                .order('created_at', desc=True)
                .limit(limit)
                .execute()
            )
            return result.data
        except Exception as e:
            logger.error(f"Error getting student assessments: {e}")
            raise



# Singleton instance
_db_client = None


def get_db_client() -> SupabaseClient:
    """Get the singleton database client instance."""
    global _db_client
    if _db_client is None:
        _db_client = SupabaseClient()
    return _db_client
