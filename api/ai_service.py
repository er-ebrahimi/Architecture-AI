# ai_service.py
import base64
import json
import os
from typing import Optional
import openai
from django.conf import settings
from .schemas import ImageFeatures

class AIImageAnalysisService:
    """
    Service class for analyzing images using OpenAI's GPT-4 Vision API.
    Follows the Single Responsibility Principle by handling only AI-related operations.
    """

    def __init__(self):
        """Initialize the OpenAI client with API key from environment variables."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            self.client = None
            self.api_key_available = False
        else:
            self.client = openai.OpenAI(api_key=api_key)
            self.api_key_available = True

    def _encode_image_to_base64(self, image_bytes: bytes) -> str:
        """
        Encode image bytes to base64 string for OpenAI API.
        
        Args:
            image_bytes: Raw bytes of the image file
            
        Returns:
            str: Base64 encoded string of the image
        """
        return base64.b64encode(image_bytes).decode('utf-8')

    def _construct_analysis_prompt(self) -> str:
        """
        Construct the prompt for GPT-4 Vision to analyze interior design images.
        
        Returns:
            str: The prompt instructing the AI to return structured JSON
        """
        # Get the JSON schema of ImageFeatures for the prompt
        schema_json = ImageFeatures.model_json_schema()
        
        prompt = f"""
        Analyze the attached image of an interior design scene or product. 
        
        Your task:
        1. Identify the main objects/furniture in the image
        2. Describe their key visual attributes (color, material, style, etc.)
        3. Determine the overall design style of the scene
        
        CRITICAL: Respond ONLY with a valid JSON object that strictly adheres to the following Pydantic schema:
        
        {json.dumps(schema_json, indent=2)}
        
        Guidelines:
        - For object_type: Use simple, clear names like 'sofa', 'chair', 'table', 'lamp', etc.
        - For attributes: Include visual descriptors like colors, materials, styles, patterns
        - For overall_style: Use recognized design terms like 'modern', 'scandinavian', 'industrial', 'minimalist', etc.
        - Be specific but concise in your descriptions
        - Only include objects that are clearly visible and identifiable
        
        Return only valid JSON, no additional text or explanation.
        """
        return prompt

    async def get_image_features(self, image_bytes: bytes) -> ImageFeatures:
        """
        Analyze an image using OpenAI's GPT-4 Vision API and return structured features.
        
        Args:
            image_bytes: Raw bytes of the image file
            
        Returns:
            ImageFeatures: Pydantic model containing structured analysis results
            
        Raises:
            ValueError: If API response is invalid or cannot be parsed
            Exception: If API call fails
        """
        if not self.api_key_available:
            # Return mock data when API key is not available
            return ImageFeatures(
                main_objects=[
                    {"object_type": "chair", "attributes": ["wooden", "modern", "minimalist"]},
                    {"object_type": "table", "attributes": ["glass", "contemporary", "sleek"]}
                ],
                overall_style=["modern", "minimalist", "contemporary"]
            )
        
        try:
            # Encode image to base64
            base64_image = self._encode_image_to_base64(image_bytes)
            
            # Construct the analysis prompt
            prompt = self._construct_analysis_prompt()
            
            # Make API call to OpenAI GPT-4 Vision
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"  # Use high detail for better analysis
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1,  # Low temperature for consistent results
            )
            
            # Extract the JSON response
            ai_response = response.choices[0].message.content.strip()
            
            # Parse and validate the JSON response using Pydantic
            try:
                # Remove any potential markdown code blocks if present
                if ai_response.startswith('```json'):
                    ai_response = ai_response[7:]
                if ai_response.endswith('```'):
                    ai_response = ai_response[:-3]
                ai_response = ai_response.strip()
                
                # Parse JSON and validate with Pydantic schema
                features_dict = json.loads(ai_response)
                image_features = ImageFeatures(**features_dict)
                
                return image_features
                
            except json.JSONDecodeError as e:
                raise ValueError(f"AI response is not valid JSON: {e}. Response: {ai_response}")
            except Exception as e:
                raise ValueError(f"AI response does not match expected schema: {e}. Response: {ai_response}")
                
        except Exception as e:
            if "API" in str(e) or "openai" in str(e).lower():
                raise Exception(f"OpenAI API error: {e}")
            else:
                raise Exception(f"Image analysis error: {e}")

# Singleton instance for dependency injection
ai_service = AIImageAnalysisService()

