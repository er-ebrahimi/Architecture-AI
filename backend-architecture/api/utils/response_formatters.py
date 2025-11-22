# utils/response_formatters.py
"""
Response formatting utilities following Single Responsibility Principle.
Each formatter has a single responsibility for specific response formatting tasks.
"""

from typing import Dict, Any, List
from ..domain.value_objects import ProductSimilarityResult


class ProductResponseFormatter:
    """Formatter for product-related responses."""
    
    @staticmethod
    def format_add_product_response(result: Dict[str, Any]) -> Dict[str, Any]:
        """Format add product response."""
        if result['success']:
            return {
                'success': True,
                'product_id': result['product_id'],
                'image_filename': result['image_filename'],
                'image_url': result['image_url'],
                'original_image_url': result.get('original_image_url', ''),
                'features': result['features'],
                'message': result['message']
            }
        else:
            return {
                'success': False,
                'error': result['error']
            }
    
    @staticmethod
    def format_similar_products_response(result: Dict[str, Any]) -> Dict[str, Any]:
        """Format similar products response."""
        if result['success']:
            # Add image URLs to similar products
            similar_products = []
            for product in result['similar_products']:
                product['image_url'] = f"/media/{product['image_filename']}"
                similar_products.append(product)
            
            return {
                'success': True,
                'query_image_source': result.get('query_image_source', ''),
                'query_features': result['query_features'],
                'query_tags': result['query_tags'],
                'total_products_checked': result['total_products_checked'],
                'similar_products': similar_products,
                'message': result['message']
            }
        else:
            return {
                'success': False,
                'error': result['error']
            }


class ImageGenerationResponseFormatter:
    """Formatter for image generation responses."""
    
    @staticmethod
    def format_generation_response(result: Dict[str, Any]) -> Dict[str, Any]:
        """Format image generation response."""
        if result['success']:
            return {
                'success': True,
                'generated_image_urls': result['generated_image_urls'],
                'generated_image_url': result['generated_image_urls'][0] if result['generated_image_urls'] else None,
                'generated_image_filenames': result['generated_image_filenames'],
                'total_images': result['total_images'],
                'original_prompt': result['original_prompt'],
                'negative_prompt': result['negative_prompt'],
                'num_inference_steps': result['num_inference_steps'],
                'message': result['message']
            }
        else:
            return {
                'success': False,
                'error': result['error']
            }


class HealthResponseFormatter:
    """Formatter for health check responses."""
    
    @staticmethod
    def format_health_response() -> Dict[str, Any]:
        """Format health check response."""
        return {
            'status': 'healthy',
            'service': 'AI Visual Product Search API',
            'endpoints': [
                'POST /api/products/ - Add product with image URL analysis (JSON: {source_url, image_url})',
                'POST /api/products/find-similar/ - Find similar products (JSON: {image_url})',
                'POST /api/generate-image/ - Generate architectural design image (multipart: {image, prompt})',
                'GET /api/health/ - Health check'
            ]
        }
