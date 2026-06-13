from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('contact-requests', views.ContactRequestViewSet, basename='contact-request')
router.register('visit-requests', views.VisitRequestViewSet, basename='visit-request')
router.register('complaints', views.ComplaintViewSet, basename='complaint')

urlpatterns = [path('', include(router.urls))]