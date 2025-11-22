# infrastructure/ai_services.py
import base64
import json
import os
import httpx
from typing import Optional
from ..domain.interfaces import ImageAnalysisServiceInterface, ImageGenerationServiceInterface
from ..domain.value_objects import ImageFeatures, ImageGenerationRequest, ImageGenerationResult


class OpenRouterImageAnalysisService(ImageAnalysisServiceInterface):
    """
    OpenRouter implementation of ImageAnalysisServiceInterface.
    Follows Single Responsibility Principle - handles only AI image analysis.
    """

    def __init__(self):
        """Initialize the OpenRouter client with API key from environment variables."""
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key or api_key == 'your_openrouter_api_key_here':
            self.api_key = None
            self.api_key_available = False
        else:
            self.api_key = api_key
            self.api_key_available = True
            self.base_url = "https://openrouter.ai/api/v1"

    def _encode_image_to_base64(self, image_bytes: bytes) -> str:
        """Encode image bytes to base64 string for OpenAI API."""
        return base64.b64encode(image_bytes).decode('utf-8')

    def _construct_analysis_prompt(self) -> str:
        """Construct the prompt for GPT-4 Vision to analyze interior design images."""
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

    async def analyze_image(self, image_bytes: bytes) -> ImageFeatures:
        """
        Analyze an image using OpenRouter's vision models and return structured features.
        
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
        
        # Use Grok 4 Fast model as specified
        models_to_try = [
            "x-ai/grok-4-fast:free"
        ]
        
        # Try each model until one works
        last_error = None
        
        for model in models_to_try:
            try:
                # Encode image to base64
                base64_image = self._encode_image_to_base64(image_bytes)
                
                # Construct the analysis prompt
                prompt = self._construct_analysis_prompt()
                
                # Prepare headers for OpenRouter API
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://architectai.local",
                    "X-Title": "ArchitectAI Visual Search"
                }
                
                # Prepare the request payload for OpenRouter
                payload = {
                    "model": model,
                    "messages": [
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
                                        "detail": "high"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.1,
                }
                
                # Make API call to OpenRouter
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=30.0
                    )
                    response.raise_for_status()
                    response_data = response.json()
                
                # Extract the JSON response
                ai_response = response_data["choices"][0]["message"]["content"].strip()
                
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
                    
            except httpx.HTTPStatusError as e:
                last_error = f"Model {model} failed: HTTP {e.response.status_code} - {e.response.text}"
                if e.response.status_code == 404:
                    # Model not found, try next one
                    continue
                else:
                    # Other HTTP error, try next model
                    continue
            except httpx.RequestError as e:
                last_error = f"Model {model} failed: Request error - {e}"
                continue
            except Exception as e:
                if "API" in str(e) or "openrouter" in str(e).lower():
                    last_error = f"Model {model} failed: OpenRouter API error - {e}"
                    continue
                else:
                    last_error = f"Model {model} failed: Image analysis error - {e}"
                    continue
        
        # If all models failed, raise the last error
        raise Exception(f"All models failed. Last error: {last_error}")


class ReplicateImageGenerationService(ImageGenerationServiceInterface):
    """
    Replicate implementation of ImageGenerationServiceInterface.
    Follows Single Responsibility Principle - handles only AI image generation.
    """

    def __init__(self):
        """Initialize the Replicate client with API token from environment variables."""
        self.api_token = os.getenv('REPLICATE_API_TOKEN')
        
        try:
            import replicate
            self.replicate_available = True
        except ImportError:
            self.replicate_available = False
            replicate = None
        
        if not self.replicate_available:
            self.api_available = False
            self.client = None
        elif not self.api_token or self.api_token == 'your_replicate_api_token_here':
            self.api_available = False
            self.client = None
        else:
            self.api_available = True
            self.client = replicate.Client(api_token=self.api_token)

    def _get_default_architectural_prompt(self) -> str:
        """Get the default architectural design prompt."""
        return (
            "Professional architectural interior design, modern space planning, "
            "sophisticated lighting design, functional furniture arrangement, "
            "harmonious color palette, premium materials and finishes, "
            "clean lines and geometric forms, optimal spatial flow, "
            "contemporary architectural elements, realistic rendering quality, "
            "natural lighting integration, professional photography style"
        )

    def _combine_prompts(self, user_prompt: str) -> str:
        """Combine user's custom prompt with the default architectural design prompt."""
        default_prompt = self._get_default_architectural_prompt()
        
        user_prompt_clean = user_prompt.strip()
        if not user_prompt_clean:
            return default_prompt
        
        return f"{default_prompt}, {user_prompt_clean}"

    def _prepare_image_for_replicate(self, image_bytes: bytes):
        """Prepare image bytes for Replicate API by ensuring proper format."""
        import io
        from PIL import Image
        
        # Open image with PIL to ensure compatibility
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary (Replicate works best with RGB)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save to BytesIO for Replicate
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=95)
        output.seek(0)
        
        return output

    def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """
        Generate an architectural interior design image using Replicate's ControlNet depth-to-image model.
        
        Args:
            request: Image generation request
            
        Returns:
            ImageGenerationResult: Result containing success status and generated image URLs
        """
        if not self.api_available:
            if not self.replicate_available:
                return ImageGenerationResult(
                    success=False,
                    error_message="Replicate package not installed. Please install it with: pip install replicate"
                )
            else:
                return ImageGenerationResult(
                    success=False,
                    error_message="Replicate API token not configured"
                )
        
        try:
            # Prepare the image for Replicate
            image_file = self._prepare_image_for_replicate(request.image_bytes)
            
            # Combine user prompt with architectural design expertise
            combined_prompt = self._combine_prompts(request.user_prompt)
            
            # Prepare input data for Replicate
            input_data = {
                "image": image_file,
                "prompt": combined_prompt,
                "negative_prompt": request.negative_prompt,
                "num_inference_steps": request.num_inference_steps,
            }
            
            # Run the Replicate model
            output = self.client.run(
                "jagilley/controlnet-depth2img:922c7bb67b87ec32cbc2fd11b1d5f94f0ba4f5519c4dbd02856376444127cc60",
                input=input_data
            )
            
            # Process all outputs
            generated_images = []
            if output and len(output) > 0:
                for index, item in enumerate(output):
                    if index == 0:
                        continue  # Skip the first output (usually depth map)
                    generated_images.append(str(item))
                
                if generated_images:
                    return ImageGenerationResult(
                        success=True,
                        generated_image_urls=generated_images
                    )
                else:
                    return ImageGenerationResult(
                        success=False,
                        error_message="No architectural images generated by the AI model"
                    )
            else:
                return ImageGenerationResult(
                    success=False,
                    error_message="No output generated by the AI model"
                )
                
        except Exception as e:
            return ImageGenerationResult(
                success=False,
                error_message=f"Image generation failed: {str(e)}"
            )
