"""
Gemini LLM service for task generation and evaluation.
"""

import google.generativeai as genai
from config import get_settings
import re
from typing import Dict, Tuple


class LLMService:
    """Service for interacting with Gemini LLM."""
    
    def __init__(self):
        """Initialize the LLM service."""
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        
        # Generation config for consistent output
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
    
    async def generate_task(self, prompt: str) -> Dict[str, str]:
        """
        Generate a task using the LLM.
        
        Args:
            prompt: The formatted prompt for task generation
            
        Returns:
            Dict containing title, instructions, and expected_input
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            # Parse the response
            task_data = self._parse_task_response(response.text)
            return task_data
            
        except Exception as e:
            raise Exception(f"Failed to generate task: {str(e)}")
    
    async def score_task(self, prompt: str) -> Tuple[float, bool, str, list]:
        """
        Score a submitted task using the LLM.
        
        Args:
            prompt: The formatted prompt for task scoring
            
        Returns:
            Tuple of (score, is_correct, feedback, areas_for_improvement)
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            # Parse the scoring response
            score_data = self._parse_scoring_response(response.text)
            return score_data
            
        except Exception as e:
            raise Exception(f"Failed to score task: {str(e)}")
    
    def _parse_task_response(self, response_text: str) -> Dict[str, str]:
        """
        Parse the LLM response for task generation.
        
        Expected format:
        TITLE: [title]
        INSTRUCTIONS:
        [instructions]
        EXPECTED INPUT:
        [expected input]
        """
        try:
            # Extract title
            title_match = re.search(r'TITLE:\s*(.+?)(?:\n|$)', response_text, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else "Learning Task"
            
            # Extract instructions
            instructions_match = re.search(
                r'INSTRUCTIONS:\s*(.+?)(?=EXPECTED INPUT:|$)', 
                response_text, 
                re.IGNORECASE | re.DOTALL
            )
            instructions = instructions_match.group(1).strip() if instructions_match else ""
            
            # Extract expected input
            expected_match = re.search(
                r'EXPECTED INPUT:\s*(.+?)$', 
                response_text, 
                re.IGNORECASE | re.DOTALL
            )
            expected_input = expected_match.group(1).strip() if expected_match else ""
            
            return {
                "title": title,
                "instructions": instructions,
                "expected_input": expected_input
            }
        except Exception as e:
            # Fallback: return raw response
            return {
                "title": "Generated Task",
                "instructions": response_text,
                "expected_input": "Please provide your answer"
            }
    
    def _parse_scoring_response(self, response_text: str) -> Tuple[float, bool, str, list]:
        """
        Parse the LLM response for task scoring.
        
        Expected format:
        SCORE: [0-100]
        CORRECT: [yes/no]
        FEEDBACK:
        [feedback]
        AREAS FOR IMPROVEMENT:
        - [area 1]
        - [area 2]
        """
        try:
            # Extract score
            score_match = re.search(r'SCORE:\s*(\d+(?:\.\d+)?)', response_text, re.IGNORECASE)
            score = float(score_match.group(1)) if score_match else 0.0
            
            # Extract correct/incorrect
            correct_match = re.search(r'CORRECT:\s*(yes|no)', response_text, re.IGNORECASE)
            is_correct = correct_match.group(1).lower() == 'yes' if correct_match else score >= 70
            
            # Extract feedback
            feedback_match = re.search(
                r'FEEDBACK:\s*(.+?)(?=AREAS FOR IMPROVEMENT:|$)', 
                response_text, 
                re.IGNORECASE | re.DOTALL
            )
            feedback = feedback_match.group(1).strip() if feedback_match else ""
            
            # Extract areas for improvement
            areas_match = re.search(
                r'AREAS FOR IMPROVEMENT:\s*(.+?)$', 
                response_text, 
                re.IGNORECASE | re.DOTALL
            )
            areas_text = areas_match.group(1).strip() if areas_match else ""
            areas = [
                area.strip().lstrip('-•*').strip() 
                for area in areas_text.split('\n') 
                if area.strip() and area.strip().lstrip('-•*').strip()
            ]
            
            return (score, is_correct, feedback, areas)
            
        except Exception as e:
            # Fallback scoring
            return (0.0, False, f"Error parsing score: {str(e)}", [])
    
    async def generate_supplementary_content(self, prompt: str) -> Dict[str, any]:
        """
        Generate supplementary learning content for struggling students.
        
        Args:
            prompt: The formatted prompt for content generation
            
        Returns:
            Dict containing concept_review, key_points, worked_example, etc.
        """
        try:
            # Use higher temperature for more creative explanations
            config = self.generation_config.copy()
            config["temperature"] = 0.8
            config["max_output_tokens"] = 3072  # More tokens for detailed content
            
            response = self.model.generate_content(
                prompt,
                generation_config=config
            )
            
            # Parse the supplementary content response
            content_data = self._parse_supplementary_content(response.text)
            return content_data
            
        except Exception as e:
            raise Exception(f"Failed to generate supplementary content: {str(e)}")
    
    def _parse_supplementary_content(self, response_text: str) -> Dict[str, any]:
        """
        Parse the LLM response for supplementary content.
        
        Expected format:
        CONCEPT REVIEW: ...
        KEY POINTS:
        - Point 1
        - Point 2
        WORKED EXAMPLE: ...
        PRACTICE TIPS:
        - Tip 1
        COMMON MISTAKES TO AVOID:
        - Mistake 1
        """
        try:
            # Extract concept review
            concept_match = re.search(
                r'CONCEPT REVIEW:\s*(.+?)(?=KEY POINTS:|$)',
                response_text,
                re.IGNORECASE | re.DOTALL
            )
            concept_review = concept_match.group(1).strip() if concept_match else ""
            
            # Extract key points
            key_points_match = re.search(
                r'KEY POINTS:\s*(.+?)(?=WORKED EXAMPLE:|$)',
                response_text,
                re.IGNORECASE | re.DOTALL
            )
            key_points_text = key_points_match.group(1).strip() if key_points_match else ""
            key_points = [
                point.strip().lstrip('-•*').strip()
                for point in key_points_text.split('\n')
                if point.strip() and point.strip().lstrip('-•*').strip()
            ]
            
            # Extract worked example
            example_match = re.search(
                r'WORKED EXAMPLE:\s*(.+?)(?=PRACTICE TIPS:|$)',
                response_text,
                re.IGNORECASE | re.DOTALL
            )
            worked_example = example_match.group(1).strip() if example_match else ""
            
            # Extract practice tips
            tips_match = re.search(
                r'PRACTICE TIPS:\s*(.+?)(?=COMMON MISTAKES TO AVOID:|$)',
                response_text,
                re.IGNORECASE | re.DOTALL
            )
            tips_text = tips_match.group(1).strip() if tips_match else ""
            practice_tips = [
                tip.strip().lstrip('-•*').strip()
                for tip in tips_text.split('\n')
                if tip.strip() and tip.strip().lstrip('-•*').strip()
            ]
            
            # Extract common mistakes
            mistakes_match = re.search(
                r'COMMON MISTAKES TO AVOID:\s*(.+?)$',
                response_text,
                re.IGNORECASE | re.DOTALL
            )
            mistakes_text = mistakes_match.group(1).strip() if mistakes_match else ""
            common_mistakes = [
                mistake.strip().lstrip('-•*').strip()
                for mistake in mistakes_text.split('\n')
                if mistake.strip() and mistake.strip().lstrip('-•*').strip()
            ]
            
            return {
                "concept_review": concept_review,
                "key_points": key_points,
                "worked_example": worked_example,
                "practice_tips": practice_tips,
                "common_mistakes": common_mistakes
            }
            
        except Exception as e:
            # Fallback: return raw text
            return {
                "concept_review": response_text,
                "key_points": [],
                "worked_example": "",
                "practice_tips": [],
                "common_mistakes": []
            }



# Singleton instance
_llm_service = None


def get_llm_service() -> LLMService:
    """Get the singleton LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
