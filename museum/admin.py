from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html

from .models import HomeBackground, HomeBackgroundSettings


@admin.register(HomeBackground)
class HomeBackgroundAdmin(admin.ModelAdmin):
    list_display = ('preview', 'title', 'active', 'created_at')
    list_editable = ('active',)
    list_filter = ('active',)
    search_fields = ('title', 'image')
    readonly_fields = ('preview_large', 'created_at')
    fields = ('title', 'image', 'active', 'preview_large', 'created_at')
    actions = ('activate_selected', 'deactivate_selected')

    def changelist_view(self, request, extra_context=None):
        settings = HomeBackgroundSettings.objects.first()
        active_count = HomeBackground.objects.filter(active=True).count()
        if not settings or not settings.enabled:
            messages.info(request, 'Смена фона главной страницы выключена. Включите ее в настройках фона.')
        elif active_count < 2:
            messages.warning(request, 'Для смены фона нужно минимум 2 активных изображения.')
        else:
            messages.success(request, f'Смена фона включена: {active_count} активных изображений.')
        return super().changelist_view(request, extra_context=extra_context)

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

    @admin.action(description='Включить выбранные фоны')
    def activate_selected(self, request, queryset):
        updated = queryset.update(active=True)
        self.message_user(request, f'Включено фонов: {updated}.', messages.SUCCESS)

    @admin.action(description='Выключить выбранные фоны')
    def deactivate_selected(self, request, queryset):
        updated = queryset.update(active=False)
        self.message_user(request, f'Выключено фонов: {updated}.', messages.SUCCESS)


@admin.register(HomeBackgroundSettings)
class HomeBackgroundSettingsAdmin(admin.ModelAdmin):
    list_display = ('enabled', 'interval_seconds', 'active_backgrounds_count', 'ready_state')
    readonly_fields = ('slideshow_status', 'backgrounds_link')
    fields = ('slideshow_status', 'enabled', 'interval_seconds', 'backgrounds_link')

    def changelist_view(self, request, extra_context=None):
        obj, _ = HomeBackgroundSettings.objects.get_or_create(pk=1)
        return redirect(reverse('admin:museum_homebackgroundsettings_change', args=[obj.pk]))

    def has_add_permission(self, request):
        return not HomeBackgroundSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description='Активных фонов')
    def active_backgrounds_count(self, obj):
        return HomeBackground.objects.filter(active=True).count()

    @admin.display(description='Статус')
    def ready_state(self, obj):
        active_count = HomeBackground.objects.filter(active=True).count()
        if not obj.enabled:
            return 'Выключено'
        if active_count < 2:
            return 'Нужно минимум 2 активных фона'
        return 'Готово'

    @admin.display(description='Статус смены фона')
    def slideshow_status(self, obj):
        active_count = HomeBackground.objects.filter(active=True).count()
        total_count = HomeBackground.objects.count()
        if not obj.enabled:
            color = '#8a6d3b'
            text = 'Смена фона выключена.'
            detail = 'Фон на главной странице не будет меняться автоматически.'
        elif active_count < 2:
            color = '#a94442'
            text = 'Смена фона включена, но не запустится.'
            detail = 'Добавьте минимум 2 активных изображения в "Фоны главной страницы".'
        else:
            color = '#3c763d'
            text = 'Смена фона работает.'
            detail = f'Главная страница будет случайно менять {active_count} активных фонов каждые {obj.interval_seconds} сек.'
        return format_html(
            '<div style="max-width:760px;margin:4px 0 8px;">'
            '<p style="margin:0 0 8px;font-size:14px;font-weight:700;color:#222;">'
            '<span style="display:inline-block;width:9px;height:9px;margin-right:8px;border-radius:50%;background:{color};vertical-align:middle;"></span>'
            '{text}'
            '</p>'
            '<p style="margin:0 0 6px;color:#444;">{detail}</p>'
            '<p style="margin:0;color:#666;">Всего загружено: {total}. Активных: {active}. Порядок новых изображений назначается автоматически.</p>'
            '</div>',
            color=color,
            text=text,
            detail=detail,
            total=total_count,
            active=active_count,
        )

    @admin.display(description='Изображения')
    def backgrounds_link(self, obj):
        url = reverse('admin:museum_homebackground_changelist')
        return format_html('<a class="button" href="{}">Открыть фоны главной страницы</a>', url)
