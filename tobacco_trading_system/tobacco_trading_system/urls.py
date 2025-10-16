from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from authentication import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Load login page first at root and keep name 'home' for templates
    path('', auth_views.login_view, name='home'),
    path('auth/', include('authentication.urls')),
    path('timb/', include('timb_dashboard.urls')),
    path('merchant/', include('merchant_app.urls')),
    path('realtime/', include('realtime_data.urls')),
    path('ai_models/', include('ai_models.urls')),
]

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        # Debug toolbar not installed, skip
        pass
# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'tobacco_trading_system.views.handler404'
handler500 = 'tobacco_trading_system.views.handler500'