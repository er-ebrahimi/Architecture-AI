# application/use_cases.py
from typing import List, Dict, Any
from asgiref.sync import sync_to_async
from ..domain.interfaces import (
    ImageAnalysisServiceInterface,
    ImageGenerationServiceInterface,
    ProductRepositoryInterface,
    ImageStorageInterface,
    ImageDownloadInterface
)
from ..domain.value_objects import ImageFeatures, ImageGenerationRequest, ImageGenerationResult


class AddProductUseCase:
    """
    Use case for adding a product with AI analysis.
    Follows Single Responsibility Principle - handles only product addition logic.
    """
    
    def __init__(
        self,
        image_analysis_service: ImageAnalysisServiceInterface,
        product_repository: ProductRepositoryInterface,
        image_storage: ImageStorageInterface,
        image_downloader: ImageDownloadInterface
    ):
        self.image_analysis_service = image_analysis_service
        self.product_repository = product_repository
        self.image_storage = image_storage
        self.image_downloader = image_downloader
    
    async def execute(self, source_url: str, image_url: str) -> Dict[str, Any]:
        """
        Execute the add product use case.
        
        Args:
            source_url: Original product URL
            image_url: URL of the product image to analyze
            
        Returns:
            Dict containing the result of the operation
        """
        try:
            # Download image
            image_bytes, file_extension = await self.image_downloader.download_image(image_url)
            
            # Generate unique filename
            import uuid
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            
            # Save image to storage
            file_path = self.image_storage.save_image(image_bytes, unique_filename)
            
            # Analyze image with AI
            image_features = await self.image_analysis_service.analyze_image(image_bytes)
            
            # Save product to database (using sync_to_async for Django ORM)
            product_id = await sync_to_async(self.product_repository.create_product)(
                source_url=source_url,
                image_filename=unique_filename,
                features=image_features.model_dump()
            )
            
            return {
                'success': True,
                'product_id': product_id,
                'image_filename': unique_filename,
                'image_url': self.image_storage.get_image_url(unique_filename),
                'features': image_features.model_dump(),
                'message': 'Product successfully analyzed and saved'
            }
            
        except Exception as e:
            # Clean up saved image if database save fails
            if 'unique_filename' in locals():
                try:
                    self.image_storage.delete_image(unique_filename)
                except:
                    pass
            
            return {
                'success': False,
                'error': f'Failed to process product: {str(e)}'
            }


class FindSimilarProductsUseCase:
    """
    Use case for finding similar products.
    Follows Single Responsibility Principle - handles only similarity search logic.
    """
    
    def __init__(
        self,
        image_analysis_service: ImageAnalysisServiceInterface,
        product_repository: ProductRepositoryInterface,
        image_storage: ImageStorageInterface,
        image_downloader: ImageDownloadInterface
    ):
        self.image_analysis_service = image_analysis_service
        self.product_repository = product_repository
        self.image_storage = image_storage
        self.image_downloader = image_downloader
    
    async def execute(self, image_bytes: bytes = None, image_url: str = None) -> Dict[str, Any]:
        """
        Execute the find similar products use case.
        
        Args:
            image_bytes: Image bytes (if uploaded directly)
            image_url: Image URL (if downloading from URL)
            
        Returns:
            Dict containing similar products
        """
        try:
            # Get image bytes from either source
            if image_bytes is None and image_url:
                image_bytes, _ = await self.image_downloader.download_image(image_url)
            elif image_bytes is None:
                return {
                    'success': False,
                    'error': 'No image data provided'
                }
            
            # Analyze query image
            query_features = await self.image_analysis_service.analyze_image(image_bytes)
            
            # Extract query tags
            query_tags = []
            for obj in query_features.main_objects:
                query_tags.append(obj.object_type)
                query_tags.extend(obj.attributes)
            query_tags.extend(query_features.overall_style)
            query_tags = [tag.lower().strip() for tag in query_tags if tag and tag.strip()]
            
            # Find similar products (using sync_to_async for Django ORM)
            similar_products = await sync_to_async(self.product_repository.find_similar_products)(query_tags, limit=10)
            
            return {
                'success': True,
                'query_features': query_features.model_dump(),
                'query_tags': query_tags,
                'similar_products': similar_products,
                'total_products_checked': len(similar_products),
                'message': f'Found {len(similar_products)} similar products'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to find similar products: {str(e)}'
            }


class GenerateArchitecturalImageUseCase:
    """
    Use case for generating architectural images.
    Follows Single Responsibility Principle - handles only image generation logic.
    """
    
    def __init__(
        self,
        image_generation_service: ImageGenerationServiceInterface,
        image_storage: ImageStorageInterface,
        image_downloader: ImageDownloadInterface
    ):
        self.image_generation_service = image_generation_service
        self.image_storage = image_storage
        self.image_downloader = image_downloader
    
    def execute(self, request: ImageGenerationRequest) -> Dict[str, Any]:
        """
        Execute the generate architectural image use case.
        
        Args:
            request: Image generation request
            
        Returns:
            Dict containing the generation result
        """
        try:
            # Generate image using AI service
            result = self.image_generation_service.generate_image(request)
            
            if not result.success:
                return {
                    'success': False,
                    'error': f'Image generation failed: {result.error_message}'
                }
            
            # Download and save generated images locally
            local_image_urls = []
            local_image_filenames = []
            
            for i, replicate_url in enumerate(result.generated_image_urls):
                try:
                    # Download image from Replicate URL
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        downloaded_image_bytes, file_extension = loop.run_until_complete(
                            self.image_downloader.download_image(replicate_url)
                        )
                    finally:
                        loop.close()
                    
                    # Generate unique filename
                    import uuid
                    generated_filename = f"generated_{uuid.uuid4()}_{i+1}.{file_extension}"
                    
                    # Save image locally
                    self.image_storage.save_image(downloaded_image_bytes, generated_filename)
                    
                    # Create local URL
                    local_url = self.image_storage.get_image_url(generated_filename)
                    local_image_urls.append(local_url)
                    local_image_filenames.append(generated_filename)
                    
                except Exception as e:
                    # Fall back to original URL if download fails
                    local_image_urls.append(replicate_url)
                    local_image_filenames.append(f"replicate_url_{i+1}")
            
            return {
                'success': True,
                'generated_image_urls': local_image_urls,
                'generated_image_filenames': local_image_filenames,
                'total_images': len(local_image_urls),
                'original_prompt': request.user_prompt,
                'negative_prompt': request.negative_prompt,
                'num_inference_steps': request.num_inference_steps,
                'message': f'Architectural design images generated successfully ({len(local_image_urls)} images)'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to generate architectural image: {str(e)}'
            }
