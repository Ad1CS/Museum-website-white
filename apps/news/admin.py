from django.contrib import admin
from django.utils.html import format_html
from .models import NewsPost


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ['thumb', 'title', 'date', 'published']
    list_display_links = ['thumb', 'title']
    list_filter = ['published']
    list_editable = ['published']
    search_fields = ['title', 'body']
    date_hierarchy = 'date'
    save_on_top = True

    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:48px;height:36px;object-fit:cover;" />', obj.image.url)
        return '—'
    thumb.short_description = ''
