from django.db import models
from django.urls import reverse
import os


class LibraryItem(models.Model):
    CATEGORY_CHOICES = [
        ('book', 'Книга'),
        ('periodical', 'Периодика'),
    ]
    category = models.CharField('Категория', max_length=20, choices=CATEGORY_CHOICES, default='book')
    title = models.CharField('Название', max_length=500)
    author = models.CharField('Автор / Редактор', max_length=300, blank=True)
    year = models.CharField('Год издания', max_length=20, blank=True)
    description = models.TextField('Описание', blank=True)
    cover = models.ImageField('Обложка', upload_to='library/covers/', blank=True, null=True)
    file = models.FileField('Файл (PDF, DJVU и др.)', upload_to='library/files/')
    published = models.BooleanField('Опубликовано', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Издание'
        verbose_name_plural = 'Библиотека'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def file_ext(self):
        return os.path.splitext(self.file.name)[1].lower() if self.file else ''

    @property
    def is_viewable(self):
        return self.file_ext in ['.pdf']

    def get_absolute_url(self):
        return reverse('library:detail', args=[self.pk])
