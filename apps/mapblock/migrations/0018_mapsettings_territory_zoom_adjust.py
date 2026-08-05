from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapblock', '0017_alter_building_page_background'),
    ]

    operations = [
        migrations.AddField(
            model_name='mapsettings',
            name='territory_zoom_adjust',
            field=models.FloatField(
                'Доп. zoom после клика по территории',
                default=0,
                help_text='Тонкая настройка приближения после клика по территории. Отрицательное значение = меньше приближение, положительное = сильнее. Например -0.10 или 0.10.',
            ),
        ),
    ]
