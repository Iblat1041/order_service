from django.contrib import admin
from django.urls import include, path
from typing import List
from django.urls import URLPattern, URLResolver

# Импорты для документации
from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularSwaggerView, 
    SpectacularRedocView
)

urlpatterns: List[URLPattern | URLResolver] = [
    path("api/", include("api.urls")),
    path('admin/', admin.site.urls),
    
    # Документация OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
