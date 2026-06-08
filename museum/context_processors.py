from django.core.cache import cache
from apps.news.models import NewsPost


def museum_context(request):
    """Global context available in all templates. Cached for 5 minutes."""
    ticker = cache.get('ticker_news')
    if ticker is None:
        ticker = list(NewsPost.objects.filter(published=True).only('title', 'date').order_by('-date')[:5])
        cache.set('ticker_news', ticker, 300)  # 5 min
    return {
        'latest_ticker_news': ticker,
        'MUSEUM_NAME': 'Ленинградский мясокомбинат им. С.М. Кирова',
        'MUSEUM_SUBTITLE': 'Музей трудовой и воинской славы',
    }
