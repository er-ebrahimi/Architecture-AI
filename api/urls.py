# urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'api'

urlpatterns = [
    # API Endpoints
    path('products/', views.add_product, name='add_product'),
    path('products/find-similar/', views.find_similar_products, name='find_similar_products'),
    path('health/', views.health_check, name='health_check'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

