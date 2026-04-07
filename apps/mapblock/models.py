from django.db import models
from django.urls import reverse


class MapSettings(models.Model):
    """Singleton — only one row ever exists. Controls the interactive map view."""
    zoom = models.PositiveIntegerField(
        'Zoom (масштаб)', default=20,
        help_text='1 = весь мир, 20 = ~50м над землёй. Рекомендуется 18–20 для территории предприятия.'
    )
    center_lat = models.FloatField(
        'Центр — широта', default=59.8228,
        help_text='Широта центра карты. Текущее значение: 59.8228'
    )
    center_lng = models.FloatField(
        'Центр — долгота', default=30.3508,
        help_text='Долгота центра карты. Текущее значение: 30.3508'
    )

    class Meta:
        verbose_name = 'Настройки карты'
        verbose_name_plural = 'Настройки карты'

    def __str__(self):
        return f'Настройки карты (zoom={self.zoom})'

    def save(self, *args, **kwargs):
        self.pk = 1  # Singleton — always overwrite row 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Building(models.Model):
    slug = models.SlugField('Slug', unique=True)
    name = models.CharField('Название', max_length=300)
    main_image = models.ImageField('Главное фото', upload_to='map/buildings/', blank=True, null=True)
    built_years = models.CharField('Год постройки', max_length=100, blank=True)
    description = models.TextField('Описание')
    # Map position (percentage from top-left of the map image)
    map_left = models.FloatField('Позиция слева (%)', default=10)
    map_top = models.FloatField('Позиция сверху (%)', default=10)
    map_width = models.FloatField('Ширина (%)', default=15)
    map_height = models.FloatField('Высота (%)', default=15)
    map_rotation = models.FloatField('Угол поворота (°)', default=0,
        help_text='Поворот фигуры в градусах (0–360). Например, 45 — диагональ.')
    map_clip_path = models.CharField(
        'Форма (clip-path polygon)', max_length=500, blank=True, default='',
        help_text=(
            'Необязательно. SVG polygon points в процентах, например: '
            '"0% 0%, 100% 0%, 100% 100%, 0% 100%" — прямоугольник. '
            '"0% 20%, 80% 0%, 100% 80%, 20% 100%" — трапеция. '
            'Оставьте пустым для стандартного прямоугольника.'
        )
    )

    photos = models.ManyToManyField('gallery.Media', blank=True,
                                     related_name='buildings', verbose_name='Фотографии')
    order = models.PositiveIntegerField('Порядок', default=0)
    published = models.BooleanField('Опубликовано', default=True)

    class Meta:
        verbose_name = 'Здание'
        verbose_name_plural = 'Здания на карте'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('mapblock:building', args=[self.slug])
