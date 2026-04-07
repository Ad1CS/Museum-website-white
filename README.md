# Музей трудовой и воинской славы
## Ленинградский мясокомбинат им. С.М. Кирова — Цифровой музей

Django 5.0 · PostgreSQL · WhiteNoise · Render-ready

---

## Структура проекта

```
museum_django/
├── manage.py
├── requirements.txt
├── render.yaml              ← Конфиг для деплоя на Render
├── .env.example             ← Шаблон переменных окружения
│
├── museum/                  ← Главное Django-приложение
│   ├── settings.py
│   ├── urls.py
│   ├── views.py             ← Главная страница
│   ├── context_processors.py
│   └── wsgi.py
│
├── apps/
│   ├── fond/                ← Фонд (каталог, фонды, описи, дела)
│   ├── gallery/             ← Фотогалерея (альбомы, фото, периоды)
│   ├── staff/               ← Сотрудники
│   ├── mapblock/            ← Интерактивная карта (здания)
│   └── news/                ← Новости
│
├── templates/
│   ├── base/                ← base.html, home.html
│   ├── fond/                ← catalog, item_detail, funds_list, fund_detail
│   ├── gallery/             ← home, album_detail
│   ├── staff/               ← list, detail
│   ├── mapblock/            ← map, building
│   └── news/                ← list, detail
│
└── static/
    ├── css/museum.css       ← Полная дизайн-система
    └── js/museum.js         ← Навигация, drawer, lightbox
```

---

## Локальный запуск

### 1. Клонировать и настроить окружение

```bash
git clone <your-repo-url>
cd museum_django

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Настроить переменные окружения

```bash
cp .env.example .env
# Отредактируйте .env — задайте SECRET_KEY и при необходимости DATABASE_URL
```

### 3. Применить миграции и загрузить демо-данные

```bash
python manage.py migrate
python manage.py load_demo_data      # Загрузить тестовые данные
python manage.py createsuperuser     # Создать администратора
```

### 4. Запустить сервер

```bash
python manage.py runserver
```

Сайт: http://127.0.0.1:8000  
Админка: http://127.0.0.1:8000/admin

---

## Деплой на Render

### Способ 1 — через render.yaml (рекомендуется)

1. Залить проект на GitHub
2. Зайти на [render.com](https://render.com) → New → Blueprint
3. Указать репозиторий — Render автоматически прочитает `render.yaml`
4. Render создаст web service + PostgreSQL базу
5. После деплоя выполнить в Render Shell:
   ```bash
   python manage.py createsuperuser
   python manage.py load_demo_data
   ```

### Способ 2 — вручную

1. New → Web Service → выбрать репозиторий
2. Environment: **Python 3**
3. Build Command:
   ```
   pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   ```
4. Start Command:
   ```
   gunicorn museum.wsgi:application --bind 0.0.0.0:$PORT
   ```
5. Добавить Environment Variables:
   - `SECRET_KEY` — длинная случайная строка
   - `DEBUG` = `False`
   - `ALLOWED_HOSTS` = `.onrender.com`
   - `DATABASE_URL` — строка подключения PostgreSQL (из Render Databases)

### Подключение собственного домена

В Render → Settings → Custom Domains → Add Custom Domain  
Прописать CNAME или A-запись у регистратора домена.  
После подключения добавить домен в `ALLOWED_HOSTS` в настройках Render.

---

## Работа с Админкой

Адрес: `/admin/`

| Раздел | Возможности |
|--------|-------------|
| **Фонд** | Предметы с фото, тип, период, учётные номера, связи со штатом |
| **Фонды / Описи / Дела** | Полная архивная иерархия, отметка «оцифровано» |
| **Фотогалерея** | Альбомы по периодам, загрузка фото, связь с фондом |
| **Сотрудники** | Биография, фото, личный фонд |
| **Карта** | Здания, координаты контуров на карте (%), фотографии |
| **Новости** | Публикации с датой и фото |

### Добавление предмета фонда

1. Фонд → Предметы фонда → Добавить предмет фонда
2. Заполнить: название, тип, период, учётные номера
3. Загрузить фотографию
4. Привязать к фонду и/или делу
5. При необходимости — связать с сотрудником
6. Поставить галочку «Опубликовано» → Сохранить

### Добавление фотографий в галерею

1. Фотогалерея → Альбомы → Выбрать или создать альбом
2. В нижней части формы — инлайн «Фотографии»
3. Загрузить фото, добавить подпись и дату
4. Если у фото есть физический оригинал в фонде — указать «Карточка в фонде»

### Настройка карты

1. Карта → Здания на карте → Выбрать здание
2. В разделе «Позиция на карте» — задать координаты контура в процентах
3. Прикрепить фотографии здания из галереи

---

## Расширение проекта

- **Полнотекстовый поиск**: добавить `django.contrib.postgres.search` (PostgreSQL)
- **REST API**: добавить `djangorestframework` для мобильного приложения
- **Загрузка архивных PDF**: добавить поле `pdf_file` в `ArchiveCase`
- **Многоязычность**: использовать `django.conf.urls.i18n`
- **Карта в Leaflet.js**: заменить схему на реальную карту с тайлами

---

## Технологии

- **Backend**: Django 5.0, Python 3.12
- **База данных**: SQLite (разработка), PostgreSQL (продакшн)
- **Статика**: WhiteNoise (раздача статики без nginx)
- **Сервер**: Gunicorn
- **Хостинг**: Render (бесплатный tier для демо)
- **Фронтенд**: Чистый HTML/CSS/JS (без фреймворков), дизайн-система в `museum.css`
- **Шрифты**: Oswald + PT Serif (Google Fonts)

---

## Запуск локально (быстрый старт)

```bash
# 1. Скопируй .env
cp .env.example .env
# .env уже содержит DEBUG=True — статика будет раздаваться без collectstatic

# 2. Установи зависимости
pip install -r requirements.txt

# 3. Примени миграции
python manage.py migrate

# 4. Загрузи демо-данные (опционально)
python manage.py load_demo_data

# 5. Запусти сервер
python manage.py runserver
```

> **Важно:** без файла `.env` (или при `DEBUG=False`) Django использует
> `CompressedManifestStaticFilesStorage`, которому нужен предварительный
> `python manage.py collectstatic --noinput`.
> При `DEBUG=True` статика раздаётся напрямую из `static/` — без collectstatic.

## Деплой на Render

`render.yaml` автоматически запускает `collectstatic` и `migrate` при каждом деплое.
Никаких дополнительных шагов не требуется.
