from django.db import models
from django.urls import reverse


class HistoricalPeriod(models.TextChoices):
    PRE_SOVIET   = 'pre-soviet',   'Досоветский период (1900–1930)'
    CONSTRUCTION = 'construction', 'Проектирование и строительство (1930–1933)'
    PREWAR       = 'prewar',       'Довоенный период (1933–1941)'
    BLOCKADE     = 'blockade',     'Блокадный период (1941–1944)'
    GOLDEN       = 'golden',       'Период расцвета (1944–1992)'
    POST_SOVIET  = 'post-soviet',  'Постсоветский период (1992–2007)'
    MODERN       = 'modern',       'Современность (2007–н/д)'


class MediaType(models.TextChoices):
    PHOTO = 'photo', 'Фотография'
    VIDEO = 'video', 'Видео'


class Album(models.Model):
    title       = models.CharField('Название', max_length=300)
    period      = models.CharField('Период', max_length=30, choices=HistoricalPeriod.choices)
    description = models.TextField('Описание', blank=True)
    cover       = models.ImageField('Обложка', upload_to='gallery/covers/', blank=True, null=True)
    order       = models.PositiveIntegerField('Порядок', default=0)
    published   = models.BooleanField('Опубликован', default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Альбом'
        verbose_name_plural = 'Альбомы'
        ordering = ['period', 'order', 'title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('gallery:album_detail', args=[self.pk])


class Media(models.Model):
    """Photo or video inside an album."""
    album      = models.ForeignKey(Album, on_delete=models.CASCADE,
                                   related_name='media', verbose_name='Альбом')
    media_type = models.CharField('Тип', max_length=10,
                                  choices=MediaType.choices, default=MediaType.PHOTO)

    # Photo fields
    image      = models.ImageField('Изображение', upload_to='gallery/photos/',
                                   blank=True, null=True)

    # Video fields
    video_file = models.FileField('Видеофайл', upload_to='gallery/videos/',
                                  blank=True, null=True,
                                  help_text='MP4, WebM, OGG — загрузить файл')
    video_url  = models.URLField('Ссылка на видео (YouTube/Vimeo)', blank=True,
                                 help_text='Вставьте ссылку вместо загрузки файла')

    caption    = models.CharField('Подпись', max_length=500, blank=True)
    date_text  = models.CharField('Дата (текст)', max_length=100, blank=True)

    # Cross-links
    fond_item  = models.ForeignKey(
        'fond.FondItem', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='gallery_photos', verbose_name='Предмет фонда (оригинал)'
    )
    linked_staff = models.ManyToManyField(
        'staff.StaffMember', blank=True,
        related_name='photos', verbose_name='Изображённые / упомянутые сотрудники'
    )

    order      = models.PositiveIntegerField('Порядок', default=0)
    published  = models.BooleanField('Опубликовано', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Медиафайл'
        verbose_name_plural = 'Медиафайлы'
        ordering = ['album', 'order']

    def __str__(self):
        return self.caption or f'{self.get_media_type_display()} #{self.pk}'

    @property
    def is_video(self):
        return self.media_type == MediaType.VIDEO

    @property
    def embed_url(self):
        """Convert YouTube/Vimeo URL to embed URL."""
        url = self.video_url
        if not url:
            return None
        # YouTube
        import re
        yt = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
        if yt:
            return f'https://www.youtube.com/embed/{yt.group(1)}'
        # Vimeo
        vm = re.search(r'vimeo\.com/(\d+)', url)
        if vm:
            return f'https://player.vimeo.com/video/{vm.group(1)}'
        return url


# Keep Photo as alias for backwards compat in cross-links
Photo = Media
