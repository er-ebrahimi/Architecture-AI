import { Search, Package, Clock, Tag } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ProductCard } from "./product-card";
import type { FindSimilarResponse } from "@/services/api";

interface SearchResultsProps {
  results: FindSimilarResponse;
  baseUrl?: string;
}

export function SearchResults({ results, baseUrl }: SearchResultsProps) {
  if (!results.similar_products || results.similar_products.length === 0) {
    return (
      <Card className="w-full">
        <CardContent className="flex flex-col items-center justify-center py-16">
          <div className="rounded-full bg-muted p-4 mb-4">
            <Package className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-semibold mb-2">
            No Similar Products Found
          </h3>
          <p className="text-sm text-muted-foreground text-center max-w-md">
            We couldn't find any products similar to your uploaded image. Try
            uploading a different image or check back later as we add more
            products.
          </p>
          <div className="mt-4 p-4 bg-muted rounded-lg">
            <p className="text-sm">
              <strong>Products checked:</strong>{" "}
              {results.total_products_checked}
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Search Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Search Results
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">
                {results.similar_products.length}
              </div>
              <div className="text-sm text-muted-foreground">
                Similar Products
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-secondary-foreground">
                {results.total_products_checked}
              </div>
              <div className="text-sm text-muted-foreground">
                Products Checked
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {results.similar_products[0]?.similarity_score || 0}/10
              </div>
              <div className="text-sm text-muted-foreground">Best Match</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {results.query_tags.length}
              </div>
              <div className="text-sm text-muted-foreground">Tags Found</div>
            </div>
          </div>

          <Separator />

          {/* Query Analysis */}
          <div className="space-y-3">
            <h4 className="font-medium flex items-center gap-2">
              <Tag className="h-4 w-4" />
              Image Analysis
            </h4>

            <div className="grid md:grid-cols-2 gap-4">
              {/* Objects Found */}
              <div>
                <h5 className="text-sm font-medium mb-2 text-muted-foreground">
                  Objects Detected:
                </h5>
                <div className="flex flex-wrap gap-1">
                  {results.query_features.main_objects.map((obj, index) => (
                    <Badge
                      key={index}
                      variant="secondary"
                      className="bg-blue-100 text-blue-800"
                    >
                      {obj.object_type}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Style Detected */}
              <div>
                <h5 className="text-sm font-medium mb-2 text-muted-foreground">
                  Style Detected:
                </h5>
                <div className="flex flex-wrap gap-1">
                  {results.query_features.overall_style.map((style, index) => (
                    <Badge
                      key={index}
                      variant="outline"
                      className="border-purple-200 text-purple-700"
                    >
                      {style}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>

            {/* All Tags */}
            <div>
              <h5 className="text-sm font-medium mb-2 text-muted-foreground">
                All Tags:
              </h5>
              <div className="flex flex-wrap gap-1 max-h-20 overflow-y-auto">
                {results.query_tags.slice(0, 20).map((tag, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {tag}
                  </Badge>
                ))}
                {results.query_tags.length > 20 && (
                  <Badge
                    variant="secondary"
                    className="text-xs bg-gray-100 text-gray-600"
                  >
                    +{results.query_tags.length - 20} more
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Products Grid */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Similar Products</h3>
          <Badge variant="outline" className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            Sorted by similarity
          </Badge>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {results.similar_products.map((product) => (
            <ProductCard key={product.id} product={product} baseUrl={baseUrl} />
          ))}
        </div>
      </div>
    </div>
  );
}
