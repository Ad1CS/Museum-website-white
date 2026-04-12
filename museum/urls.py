from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.views.static import serve
from . import views

admin.site.site_header = 'Музей трудовой и воинской славы'
admin.site.site_title = 'Администрирование музея'
admin.site.index_title = 'Управление контентом'

def preview_404(request):
    return render(request, '404.html', status=200)

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('history/', views.HistoryTimelineView.as_view(), name='history'),
    path('fond/', include('apps.fond.urls', namespace='fond')),
    path('gallery/', include('apps.gallery.urls', namespace='gallery')),
    path('staff/', include('apps.staff.urls', namespace='staff')),
    path('map/', include('apps.mapblock.urls', namespace='mapblock')),
    path('news/', include('apps.news.urls', namespace='news')),
    path('about/', include('apps.about.urls', namespace='about')),
    path('library/', include('apps.library.urls', namespace='library')),
    path('admin/', admin.site.urls),
    path('404-preview/', preview_404),
    # Explicitly serve media files in production
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
