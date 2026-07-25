from django.db import models
from django.urls import reverse


class ItemType(models.TextChoices):
    PHOTO = 'photo', 'Фото'
    VIDEO = 'video', 'Видео'
    DOCUMENT = 'document', 'Документ'
    OBJECT = 'object', 'Предмет'
    POSTCARD = 'postcard', 'Открытка'


class Period(models.TextChoices):
    P1880 = '1880-1931', '1880–1931'
    P1931 = '1931-1941', '1931–1941'
    P1941 = '1941-1945', '1941–1945'
    P1945 = '1945-1991', '1945–1991'
    P1991 = '1991-2007', '1991–2007'
    P2007 = '2007-now', '2007–н.д.'


class FundCategory(models.TextChoices):
    DOCUMENTS = 'documents', 'Документы и предметы'
    PHOTO = 'photo', 'Фотодокументы'
    PERSONAL = 'personal', 'Личные фонды'


class FondItemLayout(models.TextChoices):
    STANDARD = 'standard', 'Обычная карточка'
    POSTCARD = 'postcard', 'Открытка: лицевая и оборот'


def default_fond_metadata_template():
    return {
        'Год': '',
        'Инвентарный номер': '',
        'Номер по КП': '',
        'Номер в Госкаталоге': '',
        'Автор': '',
        'Источник': '',
        'Место': '',
        'Материал / техника': '',
        'Размер / формат': '',
        'Страницы': '',
        'Дата поступления': '',
    }


FOND_ITEM_DETAIL_TEXT_DEFAULTS = [
    'Источник',
    'Опись',
    'Номер КП',
    'Дата поступления',
    'Датировка',
    'Материал',
    'Размер',
    'Аннотация',
]


