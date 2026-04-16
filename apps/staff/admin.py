from django.contrib import admin
from .models import StaffMember


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'patronymic', 'role', 'years_of_life', 'published')
    list_filter = ('published',)
    search_fields = ('last_name', 'first_name', 'patronymic', 'role')
    list_editable = ('published',)
    fieldsets = (
        ('Имя', {'fields': ('last_name', 'first_name', 'patronymic')}),
        ('Основные данные', {'fields': ('years_of_life', 'photo', 'biography')}),
        ('Должность 1', {'fields': ('role', 'role_years')}),
        ('Должность 2', {'fields': ('role2', 'role2_years'), 'classes': ('collapse',)}),
        ('Должность 3', {'fields': ('role3', 'role3_years'), 'classes': ('collapse',)}),
        ('Прочее', {'fields': ('years_worked', 'personal_fund', 'published')}),
    )
