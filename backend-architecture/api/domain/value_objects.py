# domain/value_objects.py
from pydantic import BaseModel, Field
from typing import List


class IdentifiedObject(BaseModel):
    """Value object representing an identified object in an image with its attributes."""
    object_type: str = Field(..., description="The type of object identified, e.g., 'sofa', 'desk', 'lamp'.")
    attributes: List[str] = Field(..., description="A list of descriptive tags for the object, e.g., ['white', 'fabric', 'minimalist', 'wood legs'].")


class ImageFeatures(BaseModel):
    """Value object representing the complete feature analysis of an image."""
    main_objects: List[IdentifiedObject] = Field(..., description="A list of the primary objects identified in the image.")
    overall_style: List[str] = Field(..., description="Tags describing the overall style of the scene, e.g., ['modern', 'cozy', 'scandinavian'].")


class ProductSimilarityResult(BaseModel):
    """Value object representing a product similarity result."""
    product_id: int
    source_url: str
    image_filename: str
    image_url: str
    similarity_score: int
    features: dict
    created_at: str


class ImageGenerationRequest(BaseModel):
    """Value object representing an image generation request."""
    image_bytes: bytes
    user_prompt: str
    negative_prompt: str = "low quality, blurry, distorted, amateur, unprofessional, cluttered, poor lighting, unrealistic proportions"
    num_inference_steps: int = 20


class ImageGenerationResult(BaseModel):
    """Value object representing an image generation result."""
    success: bool
    generated_image_urls: List[str] = []
    error_message: str = ""
