from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Skin Detection App URLs
    path('', include('skin_detection.urls')),
]

# Serve media files
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)

# Serve static files
urlpatterns += static(
    settings.STATIC_URL,
    document_root=settings.STATICFILES_DIRS[0]
)