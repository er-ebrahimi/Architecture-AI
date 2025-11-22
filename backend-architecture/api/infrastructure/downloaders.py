# infrastructure/downloaders.py
import httpx
from typing import Tuple
from urllib.parse import urlparse
from ..domain.interfaces import ImageDownloadInterface


class HttpImageDownloader(ImageDownloadInterface):
    """
    HTTP implementation of ImageDownloadInterface.
    Follows Single Responsibility Principle - handles only image downloading.
    """
    
    async def download_image(self, image_url: str) -> Tuple[bytes, str]:
        """
        Download image from URL and return image bytes and file extension.
        
        Args:
            image_url: URL of the image to download
            
        Returns:
            Tuple[bytes, str]: Image bytes and file extension
            
        Raises:
            ValueError: If URL is invalid or image cannot be downloaded
            Exception: If download fails
        """
        try:
            # Validate URL
            parsed_url = urlparse(image_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Invalid URL format")
            
            # Download image with timeout and size limits
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                
                # Check content type
                content_type = response.headers.get('content-type', '').lower()
                if not content_type.startswith('image/'):
                    raise ValueError(f"URL does not point to an image. Content-Type: {content_type}")
                
                # Check content length (limit to 10MB)
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > 10 * 1024 * 1024:
                    raise ValueError("Image file too large (max 10MB)")
                
                image_bytes = response.content
                
                # Double-check size after download
                if len(image_bytes) > 10 * 1024 * 1024:
                    raise ValueError("Image file too large (max 10MB)")
                
                # Determine file extension from content type
                content_type_to_ext = {
                    'image/jpeg': 'jpg',
                    'image/jpg': 'jpg', 
                    'image/png': 'png',
                    'image/gif': 'gif',
                    'image/webp': 'webp',
                    'image/bmp': 'bmp'
                }
                
                file_extension = content_type_to_ext.get(content_type, 'jpg')
                
                return image_bytes, file_extension
                
        except httpx.HTTPStatusError as e:
            raise ValueError(f"Failed to download image: HTTP {e.response.status_code}")
        except httpx.RequestError as e:
            raise ValueError(f"Failed to download image: {str(e)}")
        except Exception as e:
            raise Exception(f"Image download error: {str(e)}")
