from django.db import models
from django.urls import reverse
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


class MapSettings(models.Model):
    """Singleton — only one row ever exists. Controls the interactive map view."""
    zoom = models.FloatField(
        'Zoom (масштаб)', default=0,
        help_text='Начальный масштаб. Может быть отрицательным (отдаление) или десятичным (точность).'
    )
    center_x = models.FloatField(
        'Центр — X (пиксели)', default=3684,
        help_text='X-координата центра карты в пикселях изображения (0 = лево, 7368 = право).'
    )
    center_y = models.FloatField(
        'Центр — Y (пиксели)', default=2072,
        help_text='Y-координата центра карты в пикселях изображения (0 = верх, 4144 = низ).'
    )
    min_zoom = models.IntegerField(
        'Минимальный zoom', default=-2,
        help_text='Минимальный zoom (отрицательные = сильное отдаление).'
    )
    max_zoom = models.IntegerField(
        'Максимальный zoom', default=3,
        help_text='Максимальный zoom (приближение).'
    )
    building_zoom = models.FloatField(
        'Zoom показа зданий', default=1,
        help_text='Здания появляются на карте начиная с этого уровня масштабирования.'
    )

    # Territory Overlay
    show_territory = models.BooleanField('Показывать рамку территории', default=True)
    show_territory_label = models.BooleanField('Показывать надпись территории', default=True)
    territory_x = models.FloatField('Территория: Центр X', default=3684)
    territory_y = models.FloatField('Территория: Центр Y', default=2072)
    territory_w = models.FloatField('Территория: Ширина', default=2000)
    territory_h = models.FloatField('Территория: Высота', default=1500)
    territory_rotation = models.FloatField('Территория: Поворот (°)', default=0)
    territory_mirror_x = models.BooleanField('Отразить по горизонтали', default=False)
    territory_mirror_y = models.BooleanField('Отразить по вертикали', default=False)
    territory_clip_path = models.CharField(
        'Территория: Форма (clip-path polygon)', max_length=2000, blank=True, default='',
        help_text='Например: "0% 0%, 100% 0%, 100% 100%, 0% 100%"'
    )
    territory_label = models.CharField('Подпись территории', max_length=100, default='Территория комбината')

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

    # Automated cropping for the map popup (16:9 ratio)
    main_image_cropped = ImageSpecField(source='main_image',
                                      processors=[ResizeToFill(420, 240)],
                                      format='JPEG',
                                      options={'quality': 90})

    built_years = models.CharField('Год постройки', max_length=100, blank=True)
    manual_crop_data = models.CharField('Данные обрезки', max_length=500, blank=True, default='')
    description = models.TextField('Описание')
    # Map position — geographic coordinates
    pos_x = models.FloatField('Позиция X (пиксели)', default=3684, help_text='X-координата центра здания на карте (0–7368)')
    pos_y = models.FloatField('Позиция Y (пиксели)', default=2072, help_text='Y-координата центра здания на карте (0–4144)')
    # Legacy percentage position (still used for static fallback)
    map_left = models.FloatField('Позиция слева (%)', default=10)
    map_top = models.FloatField('Позиция сверху (%)', default=10)
    map_width = models.FloatField('Ширина (%)', default=15)
    map_height = models.FloatField('Высота (%)', default=15)
    map_rotation = models.FloatField('Угол поворота (°)', default=0,
        help_text='Поворот фигуры в градусах (0–360). Например, 45 — диагональ.')
    map_clip_path = models.CharField(
        'Форма (clip-path polygon)', max_length=2000, blank=True, default='',
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
    published = models.BooleanField('Опубликовано', default=True, db_index=True)

    class Meta:
        verbose_name = 'Здание'
        verbose_name_plural = 'Здания на карте'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('mapblock:building', args=[self.slug])
