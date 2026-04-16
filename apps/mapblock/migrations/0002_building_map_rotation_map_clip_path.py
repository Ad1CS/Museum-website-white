from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapblock', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='building',
            name='map_rotation',
            field=models.FloatField(default=0, verbose_name='Угол поворота (°)',
                help_text='Поворот фигуры в градусах (0–360).'),
        ),
        migrations.AddField(
            model_name='building',
            name='map_clip_path',
            field=models.CharField(
                blank=True, default='', max_length=500,
                verbose_name='Форма (clip-path polygon)',
                help_text='SVG polygon points в процентах. Оставьте пустым для прямоугольника.'
            ),
        ),
    ]
