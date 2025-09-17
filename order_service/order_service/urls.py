from django.urls import include, path
from typing import List
from django.urls import URLPattern, URLResolver

urlpatterns: List[URLPattern | URLResolver] = [
    path("api/", include("api.urls")),
]
