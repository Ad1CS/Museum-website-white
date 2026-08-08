from django.db import migrations, models
import django.core.validators


def create_home_background_settings(apps, schema_editor):
    HomeBackgroundSettings = apps.get_model('museum', 'HomeBackgroundSettings')
    HomeBackgroundSettings.objects.get_or_create(
        pk=1,
        defaults={
            'enabled': False,
            'interval_seconds': 8,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ('museum', '0002_page_backgrounds'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PageBackground',
            new_name='HomeBackground',
        ),
        migrations.RemoveField(
            model_name='homebackground',
            name='page',
        ),
        migrations.AlterModelOptions(
            name='homebackground',
            options={
                'ordering': ['order', '-created_at'],
                'verbose_name': 'Фон главной страницы',
                'verbose_name_plural': 'Фоны главной страницы',
            },
        ),
        migrations.AlterField(
            model_name='homebackground',
            name='image',
            field=models.ImageField(upload_to='home/backgrounds/', verbose_name='Фон главной страницы'),
        ),
        migrations.CreateModel(
            name='HomeBackgroundSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enabled', models.BooleanField(default=False, verbose_name='Включить смену фона')),
                (
                    'interval_seconds',
                    models.PositiveIntegerField(
                        default=8,
                        help_text='Как часто менять фон на главной странице. Минимум 2, максимум 120 секунд.',
                        validators=[
                            django.core.validators.MinValueValidator(2),
                            django.core.validators.MaxValueValidator(120),
                        ],
                        verbose_name='Интервал смены (секунды)',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Настройка фона главной страницы',
                'verbose_name_plural': 'Настройки фона главной страницы',
            },
        ),
        migrations.RunPython(create_home_background_settings, migrations.RunPython.noop),
    ]
