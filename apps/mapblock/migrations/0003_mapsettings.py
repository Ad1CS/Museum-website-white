from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapblock', '0002_building_map_rotation_map_clip_path'),
    ]

    operations = [
        migrations.CreateModel(
            name='MapSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('zoom', models.PositiveIntegerField(
                    default=20,
                    verbose_name='Zoom (масштаб)',
                    help_text='1 = весь мир, 20 = ~50м над землёй.'
                )),
                ('center_lat', models.FloatField(
                    default=59.8228,
                    verbose_name='Центр — широта',
                )),
                ('center_lng', models.FloatField(
                    default=30.3508,
                    verbose_name='Центр — долгота',
                )),
            ],
            options={
                'verbose_name': 'Настройки карты',
                'verbose_name_plural': 'Настройки карты',
            },
        ),
    ]
