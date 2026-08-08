from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import migrations, models


def seed_history_text_blocks(apps, schema_editor):
    HistoryTextBlock = apps.get_model('history', 'HistoryTextBlock')
    if HistoryTextBlock.objects.exists():
        return

    defaults = [
        {
            'title': 'Верхний заголовок: лента времени',
            'text': 'лента времени',
            'left_percent': 33,
            'top_percent': 1.8,
            'width_percent': 18,
            'font_size_px': 24,
            'font_weight': 800,
            'color': '#000000',
            'text_align': 'center',
            'uppercase': True,
        },
        {
            'title': 'Верхний заголовок: история предприятия',
            'text': 'история предприятия',
            'left_percent': 69,
            'top_percent': 1.8,
            'width_percent': 22,
            'font_size_px': 24,
            'font_weight': 500,
            'color': '#ffffff',
            'text_align': 'center',
        },
        {
            'title': '1931',
            'text': '1931',
            'left_percent': 5,
            'top_percent': 9.6,
            'width_percent': 22,
            'font_size_px': 120,
            'font_weight': 800,
            'color': '#ffffff',
        },
        {
            'title': '1931: 16 июля',
            'text': '16 июля',
            'left_percent': 48,
            'top_percent': 11.4,
            'width_percent': 16,
            'font_size_px': 24,
            'font_weight': 700,
            'color': '#ffffff',
        },
        {
            'title': '1931: 7 ноября',
            'text': '7 ноября',
            'left_percent': 48,
            'top_percent': 13.3,
            'width_percent': 16,
            'font_size_px': 24,
            'font_weight': 700,
            'color': '#ffffff',
        },
        {
            'title': '1931: начало закладки',
            'text': 'начало закладки\nфундамента под\nбудущий завод',
            'left_percent': 48,
            'top_percent': 14.0,
            'width_percent': 18,
            'font_size_px': 16,
            'font_weight': 400,
            'color': '#ffffff',
        },
        {
            'title': 'Строительство комбината',
            'text': 'строительство\nкомбината',
            'left_percent': 35,
            'top_percent': 24.6,
            'width_percent': 30,
            'font_size_px': 52,
            'font_weight': 800,
            'color': '#ffffff',
            'text_align': 'center',
        },
        {
            'title': 'Строительство: 16 июля',
            'text': '16 июля',
            'left_percent': 55,
            'top_percent': 29.0,
            'width_percent': 16,
            'font_size_px': 28,
            'font_weight': 700,
            'color': '#ffffff',
        },
        {
            'title': '1933',
            'text': '1933',
            'left_percent': 5,
            'top_percent': 49.2,
            'width_percent': 22,
            'font_size_px': 120,
            'font_weight': 800,
            'color': '#ffffff',
        },
        {
            'title': 'Довоенный период',
            'text': 'довоенный\nпериод',
            'left_percent': 40,
            'top_percent': 57.8,
            'width_percent': 20,
            'font_size_px': 38,
            'font_weight': 800,
            'color': '#ffffff',
            'text_align': 'center',
        },
        {
            'title': '1937',
            'text': '1937',
            'left_percent': 5,
            'top_percent': 75.0,
            'width_percent': 22,
            'font_size_px': 120,
            'font_weight': 800,
            'color': '#ffffff',
        },
        {
            'title': 'Война',
            'text': 'война',
            'left_percent': 42,
            'top_percent': 88.0,
            'width_percent': 16,
            'font_size_px': 52,
            'font_weight': 800,
            'color': '#ffffff',
            'text_align': 'center',
        },
    ]

    for order, data in enumerate(defaults, start=10):
        HistoryTextBlock.objects.create(order=order, **data)


def unseed_history_text_blocks(apps, schema_editor):
    HistoryTextBlock = apps.get_model('history', 'HistoryTextBlock')
    HistoryTextBlock.objects.filter(order__gte=10, order__lte=21).delete()


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='HistoryTextBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Внутреннее название, чтобы было удобно находить блок.', max_length=120, verbose_name='Название в админке')),
                ('text', models.TextField(help_text='Можно писать несколько строк. Переносы сохранятся на странице.', verbose_name='Текст')),
                ('left_percent', models.FloatField(default=50, help_text='0 = левый край страницы, 100 = правый край. Можно двигать в предпросмотре ниже.', validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Позиция X (%)')),
                ('top_percent', models.FloatField(default=10, help_text='0 = верх фона, 100 = низ всего длинного фона. Можно двигать в предпросмотре ниже.', validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Позиция Y (%)')),
                ('width_percent', models.FloatField(default=24, help_text='Ширина текстовой области относительно ширины страницы.', validators=[MinValueValidator(1), MaxValueValidator(100)], verbose_name='Ширина блока (%)')),
                ('font_family', models.CharField(choices=[('var(--font), Arial, sans-serif', 'TT Hoves'), ('Arial, sans-serif', 'Arial'), ('Georgia, serif', 'Georgia'), ('Times New Roman, serif', 'Times New Roman'), ('Courier New, monospace', 'Courier New')], default='var(--font), Arial, sans-serif', max_length=80, verbose_name='Шрифт')),
                ('font_size_px', models.PositiveIntegerField(default=32, validators=[MinValueValidator(8), MaxValueValidator(260)], verbose_name='Размер шрифта (px)')),
                ('font_weight', models.PositiveSmallIntegerField(choices=[(100, '100 Thin'), (200, '200 Extra Light'), (300, '300 Light'), (400, '400 Regular'), (500, '500 Medium'), (600, '600 Demi Bold'), (700, '700 Bold'), (800, '800 Extra Bold'), (900, '900 Black')], default=700, verbose_name='Толщина')),
                ('font_style', models.CharField(choices=[('normal', 'Обычный'), ('italic', 'Курсив')], default='normal', max_length=12, verbose_name='Стиль')),
                ('color', models.CharField(default='#ffffff', max_length=7, validators=[RegexValidator('^#([0-9A-Fa-f]{6})$', 'Введите цвет в формате #ffffff.')], verbose_name='Цвет')),
                ('text_align', models.CharField(choices=[('left', 'Слева'), ('center', 'По центру'), ('right', 'Справа')], default='left', max_length=12, verbose_name='Выравнивание')),
                ('line_height', models.FloatField(default=1.1, validators=[MinValueValidator(0.8), MaxValueValidator(2.0)], verbose_name='Межстрочный интервал')),
                ('letter_spacing_px', models.FloatField(default=0, validators=[MinValueValidator(-2), MaxValueValidator(12)], verbose_name='Расстояние между буквами (px)')),
                ('text_shadow', models.BooleanField(default=True, verbose_name='Тень для читаемости')),
                ('uppercase', models.BooleanField(default=False, verbose_name='Верхний регистр')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('published', models.BooleanField(db_index=True, default=True, verbose_name='Показывать на сайте')),
            ],
            options={
                'verbose_name': 'Текст ленты времени',
                'verbose_name_plural': 'Тексты ленты времени',
                'ordering': ['order', 'id'],
            },
        ),
        migrations.RunPython(seed_history_text_blocks, unseed_history_text_blocks),
    ]
