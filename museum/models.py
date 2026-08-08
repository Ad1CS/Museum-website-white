from django.db import models


class HomeBackground(models.Model):
    title = models.CharField('Название', max_length=120, blank=True)
    image = models.ImageField('Фон главной страницы', upload_to='home/backgrounds/')
    active = models.BooleanField('Использовать в случайной смене', default=True, db_index=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Дата загрузки', auto_now_add=True)

    class Meta:
        verbose_name = 'Фон главной страницы'
        verbose_name_plural = 'Фоны главной страницы'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title or self.image.name
