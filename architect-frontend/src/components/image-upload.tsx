import React, { useState, useCallback } from "react";
import { Upload, X, Image as ImageIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface ImageUploadProps {
  onImageSelect: (file: File) => void;
  onRemoveImage: () => void;
  selectedImage: File | null;
  isLoading?: boolean;
}

export function ImageUpload({
  onImageSelect,
  onRemoveImage,
  selectedImage,
  isLoading = false,
}: ImageUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);

      const files = Array.from(e.dataTransfer.files);
      const imageFile = files.find((file) => file.type.startsWith("image/"));

      if (imageFile) {
        onImageSelect(imageFile);
      }
    },
    [onImageSelect]
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file && file.type.startsWith("image/")) {
        onImageSelect(file);
      }
    },
    [onImageSelect]
  );

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <Card className="w-full">
      {selectedImage ? (
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Selected Image</h3>
            <Button
              variant="outline"
              size="sm"
              onClick={onRemoveImage}
              disabled={isLoading}
              className="h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          <div className="flex items-center space-x-4">
            <div className="relative h-20 w-20 rounded-lg overflow-hidden bg-muted">
              <img
                src={URL.createObjectURL(selectedImage)}
                alt="Selected"
                className="h-full w-full object-cover"
              />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">
                {selectedImage.name}
              </p>
              <p className="text-sm text-muted-foreground">
                {formatFileSize(selectedImage.size)}
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div
          className={`p-8 border-2 border-dashed rounded-lg transition-colors ${
            isDragOver
              ? "border-primary bg-primary/5"
              : "border-muted-foreground/25 hover:border-primary/50"
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="flex flex-col items-center justify-center space-y-4">
            <div className="rounded-full bg-muted p-4">
              <ImageIcon className="h-8 w-8 text-muted-foreground" />
            </div>

            <div className="text-center">
              <h3 className="text-lg font-semibold mb-2">Upload an image</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Drag and drop an image here, or click to browse
              </p>

              <div className="relative">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  disabled={isLoading}
                  aria-label="Upload an image file"
                  title="Upload an image file"
                />
                <Button variant="outline" disabled={isLoading}>
                  <Upload className="h-4 w-4 mr-2" />
                  Choose Image
                </Button>
              </div>
            </div>

            <p className="text-xs text-muted-foreground">
              Supports: JPEG, PNG, WebP (Max: 10MB)
            </p>
          </div>
        </div>
      )}
    </Card>
  );
}
