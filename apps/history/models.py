from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models


class HistoryTextBlock(models.Model):
    FONT_CHOICES = (
        ('var(--font), Arial, sans-serif', 'TT Hoves (site default)'),
        ("'TT Hoves', sans-serif", 'TT Hoves (bundled website font)'),
        ("Arial, sans-serif", 'Arial'),
        ("'Arial Black', Gadget, sans-serif", 'Arial Black'),
        ("'Helvetica Neue', Helvetica, Arial, sans-serif", 'Helvetica'),
        ("'Segoe UI', Tahoma, Geneva, Verdana, sans-serif", 'Segoe UI'),
        ("Verdana, Geneva, sans-serif", 'Verdana'),
        ("Tahoma, Geneva, sans-serif", 'Tahoma'),
        ("'Trebuchet MS', Helvetica, sans-serif", 'Trebuchet MS'),
        ("Impact, Charcoal, sans-serif", 'Impact'),
        ("'Comic Sans MS', cursive, sans-serif", 'Comic Sans MS'),
        ("Georgia, serif", 'Georgia'),
        ("'Times New Roman', Times, serif", 'Times New Roman'),
        ("Garamond, serif", 'Garamond'),
        ("'Palatino Linotype', 'Book Antiqua', Palatino, serif", 'Palatino'),
        ("Cambria, Georgia, serif", 'Cambria'),
        ("Constantia, Georgia, serif", 'Constantia'),
        ("'Courier New', Courier, monospace", 'Courier New'),
        ("Consolas, 'Courier New', monospace", 'Consolas'),
        ("'Lucida Console', Monaco, monospace", 'Lucida Console'),
    )
    ALIGN_CHOICES = (
        ('left', 'Слева'),
        ('center', 'По центру'),
        ('right', 'Справа'),
    )
    STYLE_CHOICES = (
        ('normal', 'Обычный'),
        ('italic', 'Курсив'),
    )
    WEIGHT_CHOICES = (
        (100, '100 Thin'),
        (200, '200 Extra Light'),
        (300, '300 Light'),
        (400, '400 Regular'),
        (500, '500 Medium'),
        (600, '600 Demi Bold'),
        (700, '700 Bold'),
        (800, '800 Extra Bold'),
        (900, '900 Black'),
    )

    title = models.CharField(
        'Название в админке',
        max_length=120,
        help_text='Внутреннее название, чтобы было удобно находить блок.',
    )
    text = models.TextField(
        'Текст',
        help_text='Можно писать несколько строк. Переносы сохранятся на странице.',
    )
    left_percent = models.FloatField(
        'Позиция X (%)',
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='0 = левый край страницы, 100 = правый край. Можно двигать в предпросмотре ниже.',
    )
    top_percent = models.FloatField(
        'Позиция Y (%)',
        default=10,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='0 = верх фона, 100 = низ всего длинного фона. Можно двигать в предпросмотре ниже.',
    )
    width_percent = models.FloatField(
        'Ширина блока (%)',
        default=24,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text='Ширина текстовой области относительно ширины страницы.',
    )
    font_family = models.CharField('Шрифт', max_length=160, choices=FONT_CHOICES, default='var(--font), Arial, sans-serif')
    font_size_px = models.PositiveIntegerField(
        'Размер шрифта (px)',
        default=32,
        validators=[MinValueValidator(8), MaxValueValidator(260)],
    )
    font_weight = models.PositiveSmallIntegerField('Толщина', choices=WEIGHT_CHOICES, default=700)
    font_style = models.CharField('Стиль', max_length=12, choices=STYLE_CHOICES, default='normal')
    color = models.CharField(
        'Цвет',
        max_length=7,
        default='#ffffff',
        validators=[RegexValidator(r'^#([0-9A-Fa-f]{6})$', 'Введите цвет в формате #ffffff.')],
    )
    text_align = models.CharField('Выравнивание', max_length=12, choices=ALIGN_CHOICES, default='left')
    line_height = models.FloatField(
        'Межстрочный интервал',
        default=1.1,
        validators=[MinValueValidator(0.8), MaxValueValidator(2.0)],
    )
    letter_spacing_px = models.FloatField(
        'Расстояние между буквами (px)',
        default=0,
        validators=[MinValueValidator(-2), MaxValueValidator(12)],
    )
    text_shadow = models.BooleanField('Тень для читаемости', default=True)
    uppercase = models.BooleanField('Верхний регистр', default=False)
    order = models.PositiveIntegerField('Порядок', default=0)
    published = models.BooleanField('Показывать на сайте', default=True, db_index=True)

    class Meta:
        verbose_name = 'Текст ленты времени'
        verbose_name_plural = 'Тексты ленты времени'
        ordering = ['order', 'id']

    def __str__(self):
        return self.title
