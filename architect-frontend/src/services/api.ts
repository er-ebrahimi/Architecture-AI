// API configuration
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:9000";

// Types for API responses
export interface ProductFeatures {
  main_objects: Array<{
    object_type: string;
    attributes: string[];
  }>;
  overall_style: string[];
}

export interface SimilarProduct {
  id: number;
  source_url: string;
  image_filename: string;
  image_url: string;
  similarity_score: number;
  features: ProductFeatures;
  created_at: string;
}

export interface FindSimilarResponse {
  success: boolean;
  query_features: ProductFeatures;
  query_tags: string[];
  total_products_checked: number;
  similar_products: SimilarProduct[];
  message: string;
}

export interface GenerateImageResponse {
  success: boolean;
  generated_image_urls: string[];
  generated_image_url: string;
  total_images: number;
  original_prompt: string;
  combined_prompt: string;
  negative_prompt: string;
  num_inference_steps: number;
  message: string;
}

export interface ApiError {
  error: string;
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Find similar products by uploading an image
   */
  async findSimilarProducts(imageFile: File): Promise<FindSimilarResponse> {
    const formData = new FormData();
    formData.append("image", imageFile);

    const response = await fetch(`${this.baseUrl}/api/products/find-similar/`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json();
      throw new Error(
        errorData.error || `HTTP error! status: ${response.status}`
      );
    }

    return response.json();
  }

  /**
   * Add a new product (optional - for future use)
   */
  async addProduct(imageFile: File, sourceUrl: string): Promise<any> {
    const formData = new FormData();
    formData.append("image", imageFile);
    formData.append("source_url", sourceUrl);

    const response = await fetch(`${this.baseUrl}/api/products/`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json();
      throw new Error(
        errorData.error || `HTTP error! status: ${response.status}`
      );
    }

    return response.json();
  }

  /**
   * Generate architectural design image
   */
  async generateArchitecturalImage(
    imageFile: File,
    prompt: string,
    negativePrompt?: string,
    numInferenceSteps?: number
  ): Promise<GenerateImageResponse> {
    const formData = new FormData();
    formData.append("image", imageFile);
    formData.append("prompt", prompt);

    if (negativePrompt) {
      formData.append("negative_prompt", negativePrompt);
    }

    if (numInferenceSteps) {
      formData.append("num_inference_steps", numInferenceSteps.toString());
    }

    const response = await fetch(`${this.baseUrl}/api/generate-image/`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json();
      throw new Error(
        errorData.error || `HTTP error! status: ${response.status}`
      );
    }

    return response.json();
  }

  /**
   * Find similar products by image URL
   */
  async findSimilarProductsByUrl(
    imageUrl: string
  ): Promise<FindSimilarResponse> {
    const response = await fetch(`${this.baseUrl}/api/products/find-similar/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        image_url: imageUrl,
      }),
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json();
      throw new Error(
        errorData.error || `HTTP error! status: ${response.status}`
      );
    }

    return response.json();
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/health/`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Get full image URL
   */
  getImageUrl(imagePath: string): string {
    if (imagePath.startsWith("http")) {
      return imagePath;
    }
    return `${this.baseUrl}${imagePath}`;
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
