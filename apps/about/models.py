from django.db import models


class AboutPage(models.Model):
    """Singleton — only one instance, fully editable from admin."""
    title = models.CharField('Заголовок', max_length=200, default='О проекте')
    body = models.TextField('Основной текст')
    contact_email = models.EmailField('Email', blank=True)
    contact_phone = models.CharField('Телефон', max_length=50, blank=True)
    contact_address = models.CharField('Адрес', max_length=300, blank=True)
    vk_url = models.URLField('VK', blank=True)
    telegram_url = models.URLField('Telegram', blank=True)
    youtube_url = models.URLField('YouTube', blank=True)
    extra_html = models.TextField('Дополнительный HTML (необязательно)', blank=True,
                                  help_text='Любой дополнительный контент внизу страницы')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Страница «О проекте»'
        verbose_name_plural = 'Страница «О проекте»'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Enforce singleton
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={
            'title': 'О проекте',
            'body': '',
        })
        return obj
