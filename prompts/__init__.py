"""Prompts package initialization."""

from prompts.task_generator import (
    get_task_generation_prompt,
    get_task_scoring_prompt
)
from prompts.supplementary_content import (
    get_supplementary_content_prompt,
    get_remedial_task_prompt
)

__all__ = [
    "get_task_generation_prompt",
    "get_task_scoring_prompt",
    "get_supplementary_content_prompt",
    "get_remedial_task_prompt",
]
