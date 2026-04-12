from django.db import migrations

def create_initial_about(apps, schema_editor):
    AboutPage = apps.get_model('about', 'AboutPage')
    if not AboutPage.objects.exists():
        AboutPage.objects.create(
            pk=1,
            title='О проекте',
            body='Деятельность историко-краеведческого проекта направлена на сохранение памяти о Ленинградском мясокомбинате, о трудовом и воинском подвиге его работников. Это частная некоммерческая инициатива, основанная на добровольной деятельности группы энтузиастов. На сайте проекта можно ознакомиться с историей предприятия, а также с уникальными материалами из личных фондов, открытых источников и архива ООО «Самсон-Мед». Проводятся также открытые мероприятия: лекции, выставки, встречи.',
            contact_email='museum@kirovmeat.ru',
            contact_address='Санкт-Петербург, Московское шоссе',
        )

class Migration(migrations.Migration):
    dependencies = [('about', '0001_initial')]
    operations = [migrations.RunPython(create_initial_about, migrations.RunPython.noop)]
