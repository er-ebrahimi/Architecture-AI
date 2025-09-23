# views.py
import json
import uuid
import asyncio
import httpx
import os
from typing import List, Dict, Any
from urllib.parse import urlparse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Product
from .ai_service import ai_service
from .schemas import ImageFeatures
from .image_generation_service import image_generation_service


async def download_image_from_url(image_url: str) -> tuple[bytes, str]:
    """
    Download image from URL and return image bytes and file extension.
    
    Args:
        image_url (str): URL of the image to download
        
    Returns:
        tuple[bytes, str]: Image bytes and file extension
        
    Raises:
        ValueError: If URL is invalid or image cannot be downloaded
        Exception: If download fails
    """
    try:
        # Validate URL
        parsed_url = urlparse(image_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL format")
        
        # Download image with timeout and size limits
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(image_url)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                raise ValueError(f"URL does not point to an image. Content-Type: {content_type}")
            
            # Check content length (limit to 10MB)
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > 10 * 1024 * 1024:
                raise ValueError("Image file too large (max 10MB)")
            
            image_bytes = response.content
            
            # Double-check size after download
            if len(image_bytes) > 10 * 1024 * 1024:
                raise ValueError("Image file too large (max 10MB)")
            
            # Determine file extension from content type
            content_type_to_ext = {
                'image/jpeg': 'jpg',
                'image/jpg': 'jpg', 
                'image/png': 'png',
                'image/gif': 'gif',
                'image/webp': 'webp',
                'image/bmp': 'bmp'
            }
            
            file_extension = content_type_to_ext.get(content_type, 'jpg')
            
            return image_bytes, file_extension
            
    except httpx.HTTPStatusError as e:
        raise ValueError(f"Failed to download image: HTTP {e.response.status_code}")
    except httpx.RequestError as e:
        raise ValueError(f"Failed to download image: {str(e)}")
    except Exception as e:
        raise Exception(f"Image download error: {str(e)}")

@swagger_auto_schema(
    method='post',
    operation_summary="Add a Product",
    operation_description="Receive a product source URL and image URL, analyze the image using AI, and save to database.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'source_url': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Original URL of the product',
                example='https://example.com/product'
            ),
            'image_url': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='URL of the product image to download and analyze',
                example='https://example.com/product-image.jpg'
            )
        },
        required=['source_url', 'image_url']
    ),
    responses={
        201: openapi.Response(
            description="Product successfully analyzed and saved",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'product_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'image_filename': openapi.Schema(type=openapi.TYPE_STRING),
                    'image_url': openapi.Schema(type=openapi.TYPE_STRING),
                    'features': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: openapi.Response(description="Bad request - missing required fields or invalid image URL"),
        500: openapi.Response(description="Internal server error")
    },
    tags=['Products']
)
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def add_product(request):
    """
    API Endpoint 1: Add a Product
    
    Path: /products/
    Method: POST
    Purpose: Receive a product source URL and image URL, download and analyze the image using AI, and save to database.
    
    Request: JSON containing:
    - source_url: str (product page URL)
    - image_url: str (image URL to download)
    
    Returns: JSON response with product ID and analysis results
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
        
        # Download image from URL (run async function in sync context)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            image_bytes, file_extension = loop.run_until_complete(download_image_from_url(image_url))
        except (ValueError, Exception) as e:
            return JsonResponse({'error': f'Failed to download image: {str(e)}'}, status=400)
        finally:
            loop.close()
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Save image file to media directory
        file_path = default_storage.save(
            unique_filename,
            ContentFile(image_bytes)
        )
        
        # Analyze image using AI service (run async function in sync context)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            image_features = loop.run_until_complete(ai_service.get_image_features(image_bytes))
        finally:
            loop.close()
        
        # Convert Pydantic model to dictionary for JSON storage
        features_dict = image_features.model_dump()
        
        # Save to database
        product = Product.objects.create(
            source_url=source_url,
            image_filename=unique_filename,
            features=features_dict
        )
        
        return JsonResponse({
            'success': True,
            'product_id': product.id,
            'image_filename': unique_filename,
            'image_url': f"{settings.MEDIA_URL}{unique_filename}",
            'original_image_url': image_url,
            'features': features_dict,
            'message': 'Product successfully analyzed and saved'
        }, status=201)
        
    except Exception as e:
        # Clean up uploaded file if database save fails
        if 'unique_filename' in locals():
            try:
                default_storage.delete(unique_filename)
            except:
                pass
        
        return JsonResponse({
            'error': f'Failed to process product: {str(e)}'
        }, status=500)


@swagger_auto_schema(
    method='post',
    operation_summary="Find Similar Products",
    operation_description="Receive a query image URL, download and analyze it, and find most similar products in database.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'image_url': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='URL of the query image to download and analyze',
                example='https://example.com/query-image.jpg'
            )
        },
        required=['image_url']
    ),
    responses={
        200: openapi.Response(
            description="Similar products found successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'query_image_url': openapi.Schema(type=openapi.TYPE_STRING),
                    'query_features': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'query_tags': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                    'total_products_checked': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'similar_products': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'source_url': openapi.Schema(type=openapi.TYPE_STRING),
                                'image_filename': openapi.Schema(type=openapi.TYPE_STRING),
                                'image_url': openapi.Schema(type=openapi.TYPE_STRING),
                                'similarity_score': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'features': openapi.Schema(type=openapi.TYPE_OBJECT),
                                'created_at': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    ),
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: openapi.Response(description="Bad request - invalid image URL"),
        500: openapi.Response(description="Internal server error")
    },
    tags=['Products']
)
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def find_similar_products(request):
    """
    API Endpoint 2: Find Similar Products
    
    Path: /products/find-similar/
    Method: POST
    Purpose: Receive a query image file, analyze it, and find most similar products in database.
    
    Request: multipart/form-data containing:
    - image: File (image file to analyze)
    
    Alternative: JSON containing:
    - image_url: str (image URL to download and analyze)
    
    Returns: JSON response with top similar products ranked by similarity score
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
            
            # Download image from URL (run async function in sync context)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                image_bytes, file_extension = loop.run_until_complete(download_image_from_url(image_url))
            except (ValueError, Exception) as e:
                return JsonResponse({'error': f'Failed to download image: {str(e)}'}, status=400)
            finally:
                loop.close()
        
        if not image_bytes:
            return JsonResponse({'error': 'No image data received'}, status=400)
        
        # Analyze query image using AI service
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            query_features = loop.run_until_complete(ai_service.get_image_features(image_bytes))
        finally:
            loop.close()
        
        # Extract flat list of all tags from query image
        query_tags = []
        
        # Add object types and their attributes
        for obj in query_features.main_objects:
            query_tags.append(obj.object_type)
            query_tags.extend(obj.attributes)
        
        # Add overall style tags
        query_tags.extend(query_features.overall_style)
        
        # Clean and normalize tags
        query_tags = [tag.lower().strip() for tag in query_tags if tag and tag.strip()]
        
        # Get all products from database
        all_products = Product.objects.all()
        
        if not all_products.exists():
            return JsonResponse({
                'success': False,
                'query_image_url': image_url,
                'query_features': query_features.model_dump(),
                'query_tags': query_tags,
                'similar_products': [],
                'message': 'No products found in database'
            })
        
        # Calculate similarity scores for each product
        scored_products = []
        for product in all_products:
            similarity_score = product.calculate_similarity_score(query_tags)
            if similarity_score > 0:  # Only include products with some similarity
                scored_products.append({
                    'product': product,
                    'score': similarity_score
                })
        
        # Sort by similarity score (descending) and get top 10
        scored_products.sort(key=lambda x: x['score'], reverse=True)
        top_products = scored_products[:10]
        
        # Format response
        similar_products = []
        for item in top_products:
            product = item['product']
            similar_products.append({
                'id': product.id,
                'source_url': product.source_url,
                'image_filename': product.image_filename,
                'image_url': f"{settings.MEDIA_URL}{product.image_filename}",
                'similarity_score': item['score'],
                'features': product.features,
                'created_at': product.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'query_image_source': query_image_source,
            'query_features': query_features.model_dump(),
            'query_tags': query_tags,
            'total_products_checked': all_products.count(),
            'similar_products': similar_products,
            'message': f'Found {len(similar_products)} similar products'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Failed to find similar products: {str(e)}'
        }, status=500)


