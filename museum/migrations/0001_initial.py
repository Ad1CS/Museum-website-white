from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='HomeBackground',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=120, verbose_name='Название')),
                ('image', models.ImageField(upload_to='home/backgrounds/', verbose_name='Фон главной страницы')),
                ('active', models.BooleanField(db_index=True, default=True, verbose_name='Использовать в случайной смене')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')),
            ],
            options={
                'verbose_name': 'Фон главной страницы',
                'verbose_name_plural': 'Фоны главной страницы',
                'ordering': ['order', '-created_at'],
            },
        ),
    ]
