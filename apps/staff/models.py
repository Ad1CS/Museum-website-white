from django.db import models
from django.urls import reverse


class StaffMember(models.Model):
    # Name
    last_name = models.CharField('Фамилия', max_length=100)
    first_name = models.CharField('Имя', max_length=100)
    patronymic = models.CharField('Отчество', max_length=100, blank=True)

    # Bio
    years_of_life = models.CharField('Годы жизни', max_length=100, blank=True)
    role = models.CharField('Должность', max_length=300, blank=True)
    role_years = models.CharField('Годы работы (должность)', max_length=100, blank=True)
    role2 = models.CharField('Должность 2', max_length=300, blank=True)
    role2_years = models.CharField('Годы работы (должность 2)', max_length=100, blank=True)
    role3 = models.CharField('Должность 3', max_length=300, blank=True)
    role3_years = models.CharField('Годы работы (должность 3)', max_length=100, blank=True)
    years_worked = models.CharField('Годы работы', max_length=100, blank=True)
    biography = models.TextField('Биография', blank=True)
    photo = models.ImageField('Фотография', upload_to='staff/photos/', blank=True, null=True)

    # Links to fond
    personal_fund = models.ForeignKey(
        'fond.Fund', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='personal_fund_of', verbose_name='Личный фонд'
    )

    published = models.BooleanField('Опубликовано', default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name, self.patronymic]
        return ' '.join(p for p in parts if p)

    @property
    def first_letter(self):
        return self.last_name[0].upper() if self.last_name else '?'

    def get_absolute_url(self):
        return reverse('staff:detail', args=[self.pk])
