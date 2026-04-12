from django.contrib import admin
from django.utils.html import format_html
from .models import Album, Media


class MediaInline(admin.TabularInline):
    model  = Media
    extra  = 0
    fields = ['thumb_preview', 'media_type', 'image', 'video_file', 'video_url',
              'caption', 'date_text', 'order', 'published']
    readonly_fields = ['thumb_preview']
    show_change_link = True

    def thumb_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="height:44px;width:60px;object-fit:cover;" />', obj.image.url)
        if obj.pk and obj.is_video:
            return format_html(
                '<span style="display:flex;align-items:center;justify-content:center;'
                'width:60px;height:44px;background:#1a1a1a;font-size:20px;">▶</span>')
        return '—'
    thumb_preview.short_description = ''


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display  = ['cover_thumb', 'title', 'period', 'media_count', 'published', 'order']
    list_display_links = ['cover_thumb', 'title']
    list_filter   = ['period', 'published']
    list_editable = ['published', 'order']
    search_fields = ['title', 'description']
    inlines       = [MediaInline]
    save_on_top   = True

    def cover_thumb(self, obj):
        if obj.cover:
            return format_html(
                '<img src="{}" style="width:52px;height:38px;object-fit:cover;border-radius:2px;" />',
                obj.cover.url)
        return format_html('<span style="color:#555;font-size:11px">—</span>')
    cover_thumb.short_description = ''

    def media_count(self, obj):
        photos = obj.media.filter(media_type='photo').count()
        videos = obj.media.filter(media_type='video').count()
        parts = []
        if photos: parts.append(f'{photos} фото')
        if videos: parts.append(f'{videos} видео')
        return ', '.join(parts) or '0'
    media_count.short_description = 'Медиа'


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display  = ['thumb', 'media_type_badge', 'caption', 'album_link',
                     'date_text', 'fond_item_badge', 'staff_badge', 'published']
    list_display_links = ['thumb', 'caption']
    list_filter   = ['media_type', 'album__period', 'album', 'published']
    list_editable = ['published']
    search_fields = ['caption', 'date_text']
    raw_id_fields     = ['fond_item']
    filter_horizontal = ['linked_staff']
    readonly_fields   = ['thumb_large', 'video_preview', 'fond_item_link', 'staff_links_display']
    save_on_top = True

    fieldsets = (
        ('Основное', {
            'fields': ('album', 'media_type', 'caption', 'date_text', 'order', 'published'),
        }),
        ('📷 Фотография', {
            'fields': ('image', 'thumb_large'),
            'description': 'Загрузите изображение если тип = Фотография',
            'classes': ('collapse',),
        }),
        ('🎬 Видео', {
            'fields': ('video_file', 'video_url', 'video_preview'),
            'description': (
                'Если тип = Видео: загрузите файл (MP4/WebM) ИЛИ вставьте ссылку на YouTube/Vimeo. '
                'Ссылка имеет приоритет над файлом при отображении.'
            ),
            'classes': ('collapse',),
        }),
        ('🔗 Связи с другими разделами', {
            'fields': ('fond_item', 'fond_item_link', 'linked_staff', 'staff_links_display'),
            'description': (
                '<b>Предмет фонда</b> — если у этого медиафайла есть физический оригинал в архиве.<br>'
                '<b>Сотрудники</b> — изображённые или упомянутые люди.'
            ),
        }),
    )

    def thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:52px;height:38px;object-fit:cover;border-radius:2px;" />',
                obj.image.url)
        if obj.is_video:
            return format_html(
                '<span style="display:inline-flex;align-items:center;justify-content:center;'
                'width:52px;height:38px;background:#1a1a1a;border:1px solid #333;'
                'font-size:18px;border-radius:2px;">▶</span>')
        return '—'
    thumb.short_description = ''

    def media_type_badge(self, obj):
        if obj.is_video:
            return format_html('<span style="color:#e74c3c;font-weight:bold">▶ Видео</span>')
        return format_html('<span style="color:#aaa">📷 Фото</span>')
    media_type_badge.short_description = 'Тип'

    def thumb_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:300px;max-height:300px;object-fit:contain;'
                'border:1px solid #333;background:#1a1a1a;padding:4px;" />', obj.image.url)
        return '—'
    thumb_large.short_description = 'Превью фото'

    def video_preview(self, obj):
        if not obj.pk:
            return '—'
        if obj.embed_url:
            return format_html(
                '<div style="margin-top:8px">'
                '<iframe src="{}" width="320" height="180" frameborder="0" '
                'allowfullscreen style="border:1px solid #333;"></iframe></div>',
                obj.embed_url)
        if obj.video_file:
            return format_html(
                '<video controls style="max-width:320px;max-height:200px;'
                'border:1px solid #333;margin-top:8px;" src="{}"></video>',
                obj.video_file.url)
        return format_html('<span style="color:#666">Видео не загружено</span>')
    video_preview.short_description = 'Превью видео'

    def album_link(self, obj):
        url = f'/admin/gallery/album/{obj.album_id}/change/'
        return format_html('<a href="{}">{}</a>', url, obj.album)
    album_link.short_description = 'Альбом'

    def fond_item_badge(self, obj):
        if obj.fond_item_id:
            return format_html('<span style="color:#e74c3c">✓ фонд</span>')
        return format_html('<span style="color:#444">—</span>')
    fond_item_badge.short_description = 'Фонд'

    def staff_badge(self, obj):
        if not obj.pk: return '—'
        c = obj.linked_staff.count()
        return format_html('<span style="color:{}">{}</span>',
                           '#e74c3c' if c else '#444', f'✓ {c}' if c else '—')
    staff_badge.short_description = 'Сотр.'

    def fond_item_link(self, obj):
        if not obj.fond_item_id:
            return format_html('<span style="color:#666">Не выбран.</span>')
        url = f'/admin/fond/fonditem/{obj.fond_item_id}/change/'
        return format_html(
            '<a href="{}" target="_blank" style="color:#e74c3c">↗ {}</a>',
            url, obj.fond_item)
    fond_item_link.short_description = 'Ссылка на предмет фонда'

    def staff_links_display(self, obj):
        if not obj.pk: return '—'
        people = obj.linked_staff.all()
        if not people:
            return format_html('<span style="color:#666">Не выбраны.</span>')
        rows = []
        for s in people:
            url = f'/admin/staff/staffmember/{s.pk}/change/'
            rows.append(f'<a href="{url}" target="_blank" style="color:#e74c3c">↗ {s}</a>')
        return format_html('<br>'.join(rows))
    staff_links_display.short_description = 'Ссылки на сотрудников'
