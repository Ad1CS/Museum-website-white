from django.db import models
from django.urls import reverse


class NewsPost(models.Model):
    title = models.CharField('Заголовок', max_length=400)
    body = models.TextField('Текст')
    date = models.DateField('Дата')
    image = models.ImageField('Фотография', upload_to='news/', blank=True, null=True)
    published = models.BooleanField('Опубликовано', default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news:detail', args=[self.pk])
