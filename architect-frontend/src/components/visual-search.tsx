import { useState } from "react";
import { Loader2, AlertCircle, Camera } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "./ui/alert";
import { ImageUpload } from "./image-upload";
import { SearchResults } from "./search-results";
import { apiService, type FindSimilarResponse } from "@/services/api";

export function VisualSearch() {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchResults, setSearchResults] =
    useState<FindSimilarResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleImageSelect = (file: File) => {
    setSelectedImage(file);
    setSearchResults(null);
    setError(null);
  };

  const handleRemoveImage = () => {
    setSelectedImage(null);
    setSearchResults(null);
    setError(null);
  };

  const handleSearch = async () => {
    if (!selectedImage) {
      setError("Please select an image first");
      return;
    }

    setIsLoading(true);
    setError(null);
    setSearchResults(null);

    try {
      const results = await apiService.findSimilarProducts(selectedImage);
      setSearchResults(results);
    } catch (err) {
      console.error("Search error:", err);
      setError(
        err instanceof Error ? err.message : "An error occurred while searching"
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    if (selectedImage) {
      handleSearch();
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Camera className="h-5 w-5" />
            Visual Product Search
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <ImageUpload
            onImageSelect={handleImageSelect}
            onRemoveImage={handleRemoveImage}
            selectedImage={selectedImage}
            isLoading={isLoading}
          />

          {selectedImage && (
            <div className="flex justify-center">
              <Button
                onClick={handleSearch}
                disabled={isLoading}
                size="lg"
                className="min-w-[200px]"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Searching...
                  </>
                ) : (
                  "Find Similar Products"
                )}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="flex items-center justify-between">
            <span>{error}</span>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRetry}
              disabled={isLoading || !selectedImage}
            >
              Retry
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Loading State */}
      {isLoading && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
            <h3 className="text-lg font-semibold mb-2">Analyzing Your Image</h3>
            <p className="text-sm text-muted-foreground text-center max-w-md">
              Our AI is analyzing your image to identify objects, styles, and
              attributes. This may take a few seconds...
            </p>
          </CardContent>
        </Card>
      )}

      {/* Search Results */}
      {searchResults && !isLoading && <SearchResults results={searchResults} />}
    </div>
  );
}
