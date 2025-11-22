import { ExternalLink, Star } from "lucide-react";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { SimilarProduct } from "@/services/api";

interface ProductCardProps {
  product: SimilarProduct;
  baseUrl?: string;
}

export function ProductCard({
  product,
  baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
}: ProductCardProps) {
  const getImageUrl = (imagePath: string | undefined) => {
    if (!imagePath) {
      return `data:image/svg+xml;base64,${btoa(`
        <svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
          <rect width="400" height="400" fill="#f3f4f6"/>
          <text x="200" y="200" text-anchor="middle" fill="#9ca3af" font-size="16">No image</text>
        </svg>
      `)}`;
    }
    if (imagePath.startsWith("http")) {
      return imagePath;
    }
    console.log(
      "🚀 ~ getImageUrl ~ `${baseUrl}${imagePath}`:",
      `${baseUrl}${imagePath}`
    );
    return `${baseUrl}${imagePath}`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const getSimilarityColor = (score: number) => {
    if (score >= 8) return "bg-green-500";
    if (score >= 6) return "bg-yellow-500";
    if (score >= 4) return "bg-orange-500";
    return "bg-red-500";
  };

  const getSimilarityText = (score: number) => {
    if (score >= 8) return "Excellent";
    if (score >= 6) return "Good";
    if (score >= 4) return "Fair";
    return "Poor";
  };

  return (
    <Card className="h-full overflow-hidden transition-all duration-200 hover:shadow-lg hover:-translate-y-1">
      <div className="relative">
        {/* Product Image */}
        <div className="aspect-square relative overflow-hidden bg-muted">
          <img
            src={getImageUrl(product.image_url)}
            alt={`Product ${product.id}`}
            className="w-full h-full object-cover transition-transform duration-200 hover:scale-105"
            onError={(e) => {
              // Fallback to a placeholder if image fails to load
              const target = e.target as HTMLImageElement;
              target.src = `data:image/svg+xml;base64,${btoa(`
                <svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
                  <rect width="400" height="400" fill="#f3f4f6"/>
                  <text x="200" y="200" text-anchor="middle" fill="#9ca3af" font-size="16">Image not found</text>
                </svg>
              `)}`;
            }}
          />
        </div>

        {/* Similarity Score Badge */}
        <div className="absolute top-3 right-3">
          <Badge
            variant="secondary"
            className={`${getSimilarityColor(
              product.similarity_score
            )} text-white font-medium px-2 py-1`}
          >
            <Star className="w-3 h-3 mr-1 fill-current" />
            {product.similarity_score}/10
          </Badge>
        </div>

        {/* Similarity Text */}
        <div className="absolute top-3 left-3">
          <Badge variant="outline" className="bg-white/90 backdrop-blur-sm">
            {getSimilarityText(product.similarity_score)} Match
          </Badge>
        </div>
      </div>

      <CardContent className="p-4">
        {/* Product ID and Date */}
        <div className="flex justify-between items-center mb-3">
          <span className="text-sm font-medium text-muted-foreground">
            Product #{product.id}
          </span>
          <span className="text-xs text-muted-foreground">
            {formatDate(product.created_at)}
          </span>
        </div>

        {/* Features Section */}
        <div className="space-y-3">
          {/* Main Objects */}
          {product.features.main_objects &&
            product.features.main_objects.length > 0 && (
              <div>
                <h4 className="text-sm font-medium mb-2 text-foreground">
                  Objects:
                </h4>
                <div className="flex flex-wrap gap-1">
                  {product.features.main_objects.map((obj, index) => (
                    <Badge
                      key={index}
                      variant="secondary"
                      className="text-xs bg-blue-100 text-blue-800 hover:bg-blue-200"
                    >
                      {obj.object_type}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

          {/* Overall Style */}
          {product.features.overall_style &&
            product.features.overall_style.length > 0 && (
              <div>
                <h4 className="text-sm font-medium mb-2 text-foreground">
                  Style:
                </h4>
                <div className="flex flex-wrap gap-1">
                  {product.features.overall_style.map((style, index) => (
                    <Badge
                      key={index}
                      variant="outline"
                      className="text-xs border-purple-200 text-purple-700 hover:bg-purple-50"
                    >
                      {style}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

          {/* Top Attributes */}
          {product.features.main_objects &&
            product.features.main_objects.length > 0 && (
              <div>
                <h4 className="text-sm font-medium mb-2 text-foreground">
                  Attributes:
                </h4>
                <div className="flex flex-wrap gap-1">
                  {product.features.main_objects
                    .flatMap((obj) => obj.attributes)
                    .slice(0, 4) // Show only first 4 attributes
                    .map((attr, index) => (
                      <Badge
                        key={index}
                        variant="secondary"
                        className="text-xs bg-green-100 text-green-800 hover:bg-green-200"
                      >
                        {attr}
                      </Badge>
                    ))}
                  {product.features.main_objects.flatMap(
                    (obj) => obj.attributes
                  ).length > 4 && (
                    <Badge
                      variant="secondary"
                      className="text-xs bg-gray-100 text-gray-600"
                    >
                      +
                      {product.features.main_objects.flatMap(
                        (obj) => obj.attributes
                      ).length - 4}{" "}
                      more
                    </Badge>
                  )}
                </div>
              </div>
            )}
        </div>
      </CardContent>

      <CardFooter className="p-4 pt-0">
        {/* View Original Button */}
        <Button
          variant="outline"
          size="sm"
          className="w-full"
          onClick={() => window.open(product.source_url, "_blank")}
        >
          <ExternalLink className="w-4 h-4 mr-2" />
          View Original
        </Button>
      </CardFooter>
    </Card>
  );
}
