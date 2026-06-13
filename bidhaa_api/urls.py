from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api/', include('agencies.urls')),
    path('api/', include('properties.urls')),
    path('api/', include('clients.urls')),
    path('api/', include('transactions.urls')),
    path('api/', include('interactions.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
