from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='AboutPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='О проекте', max_length=200, verbose_name='Заголовок')),
                ('body', models.TextField(verbose_name='Основной текст')),
                ('contact_email', models.EmailField(blank=True, max_length=254, verbose_name='Email')),
                ('contact_phone', models.CharField(blank=True, max_length=50, verbose_name='Телефон')),
                ('contact_address', models.CharField(blank=True, max_length=300, verbose_name='Адрес')),
                ('vk_url', models.URLField(blank=True, verbose_name='VK')),
                ('telegram_url', models.URLField(blank=True, verbose_name='Telegram')),
                ('youtube_url', models.URLField(blank=True, verbose_name='YouTube')),
                ('extra_html', models.TextField(blank=True, help_text='Любой дополнительный контент внизу страницы', verbose_name='Дополнительный HTML (необязательно)')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'Страница «О проекте»', 'verbose_name_plural': 'Страница «О проекте»'},
        ),
    ]
