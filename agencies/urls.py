from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('agencies', views.AgencyViewSet)
router.register('agents', views.AgentViewSet, basename='agent')
urlpatterns = [path('', include(router.urls))]
