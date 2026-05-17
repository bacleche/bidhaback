from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()
router.register('transactions', views.TransactionViewSet)
router.register('contracts', views.ContractViewSet)
urlpatterns = [path('', include(router.urls))]
