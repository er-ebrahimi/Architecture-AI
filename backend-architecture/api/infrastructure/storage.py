# infrastructure/storage.py
import os
from typing import Tuple
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from ..domain.interfaces import ImageStorageInterface


class DjangoImageStorage(ImageStorageInterface):
    """
    Django implementation of ImageStorageInterface.
    Follows Single Responsibility Principle - handles only image storage operations.
    """
    
    def save_image(self, image_bytes: bytes, filename: str) -> str:
        """Save image bytes to storage and return the file path."""
        file_path = default_storage.save(
            filename,
            ContentFile(image_bytes)
        )
        return file_path
    
    def delete_image(self, filename: str) -> bool:
        """Delete an image from storage."""
        try:
            default_storage.delete(filename)
            return True
        except Exception:
            return False
    
    def get_image_url(self, filename: str) -> str:
        """Get the full URL for an image."""
        backend_url = os.getenv('BACKEND_URL', 'http://localhost:8000')
        return f"{backend_url}{settings.MEDIA_URL}{filename}"
