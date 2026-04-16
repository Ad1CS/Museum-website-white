from django.contrib import admin
from django.utils.html import format_html
from .models import Fund, Inventory, ArchiveCase, FondItem


# ─────────────────────────── FUND ────────────────────────────────────────────

class InventoryInline(admin.TabularInline):
    model = Inventory
    extra = 0
    fields = ['number', 'name']
    show_change_link = True


@admin.register(Fund)
class FundAdmin(admin.ModelAdmin):
    list_display  = ['code', 'name', 'date_start', 'date_end', 'item_count']
    search_fields = ['code', 'name', 'description']
    inlines       = [InventoryInline]

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Предметов'


# ─────────────────────────── INVENTORY / CASE ────────────────────────────────

class ArchiveCaseInline(admin.TabularInline):
    model = ArchiveCase
    extra = 0
    fields = ['number', 'title', 'date_start', 'date_end', 'sheets_count', 'digitized']
    show_change_link = True


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display  = ['fund', 'number', 'name', 'case_count']
    list_filter   = ['fund']
    search_fields = ['number', 'name']
    inlines       = [ArchiveCaseInline]

    def case_count(self, obj):
        return obj.cases.count()
    case_count.short_description = 'Дел'


@admin.register(ArchiveCase)
class ArchiveCaseAdmin(admin.ModelAdmin):
    list_display  = ['inventory', 'number', 'title', 'date_start', 'date_end', 'sheets_count', 'digitized']
    list_filter   = ['digitized', 'inventory__fund']
    search_fields = ['number', 'title']
    list_editable = ['digitized']


# ─────────────────────────── FOND ITEM ───────────────────────────────────────

@admin.register(FondItem)
class FondItemAdmin(admin.ModelAdmin):
    list_display  = ['thumbnail', 'title', 'item_type', 'period', 'kp_number',
                     'fund', 'gallery_photos_count', 'bulk_upload_link', 'staff_count', 'published']
    list_display_links = ['thumbnail', 'title']
    list_filter   = ['item_type', 'period', 'published', 'fund']
    list_editable = ['published']
    search_fields = ['title', 'description', 'kp_number', 'inventory_number', 'goskatalog_number']
    filter_horizontal = ['linked_staff']
    readonly_fields   = ['created_at', 'updated_at', 'image_preview', 'video_preview',
                         'gallery_photos_links', 'staff_links_display']
    save_on_top = True

    def get_urls(self):
        urls = super().get_urls()
        from .views import bulk_upload_do
        from django.urls import path
        from django.shortcuts import render, get_object_or_404
        
        def bulk_upload_view(request, item_id):
            item = get_object_or_404(FondItem, pk=item_id)
            return render(request, 'admin/fond/bulk_upload.html', {'item': item})

        my_urls = [
            path('<int:item_id>/bulk-upload/', self.admin_site.admin_view(bulk_upload_view), name='fond_item_bulk_upload'),
            path('<int:item_id>/bulk-upload/do/', self.admin_site.admin_view(bulk_upload_do), name='fond_item_bulk_upload_do'),
        ]
        return my_urls + urls

    def bulk_upload_link(self, obj):
        if not obj.pk: return '—'
        from django.urls import reverse
        url = reverse('admin:fond_item_bulk_upload', args=[obj.pk])
        return format_html(
            '<a href="{}" style="background:#417690;color:white;padding:4px 10px;'
            'border-radius:3px;font-size:12px;text-decoration:none;white-space:nowrap;">'
            '📷 Загрузить фото</a>', url)
    bulk_upload_link.short_description = 'Массовая загрузка'

    fieldsets = (
        ('Основное', {
            'fields': ('title', 'description', 'item_type', 'period', 'published'),
        }),
        ('Учётные номера', {
            'fields': ('kp_number', 'inventory_number', 'goskatalog_number'),
            'classes': ('collapse',),
        }),
        ('Физические характеристики', {
            'fields': ('size', 'material', 'creation_place', 'creation_date_text'),
            'classes': ('collapse',),
        }),
        ('Хранение', {
            'fields': ('fund', 'archive_case'),
        }),
        ('Медиа', {
            'fields': ('image', 'image_preview', 'video_file', 'video_url', 'video_preview'),
        }),
        ('🔗 Связи с другими разделами', {
            'fields': ('linked_staff', 'staff_links_display', 'gallery_photos_links'),
            'description': (
                'Выберите сотрудников, связанных с этим предметом. '
                'Фотографии галереи, ссылающиеся на этот предмет, отображаются ниже автоматически — '
                'добавлять их нужно через раздел «Фотогалерея».'
            ),
        }),
        ('Служебное', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    # ── Thumbnails ──────────────────────────────────────────────────────────

    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:52px;height:38px;object-fit:cover;border-radius:2px;" />',
                obj.image.url)
        return format_html('<span style="color:#555;font-size:11px">нет</span>')
    thumbnail.short_description = ''

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:320px;max-height:320px;object-fit:contain;'
                'border:1px solid #333;background:#1a1a1a;padding:4px;" />',
                obj.image.url)
        return '—'
    image_preview.short_description = 'Превью фото'

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
        return format_html(
            '<span style="color:#666">Видео не добавлено. Загрузите файл или вставьте ссылку выше.</span>')
    video_preview.short_description = 'Превью видео'

    # ── Counters ────────────────────────────────────────────────────────────

    def gallery_photos_count(self, obj):
        c = obj.gallery_photos.count()
        color = '#e74c3c' if c else '#555'
        return format_html('<b style="color:{}">{}</b>', color, c)
    gallery_photos_count.short_description = '📷'

    def staff_count(self, obj):
        c = obj.linked_staff.count()
        color = '#e74c3c' if c else '#555'
        return format_html('<b style="color:{}">{}</b>', color, c)
    staff_count.short_description = '👤'

    # ── Cross-link read-only displays ────────────────────────────────────────

    def staff_links_display(self, obj):
        if not obj.pk:
            return '—'
        people = obj.linked_staff.all()
        if not people:
            return format_html('<span style="color:#666">Сотрудники не выбраны.</span>')
        rows = []
        for s in people:
            url = f'/admin/staff/staffmember/{s.pk}/change/'
            rows.append(f'<a href="{url}" target="_blank" style="color:#e74c3c">↗ {s}</a>')
        return format_html('<br>'.join(rows))
    staff_links_display.short_description = 'Ссылки на страницы сотрудников'

    def gallery_photos_links(self, obj):
        if not obj.pk:
            return '—'
        photos = obj.gallery_photos.all()
        if not photos:
            return format_html(
                '<span style="color:#666">Фотографий нет. Чтобы привязать фото, откройте нужную '
                'фотографию в разделе «Фотогалерея» и выберите этот предмет в поле '
                '«Предмет фонда».</span>')
        rows = []
        for p in photos[:12]:
            url   = f'/admin/gallery/photo/{p.pk}/change/'
            label = (p.caption or f'Фото #{p.pk}')[:55]
            rows.append(f'<a href="{url}" target="_blank" style="color:#e74c3c">↗ {label}</a>')
        if photos.count() > 12:
            rows.append(f'<span style="color:#666">...ещё {photos.count()-12}</span>')
        return format_html('<br>'.join(rows))
    gallery_photos_links.short_description = 'Фотографии в галерее'
