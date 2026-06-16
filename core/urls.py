from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from core import  views


router = DefaultRouter()
router.register('notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view()),
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('auth/logout/', views.LogoutView.as_view()),
    path('auth/profile/', views.ProfileView.as_view()),
    path('client-stats/', views.ClientStatsView.as_view(), name='client-stats'),
    path('clients/', views.ClientUserListView.as_view(), name='client-list'),
    path('', include(router.urls)),
]

