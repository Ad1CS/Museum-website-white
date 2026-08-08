import random

from django.conf import settings
from django.core.cache import cache
from apps.news.models import NewsPost
from .models import PageBackground


def _page_background_key(request):
    match = getattr(request, 'resolver_match', None)
    namespace = getattr(match, 'namespace', '') or ''
    url_name = getattr(match, 'url_name', '') or ''
    view_name = getattr(getattr(match, 'func', None), '__name__', '')

    if match is None or url_name == 'page_404' or view_name == 'page_not_found':
        return 'not_found'
    if namespace == 'about':
        return 'about'
    if namespace == 'library':
        return 'library'
    if namespace == 'gallery':
        return 'gallery'
    if namespace == 'fond':
        return 'fond'
    if namespace == 'staff':
        return 'staff'
    if namespace == 'mapblock':
        if url_name == 'plans':
            return 'buildings'
        if url_name == 'building':
            return 'building'
        return ''
    if not namespace and url_name == 'home':
        return 'home'
    if not namespace and url_name == 'history':
        return 'history'
    return ''


def _random_page_background(page_key):
    if not page_key:
        return None
    try:
        backgrounds = list(
            PageBackground.objects
            .filter(page=page_key, active=True)
            .only('page', 'title', 'image', 'order', 'created_at')
        )
    except Exception:
        return None
    return random.choice(backgrounds) if backgrounds else None


def museum_context(request):
    """Global context available in all templates. Cached for 5 minutes."""
    ticker = cache.get('ticker_news')
    if ticker is None:
        ticker = list(NewsPost.objects.filter(published=True).only('title', 'date').order_by('-date')[:5])
        cache.set('ticker_news', ticker, 300)  # 5 min
    page_background_key = _page_background_key(request)
    page_background = _random_page_background(page_background_key)
    page_background_url = ''
    if page_background and page_background.image:
        try:
            page_background_url = page_background.image.url
        except ValueError:
            page_background_url = ''
    return {
        'latest_ticker_news': ticker,
        'MUSEUM_NAME': 'Ленинградский мясокомбинат им. С.М. Кирова',
        'MUSEUM_SUBTITLE': 'Музей трудовой и воинской славы',
        'SEO_CANONICAL_URL': settings.SEO_CANONICAL_URL,
        'page_background_key': page_background_key,
        'page_background': page_background,
        'page_background_url': page_background_url,
    }
