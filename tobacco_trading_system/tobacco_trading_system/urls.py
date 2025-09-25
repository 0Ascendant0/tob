from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authentication.urls')),
    path('timb/', include('timb_dashboard.urls')),
    path('merchant/', include('merchant_app.urls')),
    path('ai/', include('ai_models.urls')),
    path('realtime/', include('realtime_data.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)