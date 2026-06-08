from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('mapblock', '0005_building_main_image')]
    operations = [
        # Remove old lat/lng fields from MapSettings if they exist, add new ones
        migrations.AddField(model_name='mapsettings', name='center_x', field=models.FloatField(default=3684, verbose_name='Центр — X (пиксели)')),
        migrations.AddField(model_name='mapsettings', name='center_y', field=models.FloatField(default=2072, verbose_name='Центр — Y (пиксели)')),
        migrations.AddField(model_name='mapsettings', name='min_zoom', field=models.IntegerField(default=-2, verbose_name='Минимальный zoom')),
        migrations.AddField(model_name='mapsettings', name='max_zoom', field=models.IntegerField(default=3, verbose_name='Максимальный zoom')),
        migrations.AddField(model_name='mapsettings', name='building_zoom', field=models.IntegerField(default=1, verbose_name='Zoom показа зданий')),
        migrations.AddField(model_name='building', name='pos_x', field=models.FloatField(default=3684, verbose_name='Позиция X (пиксели)')),
        migrations.AddField(model_name='building', name='pos_y', field=models.FloatField(default=2072, verbose_name='Позиция Y (пиксели)')),
    ]
