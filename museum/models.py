from django.db import models


PAGE_BACKGROUND_CHOICES = (
    ('home', 'Главная'),
    ('about', 'О проекте'),
    ('library', 'Библиотека'),
    ('gallery', 'Галерея'),
    ('fond', 'Фонд'),
    ('staff', 'Отдел кадров'),
    ('history', 'История предприятия'),
    ('buildings', 'Карты и планы'),
    ('building', 'Страница здания'),
    ('not_found', '404'),
)


def page_background_upload_to(instance, filename):
    return f'page-backgrounds/{instance.page or "common"}/{filename}'


class PageBackground(models.Model):
    page = models.CharField('Страница', max_length=32, choices=PAGE_BACKGROUND_CHOICES, default='home', db_index=True)
    title = models.CharField('Название', max_length=120, blank=True)
    image = models.ImageField('Фон страницы', upload_to=page_background_upload_to)
    active = models.BooleanField('Использовать в случайной смене', default=True, db_index=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Дата загрузки', auto_now_add=True)

    class Meta:
        verbose_name = 'Фон страницы'
        verbose_name_plural = 'Фоны страниц'
        ordering = ['page', 'order', '-created_at']

    def __str__(self):
        page = self.get_page_display()
        name = self.title or self.image.name
        return f'{page}: {name}'
