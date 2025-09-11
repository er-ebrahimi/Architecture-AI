# URL-Based Image API Usage

## Overview

The API has been updated to accept image URLs instead of file uploads. Both endpoints now download images from provided URLs, making integration easier and reducing bandwidth usage.

## API Endpoints

### 1. Add Product with Image URL

**Endpoint:** `POST /api/products/`  
**Content-Type:** `application/json`

**Request Body:**

```json
{
  "source_url": "https://example.com/product-page",
  "image_url": "https://example.com/images/product.jpg"
}
```

**Response (201 Created):**

```json
{
  "success": true,
  "product_id": 123,
  "image_filename": "uuid-generated-filename.jpg",
  "image_url": "/media/uuid-generated-filename.jpg",
  "original_image_url": "https://example.com/images/product.jpg",
  "features": {
    "main_objects": [
      {
        "object_type": "chair",
        "attributes": ["wooden", "modern", "minimalist"]
      }
    ],
    "overall_style": ["modern", "minimalist"]
  },
  "message": "Product successfully analyzed and saved"
}
```

### 2. Find Similar Products with Image URL

**Endpoint:** `POST /api/products/find-similar/`  
**Content-Type:** `application/json`

**Request Body:**

```json
{
  "image_url": "https://example.com/query-image.jpg"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "query_image_url": "https://example.com/query-image.jpg",
  "query_features": {
    /* AI analysis results */
  },
  "query_tags": ["chair", "wooden", "modern"],
  "total_products_checked": 50,
  "similar_products": [
    {
      "id": 123,
      "source_url": "https://example.com/product",
      "image_filename": "uuid-generated-filename.jpg",
      "image_url": "/media/uuid-generated-filename.jpg",
      "similarity_score": 5,
      "features": {
        /* product features */
      },
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "message": "Found 10 similar products"
}
```

## Key Features

### Image Download & Validation

- **URL Validation**: Checks for valid URL format
- **Content-Type Validation**: Ensures URL points to an image
- **Size Limits**: Maximum 10MB image size
- **Supported Formats**: JPEG, PNG, GIF, WebP, BMP
- **Timeout Protection**: 30-second download timeout

### Error Handling

- Invalid URL format: `400 Bad Request`
- Non-image content: `400 Bad Request`
- File too large: `400 Bad Request`
- Download timeout: `400 Bad Request`
- Network errors: `400 Bad Request`

### SOLID Principles Implementation

- **Single Responsibility**: `download_image_from_url()` handles only image downloading
- **Open/Closed**: Easy to extend with new image sources
- **Dependency Inversion**: Uses httpx for HTTP operations
- **Interface Segregation**: Clear separation between download and analysis

## Example cURL Commands

### Add Product:

```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Content-Type: application/json" \
  -d '{
    "source_url": "https://example.com/product",
    "image_url": "https://example.com/product-image.jpg"
  }'
```

### Find Similar Products:

```bash
curl -X POST http://localhost:8000/api/products/find-similar/ \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/query-image.jpg"
  }'
```

## Migration Notes

- **Breaking Change**: Endpoints no longer accept `multipart/form-data`
- **New Format**: All requests now use `application/json`
- **Parameter Changes**:
  - `image` field → `image_url` field
  - File upload → URL string
