# domain/entities.py
from django.db import models
from django.utils import timezone
from typing import List, Dict, Any


class Product(models.Model):
    """
    Product entity representing a product with AI-analyzed features.
    Follows Single Responsibility Principle - only handles data representation.
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
