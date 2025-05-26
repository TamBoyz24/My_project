from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from store.admin import admin_site  # Import the custom admin site

urlpatterns = [
    path('admin/', admin_site.urls),  # Use the custom admin site
    path('', include('store.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)