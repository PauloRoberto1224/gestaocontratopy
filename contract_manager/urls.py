from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Core
    path('', include('core.urls', namespace='core')),
    
    # Apps
    path('contratos/', include('contracts.urls', namespace='contracts')),
    path('monitoramento/', include('monitoring.urls', namespace='monitoring')),
    path('relatorios/', include('reports.urls', namespace='reports')),
    
    # Auth
    path('accounts/', include('django.contrib.auth.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Error handlers
handler400 = 'core.views.handler400'
handler403 = 'core.views.handler403'
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'
