from django.contrib import admin
from .models import LibraryItem


@admin.register(LibraryItem)
class LibraryItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'year', 'file_ext', 'published')
    list_filter = ('category', 'published')
    search_fields = ('title', 'author')
    list_editable = ('published',)
    fieldsets = (
        (None, {'fields': ('category', 'title', 'author', 'year', 'description')}),
        ('Файлы', {'fields': ('cover', 'file')}),
        ('Публикация', {'fields': ('published',)}),
    )
