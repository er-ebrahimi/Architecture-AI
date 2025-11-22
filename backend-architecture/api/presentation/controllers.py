# presentation/controllers.py
import json
import asyncio
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..application.use_cases import AddProductUseCase, FindSimilarProductsUseCase, GenerateArchitecturalImageUseCase
from ..domain.value_objects import ImageGenerationRequest


class ProductController:
    """
    Controller for product-related endpoints.
    Follows Single Responsibility Principle - handles only HTTP request/response logic.
    """
    
    def __init__(self, add_product_use_case: AddProductUseCase, find_similar_use_case: FindSimilarProductsUseCase):
        self.add_product_use_case = add_product_use_case
        self.find_similar_use_case = find_similar_use_case
    
    def add_product(self, request):
        """
        API Endpoint: Add a Product
        
        Path: /products/
        Method: POST
        Purpose: Receive a product source URL and image URL, download and analyze the image using AI, and save to database.
        """
        try:
            # Parse JSON request body
            try:
                request_data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
            
            # Validate input
            if 'source_url' not in request_data:
                return JsonResponse({'error': 'source_url is required'}, status=400)
            
            if 'image_url' not in request_data:
                return JsonResponse({'error': 'image_url is required'}, status=400)
            
            source_url = request_data['source_url']
            image_url = request_data['image_url']
            
            # Execute use case
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self.add_product_use_case.execute(source_url, image_url)
                )
            finally:
                loop.close()
            
            if result['success']:
                return JsonResponse(result, status=201)
            else:
                return JsonResponse({'error': result['error']}, status=400)
                
        except Exception as e:
            return JsonResponse({
                'error': f'Failed to process product: {str(e)}'
            }, status=500)
    
    def find_similar_products(self, request):
        """
        API Endpoint: Find Similar Products
        
        Path: /products/find-similar/
        Method: POST
        Purpose: Receive a query image file, analyze it, and find most similar products in database.
        """
        try:
            image_bytes = None
            query_image_source = None
            
            # Check if request contains multipart form data (file upload)
            if request.FILES and 'image' in request.FILES:
                # Handle direct file upload
                uploaded_file = request.FILES['image']
                
                # Validate file type
                if not uploaded_file.content_type.startswith('image/'):
                    return JsonResponse({'error': 'Uploaded file must be an image'}, status=400)
                
                # Check file size (limit to 10MB)
                if uploaded_file.size > 10 * 1024 * 1024:
                    return JsonResponse({'error': 'Image file too large (max 10MB)'}, status=400)
                
                # Read image bytes
                image_bytes = uploaded_file.read()
                query_image_source = f"uploaded_file_{uploaded_file.name}"
                
            else:
                # Try to parse as JSON request body (for image URLs)
                try:
                    request_data = json.loads(request.body)
                except json.JSONDecodeError:
                    return JsonResponse({'error': 'Invalid request. Send either multipart form data with "image" file or JSON with "image_url"'}, status=400)
                
                # Validate input
                if 'image_url' not in request_data:
                    return JsonResponse({'error': 'image_url is required in JSON request'}, status=400)
                
                image_url = request_data['image_url']
                query_image_source = image_url
            
            # Execute use case
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                if image_bytes:
                    result = loop.run_until_complete(
                        self.find_similar_use_case.execute(image_bytes=image_bytes)
                    )
                else:
                    result = loop.run_until_complete(
                        self.find_similar_use_case.execute(image_url=image_url)
                    )
            finally:
                loop.close()
            
            if result['success']:
                # Add image source info to response
                result['query_image_source'] = query_image_source
                return JsonResponse(result)
            else:
                return JsonResponse({'error': result['error']}, status=400)
                
        except Exception as e:
            return JsonResponse({
                'error': f'Failed to find similar products: {str(e)}'
            }, status=500)


class ImageGenerationController:
    """
    Controller for image generation endpoints.
    Follows Single Responsibility Principle - handles only HTTP request/response logic.
    """
    
    def __init__(self, generate_image_use_case: GenerateArchitecturalImageUseCase):
        self.generate_image_use_case = generate_image_use_case
    
    def generate_architectural_image(self, request):
        """
        API Endpoint: Generate Architectural Design Image
        
        Path: /api/generate-image/
        Method: POST
        Purpose: Upload an image and custom prompt to generate a new architectural interior design image using AI.
        """
        try:
            # Validate required fields
            if not request.FILES or 'image' not in request.FILES:
                return JsonResponse({'error': 'Image file is required'}, status=400)
            
            if 'prompt' not in request.POST:
                return JsonResponse({'error': 'Prompt is required'}, status=400)
            
            # Get uploaded image
            uploaded_file = request.FILES['image']
            
            # Validate file type
            if not uploaded_file.content_type.startswith('image/'):
                return JsonResponse({'error': 'Uploaded file must be an image'}, status=400)
            
            # Check file size (limit to 10MB)
            if uploaded_file.size > 10 * 1024 * 1024:
                return JsonResponse({'error': 'Image file too large (max 10MB)'}, status=400)
            
            # Read image bytes
            image_bytes = uploaded_file.read()
            
            # Get prompt and optional parameters
            user_prompt = request.POST.get('prompt', '').strip()
            negative_prompt = request.POST.get('negative_prompt', 'low quality, blurry, distorted, amateur, unprofessional, cluttered, poor lighting, unrealistic proportions')
            num_inference_steps = int(request.POST.get('num_inference_steps', 20))
            
            # Validate prompt
            if not user_prompt:
                return JsonResponse({'error': 'Prompt cannot be empty'}, status=400)
            
            # Validate inference steps
            if not (20 <= num_inference_steps <= 50):
                return JsonResponse({'error': 'num_inference_steps must be between 20 and 50'}, status=400)
            
            # Create request object
            generation_request = ImageGenerationRequest(
                image_bytes=image_bytes,
                user_prompt=user_prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=num_inference_steps
            )
            
            # Execute use case
            result = self.generate_image_use_case.execute(generation_request)
            
            if result['success']:
                return JsonResponse(result)
            else:
                return JsonResponse({'error': result['error']}, status=500)
                
        except ValueError as e:
            return JsonResponse({'error': f'Invalid input: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({
                'error': f'Failed to generate architectural image: {str(e)}'
            }, status=500)


class HealthController:
    """
    Controller for health check endpoints.
    Follows Single Responsibility Principle - handles only health check logic.
    """
    
    def health_check(self, request):
        """Simple health check endpoint to verify API is running."""
        return JsonResponse({
            'status': 'healthy',
            'service': 'AI Visual Product Search API',
            'endpoints': [
                'POST /api/products/ - Add product with image URL analysis (JSON: {source_url, image_url})',
                'POST /api/products/find-similar/ - Find similar products (JSON: {image_url})',
                'POST /api/generate-image/ - Generate architectural design image (multipart: {image, prompt})',
                'GET /api/health/ - Health check'
            ]
        })
