# AI Image Generation API Usage Guide

## Overview

This API endpoint allows you to upload an image and generate a new architectural interior design image using AI. The service combines your custom design requirements with professional architectural design expertise.

## Endpoint

```
POST /api/generate-image/
```

## Request Format

**Content-Type:** `multipart/form-data`

### Required Parameters

- `image`: Image file (JPEG, PNG, GIF, WebP, BMP) - Max 10MB
- `prompt`: Your custom design requirements and preferences

### Optional Parameters

- `negative_prompt`: What to avoid in the generated design (default: "low quality, blurry, distorted, amateur, unprofessional, cluttered, poor lighting, unrealistic proportions")
- `num_inference_steps`: Number of inference steps, 20-50 (default: 20, higher = better quality but slower)

## Example Request (cURL)

```bash
curl -X POST "http://localhost:8000/api/generate-image/" \
  -F "image=@room04.jpg" \
  -F "prompt=modern bedroom with minimalist furniture, white walls, natural wood accents, large windows with natural light" \
  -F "negative_prompt=cluttered, dark, outdated furniture" \
  -F "num_inference_steps=25"
```

## Example Request (JavaScript/Fetch)

```javascript
const formData = new FormData();
formData.append("image", imageFile);
formData.append(
  "prompt",
  "modern bedroom with minimalist furniture, white walls, natural wood accents"
);
formData.append("negative_prompt", "cluttered, dark, outdated furniture");
formData.append("num_inference_steps", "25");

fetch("http://localhost:8000/api/generate-image/", {
  method: "POST",
  body: formData,
})
  .then((response) => response.json())
  .then((data) => {
    console.log("Generated image URL:", data.generated_image_url);
    console.log("Combined prompt:", data.combined_prompt);
  });
```

## Response Format

### Success Response (200)

```json
{
  "success": true,
  "generated_image_url": "https://replicate.delivery/pbxt/...",
  "original_prompt": "modern bedroom with minimalist furniture, white walls, natural wood accents",
  "combined_prompt": "Professional architectural interior design, modern space planning, sophisticated lighting design, functional furniture arrangement, harmonious color palette, premium materials and finishes, clean lines and geometric forms, optimal spatial flow, contemporary architectural elements, realistic rendering quality, natural lighting integration, professional photography style, modern bedroom with minimalist furniture, white walls, natural wood accents",
  "negative_prompt": "cluttered, dark, outdated furniture",
  "num_inference_steps": 25,
  "message": "Architectural design image generated successfully"
}
```

### Error Responses

#### 400 Bad Request

```json
{
  "error": "Image file is required"
}
```

#### 500 Internal Server Error

```json
{
  "error": "Image generation failed: Replicate API token not configured"
}
```

## Default Architectural Prompt

The service automatically combines your custom prompt with a professional architectural design prompt that includes:

- Professional architectural interior design
- Modern space planning
- Sophisticated lighting design
- Functional furniture arrangement
- Harmonious color palette
- Premium materials and finishes
- Clean lines and geometric forms
- Optimal spatial flow
- Contemporary architectural elements
- Realistic rendering quality
- Natural lighting integration
- Professional photography style

## Environment Setup

Make sure to set your Replicate API token in the `.env` file:

```
REPLICATE_API_TOKEN=your_actual_replicate_api_token_here
```

## Rate Limits and Costs

- The API uses Replicate's ControlNet depth-to-image model
- Generation time varies based on `num_inference_steps` (20-50)
- Higher inference steps = better quality but longer processing time
- Check Replicate's pricing for usage costs

## Tips for Better Results

1. **Clear Prompts**: Be specific about materials, colors, and style preferences
2. **Good Base Images**: Use clear, well-lit room photos as base images
3. **Inference Steps**: Use 25-30 steps for good balance of quality and speed
4. **Negative Prompts**: Specify what you want to avoid for better results
5. **Room Type**: The AI works best with interior spaces (bedrooms, living rooms, kitchens, etc.)

## Integration with Frontend

The generated image URL can be directly used in your frontend:

```javascript
// Display the generated image
const img = document.createElement("img");
img.src = response.generated_image_url;
img.alt = "Generated Architectural Design";
document.body.appendChild(img);
```
