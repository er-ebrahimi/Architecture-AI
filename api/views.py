# views.py
import json
import uuid
import asyncio
from typing import List, Dict, Any
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.db.models import Q
from .models import Product
from .ai_service import ai_service
from .schemas import ImageFeatures

@csrf_exempt
@require_http_methods(["POST"])
def add_product(request):
    """
    API Endpoint 1: Add a Product
    
    Path: /products/
    Method: POST
    Purpose: Receive a product image and source URL, analyze using AI, and save to database.
    
    Request: multipart/form-data containing:
    - source_url: str (form field)
    - image: file upload
    
    Returns: JSON response with product ID and analysis results
    """
    try:
        # Validate input
        if 'source_url' not in request.POST:
            return JsonResponse({'error': 'source_url is required'}, status=400)
        
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'image file is required'}, status=400)
        
        source_url = request.POST['source_url']
        image_file = request.FILES['image']
        
        # Validate image file
        if not image_file.content_type.startswith('image/'):
            return JsonResponse({'error': 'File must be an image'}, status=400)
        
        # Read image content
        image_bytes = image_file.read()
        
        # Generate unique filename
        file_extension = image_file.name.split('.')[-1] if '.' in image_file.name else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Save image file to static directory
        file_path = default_storage.save(
            f"product_images/{unique_filename}",
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
            'features': features_dict,
            'message': 'Product successfully analyzed and saved'
        }, status=201)
        
    except Exception as e:
        # Clean up uploaded file if database save fails
        if 'unique_filename' in locals():
            try:
                default_storage.delete(f"product_images/{unique_filename}")
            except:
                pass
        
        return JsonResponse({
            'error': f'Failed to process product: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def find_similar_products(request):
    """
    API Endpoint 2: Find Similar Products
    
    Path: /products/find-similar/
    Method: POST
    Purpose: Receive a query image, analyze it, and find most similar products in database.
    
    Request: multipart/form-data containing:
    - image: file upload
    
    Returns: JSON response with top similar products ranked by similarity score
    """
    try:
        # Validate input
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'image file is required'}, status=400)
        
        image_file = request.FILES['image']
        
        # Validate image file
        if not image_file.content_type.startswith('image/'):
            return JsonResponse({'error': 'File must be an image'}, status=400)
        
        # Read image content
        image_bytes = image_file.read()
        
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
                'query_features': query_features.model_dump(),
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


def health_check(request):
    """Simple health check endpoint to verify API is running."""
    return JsonResponse({
        'status': 'healthy',
        'service': 'AI Visual Product Search API',
        'endpoints': [
            'POST /api/products/ - Add product with image analysis',
            'POST /api/products/find-similar/ - Find similar products',
            'GET /api/health/ - Health check'
        ]
    })
