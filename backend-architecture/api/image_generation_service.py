# image_generation_service.py
import os
import io
from typing import Optional, Tuple
from PIL import Image
from django.conf import settings

try:
    import replicate
    REPLICATE_AVAILABLE = True
except ImportError:
    REPLICATE_AVAILABLE = False
    replicate = None


class AIImageGenerationService:
    """
    Service class for generating architectural interior design images using Replicate's ControlNet.
    Follows the Single Responsibility Principle by handling only AI image generation operations.
    """

    def __init__(self):
        """Initialize the Replicate client with API token from environment variables."""
        self.api_token = os.getenv('REPLICATE_API_TOKEN')
        print(f"DEBUG: REPLICATE_API_TOKEN = {self.api_token}")
        print(f"DEBUG: REPLICATE_AVAILABLE = {REPLICATE_AVAILABLE}")
        
        if not REPLICATE_AVAILABLE:
            print("DEBUG: Replicate package not available")
            self.api_available = False
            self.client = None
        elif not self.api_token or self.api_token == 'your_replicate_api_token_here':
            print("DEBUG: API token not configured or is placeholder")
            self.api_token = None
            self.api_available = False
            self.client = None
        else:
            print("DEBUG: API token found, initializing client")
            self.api_available = True
            self.client = replicate.Client(api_token=self.api_token)

    def _get_default_architectural_prompt(self) -> str:
        """
        Get the default architectural design prompt that defines the AI's core purpose.
        
        Returns:
            str: Default prompt focusing on architectural interior design
        """
        return (
            "Professional architectural interior design, modern space planning, "
            "sophisticated lighting design, functional furniture arrangement, "
            "harmonious color palette, premium materials and finishes, "
            "clean lines and geometric forms, optimal spatial flow, "
            "contemporary architectural elements, realistic rendering quality, "
            "natural lighting integration, professional photography style"
        )

    def _combine_prompts(self, user_prompt: str) -> str:
        """
        Combine user's custom prompt with the default architectural design prompt.
        
        Args:
            user_prompt: User's custom prompt for specific design requirements
            
        Returns:
            str: Combined prompt that merges architectural expertise with user needs
        """
        default_prompt = self._get_default_architectural_prompt()
        
        # Clean and prepare user prompt
        user_prompt_clean = user_prompt.strip()
        if not user_prompt_clean:
            return default_prompt
        
        # Combine prompts with architectural focus
        combined_prompt = f"{default_prompt}, {user_prompt_clean}"
        
        return combined_prompt

    def _prepare_image_for_replicate(self, image_bytes: bytes) -> io.BytesIO:
        """
        Prepare image bytes for Replicate API by ensuring proper format.
        
        Args:
            image_bytes: Raw bytes of the uploaded image
            
        Returns:
            io.BytesIO: Image file ready for Replicate API
        """
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

    def generate_architectural_image(
        self, 
        image_bytes: bytes, 
        user_prompt: str,
        negative_prompt: str = "low quality, blurry, distorted, amateur, unprofessional, cluttered, poor lighting, unrealistic proportions",
        num_inference_steps: int = 20
    ) -> Tuple[bool, Optional[list], Optional[str]]:
        """
        Generate an architectural interior design image using Replicate's ControlNet depth-to-image model.
        
        Args:
            image_bytes: Raw bytes of the uploaded image
            user_prompt: User's custom design requirements
            negative_prompt: What to avoid in the generated image
            num_inference_steps: Number of inference steps (higher = better quality, slower)
            
        Returns:
            Tuple[bool, Optional[list], Optional[str]]: (success, generated_image_urls, error_message)
        """
        if not self.api_available:
            if not REPLICATE_AVAILABLE:
                return False, None, "Replicate package not installed. Please install it with: pip install replicate"
            else:
                return False, None, "Replicate API token not configured"
        
        try:
            # Prepare the image for Replicate
            image_file = self._prepare_image_for_replicate(image_bytes)
            
            # Combine user prompt with architectural design expertise
            combined_prompt = self._combine_prompts(user_prompt)
            
            # Prepare input data for Replicate
            input_data = {
                "image": image_file,
                "prompt": combined_prompt,
                "negative_prompt": negative_prompt,
                "num_inference_steps": num_inference_steps,
            }
            
            # Run the Replicate model
            output = self.client.run(
                "jagilley/controlnet-depth2img:922c7bb67b87ec32cbc2fd11b1d5f94f0ba4f5519c4dbd02856376444127cc60",
                input=input_data
            )
            
            # Process all outputs like in the original depth_controlnet.py
            generated_images = []
            if output and len(output) > 0:
                for index, item in enumerate(output):
                    if index == 0:
                        continue  # Skip the first output (usually depth map)
                    generated_images.append(str(item))
                
                if generated_images:
                    # Return all generated architectural images
                    return True, generated_images, None
                else:
                    return False, None, "No architectural images generated by the AI model"
            else:
                return False, None, "No output generated by the AI model"
                
        except Exception as e:
            return False, None, f"Image generation failed: {str(e)}"

    def get_service_status(self) -> dict:
        """
        Get the current status of the image generation service.
        
        Returns:
            dict: Service status information
        """
        return {
            "api_available": self.api_available,
            "service_name": "Architectural Image Generation Service",
            "model": "jagilley/controlnet-depth2img",
            "default_prompt": self._get_default_architectural_prompt()
        }


# Singleton instance for dependency injection
image_generation_service = AIImageGenerationService()
