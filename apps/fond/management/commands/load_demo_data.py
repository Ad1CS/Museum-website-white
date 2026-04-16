"""
Management command to load sample/demo data.
Run: python manage.py load_demo_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
import datetime


class Command(BaseCommand):
    help = 'Load sample demo data for all museum sections'

    def handle(self, *args, **options):
        self.stdout.write('Loading demo data...')
        self._load_about()
        self._load_news()
        self._load_funds()
        self._load_staff()
        self._load_map()
        self._load_gallery()
        self.stdout.write(self.style.SUCCESS('Demo data loaded successfully!'))

    def _load_about(self):
        from apps.about.models import AboutPage
        page = AboutPage.load()
        page.contact_email = 'lmkmuseum@yandex.ru'
        page.vk_url = 'https://vk.com/myasokombinatkirova'
        page.body = (
            "Деятельность историко-краеведческого проекта направлена на сохранение памяти о Ленинградском\n"
            "мясокомбинате, о трудовом и воинском подвиге его работников. Это частная некоммерческая\n"
            "инициатива, основанная на добровольной деятельности группы энтузиастов. На сайте проекта можно\n"
            "ознакомиться с историей предприятия, а также с уникальными материалами из личных фондов,\n"
            "открытых источников и архива ООО «Самсон-Мед». Проводятся также открытые\n"
            "мероприятия: лекции, выставки, встречи."
        )
        page.save()
        self.stdout.write('  ✓ About page updated')

    def _load_news(self):
        from apps.news.models import NewsPost
        posts = [
            {'title': 'Открытие выставки «Блокадный мясокомбинат»',
             'body': 'В музее открылась постоянная экспозиция, посвящённая работе предприятия в годы блокады Ленинграда. В витринах представлены подлинные документы, личные вещи сотрудников и архивные фотографии 1941–1944 годов. На открытии присутствовали потомки работников блокадного комбината.',
             'date': datetime.date(2026, 2, 18)},
            {'title': 'Передача архива семьи Громовых',
             'body': 'Семья потомственных работников комбината передала в фонды музея личный архив Анны Петровны Громовой — бригадира убойного цеха в годы блокады. В составе архива — письма, фотографии и памятные предметы 1935–1968 годов.',
             'date': datetime.date(2026, 3, 5)},
            {'title': 'Первые результаты оцифровки фонда №12',
             'body': 'Завершён первый этап оцифровки архивных документов фонда №12. В цифровой каталог добавлено 347 новых карточек. Работа продолжается.',
             'date': datetime.date(2026, 3, 1)},
            {'title': 'Экспедиция по записи воспоминаний ветеранов',
             'body': 'Музей объявляет о начале экспедиции по сбору устных воспоминаний ветеранов предприятия и их потомков. Экспедиция пройдёт в апреле 2026 года.',
             'date': datetime.date(2026, 1, 14)},
        ]
        for p in posts:
            NewsPost.objects.get_or_create(title=p['title'], defaults={'body': p['body'], 'date': p['date'], 'published': True})
        self.stdout.write('  ✓ News posts created')

    def _load_funds(self):
        from apps.fond.models import Fund, Inventory, ArchiveCase, FondItem, ItemType, Period
        f1, _ = Fund.objects.get_or_create(code='Ф-1', defaults={
            'name': 'ЛЕНИНГРАДСКИЙ МЯСОКОМБИНАТ ИМ. С.М. КИРОВА',
            'description': 'Основной фонд предприятия. Приказы, планы, отчёты по производству.',
            'date_start': 1930, 'date_end': 1941
        })
        f2, _ = Fund.objects.get_or_create(code='Ф-2', defaults={
            'name': 'ДОКУМЕНТЫ БЛОКАДНОГО ПЕРИОДА',
            'description': 'Переписка, приказы, ведомости о работе комбината в условиях блокады.',
            'date_start': 1941, 'date_end': 1945
        })
        f3, _ = Fund.objects.get_or_create(code='Ф-3', defaults={
            'name': 'ЛИЧНЫЙ ФОНД ДИРЕКТОРА ПЕТРОВА В.И.',
            'description': 'Личные документы, переписка, фотографии директора комбината 1961–1979 гг.',
            'date_start': 1961, 'date_end': 1979
        })
        f4, _ = Fund.objects.get_or_create(code='Ф-4', defaults={
            'name': 'ФОТОФОНД МЯСОКОМБИНАТА',
            'description': 'Фотографии предприятия, сотрудников, событий и продукции.',
            'date_start': 1930, 'date_end': 1992
        })

        inv1, _ = Inventory.objects.get_or_create(fund=f1, number='1', defaults={'name': 'Приказы и распоряжения'})
        ArchiveCase.objects.get_or_create(inventory=inv1, number='1', defaults={
            'title': 'Приказы по мясокомбинату за 1941 год',
            'date_start': datetime.date(1941, 1, 1), 'date_end': datetime.date(1941, 12, 31),
            'sheets_count': 182, 'digitized': True
        })
        ArchiveCase.objects.get_or_create(inventory=inv1, number='2', defaults={
            'title': 'Приказы по мясокомбинату за 1942 год',
            'date_start': datetime.date(1942, 1, 1), 'date_end': datetime.date(1942, 12, 31),
            'sheets_count': 154, 'digitized': False
        })

        items = [
            {'title': 'Советский камполон — образец продукции мясокомбината', 'item_type': ItemType.OBJECT,
             'period': Period.P1941, 'kp_number': 'КП 264437', 'inventory_number': 'ГМИ СПб Инв.№-V-Б-496р',
             'goskatalog_number': '62751852', 'size': '1.5×6.5×9 см', 'creation_place': 'СССР, РСФСР, Ленинград',
             'creation_date_text': '1941–1945 гг.', 'fund': f2},
            {'title': 'Фотография главного здания мясокомбината, вид с фасада', 'item_type': ItemType.PHOTO,
             'period': Period.P1931, 'kp_number': 'КП 12045', 'inventory_number': 'ГМИ СПб Инв.№-Ф-1204',
             'size': '13×18 см', 'creation_place': 'Ленинград', 'creation_date_text': '1935 г.', 'fund': f4},
            {'title': 'Приказ №47 об организации ночных смен в период блокады', 'item_type': ItemType.DOCUMENT,
             'period': Period.P1941, 'kp_number': 'КП 8823', 'inventory_number': 'Ф.2 Оп.1 Д.47',
             'size': '21×29.7 см', 'creation_place': 'Ленинград', 'creation_date_text': '1942 г.', 'fund': f2},
            {'title': 'Удостоверение ударника производства Громовой А.П.', 'item_type': ItemType.DOCUMENT,
             'period': Period.P1931, 'kp_number': 'КП 5521', 'inventory_number': 'ГМИ СПб Инв.№-Д-0521',
             'size': '7×10 см', 'creation_place': 'Ленинград', 'creation_date_text': '1936 г.', 'fund': f1},
            {'title': 'Орден Трудового Красного Знамени, врученный коллективу', 'item_type': ItemType.OBJECT,
             'period': Period.P1946, 'kp_number': 'КП 41100', 'inventory_number': 'ГМИ СПб Инв.№-V-А-100',
             'size': 'Ø 42 мм', 'creation_place': 'СССР', 'creation_date_text': '1948 г.', 'fund': f1},
            {'title': 'Карта-схема территории предприятия', 'item_type': ItemType.DOCUMENT,
             'period': Period.P1931, 'kp_number': 'КП 6600', 'inventory_number': 'ГМИ СПб Инв.№-Д-0600',
             'size': '60×84 см', 'creation_place': 'Ленинград', 'creation_date_text': '1933 г.', 'fund': f1},
        ]
        for item_data in items:
            FondItem.objects.get_or_create(kp_number=item_data['kp_number'], defaults={**item_data, 'published': True})
        self.stdout.write('  ✓ Fund items created')

    def _load_staff(self):
        from apps.fond.models import Fund
        from apps.staff.models import StaffMember
        f3 = Fund.objects.filter(code='Ф-3').first()
        members = [
            {'last_name': 'Громова', 'first_name': 'Анна', 'patronymic': 'Петровна',
             'role': 'Начальник смены убойного цеха', 'years_worked': '1935–1968',
             'biography': 'Анна Петровна Громова начала работу на мясокомбинате в 1935 году разнорабочей. К 1940 году возглавила смену убойного цеха. В годы блокады обеспечивала бесперебойную работу цеха в экстремальных условиях. Награждена медалью «За оборону Ленинграда».'},
            {'last_name': 'Петров', 'first_name': 'Василий', 'patronymic': 'Иванович',
             'role': 'Директор мясокомбината', 'years_worked': '1961–1979',
             'biography': 'Василий Иванович Петров руководил предприятием в период его наибольшего расцвета. При нём были введены в строй новые производственные мощности, численность работников возросла до 3 200 человек. Заслуженный работник пищевой промышленности РСФСР.',
             'personal_fund': f3},
            {'last_name': 'Захаров', 'first_name': 'Михаил', 'patronymic': 'Сергеевич',
             'role': 'Главный инженер', 'years_worked': '1938–1955',
             'biography': 'Михаил Сергеевич Захаров разработал систему аварийного электроснабжения цехов в начале блокады, что позволило сохранить производство. После войны руководил восстановлением разрушенных корпусов.'},
            {'last_name': 'Воронова', 'first_name': 'Евдокия', 'patronymic': 'Фёдоровна',
             'role': 'Бригадир колбасного цеха', 'years_worked': '1941–1944',
             'biography': 'Евдокия Фёдоровна Воронова работала на комбинате в годы блокады. Её бригада выполняла план при жесточайших условиях, нередко живя прямо на предприятии в период обстрелов.'},
            {'last_name': 'Кузнецов', 'first_name': 'Алексей', 'patronymic': 'Иванович',
             'role': 'Технолог производства', 'years_worked': '1933–1960', 'biography': ''},
            {'last_name': 'Морозова', 'first_name': 'Нина', 'patronymic': 'Александровна',
             'role': 'Лаборант ОТК', 'years_worked': '1950–1985', 'biography': ''},
            {'last_name': 'Сидоров', 'first_name': 'Фёдор', 'patronymic': 'Михайлович',
             'role': 'Механик холодильного цеха', 'years_worked': '1940–1975', 'biography': ''},
            {'last_name': 'Лебедева', 'first_name': 'Галина', 'patronymic': 'Николаевна',
             'role': 'Нормировщик', 'years_worked': '1944–1970', 'biography': ''},
            {'last_name': 'Иванов', 'first_name': 'Пётр', 'patronymic': 'Васильевич',
             'role': 'Первый начальник скотобазы', 'years_worked': '1930–1941', 'biography': ''},
            {'last_name': 'Белова', 'first_name': 'Тамара', 'patronymic': 'Константиновна',
             'role': 'Главный бухгалтер', 'years_worked': '1955–1992', 'biography': ''},
        ]
        for m in members:
            StaffMember.objects.get_or_create(
                last_name=m['last_name'], first_name=m['first_name'],
                defaults={**m, 'published': True}
            )
        self.stdout.write('  ✓ Staff members created')

    def _load_map(self):
        from apps.mapblock.models import Building
        buildings = [
            {'slug': 'lifestak', 'name': 'Лайф-стак', 'built_years': '1930–1932',
             'description': 'Скотобаза — первый объект, возведённый на территории будущего мясокомбината. Принимала скот, поступавший со всей Ленинградской области. В годы блокады скотобаза продолжала работу в условиях острой нехватки кормов и постоянных обстрелов.',
             'map_left': 15, 'map_top': 20, 'map_width': 18, 'map_height': 22, 'order': 1},
            {'slug': 'util-zavod', 'name': 'Утиль-завод', 'built_years': '1933',
             'description': 'Завод по переработке вторичного сырья — шкур, костей, жира. Обеспечивал безотходное производство. В 1941–1944 гг. использовался для нужд обороны города.',
             'map_left': 38, 'map_top': 15, 'map_width': 22, 'map_height': 18, 'order': 2},
            {'slug': 'uboyny-korpus', 'name': 'Убойно-разделочный корпус', 'built_years': '1932',
             'description': 'Главный производственный корпус комбината. Проектировался по образцу современных американских мясокомбинатов. Серьёзно пострадал в ходе авиационных налётов 1941–1942 гг., восстановлен к 1946 году.',
             'map_left': 20, 'map_top': 50, 'map_width': 25, 'map_height': 20, 'order': 3},
            {'slug': 'holodilno-kolbasny', 'name': 'Холодильно-колбасный корпус', 'built_years': '1935',
             'description': 'Введён в эксплуатацию в 1935 году. Включал холодильные камеры ёмкостью 5 000 тонн и цех по производству колбасных изделий. В блокаду стал одним из ключевых объектов продовольственного обеспечения Ленинграда.',
             'map_left': 50, 'map_top': 45, 'map_width': 28, 'map_height': 24, 'order': 4},
            {'slug': 'administrativny', 'name': 'Административный корпус', 'built_years': '1931',
             'description': 'Построен одновременно с первыми производственными корпусами. Здесь размещались дирекция, плановый отдел и партийный комитет предприятия. В настоящее время в корпусе находится музей трудовой и воинской славы.',
             'map_left': 65, 'map_top': 15, 'map_width': 16, 'map_height': 16, 'order': 5},
        ]
        for b in buildings:
            Building.objects.get_or_create(slug=b['slug'], defaults={**b, 'published': True})
        self.stdout.write('  ✓ Map buildings created')

    def _load_gallery(self):
        from apps.gallery.models import Album, HistoricalPeriod, Media
        albums = [
            {'title': 'Первые строители комбината', 'period': HistoricalPeriod.PRE_SOVIET, 'order': 1},
            {'title': 'Строительство главного корпуса', 'period': HistoricalPeriod.CONSTRUCTION, 'order': 1},
            {'title': 'Торжественное открытие, 1933', 'period': HistoricalPeriod.CONSTRUCTION, 'order': 2},
            {'title': 'Рабочие будни 1930-х', 'period': HistoricalPeriod.PREWAR, 'order': 1},
            {'title': 'Стахановцы комбината', 'period': HistoricalPeriod.PREWAR, 'order': 2},
            {'title': 'Комбинат в годы блокады', 'period': HistoricalPeriod.BLOCKADE, 'order': 1},
            {'title': 'Восстановление предприятия, 1944–1950', 'period': HistoricalPeriod.GOLDEN, 'order': 1},
            {'title': 'Юбилей 50 лет комбинату, 1980', 'period': HistoricalPeriod.GOLDEN, 'order': 2},
            {'title': 'Реорганизация предприятия', 'period': HistoricalPeriod.POST_SOVIET, 'order': 1},
            {'title': 'Музей трудовой и воинской славы', 'period': HistoricalPeriod.MODERN, 'order': 1},
        ]
        for a in albums:
            Album.objects.get_or_create(title=a['title'], defaults={**a, 'published': True})
        self.stdout.write('  ✓ Gallery albums created')
