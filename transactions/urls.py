from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()
router.register('transactions', views.TransactionViewSet, basename='transaction')
router.register('contracts', views.ContractViewSet, basename='contract')
urlpatterns = [path('', include(router.urls))]
