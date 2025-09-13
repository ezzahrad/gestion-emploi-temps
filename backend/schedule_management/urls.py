from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.shortcuts import render
from core.views import dashboard_stats

def api_home(request):
    """Page d'accueil de l'API"""
    return render(request, 'api_home.html', {
        'title': 'AppGET - Gestion des Emplois du Temps',
        'version': '1.0.0',
        'status': 'active'
    })

def api_status(request):
    """Status de l'API"""
    return JsonResponse({
        'status': 'OK',
        'message': 'Backend AppGET fonctionnel',
        'services': ['Django', 'PostgreSQL', 'Redis', 'Celery']
    })

urlpatterns = [
    path('', api_home, name='api_home'),
    path('status/', api_status, name='api_status'),
    path('admin/', admin.site.urls),
    path('api/dashboard/', dashboard_stats, name='dashboard_stats'),
    path('api/auth/', include('authentication.urls')),
    path('api/core/', include('core.urls')),
    path('api/schedule/', include('schedule.urls')),
    path('api/notifications/', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
