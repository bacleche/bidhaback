from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()
router.register('properties', views.PropertyViewSet, basename='property')
router.register('property-images', views.PropertyImageViewSet)
urlpatterns = [path('', include(router.urls))]
