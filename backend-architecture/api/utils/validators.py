# utils/validators.py
"""
Validation utilities following Single Responsibility Principle.
Each validator has a single responsibility for specific validation tasks.
"""

import re
from typing import Optional, Tuple


class ImageValidator:
    """Validator for image-related operations."""
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_CONTENT_TYPES = [
        'image/jpeg', 'image/jpg', 'image/png', 
        'image/gif', 'image/webp', 'image/bmp'
    ]
    
    @staticmethod
    def validate_file_size(file_size: int) -> Tuple[bool, Optional[str]]:
        """Validate file size is within limits."""
        if file_size > ImageValidator.MAX_FILE_SIZE:
            return False, f"File too large (max {ImageValidator.MAX_FILE_SIZE // (1024*1024)}MB)"
        return True, None
    
    @staticmethod
    def validate_content_type(content_type: str) -> Tuple[bool, Optional[str]]:
        """Validate content type is an image."""
        if not content_type.startswith('image/'):
            return False, "File must be an image"
        return True, None


class URLValidator:
    """Validator for URL-related operations."""
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, Optional[str]]:
        """Validate URL format."""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            return False, "Invalid URL format"
        return True, None


class PromptValidator:
    """Validator for prompt-related operations."""
    
    @staticmethod
    def validate_prompt(prompt: str) -> Tuple[bool, Optional[str]]:
        """Validate prompt is not empty and within reasonable length."""
        if not prompt or not prompt.strip():
            return False, "Prompt cannot be empty"
        
        if len(prompt.strip()) > 1000:
            return False, "Prompt too long (max 1000 characters)"
        
        return True, None
    
    @staticmethod
    def validate_inference_steps(steps: int) -> Tuple[bool, Optional[str]]:
        """Validate inference steps are within acceptable range."""
        if not (20 <= steps <= 50):
            return False, "Inference steps must be between 20 and 50"
        return True, None