class Fund(models.Model):
    """Museum fund (фонд)."""
    category = models.CharField('Категория', max_length=20, choices=FundCategory.choices, default=FundCategory.DOCUMENTS)
    period = models.CharField('Исторический период', max_length=20, choices=Period.choices, blank=True,
                              help_text='Для личных фондов можно оставить пустым.')
    code = models.CharField('Номер фонда', max_length=20, unique=True)
    name = models.CharField('Название фонда', max_length=500)
    description = models.TextField('Описание', blank=True)
    date_start = models.IntegerField('Год начала', null=True, blank=True)
    date_end = models.IntegerField('Год окончания', null=True, blank=True)

    # New fields for museum card layout
    accession_number = models.CharField('Номер книги поступлений', max_length=100, blank=True)
    pages_count = models.PositiveIntegerField('К-во страниц', default=0)
    admission_date = models.DateField('Дата поступления', null=True, blank=True)

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
    def display_pages_count(self):
        """Returns manual pages_count if set, otherwise calculates sum from cases."""
        if self.pages_count > 0:
            return self.pages_count
        
        # Calculate sum from cases
        from django.db.models import Sum
        return self.inventories.aggregate(total=Sum('cases__sheets_count'))['total'] or 0

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
    display_layout = models.CharField('Макет карточки', max_length=20, choices=FondItemLayout.choices,
                                      default=FondItemLayout.STANDARD)

    # Accession data
    kp_number = models.CharField('Номер по КП (книге поступлений)', max_length=100, blank=True)
    inventory_number = models.CharField('Инвентарный номер', max_length=100, blank=True)
    goskatalog_number = models.CharField('Номер в Госкаталоге', max_length=100, blank=True)
    acquisition_date = models.DateField('Дата поступления', null=True, blank=True)

    # Physical properties
    year = models.CharField('Год', max_length=100, blank=True)
    author = models.CharField('Автор', max_length=200, blank=True)
    source = models.CharField('Источник', max_length=300, blank=True)
    location = models.CharField('Место', max_length=200, blank=True)
    pages = models.CharField('Страницы', max_length=100, blank=True)
    size = models.CharField('Размер', max_length=200, blank=True)
    material = models.CharField('Материал / техника', max_length=200, blank=True)
    creation_place = models.CharField('Место создания', max_length=200, blank=True)
    creation_date_text = models.CharField('Период создания (текст)', max_length=200, blank=True)
    detail_path_text = models.CharField(
        'Путь в шапке страницы',
        max_length=300,
        default='фонд >>> каталог',
        blank=True,
        help_text='Текст слева под навигацией на странице предмета.',
    )
    register_text = models.CharField(
        'Учётная строка над заголовком',
        max_length=500,
        blank=True,
        help_text='Если оставить пустым, строка будет собрана из КП, описи, дела и страниц.',
    )
    empty_media_text = models.CharField(
        'Текст вместо изображения',
        max_length=100,
        default='MUSEUM',
        blank=True,
    )
    metadata_template = models.JSONField(
        'Дополнительные поля макета',
        default=default_fond_metadata_template,
        blank=True,
        help_text='Ключи и значения отображаются в таблице карточки. Новые предметы создаются с пустым шаблоном.',
    )

    # Storage
    fund = models.ForeignKey(Fund, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='items', verbose_name='Фонд')
    archive_case = models.ForeignKey(ArchiveCase, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='items', verbose_name='Дело')

    # Media
    image      = models.ImageField('Фотография', upload_to='fond/items/', blank=True, null=True)
    back_image = models.ImageField('Оборотная сторона (для открыток)', upload_to='fond/items/', blank=True, null=True)
    video_file = models.FileField('Видеофайл', upload_to='fond/videos/', blank=True, null=True,
                                  help_text='MP4, WebM — загрузить файл')
    video_url  = models.URLField('Ссылка на видео (YouTube/Vimeo)', blank=True,
                                 help_text='Вставьте ссылку вместо загрузки файла')

    # Cross-links
    linked_staff = models.ManyToManyField('staff.StaffMember', blank=True,
                                           related_name='fond_items', verbose_name='Связанные сотрудники')

    published = models.BooleanField('Опубликовано', default=True, db_index=True)
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

    @property
    def uses_postcard_layout(self):
        return self.display_layout == FondItemLayout.POSTCARD or self.item_type == ItemType.POSTCARD

    @property
    def display_year(self):
        return self.year or self.creation_date_text or self.get_period_display()

    @property
    def metadata_rows(self):
        rows = [
            ('Год', self.display_year),
            ('Инвентарный номер', self.inventory_number),
            ('Номер по КП', self.kp_number),
            ('Номер в Госкаталоге', self.goskatalog_number),
            ('Автор', self.author),
            ('Источник', self.source),
            ('Место', self.location or self.creation_place),
            ('Материал / техника', self.material),
            ('Размер / формат', self.size),
            ('Страницы', self.pages),
            ('Дата поступления', self.acquisition_date.strftime('%d.%m.%Y') if self.acquisition_date else ''),
        ]
        seen = {label for label, _ in rows}
        for label, value in (self.metadata_template or {}).items():
            if label not in seen:
                rows.append((label, value))
        return rows

    @property
    def generated_register_text(self):
        parts = []
        first_number = self.kp_number or self.inventory_number
        if first_number:
            parts.append(first_number)

        if self.archive_case_id and self.archive_case:
            inventory = self.archive_case.inventory
            if inventory:
                case_suffix = f'-{self.archive_case.number}' if self.archive_case.number else ''
                parts.append(f'Опись {inventory.number}{case_suffix}')

        if self.inventory_number and self.inventory_number != first_number:
            parts.append(self.inventory_number)

        if self.pages:
            parts.append(f'{self.pages} с.')

        return ' / '.join(parts)

    @property
    def display_register_text(self):
        return self.register_text or self.generated_register_text

    def default_detail_text_rows(self, empty_values=False):
        inventory = self.archive_case.inventory if self.archive_case_id and self.archive_case else None
        inventory_value = ''
        if inventory:
            inventory_value = inventory.number
            if inventory.name:
                inventory_value = f'{inventory_value} ({inventory.name})'

        values = {
            'Источник': self.source,
            'Опись': inventory_value,
            'Номер КП': self.inventory_number.replace('КП', '').strip() if self.inventory_number else self.kp_number,
            'Дата поступления': self.acquisition_date.strftime('%d.%m.%y') if self.acquisition_date else '',
            'Датировка': self.year or self.creation_date_text,
            'Материал': self.material,
            'Размер': self.size,
            'Аннотация': self.description,
        }
        return [
            {'label': label, 'value': '' if empty_values else values.get(label, '')}
            for label in FOND_ITEM_DETAIL_TEXT_DEFAULTS
        ]

    def detail_text_rows_for_page(self):
        rows = list(self.detail_text_rows.filter(visible=True).order_by('order', 'pk'))
        if rows:
            return rows
        return self.default_detail_text_rows()

    def create_default_detail_text_rows(self, empty_values=False):
        if not self.pk or self.detail_text_rows.exists():
            return
        FondItemDetailText.objects.bulk_create([
            FondItemDetailText(
                item=self,
                order=index,
                label=row['label'],
                value=row['value'],
            )
            for index, row in enumerate(self.default_detail_text_rows(empty_values=empty_values), start=1)
        ])


class FondItemDetailText(models.Model):
    item = models.ForeignKey(
        FondItem,
        on_delete=models.CASCADE,
        related_name='detail_text_rows',
        verbose_name='Предмет фонда',
    )
    order = models.PositiveIntegerField('Порядок', default=0)
    label = models.CharField('Подпись', max_length=120)
    value = models.TextField('Текст', blank=True)
    visible = models.BooleanField('Показывать', default=True)

    class Meta:
        verbose_name = 'Текстовая строка страницы предмета'
        verbose_name_plural = 'Текстовые строки страницы предмета'
        ordering = ['order', 'pk']

    def __str__(self):
        return self.label


class FondItemMedia(models.Model):
    item = models.ForeignKey(FondItem, on_delete=models.CASCADE, related_name='media', verbose_name='Предмет')
    image = models.ImageField('Изображение', upload_to='fond/items/')
    description = models.TextField('Описание', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Медиафайл предмета'
        verbose_name_plural = 'Медиафайлы предмета'
        ordering = ['order']
