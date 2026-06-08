from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('library', '0001_initial')]
    operations = [
        migrations.AlterField(
            model_name='libraryitem', name='category',
            field=models.CharField(choices=[('history', 'История предприятия'), ('periodical', 'Периодика'), ('special', 'Специальная литература'), ('museum_fund', 'Литфонд музея')], default='history', max_length=20, verbose_name='Категория'),
        ),
    ]