# Swagger documentation temporarily removed due to multipart/form-data conflicts
# Will be added back with proper parser configuration
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def generate_architectural_image(request):
    """
    API Endpoint: Generate Architectural Design Image
    
    Path: /api/generate-image/
    Method: POST
    Purpose: Upload an image and custom prompt to generate a new architectural interior design image using AI.
    
    Request: multipart/form-data containing:
    - image: File (image file to use as base)
    - prompt: str (custom design requirements)
    - negative_prompt: str (optional, what to avoid)
    - num_inference_steps: int (optional, 20-50, default 20)
    
    Returns: JSON response with generated image URL and prompt information
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
        
        # Generate architectural image using AI service
        success, generated_image_urls, error_message = image_generation_service.generate_architectural_image(
            image_bytes=image_bytes,
            user_prompt=user_prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps
        )
        
        if not success:
            return JsonResponse({
                'error': f'Image generation failed: {error_message}'
            }, status=500)
        
        # Get the combined prompt for reference
        combined_prompt = image_generation_service._combine_prompts(user_prompt)
        
        return JsonResponse({
            'success': True,
            'generated_image_urls': generated_image_urls,
            'generated_image_url': generated_image_urls[0] if generated_image_urls else None,  # For backward compatibility
            'total_images': len(generated_image_urls) if generated_image_urls else 0,
            'original_prompt': user_prompt,
            'combined_prompt': combined_prompt,
            'negative_prompt': negative_prompt,
            'num_inference_steps': num_inference_steps,
            'message': f'Architectural design images generated successfully ({len(generated_image_urls) if generated_image_urls else 0} images)'
        })
        
    except ValueError as e:
        return JsonResponse({'error': f'Invalid input: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Failed to generate architectural image: {str(e)}'
        }, status=500)


@swagger_auto_schema(
    method='get',
    operation_summary="Health Check",
    operation_description="Simple health check endpoint to verify API is running.",
    responses={
        200: openapi.Response(
            description="API is healthy",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, example='healthy'),
                    'service': openapi.Schema(type=openapi.TYPE_STRING, example='AI Visual Product Search API'),
                    'endpoints': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING)
                    )
                }
            )
        )
    },
    tags=['System']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
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
