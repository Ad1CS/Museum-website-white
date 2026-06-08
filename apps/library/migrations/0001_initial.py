from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='LibraryItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('book', 'Книга'), ('periodical', 'Периодика')], default='book', max_length=20, verbose_name='Категория')),
                ('title', models.CharField(max_length=500, verbose_name='Название')),
                ('author', models.CharField(blank=True, max_length=300, verbose_name='Автор / Редактор')),
                ('year', models.CharField(blank=True, max_length=20, verbose_name='Год издания')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('cover', models.ImageField(blank=True, null=True, upload_to='library/covers/', verbose_name='Обложка')),
                ('file', models.FileField(upload_to='library/files/', verbose_name='Файл (PDF, DJVU и др.)')),
                ('published', models.BooleanField(default=True, verbose_name='Опубликовано')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'verbose_name': 'Издание', 'verbose_name_plural': 'Библиотека', 'ordering': ['-created_at']},
        ),
    ]
