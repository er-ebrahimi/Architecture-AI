# domain/interfaces.py
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from .value_objects import ImageFeatures, ImageGenerationRequest, ImageGenerationResult


class ImageAnalysisServiceInterface(ABC):
    """Interface for image analysis services following Interface Segregation Principle."""
    
    @abstractmethod
    async def analyze_image(self, image_bytes: bytes) -> ImageFeatures:
        """Analyze an image and return structured features."""
        pass


class ImageGenerationServiceInterface(ABC):
    """Interface for image generation services following Interface Segregation Principle."""
    
    @abstractmethod
    def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """Generate an image based on the request."""
        pass


class ProductRepositoryInterface(ABC):
    """Interface for product data access following Interface Segregation Principle."""
    
    @abstractmethod
    def create_product(self, source_url: str, image_filename: str, features: dict) -> int:
        """Create a new product and return its ID."""
        pass
    
    @abstractmethod
    def get_all_products(self) -> List[dict]:
        """Get all products from the database."""
        pass
    
    @abstractmethod
    def find_similar_products(self, query_tags: List[str], limit: int = 10) -> List[dict]:
        """Find products similar to the query tags."""
        pass


class ImageStorageInterface(ABC):
    """Interface for image storage operations following Interface Segregation Principle."""
    
    @abstractmethod
    def save_image(self, image_bytes: bytes, filename: str) -> str:
        """Save image bytes to storage and return the file path."""
        pass
    
    @abstractmethod
    def delete_image(self, filename: str) -> bool:
        """Delete an image from storage."""
        pass
    
    @abstractmethod
    def get_image_url(self, filename: str) -> str:
        """Get the full URL for an image."""
        pass


class ImageDownloadInterface(ABC):
    """Interface for downloading images from URLs following Interface Segregation Principle."""
    
    @abstractmethod
    async def download_image(self, image_url: str) -> Tuple[bytes, str]:
        """Download image from URL and return bytes and file extension."""
        pass
