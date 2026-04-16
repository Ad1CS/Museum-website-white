from django.db import migrations

def create_initial_about(apps, schema_editor):
    AboutPage = apps.get_model('about', 'AboutPage')
    if not AboutPage.objects.exists():
        AboutPage.objects.create(
            pk=1,
            title='О проекте',
            body='Деятельность историко-краеведческого проекта направлена на сохранение памяти о Ленинградском\nмясокомбинате, о трудовом и воинском подвиге его работников. Это частная некоммерческая\nинициатива, основанная на добровольной деятельности группы энтузиастов. На сайте проекта можно\nознакомиться с историей предприятия, а также с уникальными материалами из личных фондов,\nоткрытых источников и архива ООО «Самсон-Мед». Проводятся также открытые\nмероприятия: лекции, выставки, встречи.',
            contact_email='lmkmuseum@yandex.ru',
            vk_url='https://vk.com/myasokombinatkirova',
            contact_address='Санкт-Петербург, Московское шоссе',
        )

class Migration(migrations.Migration):
    dependencies = [('about', '0001_initial')]
    operations = [migrations.RunPython(create_initial_about, migrations.RunPython.noop)]
