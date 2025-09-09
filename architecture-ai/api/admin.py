from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'source_url', 'image_filename', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('source_url', 'image_filename')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('source_url', 'image_filename')
        }),
        ('AI Features', {
            'fields': ('features',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
