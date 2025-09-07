# models.py
from django.db import models
from django.utils import timezone

class Product(models.Model):
    """
    Product model for storing AI-analyzed product information.
    Uses JSONField to store the ImageFeatures Pydantic model as JSON.
    """
    source_url = models.URLField(unique=True, db_index=True, help_text="Original URL of the product", default="")
    image_filename = models.CharField(max_length=255, unique=True, help_text="Unique filename of the saved image", default="")
    features = models.JSONField(default=dict, help_text="AI-generated features stored as JSON (ImageFeatures schema)")
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['source_url']),
            models.Index(fields=['image_filename']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Product {self.id} - {self.source_url[:50]}..."

    def get_all_tags(self):
        """
        Extract all tags from the features JSON for similarity comparison.
        Returns a flat list of all object attributes and overall style tags.
        """
        if not self.features:
            return []
        
        tags = []
        
        # Extract object types and their attributes
        main_objects = self.features.get('main_objects', [])
        for obj in main_objects:
            tags.append(obj.get('object_type', ''))
            tags.extend(obj.get('attributes', []))
        
        # Extract overall style tags
        overall_style = self.features.get('overall_style', [])
        tags.extend(overall_style)
        
        # Return unique, non-empty tags in lowercase
        return list(set([tag.lower().strip() for tag in tags if tag and tag.strip()]))

    def calculate_similarity_score(self, query_tags):
        """
        Calculate similarity score based on common tags.
        Args:
            query_tags (list): List of tags from query image
        Returns:
            int: Number of matching tags
        """
        product_tags = self.get_all_tags()
        query_tags_lower = [tag.lower().strip() for tag in query_tags if tag and tag.strip()]
        
        # Count common tags
        common_tags = set(product_tags).intersection(set(query_tags_lower))
        return len(common_tags)