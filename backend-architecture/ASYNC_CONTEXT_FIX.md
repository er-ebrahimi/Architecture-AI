# Async Context Fix

## Summary

Fixed the "You cannot call this from an async context" error by properly handling synchronous Django ORM operations in async contexts.

## Problem

The error occurred because we were calling synchronous Django ORM operations (`Product.objects.create()`, `Product.objects.all()`) from within async functions without proper async handling.

## Root Cause

- The `FindSimilarProductsUseCase.execute()` method is async
- It calls `self.product_repository.find_similar_products()` which uses Django ORM
- Django ORM operations are synchronous and cannot be called directly from async contexts
- This caused the error: "You cannot call this from an async context - use a thread or sync_to_async"

## Solution Applied

### 1. Added sync_to_async Import

```python
from asgiref.sync import sync_to_async
```

### 2. Updated Database Operations

**In AddProductUseCase:**

```python
# Before (synchronous)
product_id = self.product_repository.create_product(...)

# After (async-safe)
product_id = await sync_to_async(self.product_repository.create_product)(
    source_url=source_url,
    image_filename=unique_filename,
    features=image_features.model_dump()
)
```

**In FindSimilarProductsUseCase:**

```python
# Before (synchronous)
similar_products = self.product_repository.find_similar_products(query_tags, limit=10)

# After (async-safe)
similar_products = await sync_to_async(self.product_repository.find_similar_products)(query_tags, limit=10)
```

## How sync_to_async Works

- `sync_to_async` wraps synchronous functions to make them callable from async contexts
- It runs the synchronous function in a thread pool
- Returns a coroutine that can be awaited
- Maintains the same function signature and behavior

## Benefits

- ✅ Eliminates async context errors
- ✅ Maintains clean architecture
- ✅ Preserves existing functionality
- ✅ No breaking changes to interfaces
- ✅ Proper async/await pattern

## Files Modified

- `api/application/use_cases.py`: Added sync_to_async for database operations

## Testing

To test the fix:

1. Start the Django server
2. Upload an image via `/api/products/add/`
3. Search for similar products via `/api/products/find-similar/`
4. Verify no async context errors occur

## References

- [Django async support documentation](https://docs.djangoproject.com/en/5.2/topics/async/)
- [asgiref.sync documentation](https://github.com/django/asgiref/blob/main/sync.py)
