from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffmember',
            name='years_of_life',
            field=models.CharField(blank=True, max_length=100, verbose_name='Годы жизни'),
        ),
        migrations.AddField(
            model_name='staffmember',
            name='role_years',
            field=models.CharField(blank=True, max_length=100, verbose_name='Годы работы (должность)'),
        ),
        migrations.AddField(
            model_name='staffmember',
            name='role2',
            field=models.CharField(blank=True, max_length=300, verbose_name='Должность 2'),
        ),
        migrations.AddField(
            model_name='staffmember',
            name='role2_years',
            field=models.CharField(blank=True, max_length=100, verbose_name='Годы работы (должность 2)'),
        ),
        migrations.AddField(
            model_name='staffmember',
            name='role3',
            field=models.CharField(blank=True, max_length=300, verbose_name='Должность 3'),
        ),
        migrations.AddField(
            model_name='staffmember',
            name='role3_years',
            field=models.CharField(blank=True, max_length=100, verbose_name='Годы работы (должность 3)'),
        ),
    ]
