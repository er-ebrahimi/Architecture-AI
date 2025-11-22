# views.py
"""
Refactored views following SOLID principles and clean architecture.
This file replaces the original monolithic views with a clean, maintainable structure.
"""

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .dependency_injection import container


# Product endpoints
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def add_product(request):
    """Add a product with AI analysis."""
    return container.product_controller.add_product(request)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def find_similar_products(request):
    """Find similar products based on image analysis."""
    return container.product_controller.find_similar_products(request)


# Image generation endpoints
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def generate_architectural_image(request):
    """Generate architectural design images."""
    return container.image_generation_controller.generate_architectural_image(request)


# System endpoints
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint."""
    return container.health_controller.health_check(request)