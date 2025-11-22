# dependency_injection.py
"""
Dependency injection container following Dependency Inversion Principle.
This module provides a centralized way to configure and inject dependencies.
"""

from .infrastructure.repositories import DjangoProductRepository
from .infrastructure.storage import DjangoImageStorage
from .infrastructure.downloaders import HttpImageDownloader
from .infrastructure.ai_services import OpenRouterImageAnalysisService, ReplicateImageGenerationService
from .application.use_cases import AddProductUseCase, FindSimilarProductsUseCase, GenerateArchitecturalImageUseCase
from .presentation.controllers import ProductController, ImageGenerationController, HealthController


class DependencyContainer:
    """
    Dependency injection container that manages all service dependencies.
    Follows Dependency Inversion Principle by providing abstractions instead of concrete implementations.
    """
    
    def __init__(self):
        # Infrastructure layer dependencies
        self._product_repository = None
        self._image_storage = None
        self._image_downloader = None
        self._image_analysis_service = None
        self._image_generation_service = None
        
        # Application layer dependencies
        self._add_product_use_case = None
        self._find_similar_use_case = None
        self._generate_image_use_case = None
        
        # Presentation layer dependencies
        self._product_controller = None
        self._image_generation_controller = None
        self._health_controller = None
    
    # Infrastructure layer getters
    @property
    def product_repository(self):
        if self._product_repository is None:
            self._product_repository = DjangoProductRepository()
        return self._product_repository
    
    @property
    def image_storage(self):
        if self._image_storage is None:
            self._image_storage = DjangoImageStorage()
        return self._image_storage
    
    @property
    def image_downloader(self):
        if self._image_downloader is None:
            self._image_downloader = HttpImageDownloader()
        return self._image_downloader
    
    @property
    def image_analysis_service(self):
        if self._image_analysis_service is None:
            self._image_analysis_service = OpenRouterImageAnalysisService()
        return self._image_analysis_service
    
    @property
    def image_generation_service(self):
        if self._image_generation_service is None:
            self._image_generation_service = ReplicateImageGenerationService()
        return self._image_generation_service
    
    # Application layer getters
    @property
    def add_product_use_case(self):
        if self._add_product_use_case is None:
            self._add_product_use_case = AddProductUseCase(
                image_analysis_service=self.image_analysis_service,
                product_repository=self.product_repository,
                image_storage=self.image_storage,
                image_downloader=self.image_downloader
            )
        return self._add_product_use_case
    
    @property
    def find_similar_use_case(self):
        if self._find_similar_use_case is None:
            self._find_similar_use_case = FindSimilarProductsUseCase(
                image_analysis_service=self.image_analysis_service,
                product_repository=self.product_repository,
                image_storage=self.image_storage,
                image_downloader=self.image_downloader
            )
        return self._find_similar_use_case
    
    @property
    def generate_image_use_case(self):
        if self._generate_image_use_case is None:
            self._generate_image_use_case = GenerateArchitecturalImageUseCase(
                image_generation_service=self.image_generation_service,
                image_storage=self.image_storage,
                image_downloader=self.image_downloader
            )
        return self._generate_image_use_case
    
    # Presentation layer getters
    @property
    def product_controller(self):
        if self._product_controller is None:
            self._product_controller = ProductController(
                add_product_use_case=self.add_product_use_case,
                find_similar_use_case=self.find_similar_use_case
            )
        return self._product_controller
    
    @property
    def image_generation_controller(self):
        if self._image_generation_controller is None:
            self._image_generation_controller = ImageGenerationController(
                generate_image_use_case=self.generate_image_use_case
            )
        return self._image_generation_controller
    
    @property
    def health_controller(self):
        if self._health_controller is None:
            self._health_controller = HealthController()
        return self._health_controller


# Global dependency container instance
container = DependencyContainer()
