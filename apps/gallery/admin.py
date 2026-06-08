from django.contrib import admin
from django.utils.html import format_html
from .models import Album, Media, GalleryPeriod

@admin.register(GalleryPeriod)
class GalleryPeriodAdmin(admin.ModelAdmin):
    list_display = ["title", "order"]
    list_editable = ["order"]

class MediaInline(admin.StackedInline):
    model = Media
    extra = 0
    fields = [("thumb_preview", "image"), "caption", ("date_text", "photographer"), "fond_item", "order", "published"]
    readonly_fields = ["thumb_preview"]
    classes = ["collapse"]

    def thumb_preview(self, obj):
        if obj.pk and obj.image:
            return format_html("<img src=\"{}\" style=\"max-height:150px;max-width:200px;\" />", obj.image.url)
        return "Нет изображения"
    thumb_preview.short_description = "Превью"

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ["cover_thumb", "title", "gallery_period", "is_newsreel", "published", "order"]
    list_filter = ["gallery_period", "is_newsreel", "published"]
    inlines = [MediaInline]

    def cover_thumb(self, obj):
        if obj.cover:
            return format_html("<img src=\"{}\" style=\"height:40px;\" />", obj.cover.url)
        return "—"
    cover_thumb.short_description = ""

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ["thumb", "caption", "date_text", "photographer", "album", "fond_item", "published"]
    list_filter = ["album", "published"]
    raw_id_fields = ["fond_item"]

    def thumb(self, obj):
        if obj.image:
            return format_html("<img src=\"{}\" style=\"height:40px;\" />", obj.image.url)
        return "—"
    thumb.short_description = ""
