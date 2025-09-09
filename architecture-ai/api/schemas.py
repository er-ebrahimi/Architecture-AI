# schemas.py
from pydantic import BaseModel, Field
from typing import List

class IdentifiedObject(BaseModel):
    """Represents an identified object in an image with its attributes."""
    object_type: str = Field(..., description="The type of object identified, e.g., 'sofa', 'desk', 'lamp'.")
    attributes: List[str] = Field(..., description="A list of descriptive tags for the object, e.g., ['white', 'fabric', 'minimalist', 'wood legs'].")

class ImageFeatures(BaseModel):
    """Represents the complete feature analysis of an image."""
    main_objects: List[IdentifiedObject] = Field(..., description="A list of the primary objects identified in the image.")
    overall_style: List[str] = Field(..., description="Tags describing the overall style of the scene, e.g., ['modern', 'cozy', 'scandinavian'].")

