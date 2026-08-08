from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Max


def page_background_upload_to(instance, filename):
    page = getattr(instance, 'page', 'home') or 'home'
    return f'page-backgrounds/{page}/{filename}'


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

    def save(self, *args, **kwargs):
        if self._state.adding and not self.order:
            max_order = HomeBackground.objects.aggregate(max_order=Max('order'))['max_order'] or 0
            self.order = max_order + 1
        super().save(*args, **kwargs)


class HomeBackgroundSettings(models.Model):
    enabled = models.BooleanField('Включить смену фона', default=False)
    interval_seconds = models.PositiveIntegerField(
        'Интервал смены (секунды)',
        default=8,
        validators=[MinValueValidator(2), MaxValueValidator(120)],
        help_text='Как часто менять фон на главной странице. Минимум 2, максимум 120 секунд.',
    )

    class Meta:
        verbose_name = 'Настройка фона главной страницы'
        verbose_name_plural = 'Настройки фона главной страницы'

    def __str__(self):
        return 'Смена фона главной страницы'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
