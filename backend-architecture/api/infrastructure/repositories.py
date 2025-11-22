# infrastructure/repositories.py
from typing import List, Dict
from ..domain.interfaces import ProductRepositoryInterface
from ..domain.entities import Product


class DjangoProductRepository(ProductRepositoryInterface):
    """
    Django implementation of ProductRepositoryInterface.
    Follows Single Responsibility Principle - handles only data access.
    """
    
    def create_product(self, source_url: str, image_filename: str, features: dict) -> int:
        """Create a new product and return its ID."""
        product = Product.objects.create(
            source_url=source_url,
            image_filename=image_filename,
            features=features
        )
        return product.id
    
    def get_all_products(self) -> List[dict]:
        """Get all products from the database."""
        products = Product.objects.all()
        return [
            {
                'id': product.id,
                'source_url': product.source_url,
                'image_filename': product.image_filename,
                'features': product.features,
                'created_at': product.created_at.isoformat()
            }
            for product in products
        ]
    
    def find_similar_products(self, query_tags: List[str], limit: int = 10) -> List[dict]:
        """Find products similar to the query tags."""
        all_products = Product.objects.all()
        
        if not all_products.exists():
            return []
        
        # Calculate similarity scores for each product
        scored_products = []
        for product in all_products:
            similarity_score = self._calculate_similarity_score(product, query_tags)
            if similarity_score > 0:  # Only include products with some similarity
                # Generate image URL
                from django.conf import settings
                image_url = f"{settings.MEDIA_URL}{product.image_filename}"
                
                scored_products.append({
                    'id': product.id,
                    'source_url': product.source_url,
                    'image_filename': product.image_filename,
                    'image_url': image_url,
                    'similarity_score': similarity_score,
                    'features': product.features,
                    'created_at': product.created_at.isoformat()
                })
        
        # Sort by similarity score (descending) and get top results
        scored_products.sort(key=lambda x: x['similarity_score'], reverse=True)
        return scored_products[:limit]
    
    def _calculate_similarity_score(self, product: Product, query_tags: List[str]) -> int:
        """Calculate similarity score based on common tags."""
        if not product.features:
            return 0
        
        product_tags = []
        
        # Extract object types and their attributes
        main_objects = product.features.get('main_objects', [])
        for obj in main_objects:
            product_tags.append(obj.get('object_type', ''))
            product_tags.extend(obj.get('attributes', []))
        
        # Extract overall style tags
        overall_style = product.features.get('overall_style', [])
        product_tags.extend(overall_style)
        
        # Clean and normalize tags
        product_tags = [tag.lower().strip() for tag in product_tags if tag and tag.strip()]
        query_tags_lower = [tag.lower().strip() for tag in query_tags if tag and tag.strip()]
        
        # Count common tags
        common_tags = set(product_tags).intersection(set(query_tags_lower))
        return len(common_tags)
