from django.contrib import admin
from django.utils.html import format_html

from .models import HomeBackground


@admin.register(HomeBackground)
class HomeBackgroundAdmin(admin.ModelAdmin):
    list_display = ('preview', 'title', 'active', 'order', 'created_at')
    list_editable = ('active', 'order')
    list_filter = ('active',)
    search_fields = ('title', 'image')
    readonly_fields = ('preview_large', 'created_at')
    fields = ('title', 'image', 'active', 'order', 'preview_large', 'created_at')

    @admin.display(description='Превью')
    def preview(self, obj):
        if not obj.image:
            return ''
        return format_html(
            '<img src="{}" style="width:120px;height:64px;object-fit:cover;border-radius:2px;">',
            obj.image.url,
        )

    @admin.display(description='Превью')
    def preview_large(self, obj):
        if not obj or not obj.image:
            return ''
        return format_html(
            '<img src="{}" style="max-width:520px;width:100%;height:auto;object-fit:cover;border-radius:2px;">',
            obj.image.url,
        )
