import { useState } from "react";
import { Loader2, AlertCircle, Camera, Wand2, Search } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Alert, AlertDescription } from "./ui/alert";
import { ImageUpload } from "./image-upload";
import { SearchResults } from "./search-results";
import {
  apiService,
  type GenerateImageResponse,
  type FindSimilarResponse,
} from "@/services/api";

const PREDEFINED_PROMPTS = [
  "Modern minimalist bedroom with clean lines",
  "Scandinavian living room with natural wood",
  "Industrial loft style with exposed brick",
  "Contemporary kitchen with marble countertops",
  "Cozy bedroom with warm lighting",
  "Modern office space with glass elements",
  "Luxury bathroom with gold accents",
  "Bohemian style with plants and textures",
  "Mid-century modern with vintage furniture",
  "Rustic farmhouse with wooden beams",
];

export function ArchitecturalDesign() {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [prompt, setPrompt] = useState("");
  const [selectedPredefinedPrompt, setSelectedPredefinedPrompt] = useState("");
  const [customPrompt, setCustomPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [generatedImage, setGeneratedImage] =
    useState<GenerateImageResponse | null>(null);
  const [searchResults, setSearchResults] =
    useState<FindSimilarResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleImageSelect = (file: File) => {
    setSelectedImage(file);
    setGeneratedImage(null);
    setSearchResults(null);
    setError(null);
  };

  const handleRemoveImage = () => {
    setSelectedImage(null);
    setGeneratedImage(null);
    setSearchResults(null);
    setError(null);
  };

  const handlePredefinedPromptChange = (value: string) => {
    setSelectedPredefinedPrompt(value);
    if (value) {
      setPrompt(value);
    }
  };

  const handleCustomPromptChange = (value: string) => {
    setCustomPrompt(value);
    if (value) {
      setPrompt(value);
    }
  };

  const handleGenerate = async () => {
    if (!selectedImage) {
      setError("Please select an image first");
      return;
    }

    if (!prompt.trim()) {
      setError("Please enter a design prompt");
      return;
    }

    setIsGenerating(true);
    setError(null);
    setGeneratedImage(null);
    setSearchResults(null);

    try {
      const result = await apiService.generateArchitecturalImage(
        selectedImage,
        prompt.trim()
      );
      setGeneratedImage(result);
    } catch (err) {
      console.error("Generation error:", err);
      setError(
        err instanceof Error
          ? err.message
          : "An error occurred while generating the image"
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const handleFindSimilar = async () => {
    if (!generatedImage?.generated_image_url) {
      setError("No generated image available");
      return;
    }

    setIsSearching(true);
    setError(null);
    setSearchResults(null);

    try {
      const results = await apiService.findSimilarProductsByUrl(
        generatedImage.generated_image_url
      );
      setSearchResults(results);
    } catch (err) {
      console.error("Search error:", err);
      setError(
        err instanceof Error
          ? err.message
          : "An error occurred while searching for similar products"
      );
    } finally {
      setIsSearching(false);
    }
  };

  const handleRetry = () => {
    if (selectedImage && prompt) {
      handleGenerate();
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload and Prompt Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wand2 className="h-5 w-5" />
            Architectural Design Generator
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <ImageUpload
            onImageSelect={handleImageSelect}
            onRemoveImage={handleRemoveImage}
            selectedImage={selectedImage}
            isLoading={isGenerating}
          />

          {selectedImage && (
            <div className="space-y-4">
              {/* Predefined Prompts */}
              <div className="space-y-2">
                <Label htmlFor="predefined-prompt">
                  Choose a predefined style:
                </Label>
                <Select
                  value={selectedPredefinedPrompt}
                  onValueChange={handlePredefinedPromptChange}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a predefined style..." />
                  </SelectTrigger>
                  <SelectContent>
                    {PREDEFINED_PROMPTS.map((prompt, index) => (
                      <SelectItem key={index} value={prompt}>
                        {prompt}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Custom Prompt */}
              <div className="space-y-2">
                <Label htmlFor="custom-prompt">
                  Or enter your own design description:
                </Label>
                <Textarea
                  id="custom-prompt"
                  placeholder="Describe the architectural design you want... (e.g., 'modern bedroom with minimalist furniture, white walls, natural wood accents')"
                  value={customPrompt}
                  onChange={(e) => handleCustomPromptChange(e.target.value)}
                  rows={3}
                />
              </div>

              <div className="flex justify-center">
                <Button
                  onClick={handleGenerate}
                  disabled={isGenerating || !prompt.trim()}
                  size="lg"
                  className="min-w-[200px]"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Wand2 className="h-4 w-4 mr-2" />
                      Generate Design
                    </>
                  )}
                </Button>
              </div>
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
              disabled={isGenerating || !selectedImage || !prompt.trim()}
            >
              Retry
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Generating State */}
      {isGenerating && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
            <h3 className="text-lg font-semibold mb-2">
              Generating Your Design
            </h3>
            <p className="text-sm text-muted-foreground text-center max-w-md">
              Our AI is creating a new architectural design based on your image
              and prompt. This may take 30-60 seconds...
            </p>
          </CardContent>
        </Card>
      )}

      {/* Generated Image Display */}
      {generatedImage && !isGenerating && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Camera className="h-5 w-5" />
              Generated Architectural Design
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-col items-center space-y-4">
              <img
                src={generatedImage.generated_image_url}
                alt="Generated architectural design"
                className="max-w-full h-auto rounded-lg shadow-lg max-h-[500px]"
              />

              <div className="text-center space-y-2">
                <p className="text-sm text-muted-foreground">
                  <strong>Your prompt:</strong> {generatedImage.original_prompt}
                </p>
                <p className="text-xs text-muted-foreground">
                  Generated {generatedImage.total_images} image(s)
                </p>
              </div>

              <Button
                onClick={handleFindSimilar}
                disabled={isSearching}
                size="lg"
                className="min-w-[200px]"
              >
                {isSearching ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Finding Similar...
                  </>
                ) : (
                  <>
                    <Search className="h-4 w-4 mr-2" />
                    Find Similar Products
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Searching State */}
      {isSearching && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
            <h3 className="text-lg font-semibold mb-2">
              Finding Similar Products
            </h3>
            <p className="text-sm text-muted-foreground text-center max-w-md">
              Analyzing your generated design to find similar products in our
              database...
            </p>
          </CardContent>
        </Card>
      )}

      {/* Search Results */}
      {searchResults && !isSearching && (
        <SearchResults results={searchResults} />
      )}
    </div>
  );
}
