from django.db import models
from django.urls import reverse


class ItemType(models.TextChoices):
    PHOTO = 'photo', 'Фото'
    VIDEO = 'video', 'Видео'
    DOCUMENT = 'document', 'Документ'
    OBJECT = 'object', 'Предмет'


class Period(models.TextChoices):
    P1900 = '1900-1930', '1900–1930'
    P1931 = '1931-1940', '1931–1940'
    P1941 = '1941-1945', '1941–1945 (Блокада)'
    P1946 = '1946-1992', '1946–1992'
    P1992 = '1992-2007', '1992–2007'
    P2007 = '2007-now', '2007–настоящее время'


class Fund(models.Model):
    """Museum fund (фонд)."""
    code = models.CharField('Номер фонда', max_length=20, unique=True)
    name = models.CharField('Название фонда', max_length=500)
    description = models.TextField('Описание', blank=True)
    date_start = models.IntegerField('Год начала', null=True, blank=True)
    date_end = models.IntegerField('Год окончания', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Фонд'
        verbose_name_plural = 'Фонды'
        ordering = ['code']

    def __str__(self):
        return f'{self.code} — {self.name}'

    def get_absolute_url(self):
        return reverse('fond:fund_detail', args=[self.pk])

    @property
    def dates_display(self):
        if self.date_start and self.date_end:
            return f'{self.date_start}–{self.date_end}'
        if self.date_start:
            return f'{self.date_start}–н/в'
        return '—'


class Inventory(models.Model):
    """Опись."""
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE, related_name='inventories', verbose_name='Фонд')
    number = models.CharField('Номер описи', max_length=20)
    name = models.CharField('Название описи', max_length=500)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Опись'
        verbose_name_plural = 'Описи'
        ordering = ['fund', 'number']
        unique_together = ['fund', 'number']

    def __str__(self):
        return f'Оп.{self.number} — {self.name}'


class ArchiveCase(models.Model):
    """Дело."""
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='cases', verbose_name='Опись')
    number = models.CharField('Номер дела', max_length=20)
    title = models.CharField('Заголовок дела', max_length=500)
    date_start = models.DateField('Дата начала', null=True, blank=True)
    date_end = models.DateField('Дата окончания', null=True, blank=True)
    sheets_count = models.PositiveIntegerField('Количество листов', default=0)
    digitized = models.BooleanField('Оцифровано', default=False)

    class Meta:
        verbose_name = 'Дело'
        verbose_name_plural = 'Дела'
        ordering = ['inventory', 'number']

    def __str__(self):
        return f'Д.{self.number} — {self.title}'

    def get_absolute_url(self):
        return reverse('fond:case_detail', args=[self.pk])


class FondItem(models.Model):
    """Individual catalog item / museum object."""
    title = models.CharField('Название', max_length=500)
    description = models.TextField('Описание', blank=True)
    item_type = models.CharField('Тип', max_length=20, choices=ItemType.choices, default=ItemType.OBJECT)
    period = models.CharField('Период', max_length=20, choices=Period.choices, blank=True)

    # Accession data
    kp_number = models.CharField('Номер по КП (книге поступлений)', max_length=100, blank=True)
    inventory_number = models.CharField('Инвентарный номер', max_length=100, blank=True)
    goskatalog_number = models.CharField('Номер в Госкаталоге', max_length=100, blank=True)

    # Physical properties
    size = models.CharField('Размер', max_length=200, blank=True)
    material = models.CharField('Материал / техника', max_length=200, blank=True)
    creation_place = models.CharField('Место создания', max_length=200, blank=True)
    creation_date_text = models.CharField('Период создания (текст)', max_length=200, blank=True)

    # Storage
    fund = models.ForeignKey(Fund, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='items', verbose_name='Фонд')
    archive_case = models.ForeignKey(ArchiveCase, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='items', verbose_name='Дело')

    # Media
    image      = models.ImageField('Фотография', upload_to='fond/items/', blank=True, null=True)
    video_file = models.FileField('Видеофайл', upload_to='fond/videos/', blank=True, null=True,
                                  help_text='MP4, WebM — загрузить файл')
    video_url  = models.URLField('Ссылка на видео (YouTube/Vimeo)', blank=True,
                                 help_text='Вставьте ссылку вместо загрузки файла')

    # Cross-links
    linked_staff = models.ManyToManyField('staff.StaffMember', blank=True,
                                           related_name='fond_items', verbose_name='Связанные сотрудники')

    published = models.BooleanField('Опубликовано', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Предмет фонда'
        verbose_name_plural = 'Предметы фонда'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('fond:item_detail', args=[self.pk])

    @property
    def embed_url(self):
        url = self.video_url
        if not url:
            return None
        import re
        yt = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
        if yt:
            return f'https://www.youtube.com/embed/{yt.group(1)}'
        vm = re.search(r'vimeo\.com/(\d+)', url)
        if vm:
            return f'https://player.vimeo.com/video/{vm.group(1)}'
        return url
