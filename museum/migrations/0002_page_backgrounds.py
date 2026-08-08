from django.db import migrations, models
import museum.models


class Migration(migrations.Migration):

    dependencies = [
        ('museum', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='HomeBackground',
            new_name='PageBackground',
        ),
        migrations.AddField(
            model_name='pagebackground',
            name='page',
            field=models.CharField(
                choices=[
                    ('home', 'Главная'),
                    ('about', 'О проекте'),
                    ('library', 'Библиотека'),
                    ('gallery', 'Галерея'),
                    ('fond', 'Фонд'),
                    ('staff', 'Отдел кадров'),
                    ('history', 'История предприятия'),
                    ('buildings', 'Карты и планы'),
                    ('building', 'Страница здания'),
                    ('not_found', '404'),
                ],
                db_index=True,
                default='home',
                max_length=32,
                verbose_name='Страница',
            ),
        ),
        migrations.AlterModelOptions(
            name='pagebackground',
            options={
                'ordering': ['page', 'order', '-created_at'],
                'verbose_name': 'Фон страницы',
                'verbose_name_plural': 'Фоны страниц',
            },
        ),
        migrations.AlterField(
            model_name='pagebackground',
            name='image',
            field=models.ImageField(upload_to=museum.models.page_background_upload_to, verbose_name='Фон страницы'),
        ),
        migrations.AlterField(
            model_name='pagebackground',
            name='title',
            field=models.CharField(blank=True, max_length=120, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='pagebackground',
            name='active',
            field=models.BooleanField(db_index=True, default=True, verbose_name='Использовать в случайной смене'),
        ),
        migrations.AlterField(
            model_name='pagebackground',
            name='order',
            field=models.PositiveIntegerField(default=0, verbose_name='Порядок'),
        ),
        migrations.AlterField(
            model_name='pagebackground',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки'),
        ),
    ]
