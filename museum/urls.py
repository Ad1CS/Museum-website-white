from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from . import views
from .seo import robots_txt, sitemap_xml
from .sitemaps import sitemaps

admin.site.site_header = 'Музей трудовой и воинской славы'
admin.site.site_title = 'Администрирование музея'
admin.site.index_title = 'Управление контентом'

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
    path('sitemap.xml', sitemap_xml, {'sitemaps': sitemaps}, name='sitemap_xml'),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('admin/', admin.site.urls),
    path('404/', views.page_404, name='page_404'),
    path('404-preview/', views.legacy_404_preview_redirect),
    # Explicitly serve media files in production
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

handler404 = 'museum.views.page_not_found'

if settings.DEBUG:
    urlpatterns.append(re_path(r'^.*$', views.page_not_found))
