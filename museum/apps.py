from django.contrib.admin import AdminSite
from django.apps import AppConfig


class MuseumAdminSite(AdminSite):
    site_header = 'Музей трудовой и воинской славы'
    site_title = 'Администрирование музея'
    index_title = 'Управление контентом'
    site_url = '/'


class MuseumAdminConfig(AppConfig):
    name = 'museum'
    verbose_name = 'Музей'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        pass
