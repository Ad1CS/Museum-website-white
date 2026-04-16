from django.contrib import admin
from .models import AboutPage


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Содержание', {'fields': ('title', 'body')}),
        ('Контакты', {'fields': ('contact_email', 'contact_phone', 'contact_address')}),
        ('Соцсети', {'fields': ('vk_url', 'telegram_url', 'youtube_url')}),
        ('Дополнительно', {'fields': ('extra_html',), 'classes': ('collapse',)}),
    )

    def has_add_permission(self, request):
        return not AboutPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
