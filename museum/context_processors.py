from apps.news.models import NewsPost


def museum_context(request):
    """Global context available in all templates."""
    return {
        'latest_ticker_news': NewsPost.objects.filter(published=True).order_by('-date')[:5],
        'MUSEUM_NAME': 'Ленинградский мясокомбинат им. С.М. Кирова',
        'MUSEUM_SUBTITLE': 'Музей трудовой и воинской славы',
    }
