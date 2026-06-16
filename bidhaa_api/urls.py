from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.http import JsonResponse

def debug_cloudinary(request):
    return JsonResponse({
        'cloud_name': os.environ.get('CLOUDINARY_CLOUD_NAME', 'NON DÉFINI'),
        'api_key': os.environ.get('CLOUDINARY_API_KEY', 'NON DÉFINI'),
        'has_secret': bool(os.environ.get('CLOUDINARY_API_SECRET')),
    })
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api/', include('agencies.urls')),
    path('api/', include('properties.urls')),
    path('api/', include('clients.urls')),
    path('api/', include('transactions.urls')),
    path('api/', include('interactions.urls')),

    path('debug-cloudinary/', debug_cloudinary),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
